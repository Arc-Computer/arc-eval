"""
Agent-as-a-Judge framework with modular judge architecture.

Based on MetaAuto AI's ICML 2025 research, this module implements Agent-as-a-Judge
methodology that transforms evaluation from simple pass/fail to continuous improvement loops.
"""

import logging
from typing import Dict, List, Optional, Any

from .api_manager import APIManager
from .base import JudgmentResult, ContinuousFeedback
from .domain import SecurityJudge, MLJudge, FinanceJudge
from agent_eval.core.types import AgentOutput, EvaluationScenario


logger = logging.getLogger(__name__)


class AgentJudge:
    """Main Agent-as-a-Judge evaluation framework."""
    
    def __init__(self, domain: str, enable_confidence_calibration: bool = False, preferred_model: str = "auto"):
        """Initialize Agent Judge for specific domain."""
        self.domain = domain
        self.api_manager = APIManager(preferred_model=preferred_model)
        self.enable_confidence_calibration = enable_confidence_calibration
        
        # Initialize domain-specific judge
        if domain == "security":
            self.judge = SecurityJudge(self.api_manager, enable_confidence_calibration)
        elif domain == "ml":
            self.judge = MLJudge(self.api_manager, enable_confidence_calibration)
        elif domain == "finance":
            self.judge = FinanceJudge(self.api_manager, enable_confidence_calibration)
        else:
            raise ValueError(f"Domain '{domain}' not yet implemented")
    
    def evaluate_scenario(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> JudgmentResult:
        """Evaluate single scenario with Agent-as-a-Judge."""
        return self.judge.evaluate(agent_output, scenario)
    
    def evaluate_batch(self, agent_outputs: List[AgentOutput], scenarios: List[EvaluationScenario]) -> List[JudgmentResult]:
        """Evaluate multiple scenarios with continuous feedback.
        
        Automatically uses batch processing for 5+ scenarios to reduce costs by 50%.
        """
        # Check if we have enough scenarios for batch processing
        from agent_eval.core.constants import BATCH_PROCESSING_THRESHOLD
        
        if len(scenarios) >= BATCH_PROCESSING_THRESHOLD:
            # Use batch evaluation for efficiency
            logger.info(f"Using batch evaluation for {len(scenarios)} scenarios (threshold: {BATCH_PROCESSING_THRESHOLD})")
            
            # Create evaluation pairs
            evaluations = list(zip(agent_outputs, scenarios))
            
            # Delegate to the domain judge's batch evaluation
            return self.judge.evaluate_batch(evaluations)
        else:
            # Fall back to sequential evaluation for small batches
            logger.info(f"Using sequential evaluation for {len(scenarios)} scenarios (below threshold)")
            results = []
            
            for output, scenario in zip(agent_outputs, scenarios):
                try:
                    result = self.evaluate_scenario(output, scenario)
                    results.append(result)
                    logger.info(f"Evaluated scenario {scenario.id}: {result.judgment}")
                except Exception as e:
                    logger.error(f"Failed to evaluate scenario {scenario.id}: {e}")
                    # Continue with other scenarios
                    continue
            
            return results
    
    def generate_improvement_report(self, results: List[JudgmentResult], agent_outputs: Optional[List[AgentOutput]] = None) -> Dict[str, Any]:
        """Generate comprehensive improvement report with bias detection."""
        if not results:
            return {"error": "No evaluation results available"}
        
        feedback = self.judge.generate_continuous_feedback(results)
        
        # Calculate metrics
        total_scenarios = len(results)
        passed = len([r for r in results if r.judgment == "pass"])
        failed = len([r for r in results if r.judgment == "fail"])
        warnings = len([r for r in results if r.judgment == "warning"])
        
        avg_confidence = sum(r.confidence for r in results) / total_scenarios
        total_cost = self.api_manager.total_cost
        
        # Generate bias detection metrics for transparency using actual outputs
        bias_metrics = None
        if agent_outputs:
            from agent_eval.evaluation.bias_detection import BasicBiasDetection
            bias_detector = BasicBiasDetection()
            
            # Extract content from agent outputs for bias analysis
            output_contents = [output.normalized_output for output in agent_outputs[:len(results)]]
            bias_metrics = bias_detector.generate_bias_report(results, output_contents)
        else:
            # Fallback if no outputs provided (shouldn't happen in normal usage)
            from agent_eval.evaluation.bias_detection import BasicBiasDetection
            bias_detector = BasicBiasDetection()
            dummy_outputs = [""] * len(results)  # Empty strings for minimal bias analysis
            bias_metrics = bias_detector.generate_bias_report(results, dummy_outputs)
        
        return {
            "summary": {
                "total_scenarios": total_scenarios,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "pass_rate": passed / total_scenarios,
                "average_confidence": avg_confidence,
                "total_cost": total_cost,
                "bias_risk_level": bias_metrics.overall_bias_risk,
                "batch_processing_used": total_scenarios >= 5,
                "estimated_savings": total_cost if total_scenarios >= 5 else 0.0  # 50% savings with batch
            },
            "continuous_feedback": {
                "strengths": feedback.strengths,
                "weaknesses": feedback.weaknesses,
                "improvement_recommendations": feedback.specific_improvements,
                "training_suggestions": feedback.training_suggestions,
                "compliance_gaps": feedback.compliance_gaps
            },
            "bias_detection": {
                "overall_risk": bias_metrics.overall_bias_risk,
                "length_bias": bias_metrics.length_bias_score,
                "position_bias": bias_metrics.position_bias_score,
                "style_bias": bias_metrics.style_bias_score,
                "total_evaluations": len(results),
                "recommendations": bias_metrics.recommendations
            } if bias_metrics else None,
            "reward_signals": {
                result.scenario_id: result.reward_signals 
                for result in results
            },
            "detailed_results": [
                {
                    "scenario_id": r.scenario_id,
                    "judgment": r.judgment,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning,
                    "model_used": r.model_used,
                    "evaluation_time": r.evaluation_time
                }
                for r in results
            ]
        }


# Maintain backwards compatibility - import the main class for existing code
__all__ = ["AgentJudge", "JudgmentResult", "ContinuousFeedback"]
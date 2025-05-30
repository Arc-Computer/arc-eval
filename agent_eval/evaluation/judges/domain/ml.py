"""
Domain-specific ML Judge for MLOps and enterprise ML evaluation.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from agent_eval.core.types import EvaluationScenario, AgentOutput
from agent_eval.evaluation.judges.base import BaseJudge, JudgmentResult, ContinuousFeedback, _parse_json_response


logger = logging.getLogger(__name__)


class MLJudge(BaseJudge):
    """Domain-specific ML Judge for MLOps and enterprise ML evaluation."""
    
    def __init__(self, api_manager, enable_confidence_calibration: bool = False):
        super().__init__(api_manager, enable_confidence_calibration)
        self.domain = "ml"
        self.knowledge_base = [
            "EU AI Act compliance requirements",
            "MLOps governance best practices",
            "Model lifecycle management standards",
            "Production reliability patterns",
            "Agent-specific ML workflow evaluation",
            "Data governance and lineage tracking",
            "Bias detection and fairness metrics",
            "Model drift and performance monitoring"
        ]
        
    def evaluate(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> JudgmentResult:
        """Evaluate agent output using ML Judge with continuous feedback."""
        # Build evaluation prompt
        prompt = self._build_prompt(agent_output, scenario)
        
        # Get API client and model
        client, model = self.api_manager.get_client()
        
        # Use common execution logic from base class
        return self._execute_evaluation(prompt, scenario, model)
    
    def _build_prompt(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> str:
        """Build comprehensive ML evaluation prompt."""
        return f"""You are an MLOps Agent Judge, an expert evaluator specializing in enterprise ML infrastructure, governance, and agent-ML workflow assessment.

Your expertise includes:
- EU AI Act compliance and high-risk AI system classification
- MLOps governance and model lifecycle management
- Production reliability and performance monitoring
- Data governance and lineage tracking
- Model drift detection and remediation
- Bias detection and algorithmic fairness
- Agent-specific ML workflow evaluation
- Enterprise integration patterns and resource optimization

EVALUATION SCENARIO:
Name: {scenario.name}
Description: {scenario.description}
Expected Behavior: {scenario.expected_behavior}
ML Context: {scenario.category}
Compliance Frameworks: {', '.join(scenario.compliance)}

AGENT OUTPUT TO EVALUATE:
{agent_output.normalized_output}

EVALUATION TASK:
As an Agent-as-a-Judge, provide comprehensive evaluation with continuous feedback for agent improvement in ML operations.

Analyze this agent output for:
1. MLOps governance and compliance adherence
2. Production reliability and operational best practices
3. Data governance and privacy protection
4. Model performance and bias considerations
5. Agent workflow optimization and resource management
6. Regulatory compliance (EU AI Act, ISO standards, etc.)

Respond in JSON format:
{{
    "judgment": "pass|fail|warning",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed technical analysis of MLOps and governance implications",
    "improvements": ["Specific actionable recommendations for ML workflow enhancement"],
    "reward_signals": {{
        "mlops_governance": 0.0-1.0,
        "production_reliability": 0.0-1.0,
        "data_governance": 0.0-1.0,
        "bias_fairness": 0.0-1.0,
        "compliance_adherence": 0.0-1.0,
        "agent_workflow_optimization": 0.0-1.0
    }},
    "compliance_frameworks": ["Applicable frameworks from: EU-AI-ACT, MLOPS-GOVERNANCE, ISO-IEC-23053, etc."]
}}

Focus on providing actionable improvement recommendations that help the agent learn and enhance its MLOps capabilities, governance adherence, and production reliability."""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into structured judgment data."""
        return _parse_json_response(
            response_text,
            default_reward_signals={
                "mlops_governance": 0.5,
                "production_reliability": 0.5,
                "data_governance": 0.5,
                "bias_fairness": 0.5,
                "compliance_adherence": 0.5,
                "agent_workflow_optimization": 0.5
            },
            default_improvements=["Review evaluation prompt structure and MLOps best practices"]
        )
    
    def generate_continuous_feedback(self, results: List[JudgmentResult]) -> ContinuousFeedback:
        """Generate continuous feedback for ML agent improvement."""
        strengths = []
        weaknesses = []
        improvements = []
        
        # Analyze patterns across evaluations
        pass_rate = len([r for r in results if r.judgment == "pass"]) / len(results)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        if pass_rate > 0.8:
            strengths.append("Strong MLOps governance and compliance")
        else:
            weaknesses.append("Inconsistent MLOps and governance performance")
        
        if avg_confidence > 0.8:
            strengths.append("High confidence in ML decisions and workflows")
        else:
            improvements.append("Improve ML decision confidence through better governance and monitoring")
        
        # Aggregate improvement recommendations
        all_improvements = []
        for result in results:
            all_improvements.extend(result.improvement_recommendations)
        
        # Remove duplicates and prioritize
        unique_improvements = list(set(all_improvements))
        
        return ContinuousFeedback(
            strengths=strengths,
            weaknesses=weaknesses,
            specific_improvements=unique_improvements[:5],  # Top 5
            training_suggestions=[
                f"Implement {weaknesses[0].lower()}" if weaknesses else "Add model validation",
                f"Fix issues in: {', '.join(list(set(r.scenario_id for r in results if r.judgment == 'fail'))[:3])}",
                f"Apply MLOps best practices to resolve {len([r for r in results if r.judgment == 'fail'])} failures"
            ] if any(r.judgment == "fail" for r in results) else [],
            compliance_gaps=[r.scenario_id for r in results if r.judgment == "fail"]
        )
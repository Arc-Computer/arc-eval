"""
Base judge class and shared utilities for Agent-as-a-Judge framework.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from agent_eval.core.types import EvaluationResult, EvaluationScenario, AgentOutput, VerificationSummary, BiasMetrics


logger = logging.getLogger(__name__)


def _parse_json_response(response_text: str, default_reward_signals: Dict[str, float], default_improvements: List[str]) -> Dict[str, Any]:
    """Standardized JSON parsing for all domain judges with robust error handling."""
    try:
        # Method 1: Clean control characters and try standard extraction
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_text)
        
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            potential_json = cleaned_text[json_start:json_end]
            try:
                judgment_data = json.loads(potential_json)
                # Validate and return if successful
                return _validate_judgment_data(judgment_data, default_reward_signals, default_improvements)
            except json.JSONDecodeError:
                pass
        
        # Method 2: Brace counting for nested JSON
        brace_count = 0
        start_pos = cleaned_text.find('{')
        if start_pos != -1:
            for i, char in enumerate(cleaned_text[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = cleaned_text[start_pos:i+1]
                        try:
                            judgment_data = json.loads(json_str)
                            return _validate_judgment_data(judgment_data, default_reward_signals, default_improvements)
                        except json.JSONDecodeError:
                            break
        
        # Method 3: Line-by-line reconstruction for malformed JSON
        lines = cleaned_text.split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if '{' in line and not in_json:
                in_json = True
                json_lines.append(line[line.find('{'):])
            elif in_json:
                json_lines.append(line)
                if '}' in line and line.count('}') >= line.count('{'):
                    break
        
        if json_lines:
            reconstructed_json = '\n'.join(json_lines)
            try:
                judgment_data = json.loads(reconstructed_json)
                return _validate_judgment_data(judgment_data, default_reward_signals, default_improvements)
            except json.JSONDecodeError:
                pass
        
        raise ValueError("No valid JSON found in response")
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse JSON response: {e}")
        logger.debug(f"Response text sample: {response_text[:200]}...")
        # Return fallback structured response
        return {
            "judgment": "warning",
            "confidence": 0.5,
            "reasoning": "Unable to parse detailed evaluation response",
            "improvements": default_improvements,
            "reward_signals": default_reward_signals
        }


def _validate_judgment_data(judgment_data: Dict[str, Any], default_reward_signals: Dict[str, float], default_improvements: List[str]) -> Dict[str, Any]:
    """Validate and normalize judgment data with defaults."""
    judgment = judgment_data.get("judgment", "warning")
    confidence = float(judgment_data.get("confidence", 0.5))
    reasoning = judgment_data.get("reasoning", "Evaluation completed with limited response parsing")
    improvements = judgment_data.get("improvements", default_improvements)
    
    # Ensure improvements is a list
    if isinstance(improvements, str):
        improvements = [improvements]
    
    # Handle reward_signals with defaults
    reward_signals = judgment_data.get("reward_signals", {})
    
    # Fill missing reward signals
    for key, default_value in default_reward_signals.items():
        if key not in reward_signals:
            reward_signals[key] = default_value
        else:
            try:
                reward_signals[key] = float(reward_signals[key])
            except (ValueError, TypeError):
                reward_signals[key] = default_value
    
    return {
        "judgment": judgment,
        "confidence": confidence,
        "reasoning": reasoning,
        "improvements": improvements,
        "reward_signals": reward_signals
    }


@dataclass
class JudgmentResult:
    """Result from Agent-as-a-Judge evaluation."""
    scenario_id: str
    judgment: str  # "pass", "fail", "warning"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    improvement_recommendations: List[str]
    reward_signals: Dict[str, float]
    evaluation_time: float
    model_used: str
    
    # Enhanced fields for compound judge architecture (optional)
    verification: Optional[VerificationSummary] = None
    bias_metrics: Optional[BiasMetrics] = None
    benchmark_scores: Optional[Dict[str, float]] = None


@dataclass
class ContinuousFeedback:
    """Continuous feedback for agent improvement."""
    strengths: List[str]
    weaknesses: List[str]
    specific_improvements: List[str]
    training_suggestions: List[str]
    compliance_gaps: List[str]


class BaseJudge(ABC):
    """Abstract base class for domain-specific judges."""
    
    def __init__(self, api_manager, enable_confidence_calibration: bool = False):
        self.api_manager = api_manager
        self.enable_confidence_calibration = enable_confidence_calibration
        
        # Initialize confidence calibrator if enabled
        if self.enable_confidence_calibration:
            from agent_eval.evaluation.confidence_calibrator import ConfidenceCalibrator
            self.confidence_calibrator = ConfidenceCalibrator()
    
    @abstractmethod
    def evaluate(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> JudgmentResult:
        """Evaluate agent output using domain-specific judge."""
        pass
    
    def evaluate_batch(self, evaluations: List[Tuple[AgentOutput, EvaluationScenario]]) -> List[JudgmentResult]:
        """Evaluate multiple agent outputs in batch for efficiency.
        
        Args:
            evaluations: List of (agent_output, scenario) tuples
            
        Returns:
            List of JudgmentResult objects
        """
        from agent_eval.core.constants import BATCH_PROCESSING_THRESHOLD
        
        # Check if batch processing should be used
        if len(evaluations) < BATCH_PROCESSING_THRESHOLD:
            # Fall back to sequential processing for small batches
            logger.info(f"Processing {len(evaluations)} evaluations sequentially (below threshold)")
            return [self.evaluate(output, scenario) for output, scenario in evaluations]
        
        # Prepare prompts for batch processing
        prompts = []
        for agent_output, scenario in evaluations:
            prompt = self._build_prompt(agent_output, scenario)
            prompts.append({
                "prompt": prompt,
                "scenario_id": scenario.id,
                "agent_output": agent_output,
                "scenario": scenario
            })
        
        # Use cascade batch processing
        logger.info(f"Processing {len(evaluations)} evaluations in batch mode")
        batch_results = self.api_manager.process_batch_cascade(prompts)
        
        # Convert batch results to JudgmentResult objects
        judgment_results = []
        results_dict = batch_results["results"]
        telemetry = batch_results["telemetry"]
        
        # Log cost savings
        if telemetry["cost_savings"] > 0:
            logger.info(f"Batch processing saved ${telemetry['cost_savings']:.2f} "
                       f"({telemetry['savings_percentage']:.1f}%) in API costs")
        
        for prompt_data in prompts:
            scenario_id = prompt_data["scenario_id"]
            
            if scenario_id in results_dict:
                result_data = results_dict[scenario_id]
                response_text = result_data["response"]
                model_used = result_data["model"]
                
                # Parse the response
                try:
                    judgment_data = self._parse_response(response_text)
                    
                    # Override confidence with extracted value
                    judgment_data["confidence"] = result_data["confidence"]
                    
                    judgment_result = JudgmentResult(
                        scenario_id=scenario_id,
                        judgment=judgment_data["judgment"],
                        confidence=judgment_data["confidence"],
                        reasoning=judgment_data["reasoning"],
                        improvement_recommendations=judgment_data["improvements"],
                        reward_signals=judgment_data["reward_signals"],
                        evaluation_time=telemetry["duration"] / len(prompts),  # Average time
                        model_used=model_used
                    )
                    judgment_results.append(judgment_result)
                except Exception as e:
                    logger.error(f"Failed to parse batch result for {scenario_id}: {e}")
                    # Create fallback result
                    judgment_results.append(self._create_fallback_result(
                        prompt_data["scenario"],
                        str(e)
                    ))
            else:
                # No result for this scenario - create error result
                judgment_results.append(self._create_fallback_result(
                    prompt_data["scenario"],
                    "No result returned from batch processing"
                ))
        
        return judgment_results
    
    def _create_fallback_result(self, scenario: EvaluationScenario, error_message: str) -> JudgmentResult:
        """Create a fallback result for failed evaluations."""
        return JudgmentResult(
            scenario_id=scenario.id,
            judgment="warning",
            confidence=0.0,
            reasoning=f"Evaluation failed: {error_message}",
            improvement_recommendations=["Re-run evaluation with different parameters"],
            reward_signals={"error": 1.0},
            evaluation_time=0.0,
            model_used="unknown"
        )
    
    @abstractmethod
    def _build_prompt(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> str:
        """Build domain-specific evaluation prompt."""
        pass
    
    @abstractmethod
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into structured judgment data."""
        pass
    
    @abstractmethod
    def generate_continuous_feedback(self, results: List[JudgmentResult]) -> ContinuousFeedback:
        """Generate continuous feedback for agent improvement."""
        pass
    
    def _execute_evaluation(self, prompt: str, scenario: EvaluationScenario, model: str) -> JudgmentResult:
        """Common evaluation execution logic."""
        start_time = datetime.now()
        
        try:
            # Call Claude for Agent-as-a-Judge evaluation with optional logprobs
            if self.enable_confidence_calibration:
                response_text, logprobs = self.api_manager.call_with_logprobs(prompt, enable_logprobs=True)
            else:
                client, model = self.api_manager.get_client()
                
                if self.api_manager.provider == "anthropic":
                    response = client.messages.create(
                        model=model,
                        max_tokens=2000,
                        temperature=0.1,  # Low temperature for consistent evaluation
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    response_text = response.content[0].text
                elif self.api_manager.provider == "openai":
                    response = client.chat.completions.create(
                        model=model,
                        max_tokens=2000,
                        temperature=0.1,  # Low temperature for consistent evaluation
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    response_text = response.choices[0].message.content
                else:
                    raise ValueError(f"Unsupported provider: {self.api_manager.provider}")
                
                logprobs = None
                
                # Track API costs for standard call
                input_tokens = len(prompt) // 4  # Rough approximation
                output_tokens = len(response_text) // 4
                self.api_manager.track_cost(input_tokens, output_tokens, model)
            
            # Parse response
            judgment_data = self._parse_response(response_text)
            
            # Apply confidence calibration if enabled
            if self.enable_confidence_calibration and hasattr(self, 'confidence_calibrator'):
                calibration = self.confidence_calibrator.calibrate_confidence(response_text, logprobs)
                # Override the confidence with calibrated value
                judgment_data["confidence"] = calibration.calibrated_confidence
                # Add calibration metadata to reward signals
                judgment_data["reward_signals"]["calibration_quality"] = calibration.quality_score
                judgment_data["reward_signals"]["uncertainty"] = calibration.uncertainty
            
            evaluation_time = (datetime.now() - start_time).total_seconds()
            
            return JudgmentResult(
                scenario_id=scenario.id,
                judgment=judgment_data["judgment"],
                confidence=judgment_data["confidence"],
                reasoning=judgment_data["reasoning"],
                improvement_recommendations=judgment_data["improvements"],
                reward_signals=judgment_data["reward_signals"],
                evaluation_time=evaluation_time,
                model_used=model
            )
            
        except Exception as e:
            logger.error(f"{self.__class__.__name__} evaluation failed: {e}")
            # Fallback to alternative model if primary fails
            if "sonnet" in model:
                logger.info("Falling back to Haiku model")
                _, fallback_model = self.api_manager.get_client(prefer_primary=False)
                return self._execute_evaluation(prompt, scenario, fallback_model)
            else:
                raise
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
from contextlib import contextmanager

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

    @contextmanager
    def _api_manager_context(self, provider: str, primary_model: str, preferred_model: str, api_key: str):
        """Thread-safe context manager for temporarily switching API manager configuration."""
        # Save original state
        original_provider = self.api_manager.provider
        original_model = self.api_manager.primary_model
        original_preferred_model = self.api_manager.preferred_model
        original_api_key = self.api_manager.api_key

        try:
            # Apply temporary state
            self.api_manager.provider = provider
            self.api_manager.primary_model = primary_model
            self.api_manager.preferred_model = preferred_model
            self.api_manager.api_key = api_key
            yield
        finally:
            # Restore original state
            self.api_manager.provider = original_provider
            self.api_manager.primary_model = original_model
            self.api_manager.preferred_model = original_preferred_model
            self.api_manager.api_key = original_api_key
    
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
        """Common evaluation execution logic with hybrid architecture support."""
        start_time = datetime.now()

        try:
            # Check if hybrid architecture is enabled (Cerebras + Gemini QA)
            use_hybrid = (
                (
                    self.api_manager.provider == "cerebras" and
                    hasattr(self.api_manager, 'enable_hybrid_qa') and
                    self.api_manager.enable_hybrid_qa
                )
            )

            if use_hybrid:
                return self._execute_hybrid_evaluation(prompt, scenario, model, start_time)
            else:
                return self._execute_standard_evaluation(prompt, scenario, model, start_time)

        except Exception as e:
            logger.error(f"{self.__class__.__name__} evaluation failed: {e}")
            # Fallback to alternative model if primary fails
            if "sonnet" in model:
                logger.info("Falling back to Haiku model")
                _, fallback_model = self.api_manager.get_client(prefer_primary=False)
                return self._execute_evaluation(prompt, scenario, fallback_model)
            else:
                raise

    def _execute_hybrid_evaluation(self, prompt: str, scenario: EvaluationScenario, model: str, start_time: datetime) -> JudgmentResult:
        """Execute hybrid evaluation: Cerebras primary + Gemini QA for low confidence."""
        # Step 1: Get initial evaluation from Cerebras with performance tracking
        cerebras_start_time = datetime.now()
        response_text, logprobs = self.api_manager.call_with_logprobs(prompt, enable_logprobs=True)
        cerebras_end_time = datetime.now()

        # Calculate Cerebras-specific performance metrics
        cerebras_evaluation_time = (cerebras_end_time - cerebras_start_time).total_seconds()

        # Get token counts for accurate throughput calculation
        input_tokens = self.api_manager._count_tokens(prompt)
        output_tokens = self.api_manager._count_tokens(response_text)
        total_tokens = input_tokens + output_tokens

        # Calculate actual Cerebras token throughput
        cerebras_tokens_per_second = total_tokens / cerebras_evaluation_time if cerebras_evaluation_time > 0 else 0

        judgment_data = self._parse_response(response_text)

        initial_confidence = judgment_data.get("confidence", 0.5)
        is_critical_domain = getattr(scenario, 'severity', 'medium') == 'critical'

        # Step 2: Determine if QA routing is needed with adaptive thresholds
        # Load configuration-based thresholds
        from agent_eval.core.config import get_confidence_thresholds, get_cost_protection, get_performance_protection

        confidence_config = get_confidence_thresholds()
        cost_config = get_cost_protection()
        performance_config = get_performance_protection()

        # Adaptive threshold based on domain criticality and failure patterns
        if is_critical_domain:
            confidence_threshold = confidence_config.critical_domain_threshold
        elif judgment_data.get("judgment") == "fail":
            confidence_threshold = confidence_config.failure_threshold
        else:
            confidence_threshold = confidence_config.base_threshold

        # Add cost circuit breaker using configuration
        cost_threshold_exceeded = self.api_manager.total_cost > (self.api_manager.cost_threshold * cost_config.qa_skip_threshold)

        needs_qa = (
            initial_confidence < confidence_threshold or
            is_critical_domain or
            judgment_data.get("judgment") == "fail"
        ) and not cost_threshold_exceeded  # Skip QA if cost limit approaching

        # Log confidence routing decision for post-launch analysis
        logger.info(f"Confidence routing: {initial_confidence:.2f} vs {confidence_threshold:.2f} threshold, "
                   f"critical={is_critical_domain}, judgment={judgment_data.get('judgment')}, qa_needed={needs_qa}")

        # Create performance metrics dictionary
        performance_metrics = {
            "cerebras_tokens_per_second": cerebras_tokens_per_second,
            "cerebras_evaluation_time": cerebras_evaluation_time,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }

        if needs_qa:
            logger.info(f"Routing to Gemini QA: confidence={initial_confidence:.2f}, critical={is_critical_domain}")

            # Create QA prompt for Gemini
            qa_prompt = self._build_qa_prompt(prompt, response_text, judgment_data)

            # Add performance circuit breaker using configuration
            if cerebras_evaluation_time > performance_config.max_cerebras_time:
                logger.warning(f"Cerebras evaluation took {cerebras_evaluation_time:.1f}s - skipping QA to prevent timeout")
                final_judgment_data = judgment_data
                final_judgment_data["reasoning"] += "\n[QA skipped due to performance constraints]"
                model_used = f"{model} (QA skipped - performance)"
            else:
                # Use context manager for thread-safe provider switching
                import os
                with self._api_manager_context(
                    provider="google",
                    primary_model="gemini-2.5-flash-preview-05-20",
                    preferred_model="gemini-2.5-flash-preview-05-20",
                    api_key=os.getenv("GEMINI_API_KEY")
                ):
                    qa_response, _ = self.api_manager.call_with_logprobs(qa_prompt, enable_logprobs=False)
                    qa_judgment_data = self._parse_response(qa_response)

                    # Combine results: use QA judgment but preserve Cerebras performance metrics
                    final_judgment_data = self._combine_hybrid_results(judgment_data, qa_judgment_data, performance_metrics)
                    model_used = f"{model} + gemini-2.5-flash (QA)"
        else:
            logger.info(f"Cerebras confidence sufficient: {initial_confidence:.2f}")
            # Add performance metrics to Cerebras-only results
            if "reward_signals" not in judgment_data:
                judgment_data["reward_signals"] = {}
            judgment_data["reward_signals"]["cerebras_speed"] = cerebras_tokens_per_second
            judgment_data["reward_signals"]["cerebras_evaluation_time"] = cerebras_evaluation_time
            judgment_data["reward_signals"]["total_tokens"] = total_tokens

            final_judgment_data = judgment_data
            model_used = model

        evaluation_time = (datetime.now() - start_time).total_seconds()

        # Collect confidence calibration data for post-launch analysis
        calibration_data = {
            "cerebras_confidence": initial_confidence,
            "cerebras_judgment": judgment_data.get("judgment"),
            "final_confidence": final_judgment_data["confidence"],
            "final_judgment": final_judgment_data["judgment"],
            "qa_applied": needs_qa and not cost_threshold_exceeded,
            "confidence_threshold_used": confidence_threshold,
            "scenario_severity": getattr(scenario, 'severity', 'medium'),
            "timestamp": datetime.now().isoformat()
        }

        # Add calibration data to reward signals for analysis
        if "reward_signals" not in final_judgment_data:
            final_judgment_data["reward_signals"] = {}
        final_judgment_data["reward_signals"]["confidence_calibration"] = calibration_data

        return JudgmentResult(
            scenario_id=scenario.id,
            judgment=final_judgment_data["judgment"],
            confidence=final_judgment_data["confidence"],
            reasoning=final_judgment_data["reasoning"],
            improvement_recommendations=final_judgment_data["improvements"],
            reward_signals=final_judgment_data["reward_signals"],
            evaluation_time=evaluation_time,
            model_used=model_used
        )

    def _execute_standard_evaluation(self, prompt: str, scenario: EvaluationScenario, model: str, start_time: datetime) -> JudgmentResult:
        """Execute standard single-provider evaluation."""
        # Call API for Agent-as-a-Judge evaluation with optional logprobs
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
            elif self.api_manager.provider == "google":
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                response_text = response.text
            elif self.api_manager.provider == "cerebras":
                response = client.chat.completions.create(
                    model=model,
                    max_tokens=2000,
                    temperature=0.1,
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

        # Add real performance metrics for Cerebras provider
        if self.api_manager.provider == "cerebras":
            # Calculate actual token throughput for Cerebras
            input_tokens = self.api_manager._count_tokens(prompt)
            output_tokens = self.api_manager._count_tokens(response_text)
            total_tokens = input_tokens + output_tokens
            cerebras_tokens_per_second = total_tokens / evaluation_time if evaluation_time > 0 else 0

            # Add real performance metrics to reward signals
            if "reward_signals" not in judgment_data:
                judgment_data["reward_signals"] = {}
            judgment_data["reward_signals"]["cerebras_speed"] = cerebras_tokens_per_second
            judgment_data["reward_signals"]["cerebras_evaluation_time"] = evaluation_time
            judgment_data["reward_signals"]["total_tokens"] = total_tokens
            judgment_data["reward_signals"]["input_tokens"] = input_tokens
            judgment_data["reward_signals"]["output_tokens"] = output_tokens

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

    def _build_qa_prompt(self, original_prompt: str, cerebras_response: str, cerebras_judgment: Dict[str, Any]) -> str:
        """Build QA prompt for Gemini to review Cerebras evaluation."""
        return f"""You are a Senior Quality Assurance Judge reviewing an AI evaluation for accuracy and completeness.

ORIGINAL EVALUATION TASK:
{original_prompt}

INITIAL EVALUATION RESPONSE:
{cerebras_response}

PARSED JUDGMENT:
- Judgment: {cerebras_judgment.get('judgment', 'unknown')}
- Confidence: {cerebras_judgment.get('confidence', 0.5)}
- Reasoning: {cerebras_judgment.get('reasoning', 'No reasoning provided')}

QUALITY ASSURANCE TASK:
Review the initial evaluation for:
1. Accuracy of judgment (PASS/FAIL/WARNING)
2. Completeness of reasoning
3. Appropriateness of confidence level
4. Quality of improvement recommendations
5. Compliance with regulatory requirements

Provide your final judgment in JSON format:
{{
    "judgment": "pass|fail|warning",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed analysis incorporating QA review",
    "improvements": ["Specific actionable recommendations"],
    "reward_signals": {{
        "accuracy": 0.0-1.0,
        "completeness": 0.0-1.0,
        "regulatory_compliance": 0.0-1.0,
        "recommendation_quality": 0.0-1.0
    }},
    "qa_notes": "Quality assurance review notes and corrections"
}}

CRITICAL: If the initial evaluation missed important compliance issues or made incorrect judgments, override with the correct assessment."""

    def _combine_hybrid_results(self, cerebras_result: Dict[str, Any], gemini_result: Dict[str, Any], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Combine Cerebras and Gemini results for final judgment with real performance metrics."""
        # Use Gemini's judgment as authoritative (QA override)
        final_result = gemini_result.copy()

        # Preserve Cerebras performance metrics in reward signals
        if "reward_signals" not in final_result:
            final_result["reward_signals"] = {}

        # Add real performance metrics instead of hardcoded values
        final_result["reward_signals"]["cerebras_speed"] = performance_metrics["cerebras_tokens_per_second"]
        final_result["reward_signals"]["cerebras_evaluation_time"] = performance_metrics["cerebras_evaluation_time"]
        final_result["reward_signals"]["total_tokens"] = performance_metrics["total_tokens"]
        final_result["reward_signals"]["input_tokens"] = performance_metrics["input_tokens"]
        final_result["reward_signals"]["output_tokens"] = performance_metrics["output_tokens"]
        final_result["reward_signals"]["gemini_qa"] = 1.0      # Quality assurance applied

        # Combine improvement recommendations
        cerebras_improvements = cerebras_result.get("improvements", [])
        gemini_improvements = gemini_result.get("improvements", [])

        # Merge and deduplicate improvements
        all_improvements = cerebras_improvements + gemini_improvements
        unique_improvements = list(dict.fromkeys(all_improvements))  # Preserve order, remove duplicates
        final_result["improvements"] = unique_improvements[:5]  # Limit to top 5

        # Add hybrid reasoning note
        original_reasoning = final_result.get("reasoning", "")
        final_result["reasoning"] = f"{original_reasoning}\n\n[Hybrid Evaluation: Cerebras initial assessment + Gemini QA review]"

        return final_result

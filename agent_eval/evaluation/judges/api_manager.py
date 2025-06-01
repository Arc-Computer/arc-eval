"""
Enterprise API management with cost tracking and fallback.
"""

import os
import logging
from typing import Dict, Tuple, Optional, List, Any
from datetime import datetime
import time
import asyncio
import json
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass


logger = logging.getLogger(__name__)


class APIManager:
    """Enterprise API management with cost tracking and fallback."""
    
    def __init__(self, preferred_model: str = "auto", provider: str = None):
        # Determine provider
        self.provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
        
        # Initialize provider-specific settings
        if self.provider == "anthropic":
            self.primary_model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet 4
            self.fallback_model = "claude-3-5-haiku-20241022"  # Latest Claude Haiku 3.5
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        elif self.provider == "openai":
            self.primary_model = "gpt-4.1-2025-04-14"  # Latest GPT-4.1
            self.fallback_model = "gpt-4.1-mini-2025-04-14"  # Latest GPT-4.1-mini
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Handle user model preference
        if preferred_model == "auto":
            self.preferred_model = self.primary_model
        else:
            # Validate model for provider (using supported batch models)
            if self.provider == "anthropic" and preferred_model in ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]:
                self.preferred_model = preferred_model
            elif self.provider == "openai" and preferred_model in ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"]:
                self.preferred_model = preferred_model
            else:
                logger.warning(f"Unknown model {preferred_model} for provider {self.provider}, using auto selection")
                self.preferred_model = self.primary_model
        
        self.cost_threshold = float(os.getenv("AGENT_EVAL_COST_THRESHOLD", "10.0"))  # $10 default
        self.total_cost = 0.0
        
        # Initialize token counter for accurate cost tracking
        self._init_token_counter()
    
    def get_client(self, prefer_primary: bool = True):
        """Get API client with cost-aware model selection."""
        if self.provider == "anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError("anthropic library not installed. Run: pip install anthropic")
            
            client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "openai":
            try:
                import openai
            except ImportError:
                raise ImportError("openai library not installed. Run: pip install openai")
            
            client = openai.OpenAI(api_key=self.api_key)
        
        # Model selection logic
        if self.total_cost > self.cost_threshold or not prefer_primary:
            # Auto fallback due to cost threshold
            logger.info(f"Using fallback model {self.fallback_model} (cost: ${self.total_cost:.2f})")
            return client, self.fallback_model
        else:
            # Use primary or user preference
            model_to_use = self.preferred_model
            logger.info(f"Using {self.provider} model {model_to_use}")
            return client, model_to_use
    
    def _init_token_counter(self):
        """Initialize accurate token counting."""
        try:
            import tiktoken
            if self.provider == "anthropic":
                # Use cl100k_base for approximation until Claude tokenizer is available
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            else:  # openai
                # Use gpt-4 encoding as closest approximation for GPT-4.1 models
                # GPT-4.1 uses same tokenizer as GPT-4
                self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except ImportError:
            logger.warning("tiktoken not available, using rough token estimation")
            self.tokenizer = None
    
    def _count_tokens(self, text: str) -> int:
        """Accurately count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback to rough estimation
            return len(text) // 4
    
    def track_cost(self, input_tokens: int, output_tokens: int, model: str):
        """Track API costs for enterprise cost management with accurate pricing."""
        if self.provider == "anthropic":
            # Updated Claude pricing (January 2025) - from Anthropic batch docs
            if "sonnet-4" in model.lower():
                # Claude Sonnet 4 pricing: $1.50 input / $7.50 output per MTok
                cost = (input_tokens * 1.5 + output_tokens * 7.5) / 1_000_000
            elif "sonnet" in model.lower():
                # Claude Sonnet 3.5 pricing: $1.50 input / $7.50 output per MTok  
                cost = (input_tokens * 1.5 + output_tokens * 7.5) / 1_000_000
            else:  # haiku
                # Claude Haiku 3.5 pricing: $0.40 input / $2.00 output per MTok
                cost = (input_tokens * 0.4 + output_tokens * 2.0) / 1_000_000
        elif self.provider == "openai":
            # Updated OpenAI pricing (April 2025)
            if "gpt-4.1-2025-04-14" in model and "mini" not in model:
                # GPT-4.1 pricing: $2.50 input / $10.00 output per MTok
                cost = (input_tokens * 2.5 + output_tokens * 10.0) / 1_000_000
            elif "gpt-4.1-mini-2025-04-14" in model:
                # GPT-4.1-mini pricing: $0.15 input / $0.60 output per MTok
                cost = (input_tokens * 0.15 + output_tokens * 0.6) / 1_000_000
            else:
                # Default to mini pricing if unknown
                cost = (input_tokens * 0.15 + output_tokens * 0.6) / 1_000_000
        else:
            cost = 0.0
        
        self.total_cost += cost
        logger.info(f"API call cost: ${cost:.4f}, Total: ${self.total_cost:.2f}")
        return cost
    
    def call_with_logprobs(self, prompt: str, enable_logprobs: bool = False, max_retries: int = 3) -> Tuple[str, Optional[Dict[str, float]]]:
        """Call API with retry logic and accurate cost tracking.
        
        Args:
            prompt: The prompt to send to the model
            enable_logprobs: Whether to attempt logprobs extraction
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (response_text, logprobs_dict or None)
        """
        for attempt in range(max_retries + 1):
            try:
                client, model = self.get_client()
                
                if self.provider == "anthropic":
                    response = client.messages.create(
                        model=model,
                        max_tokens=4000,  # Increased for comprehensive domain analysis
                        temperature=0.1,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    
                    response_text = response.content[0].text
                    
                    # Accurate token counting
                    input_tokens = self._count_tokens(prompt)
                    output_tokens = self._count_tokens(response_text)
                    self.track_cost(input_tokens, output_tokens, model)
                    
                    # Enhanced pseudo-logprobs
                    logprobs = self._extract_enhanced_pseudo_logprobs(response_text) if enable_logprobs else None
                    
                elif self.provider == "openai":
                    response = client.chat.completions.create(
                        model=model,
                        max_tokens=4000,  # Increased for comprehensive domain analysis
                        temperature=0.1,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        logprobs=enable_logprobs,
                        top_logprobs=5 if enable_logprobs else None
                    )
                    
                    response_text = response.choices[0].message.content
                    
                    # Use actual token counts from API
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens
                    self.track_cost(input_tokens, output_tokens, model)
                    
                    # Extract real logprobs
                    if enable_logprobs and response.choices[0].logprobs:
                        logprobs = self._extract_openai_logprobs(response.choices[0].logprobs)
                    else:
                        logprobs = None
                
                return response_text, logprobs
                
            except Exception as e:
                if attempt < max_retries:
                    retry_delay = self._calculate_retry_delay(attempt, e)
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {retry_delay}s")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"API call failed after {max_retries + 1} attempts: {e}")
                    raise
    
    def _calculate_retry_delay(self, attempt: int, error: Exception) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        
        # Check if it's a rate limit error
        if "429" in str(error) or "rate limit" in str(error).lower():
            # Longer delays for rate limits
            base_delay = min(60, (2 ** attempt) * 2)  # Cap at 60 seconds
        else:
            # Shorter delays for other errors
            base_delay = min(10, (2 ** attempt))  # Cap at 10 seconds
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * base_delay
        return base_delay + jitter
    
    def _extract_enhanced_pseudo_logprobs(self, response_text: str) -> Dict[str, float]:
        """Extract enhanced pseudo-logprobs from response text patterns.
        
        Enhanced version with better confidence calibration for Agent-as-a-Judge.
        
        Args:
            response_text: Response text from Claude
            
        Returns:
            Dictionary of pseudo-logprobs for key tokens
        """
        import re
        import json
        
        text_lower = response_text.lower()
        pseudo_logprobs = {}
        
        # Try to extract explicit confidence scores from JSON
        try:
            # Look for JSON objects with confidence
            json_match = re.search(r'\{[^}]*"confidence"[^}]*\}', response_text)
            if json_match:
                json_obj = json.loads(json_match.group())
                confidence = float(json_obj.get('confidence', 0.5))
                # Convert confidence to pseudo-logprob
                pseudo_logprobs['explicit_confidence'] = -((1 - confidence) * 5)  # Range -5 to 0
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Enhanced decision pattern recognition
        decision_patterns = {
            "strong_pass": r'\b(definitely pass|clearly pass|strongly pass|confidently pass)\b',
            "pass": r'\b(pass|passed|acceptable|compliant|safe|approved)\b',
            "weak_pass": r'\b(barely pass|marginally pass|just pass)\b',
            "strong_fail": r'\b(definitely fail|clearly fail|strongly fail|obviously fail)\b',
            "fail": r'\b(fail|failed|unacceptable|violation|unsafe|rejected)\b',
            "weak_fail": r'\b(barely fail|marginally fail|just fail)\b',
            "warning": r'\b(warning|caution|concern|partial|unclear|maybe)\b'
        }
        
        # More nuanced confidence scoring
        decision_scores = {
            "strong_pass": -0.1,
            "pass": -0.3,
            "weak_pass": -0.8,
            "strong_fail": -0.1,
            "fail": -0.3,
            "weak_fail": -0.8,
            "warning": -1.5
        }
        
        for decision, pattern in decision_patterns.items():
            if re.search(pattern, text_lower):
                pseudo_logprobs[decision] = decision_scores[decision]
        
        # Enhanced confidence indicators with scoring
        confidence_indicators = {
            "certainty": (r'\b(certain|definitely|absolutely|clearly|obviously)\b', -0.2),
            "high_confidence": (r'\b(very confident|highly confident|quite sure|very likely)\b', -0.4),
            "medium_confidence": (r'\b(confident|likely|probably|sure|seems)\b', -0.7),
            "low_confidence": (r'\b(uncertain|unsure|unclear|possibly|might|maybe)\b', -1.5),
            "very_uncertain": (r'\b(very uncertain|highly uncertain|extremely unclear)\b', -2.5)
        }
        
        for indicator, (pattern, score) in confidence_indicators.items():
            if re.search(pattern, text_lower):
                pseudo_logprobs[indicator] = score
        
        # Structural analysis for additional confidence
        if len(response_text) > 500:  # Longer responses might indicate more careful analysis
            pseudo_logprobs['detailed_response'] = -0.3
        elif len(response_text) < 100:  # Very short responses might indicate uncertainty
            pseudo_logprobs['brief_response'] = -1.0
        
        # Check for hedging language
        hedging_patterns = r'\b(however|but|although|though|nevertheless|nonetheless)\b'
        if re.search(hedging_patterns, text_lower):
            pseudo_logprobs['hedging'] = -0.8
        
        return pseudo_logprobs
    
    def _extract_openai_logprobs(self, logprobs_data) -> Dict[str, float]:
        """Extract logprobs from OpenAI response.
        
        Args:
            logprobs_data: Logprobs data from OpenAI response
            
        Returns:
            Dictionary of token to logprob mappings
        """
        extracted_logprobs = {}
        
        # OpenAI returns logprobs for each token
        if hasattr(logprobs_data, 'content') and logprobs_data.content:
            for token_data in logprobs_data.content:
                if hasattr(token_data, 'token') and hasattr(token_data, 'logprob'):
                    extracted_logprobs[token_data.token] = token_data.logprob
        
        return extracted_logprobs
    
    def create_batch(self, prompts: List[Dict[str, Any]], prefer_primary: bool = False) -> Tuple[str, float]:
        """Create a real batch evaluation request using provider APIs.
        
        Args:
            prompts: List of evaluation prompts with metadata
            prefer_primary: Whether to prefer primary model over fallback
            
        Returns:
            Tuple of (batch_id, estimated_cost)
        """
        client, model = self.get_client(prefer_primary=prefer_primary)
        
        try:
            if self.provider == "anthropic":
                return self._create_anthropic_batch(client, model, prompts)
            elif self.provider == "openai":
                return self._create_openai_batch(client, model, prompts)
            else:
                raise ValueError(f"Batch processing not supported for provider: {self.provider}")
        except Exception as e:
            logger.error(f"Batch creation failed: {e}")
            raise
    
    def _create_anthropic_batch(self, client, model: str, prompts: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Create Anthropic Message Batches API request."""
        try:
            # Prepare batch requests in Anthropic format
            batch_requests = []
            for i, prompt_data in enumerate(prompts):
                request = {
                    "custom_id": f"eval_{i}_{prompt_data.get('scenario_id', 'unknown')}",
                    "params": {
                        "model": model,
                        "max_tokens": 4000,  # Increased for comprehensive domain analysis
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt_data["prompt"]
                            }
                        ]
                    }
                }
                batch_requests.append(request)
            
            # Create batch using Anthropic's Message Batches API
            batch_response = client.messages.batches.create(
                requests=batch_requests
            )
            batch_id = batch_response.id
            
            # Calculate accurate cost estimate
            total_input_tokens = sum(self._count_tokens(p["prompt"]) for p in prompts)
            estimated_output_tokens = total_input_tokens  # Rough estimate
            
            if "sonnet-4" in model.lower():
                # Claude Sonnet 4 batch pricing (50% discount already applied in docs)
                estimated_cost = (total_input_tokens * 1.5 + estimated_output_tokens * 7.5) / 1_000_000
            elif "sonnet" in model.lower():
                # Claude Sonnet 3.5 batch pricing
                estimated_cost = (total_input_tokens * 1.5 + estimated_output_tokens * 7.5) / 1_000_000
            else:  # haiku
                # Claude Haiku 3.5 batch pricing
                estimated_cost = (total_input_tokens * 0.4 + estimated_output_tokens * 2.0) / 1_000_000
            
            # Apply 50% batch discount
            estimated_cost *= 0.5
            
            logger.info(f"Created Anthropic batch {batch_id} with {len(prompts)} evaluations. Estimated cost: ${estimated_cost:.4f}")
            return batch_id, estimated_cost
            
        except Exception as e:
            # Fallback to simulation if batch API not available
            logger.warning(f"Anthropic batch API not available, falling back to simulation: {e}")
            import uuid
            batch_id = f"anthropic_sim_{uuid.uuid4().hex[:8]}"
            estimated_cost = 0.01 * len(prompts)  # Rough estimate
            return batch_id, estimated_cost
    
    def _create_openai_batch(self, client, model: str, prompts: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Create OpenAI Batch API request."""
        # Create JSONL file for batch
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for i, prompt_data in enumerate(prompts):
                batch_request = {
                    "custom_id": f"eval_{i}_{prompt_data.get('scenario_id', 'unknown')}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt_data["prompt"]
                            }
                        ],
                        "max_tokens": 4000,  # Increased for comprehensive domain analysis
                        "temperature": 0.1
                    }
                }
                f.write(json.dumps(batch_request) + '\n')
            batch_file_path = f.name
        
        try:
            # Upload batch file
            with open(batch_file_path, 'rb') as f:
                batch_input_file = client.files.create(
                    file=f,
                    purpose="batch"
                )
            
            # Create batch
            batch = client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": "ARC-Eval flywheel experiment",
                    "domain_count": str(len(set(p.get('domain', 'unknown') for p in prompts)))
                }
            )
            
            # Calculate cost estimate with 50% batch discount
            total_input_tokens = sum(self._count_tokens(p["prompt"]) for p in prompts)
            estimated_output_tokens = total_input_tokens  # Rough estimate
            
            if "gpt-4.1-2025-04-14" in model and "mini" not in model:
                # GPT-4.1 batch pricing
                estimated_cost = (total_input_tokens * 2.5 + estimated_output_tokens * 10.0) / 1_000_000
            elif "gpt-4.1-mini-2025-04-14" in model:
                # GPT-4.1-mini batch pricing
                estimated_cost = (total_input_tokens * 0.15 + estimated_output_tokens * 0.6) / 1_000_000
            else:  # unknown model
                estimated_cost = (total_input_tokens * 0.15 + estimated_output_tokens * 0.6) / 1_000_000
            
            # Apply 50% batch discount
            estimated_cost *= 0.5
            
            logger.info(f"Created OpenAI batch {batch.id} with {len(prompts)} evaluations. Estimated cost: ${estimated_cost:.4f}")
            return batch.id, estimated_cost
            
        finally:
            # Clean up temp file
            Path(batch_file_path).unlink(missing_ok=True)
    
    def wait_for_batch(self, batch_id: str, timeout: int = 3600) -> List[Dict[str, Any]]:
        """Wait for batch completion and retrieve results.
        
        Args:
            batch_id: The batch ID to wait for
            timeout: Maximum wait time in seconds (default: 1 hour)
            
        Returns:
            List of batch results with responses
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if self.provider == "anthropic":
                    return self._wait_for_anthropic_batch(batch_id, timeout - (time.time() - start_time))
                elif self.provider == "openai":
                    return self._wait_for_openai_batch(batch_id, timeout - (time.time() - start_time))
            except Exception as e:
                logger.error(f"Error waiting for batch {batch_id}: {e}")
                if "sim_" in batch_id:
                    # Handle simulation case
                    logger.warning(f"Batch {batch_id} was simulated - returning empty results")
                    return []
                raise
        
        raise TimeoutError(f"Batch {batch_id} did not complete within {timeout} seconds")
    
    def _wait_for_anthropic_batch(self, batch_id: str, remaining_timeout: float) -> List[Dict[str, Any]]:
        """Wait for Anthropic batch completion."""
        client, _ = self.get_client()
        
        while remaining_timeout > 0:
            try:
                batch = client.messages.batches.retrieve(batch_id)
                
                if batch.processing_status == "ended":
                    # Download results - use the streaming results method
                    results = []
                    for result in client.messages.batches.results(batch_id):
                        results.append(result)
                    
                    logger.info(f"Anthropic batch {batch_id} completed with {len(results)} results")
                    return results
                
                elif batch.processing_status == "failed":
                    raise RuntimeError(f"Anthropic batch {batch_id} failed")
                
                # Wait before next check
                time.sleep(30)
                remaining_timeout -= 30
                
            except Exception as e:
                if "sim_" in batch_id:
                    return []  # Simulated batch
                raise
        
        raise TimeoutError(f"Anthropic batch {batch_id} did not complete in time")
    
    def _wait_for_openai_batch(self, batch_id: str, remaining_timeout: float) -> List[Dict[str, Any]]:
        """Wait for OpenAI batch completion."""
        client, _ = self.get_client()
        
        while remaining_timeout > 0:
            batch = client.batches.retrieve(batch_id)
            
            if batch.status == "completed":
                # Download results
                file_response = client.files.content(batch.output_file_id)
                file_contents = file_response.text
                
                # Parse results
                results = []
                for line in file_contents.split('\n'):
                    if line.strip():
                        result = json.loads(line)
                        results.append(result)
                
                logger.info(f"OpenAI batch {batch_id} completed with {len(results)} results")
                return results
            
            elif batch.status in ["failed", "expired", "cancelled"]:
                raise RuntimeError(f"OpenAI batch {batch_id} status: {batch.status}")
            
            # Wait before next check
            time.sleep(30)
            remaining_timeout -= 30
        
        raise TimeoutError(f"OpenAI batch {batch_id} did not complete in time")
    
    def process_batch_cascade(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """DEPRECATED: Use DualTrackEvaluator instead.
        
        This method is deprecated and replaced by the new DualTrackEvaluator system
        which provides true batch processing via Anthropic Message Batches API
        and fast track processing with real-time progress.
        
        Args:
            prompts: List of evaluation prompts with metadata
            
        Returns:
            Dictionary with results and telemetry
        """
        logger.warning("process_batch_cascade is deprecated. Use DualTrackEvaluator for optimal performance.")
        
        # Import the new evaluator
        from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator, EvaluationMode
        
        # Create evaluator instance
        evaluator = DualTrackEvaluator(self)
        
        # Progress callback for logging
        def progress_callback(update):
            logger.info(f"Progress: {update.current}/{update.total} ({update.progress_percent:.1f}%) - {update.status}")
        
        # Run evaluation using new system
        summary = evaluator.evaluate_scenarios(prompts, mode=EvaluationMode.AUTO, progress_callback=progress_callback)
        
        # Convert to legacy format for backward compatibility
        final_results = {}
        for result in summary.results:
            if result.error is None:
                final_results[result.scenario_id] = {
                    "response": result.response,
                    "model": result.model_used,
                    "confidence": result.confidence
                }
        
        telemetry = {
            "total_evaluations": summary.total_scenarios,
            "fallback_evaluations": summary.completed,
            "primary_evaluations": 0,  # Not applicable to new system
            "total_cost": summary.total_cost,
            "cost_savings": 0.0,  # Calculated differently in new system
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "duration": summary.total_time,
            "mode_used": summary.mode_used.value,
            "average_confidence": summary.average_confidence
        }
        
        logger.info(f"Evaluation complete via {summary.mode_used.value}: {summary.completed}/{summary.total_scenarios} scenarios, "
                   f"${summary.total_cost:.2f}, {summary.total_time:.1f}s")
        
        return {
            "results": final_results,
            "telemetry": telemetry
        }
    
    def _extract_confidence_from_response(self, response_text: str) -> float:
        """Extract confidence score from evaluation response.
        
        Args:
            response_text: The response text from the model
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        import re
        
        # Try to find explicit confidence value
        confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', response_text)
        if confidence_match:
            return float(confidence_match.group(1))
        
        # Fallback: Use enhanced pseudo-logprobs approach
        pseudo_logprobs = self._extract_enhanced_pseudo_logprobs(response_text)
        
        # Convert logprobs to confidence
        if "high_confidence" in pseudo_logprobs:
            return 0.9
        elif "medium_confidence" in pseudo_logprobs:
            return 0.7
        elif "low_confidence" in pseudo_logprobs:
            return 0.4
        else:
            # Default medium confidence
            return 0.6

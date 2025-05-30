"""
Enterprise API management with cost tracking and fallback.
"""

import os
import logging
from typing import Dict, Tuple, Optional, List, Any
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
    
    def __init__(self, preferred_model: str = "auto"):
        # Model configuration with Claude 4 Sonnet as primary
        self.primary_model = "claude-sonnet-4-20250514"  # Primary model
        self.fallback_model = "claude-3-5-haiku-latest"    # Cost-effective fallback
        
        # Handle user model preference
        if preferred_model == "auto":
            self.preferred_model = self.primary_model
        elif preferred_model in ["claude-sonnet-4-20250514", "claude-3-5-haiku-latest"]:
            self.preferred_model = preferred_model
        else:
            logger.warning(f"Unknown model {preferred_model}, using auto selection")
            self.preferred_model = self.primary_model
        
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.cost_threshold = float(os.getenv("AGENT_EVAL_COST_THRESHOLD", "10.0"))  # $10 default
        self.total_cost = 0.0
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    def get_client(self, prefer_primary: bool = True):
        """Get API client with cost-aware model selection."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic library not installed. Run: pip install anthropic")
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # Use user's preferred model if specified, otherwise smart selection
        if self.preferred_model == "claude-3-5-haiku":
            # User explicitly wants Haiku (cost optimization)
            logger.info(f"Using user-preferred model {self.preferred_model}")
            return client, self.preferred_model
        elif self.total_cost > self.cost_threshold or not prefer_primary:
            # Auto fallback due to cost threshold
            logger.info(f"Using fallback model {self.fallback_model} (cost: ${self.total_cost:.2f})")
            return client, self.fallback_model
        else:
            # Use primary (Claude 4 Sonnet) or user preference
            model_to_use = self.preferred_model if self.preferred_model != "auto" else self.primary_model
            logger.info(f"Using primary model {model_to_use}")
            return client, model_to_use
    
    def track_cost(self, input_tokens: int, output_tokens: int, model: str):
        """Track API costs for enterprise cost management."""
        # Claude pricing (approximate)
        if "sonnet" in model:
            cost = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
        else:  # haiku
            cost = (input_tokens * 0.25 + output_tokens * 1.25) / 1_000_000
        
        self.total_cost += cost
        logger.info(f"API call cost: ${cost:.4f}, Total: ${self.total_cost:.2f}")
        return cost
    
    def call_with_logprobs(self, prompt: str, enable_logprobs: bool = False) -> Tuple[str, Optional[Dict[str, float]]]:
        """Call API with optional logprobs extraction for confidence calibration.
        
        Args:
            prompt: The prompt to send to the model
            enable_logprobs: Whether to attempt logprobs extraction
            
        Returns:
            Tuple of (response_text, logprobs_dict or None)
        """
        client, model = self.get_client()
        
        try:
            # Note: Anthropic Claude API doesn't directly support logprobs like OpenAI
            # This is a placeholder for when/if that functionality becomes available
            # For now, we'll make a standard call and return None for logprobs
            
            response = client.messages.create(
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
            
            response_text = response.content[0].text
            
            # Track API costs
            input_tokens = len(prompt) // 4  # Rough approximation
            output_tokens = len(response_text) // 4
            self.track_cost(input_tokens, output_tokens, model)
            
            # For now, logprobs are not available from Anthropic Claude API
            # We'll extract pseudo-logprobs from response patterns
            logprobs = self._extract_pseudo_logprobs(response_text) if enable_logprobs else None
            
            return response_text, logprobs
            
        except Exception as e:
            logger.error(f"API call with logprobs failed: {e}")
            raise
    
    def _extract_pseudo_logprobs(self, response_text: str) -> Dict[str, float]:
        """Extract pseudo-logprobs from response text patterns.
        
        This is a workaround since Claude API doesn't provide actual logprobs.
        We estimate confidence based on text patterns and language cues.
        
        Args:
            response_text: Response text from Claude
            
        Returns:
            Dictionary of pseudo-logprobs for key tokens
        """
        import re
        
        text_lower = response_text.lower()
        pseudo_logprobs = {}
        
        # Decision tokens with confidence-based pseudo-logprobs
        decision_patterns = {
            "pass": r'\b(pass|passed|acceptable|compliant|safe|approved)\b',
            "fail": r'\b(fail|failed|unacceptable|violation|unsafe|rejected)\b',
            "warning": r'\b(warning|caution|concern|partial|unclear|maybe)\b'
        }
        
        for decision, pattern in decision_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                # More matches = higher confidence (pseudo-logprob)
                # Convert to log probability scale (higher count = less negative)
                count = len(matches)
                pseudo_logprob = -1.0 / (count + 1)  # Range roughly -1.0 to -0.5
                pseudo_logprobs[decision] = pseudo_logprob
        
        # Confidence indicators
        confidence_patterns = {
            "high_confidence": r'\b(very confident|highly confident|certain|definitely|clearly)\b',
            "medium_confidence": r'\b(confident|likely|probably|sure)\b',
            "low_confidence": r'\b(uncertain|unsure|unclear|possibly|might|maybe)\b'
        }
        
        for confidence_level, pattern in confidence_patterns.items():
            if re.search(pattern, text_lower):
                # Map confidence levels to pseudo-logprobs
                confidence_scores = {
                    "high_confidence": -0.2,
                    "medium_confidence": -0.7,
                    "low_confidence": -2.0
                }
                pseudo_logprobs[confidence_level] = confidence_scores[confidence_level]
        
        return pseudo_logprobs
    
    def create_batch(self, prompts: List[Dict[str, Any]], prefer_primary: bool = False) -> Tuple[str, float]:
        """Create a batch evaluation request using Anthropic's Message Batches API.
        
        Args:
            prompts: List of evaluation prompts with metadata
            prefer_primary: Whether to prefer primary model (Sonnet) over fallback (Haiku)
            
        Returns:
            Tuple of (batch_id, estimated_cost)
        """
        client, model = self.get_client(prefer_primary=prefer_primary)
        
        try:
            # Prepare batch messages
            batch_requests = []
            for i, prompt_data in enumerate(prompts):
                request = {
                    "custom_id": f"eval_{i}_{prompt_data.get('scenario_id', 'unknown')}",
                    "params": {
                        "model": model,
                        "max_tokens": 2000,
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
            
            # Create batch via Anthropic API
            # Note: Using the Message Batches Beta API
            # TODO: When Anthropic batch API is available, use:
            # batch_response = client.beta.messages.batches.create(
            #     requests=batch_requests
            # )
            # batch_id = batch_response.id
            
            # For now, simulate batch creation with a unique ID
            import uuid
            batch_id = f"batch_{uuid.uuid4().hex[:8]}"
            logger.info(f"Simulated batch creation (real API pending): {batch_id}")
            
            # Estimate cost with batch discount
            from agent_eval.core.constants import BATCH_API_DISCOUNT
            total_tokens = sum(len(p["prompt"]) // 4 for p in prompts) * 2  # Rough estimate
            
            if "sonnet" in model:
                base_cost = (total_tokens * 3.0 + total_tokens * 15.0) / 1_000_000
            else:  # haiku
                base_cost = (total_tokens * 0.25 + total_tokens * 1.25) / 1_000_000
            
            discounted_cost = base_cost * BATCH_API_DISCOUNT
            
            logger.info(f"Created batch {batch_id} with {len(prompts)} evaluations. Estimated cost: ${discounted_cost:.4f}")
            
            return batch_id, discounted_cost
            
        except Exception as e:
            logger.error(f"Batch creation failed: {e}")
            raise
    
    def wait_for_batch(self, batch_id: str, timeout: int = 3600) -> List[Dict[str, Any]]:
        """Wait for batch completion and retrieve results.
        
        Args:
            batch_id: The batch ID to wait for
            timeout: Maximum wait time in seconds (default: 1 hour)
            
        Returns:
            List of batch results with responses
        """
        # TODO: When Anthropic batch API is available, use the real implementation
        # For now, this is a placeholder that processes synchronously
        logger.warning(f"Batch API not yet available - processing synchronously for batch {batch_id}")
        
        # This method should be called with the original prompts stored somewhere
        # For now, return empty results to avoid breaking the flow
        return []
    
    def process_batch_cascade(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process evaluations using cascade approach: Haiku batch → filter → Sonnet batch.
        
        This implements the cost-efficient cascade strategy:
        1. Run all evaluations through Haiku in batch
        2. Identify low-confidence results
        3. Re-run low-confidence cases through Sonnet
        
        Args:
            prompts: List of evaluation prompts with metadata
            
        Returns:
            Dictionary with results and telemetry
        """
        from agent_eval.core.constants import BATCH_CONFIDENCE_THRESHOLD, BATCH_API_DISCOUNT
        
        telemetry = {
            "total_evaluations": len(prompts),
            "haiku_evaluations": 0,
            "sonnet_evaluations": 0,
            "total_cost": 0.0,
            "cost_savings": 0.0,
            "start_time": datetime.now()
        }
        
        try:
            # Until batch API is available, process synchronously with simulated batching
            logger.info(f"Processing {len(prompts)} scenarios with cascade strategy (simulated batch)")
            
            # Phase 1: Process all with Haiku
            client, haiku_model = self.get_client(prefer_primary=False)
            haiku_results = []
            
            for prompt_data in prompts:
                try:
                    response = client.messages.create(
                        model=haiku_model,
                        max_tokens=2000,
                        temperature=0.1,
                        messages=[{"role": "user", "content": prompt_data["prompt"]}]
                    )
                    response_text = response.content[0].text
                    
                    # Track cost with batch discount simulation
                    input_tokens = len(prompt_data["prompt"]) // 4
                    output_tokens = len(response_text) // 4
                    cost = (input_tokens * 0.25 + output_tokens * 1.25) / 1_000_000
                    telemetry["total_cost"] += cost * BATCH_API_DISCOUNT
                    
                    haiku_results.append({
                        "response": response_text,
                        "error": None,
                        "prompt_data": prompt_data
                    })
                except Exception as e:
                    haiku_results.append({
                        "response": None,
                        "error": str(e),
                        "prompt_data": prompt_data
                    })
            
            telemetry["haiku_evaluations"] = len(prompts)
            
            # Phase 2: Identify low-confidence results
            low_confidence_prompts = []
            final_results = {}
            
            for result in haiku_results:
                prompt_data = result["prompt_data"]
                scenario_id = prompt_data.get("scenario_id", "unknown")
                
                if result["error"]:
                    low_confidence_prompts.append(prompt_data)
                    continue
                
                confidence = self._extract_confidence_from_response(result["response"])
                
                if confidence < BATCH_CONFIDENCE_THRESHOLD:
                    low_confidence_prompts.append(prompt_data)
                else:
                    final_results[scenario_id] = {
                        "response": result["response"],
                        "model": haiku_model,
                        "confidence": confidence
                    }
            
            # Phase 3: Re-evaluate low confidence with Sonnet
            if low_confidence_prompts:
                logger.info(f"Re-evaluating {len(low_confidence_prompts)} low-confidence scenarios with Sonnet")
                client, sonnet_model = self.get_client(prefer_primary=True)
                
                for prompt_data in low_confidence_prompts:
                    try:
                        response = client.messages.create(
                            model=sonnet_model,
                            max_tokens=2000,
                            temperature=0.1,
                            messages=[{"role": "user", "content": prompt_data["prompt"]}]
                        )
                        response_text = response.content[0].text
                        
                        # Track cost with batch discount
                        input_tokens = len(prompt_data["prompt"]) // 4
                        output_tokens = len(response_text) // 4
                        cost = (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
                        telemetry["total_cost"] += cost * BATCH_API_DISCOUNT
                        
                        scenario_id = prompt_data.get("scenario_id", "unknown")
                        final_results[scenario_id] = {
                            "response": response_text,
                            "model": sonnet_model,
                            "confidence": self._extract_confidence_from_response(response_text)
                        }
                    except Exception as e:
                        logger.error(f"Sonnet evaluation failed: {e}")
                
                telemetry["sonnet_evaluations"] = len(low_confidence_prompts)
            
            # Calculate telemetry
            telemetry["end_time"] = datetime.now()
            telemetry["duration"] = (telemetry["end_time"] - telemetry["start_time"]).total_seconds()
            
            # Calculate cost savings vs all-Sonnet approach
            all_sonnet_cost = len(prompts) * (3.0 + 15.0) * 2000 / 1_000_000
            telemetry["cost_savings"] = all_sonnet_cost - telemetry["total_cost"]
            telemetry["savings_percentage"] = (telemetry["cost_savings"] / all_sonnet_cost) * 100 if all_sonnet_cost > 0 else 0
            
            logger.info(f"Cascade complete. Cost: ${telemetry['total_cost']:.2f}, "
                       f"Savings: ${telemetry['cost_savings']:.2f} ({telemetry['savings_percentage']:.1f}%)")
            
            return {
                "results": final_results,
                "telemetry": telemetry
            }
            
        except Exception as e:
            logger.error(f"Batch cascade processing failed: {e}")
            raise
    
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
        
        # Fallback: Use pseudo-logprobs approach
        pseudo_logprobs = self._extract_pseudo_logprobs(response_text)
        
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
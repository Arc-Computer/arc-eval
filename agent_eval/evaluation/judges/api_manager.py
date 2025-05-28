"""
Enterprise API management with cost tracking and fallback.
"""

import os
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

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
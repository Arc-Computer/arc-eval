"""Smart input detection for automatic workflow routing."""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class SmartInputDetector:
    """Automatically detect input type for intelligent routing.
    
    This enables the test harness to work seamlessly without new CLI flags,
    by detecting whether the user provided:
    - Agent configuration (proactive testing)
    - Failed trace (reactive analysis + similar pattern testing)
    - Agent outputs (standard evaluation)
    - Mixed input (do both)
    """
    
    def __init__(self):
        # Common patterns that indicate each type
        self.config_indicators = {
            "required": ["agent", "tools", "system_prompt"],
            "optional": ["model", "temperature", "max_tokens", "framework"],
            "paths": ["agent_config", "config", "definition"]
        }
        
        self.trace_indicators = {
            "required": ["error", "stack_trace", "failed"],
            "optional": ["execution_time", "memory_usage", "timestamps"],
            "frameworks": ["langchain", "crewai", "openai", "anthropic"]
        }
        
        self.output_indicators = {
            "required": ["output", "scenario_id"],
            "optional": ["messages", "tool_calls", "reasoning"],
            "batch": ["outputs", "results", "evaluations"]
        }
    
    def detect_input_type(self, input_data: Any) -> str:
        """Detect the type of input provided.
        
        Returns:
            'config': Agent configuration file (trigger proactive testing)
            'trace': Failed execution trace (trigger reactive + similar)
            'output': Agent outputs for evaluation
            'mixed': Multiple types detected
        """
        if isinstance(input_data, str):
            # If string, try to load as file or JSON
            input_data = self._load_input(input_data)
        
        if isinstance(input_data, list):
            # Check if it's a batch of outputs
            if all(self._is_agent_output(item) for item in input_data):
                return 'output'
            # Could be mixed
            types = set(self.detect_input_type(item) for item in input_data)
            return 'mixed' if len(types) > 1 else types.pop()
        
        # Single item detection
        if self._is_agent_config(input_data):
            return 'config'
        elif self._is_failed_trace(input_data):
            return 'trace'
        elif self._is_agent_output(input_data):
            return 'output'
        
        return 'mixed'
    
    def _load_input(self, input_path: str) -> Any:
        """Load input from file path."""

        try:
            path = Path(input_path)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, PermissionError) as e:
            # Log file access error
            pass
        except json.JSONDecodeError as e:
            # Log JSON parsing error
            pass
        

        # Try parsing as JSON string

        try:
            return json.loads(input_path)
        except json.JSONDecodeError:
            return input_path

    
    def _is_agent_config(self, data: Any) -> bool:
        """Check if data is an agent configuration."""
        if not isinstance(data, dict):
            return False
        
        # Check for config file naming
        if "_config" in str(data.get("_source_file", "")).lower():
            return True
        
        # Check required fields
        required_found = sum(1 for field in self.config_indicators["required"] 
                           if field in data)
        
        # Check optional fields
        optional_found = sum(1 for field in self.config_indicators["optional"] 
                           if field in data)
        
        # Strong indication if most required fields present
        if required_found >= 2:
            return True
        
        # Medium indication with some required and optional
        if required_found >= 1 and optional_found >= 2:
            return True
        
        return False
    
    def _is_failed_trace(self, data: Any) -> bool:
        """Check if data is a failed execution trace."""
        if not isinstance(data, dict):
            return False
        
        # Explicit failure indicators
        if any(key in data for key in ["error", "exception", "failure", "failed"]):
            return True
        
        # Stack trace patterns
        if "stack_trace" in data or "traceback" in data:
            return True
        
        # Framework-specific failure patterns
        if data.get("status") == "failed":
            return True
        
        # LangChain specific
        if "intermediate_steps" in data and data.get("error"):
            return True
        
        # CrewAI specific
        if "crew_output" in data and data.get("execution_error"):
            return True
        
        return False
    
    def _is_agent_output(self, data: Any) -> bool:
        """Check if data is standard agent output for evaluation."""
        if not isinstance(data, dict):
            return False
        
        # Must have output
        if "output" not in data:
            return False
        
        # Should have scenario_id for evaluation
        if "scenario_id" in data:
            return True
        
        # Or have messages/tool_calls indicating execution
        if "messages" in data or "tool_calls" in data:
            return True
        
        return False
    
    def get_detected_domain(self, input_data: Any) -> Optional[str]:
        """Auto-detect domain from input data."""
        if not isinstance(input_data, dict):
            return None
            
        # Check for explicit domain
        if "domain" in input_data:
            return input_data["domain"]
        
        # Check for domain-specific keywords
        finance_keywords = ["transaction", "kyc", "aml", "sox", "payment", "banking"]
        security_keywords = ["auth", "injection", "owasp", "vulnerability", "exploit"]
        ml_keywords = ["model", "training", "bias", "fairness", "dataset"]
        
        content = json.dumps(input_data).lower()
        
        finance_score = sum(1 for kw in finance_keywords if kw in content)
        security_score = sum(1 for kw in security_keywords if kw in content)
        ml_score = sum(1 for kw in ml_keywords if kw in content)
        
        scores = {"finance": finance_score, "security": security_score, "ml": ml_score}
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def prepare_for_test_harness(self, input_data: Any, input_type: str) -> Dict:
        """Prepare input data for test harness based on detected type."""
        prepared = {
            "input_type": input_type,
            "domain": self.get_detected_domain(input_data),
            "data": input_data
        }
        
        if input_type == "config":
            # Extract key config elements for testing
            prepared["test_config"] = {
                "agent_type": input_data.get("agent", {}).get("type", "unknown"),
                "tools": input_data.get("tools", []),
                "system_prompt": input_data.get("system_prompt", ""),
                "framework": input_data.get("framework", "unknown")
            }
        
        elif input_type == "trace":
            # Extract failure patterns for similar testing
            prepared["failure_info"] = {
                "error_type": input_data.get("error", {}).get("type", "unknown"),
                "error_message": input_data.get("error", {}).get("message", ""),
                "failed_step": input_data.get("failed_step", ""),
                "framework": self._detect_framework(input_data)
            }
        
        return prepared
    
    def _detect_framework(self, data: Dict) -> str:
        """Detect which agent framework was used."""
        if "intermediate_steps" in data:
            return "langchain"
        elif "crew_output" in data:
            return "crewai"
        elif "messages" in data and "model" in data:
            if "anthropic" in data.get("model", ""):
                return "anthropic"
            return "openai"
        return "unknown"
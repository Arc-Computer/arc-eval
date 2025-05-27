"""Reliability validation for agent tool calls and error handling patterns."""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ToolCallValidation:
    """Result of tool call validation for a single output."""
    
    expected_tools: List[str]
    detected_tools: List[str]
    missing_tools: List[str]
    unexpected_tools: List[str]
    tool_call_accuracy: float  # Percentage of expected tools found
    framework_detected: Optional[str]
    error_recovery_detected: bool
    timeout_detected: bool
    reliability_score: float  # Overall reliability (0.0-1.0)
    validation_details: Dict[str, Any]


class ReliabilityValidator:
    """Validates agent reliability through tool call analysis and error pattern detection."""
    
    def __init__(self):
        """Initialize reliability validator with framework-specific patterns."""
        
        # Tool call patterns for different frameworks
        self.tool_patterns = {
            "openai": [
                r'"function":\s*{\s*"name":\s*"([^"]+)"',  # OpenAI function calls
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',
                r'```python\n.*?(\w+)\(',  # Code execution tools
            ],
            "anthropic": [
                r'<function_calls>.*?<invoke name="([^"]+)"',  # Claude function calls
                r'<tool_use>.*?<name>([^<]+)</name>',
                r'Tool: ([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "langchain": [
                r'"tool":\s*"([^"]+)"',  # LangChain tool calls
                r'Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'```\s*(\w+)\(',  # Code tools
                r'using tool ([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "crewai": [
                r'"tool_name":\s*"([^"]+)"',  # CrewAI tool calls
                r'Tool Used:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Thought.*?Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "autogen": [
                r'"function_call".*?"name":\s*"([^"]+)"',  # AutoGen function calls
                r'execute_code.*?language.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Tool execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "agno": [
                r'"tools_used":\s*\[.*?"([^"]+)".*?\]',  # Agno tools_used array
                r'"function_calls".*?"name":\s*"([^"]+)"',  # Agno function calls
                r'using tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "google_adk": [
                r'"functionCall":\s*{\s*"name":\s*"([^"]+)"',  # Google ADK function calls
                r'function call:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "nvidia_aiq": [
                r'(?:tool|action|execute):\s*([a-zA-Z_][a-zA-Z0-9_]*)',  # NVIDIA AIQ patterns
                r'workflow execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "langgraph": [
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',  # LangGraph tool calls
                r'node execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "generic": [
                r'(?:call|calling|invoke|invoking|use|using|execute|executing).*?tool.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'(?:function|method|api).*?call.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'```(\w+)\n',  # Code blocks as tool calls
            ]
        }
        
        # Error recovery patterns
        self.error_patterns = {
            "graceful_error": [
                r'(?:error|exception|failure).*?(?:handled|caught|recovered)',
                r'fallback.*?(?:strategy|mechanism|approach)',
                r'retry.*?(?:attempt|mechanism|strategy)',
                r'alternative.*?(?:approach|method|solution)',
            ],
            "timeout_handling": [
                r'timeout.*?(?:detected|occurred|handled)',
                r'request.*?timed out',
                r'connection.*?timeout',
                r'maximum.*?(?:time|duration).*?exceeded',
            ]
        }
    
    def detect_framework(self, agent_output: str) -> Optional[str]:
        """Detect the agent framework based on output patterns."""
        for framework, patterns in self.tool_patterns.items():
            if framework == "generic":
                continue
            for pattern in patterns:
                if re.search(pattern, agent_output, re.IGNORECASE | re.DOTALL):
                    return framework
        return None
    
    def extract_tool_calls(self, agent_output, framework: Optional[str] = None) -> List[str]:
        """Extract tool calls from agent output."""
        detected_tools = []
        
        # Handle both string and AgentOutput inputs for backward compatibility
        from agent_eval.core.types import AgentOutput
        if isinstance(agent_output, AgentOutput):
            # Convert AgentOutput to string representation
            if agent_output.raw_output:
                output_str = str(agent_output.raw_output)
                # Convert Python dict syntax to JSON syntax for pattern matching
                if output_str.startswith("{") and "'" in output_str:
                    # Replace single quotes with double quotes for JSON compatibility
                    import re
                    output_str = re.sub(r"'([^']*)':", r'"\1":', output_str)  # Keys
                    output_str = re.sub(r":\s*'([^']*)'", r': "\1"', output_str)  # String values
            else:
                output_str = ""
        else:
            output_str = str(agent_output)
        
        # Try framework-specific patterns first
        if framework and framework in self.tool_patterns:
            patterns = self.tool_patterns[framework]
        else:
            # Try all patterns if framework is unknown
            patterns = []
            for fw_patterns in self.tool_patterns.values():
                patterns.extend(fw_patterns)
        
        for pattern in patterns:
            matches = re.findall(pattern, output_str, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle multiple capture groups
                    for group in match:
                        if group and group.strip():
                            detected_tools.append(group.strip().lower())
                else:
                    if match and match.strip():
                        detected_tools.append(match.strip().lower())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in detected_tools:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)
        
        return unique_tools
    
    def detect_error_recovery(self, agent_output: str) -> Dict[str, bool]:
        """Detect error recovery patterns in agent output."""
        recovery_detected = {}
        
        for error_type, patterns in self.error_patterns.items():
            detected = False
            for pattern in patterns:
                if re.search(pattern, agent_output, re.IGNORECASE | re.DOTALL):
                    detected = True
                    break
            recovery_detected[error_type] = detected
        
        return recovery_detected
    
    def validate_tool_calls(
        self, 
        agent_output: str, 
        expected_tools: List[str],
        scenario_context: Optional[Dict[str, Any]] = None
    ) -> ToolCallValidation:
        """Validate tool calls in agent output against expected tools."""
        
        # Normalize expected tools to lowercase
        expected_tools_norm = [tool.lower() for tool in expected_tools]
        
        # Detect framework
        framework = self.detect_framework(agent_output)
        
        # Extract actual tool calls
        detected_tools = self.extract_tool_calls(agent_output, framework)
        
        # Calculate missing and unexpected tools
        detected_set = set(detected_tools)
        expected_set = set(expected_tools_norm)
        
        missing_tools = list(expected_set - detected_set)
        unexpected_tools = list(detected_set - expected_set)
        
        # Calculate tool call accuracy
        if not expected_tools_norm:
            tool_call_accuracy = 1.0 if not detected_tools else 0.5
        else:
            correct_tools = len(expected_set.intersection(detected_set))
            tool_call_accuracy = correct_tools / len(expected_set)
        
        # Detect error recovery patterns
        error_recovery = self.detect_error_recovery(agent_output)
        error_recovery_detected = any(error_recovery.values())
        timeout_detected = error_recovery.get("timeout_handling", False)
        
        # Calculate overall reliability score
        reliability_score = self._calculate_reliability_score(
            tool_call_accuracy, 
            error_recovery_detected, 
            timeout_detected,
            len(missing_tools),
            len(unexpected_tools)
        )
        
        validation_details = {
            "framework_patterns_matched": framework is not None,
            "error_recovery_patterns": error_recovery,
            "tool_call_patterns_found": len(detected_tools) > 0,
            "scenario_context": scenario_context
        }
        
        return ToolCallValidation(
            expected_tools=expected_tools,
            detected_tools=detected_tools,
            missing_tools=missing_tools,
            unexpected_tools=unexpected_tools,
            tool_call_accuracy=tool_call_accuracy,
            framework_detected=framework,
            error_recovery_detected=error_recovery_detected,
            timeout_detected=timeout_detected,
            reliability_score=reliability_score,
            validation_details=validation_details
        )
    
    def _calculate_reliability_score(
        self, 
        tool_accuracy: float, 
        error_recovery: bool, 
        timeout_handling: bool,
        missing_count: int,
        unexpected_count: int
    ) -> float:
        """Calculate overall reliability score from various factors."""
        
        # Base score from tool call accuracy
        score = tool_accuracy * 0.6  # 60% weight for tool accuracy
        
        # Bonus for error recovery
        if error_recovery:
            score += 0.2
        
        # Bonus for timeout handling
        if timeout_handling:
            score += 0.1
        
        # Penalty for missing tools
        missing_penalty = min(missing_count * 0.1, 0.3)
        score -= missing_penalty
        
        # Smaller penalty for unexpected tools (might be beneficial)
        unexpected_penalty = min(unexpected_count * 0.05, 0.15)
        score -= unexpected_penalty
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def batch_validate(
        self, 
        agent_outputs: List[str], 
        expected_tools_list: List[List[str]],
        scenario_contexts: Optional[List[Dict[str, Any]]] = None
    ) -> List[ToolCallValidation]:
        """Validate tool calls for multiple agent outputs."""
        
        if len(agent_outputs) != len(expected_tools_list):
            raise ValueError("Number of agent outputs must match number of expected tool lists")
        
        results = []
        for i, (output, expected_tools) in enumerate(zip(agent_outputs, expected_tools_list)):
            context = scenario_contexts[i] if scenario_contexts and i < len(scenario_contexts) else None
            validation = self.validate_tool_calls(output, expected_tools, context)
            results.append(validation)
        
        return results
    
    def generate_reliability_metrics(self, validations: List[ToolCallValidation]) -> Dict[str, Any]:
        """Generate comprehensive reliability metrics from validation results."""
        
        if not validations:
            return {
                "overall_reliability_score": 0.0,
                "tool_call_accuracy": 0.0,
                "error_recovery_rate": 0.0,
                "timeout_handling_rate": 0.0,
                "framework_detection_rate": 0.0,
                "reliability_issues": ["No validation data available"]
            }
        
        # Calculate aggregate metrics
        total_validations = len(validations)
        avg_tool_accuracy = sum(v.tool_call_accuracy for v in validations) / total_validations
        error_recovery_rate = sum(1 for v in validations if v.error_recovery_detected) / total_validations
        timeout_rate = sum(1 for v in validations if v.timeout_detected) / total_validations
        framework_detection_rate = sum(1 for v in validations if v.framework_detected) / total_validations
        avg_reliability_score = sum(v.reliability_score for v in validations) / total_validations
        
        # Identify common issues
        reliability_issues = []
        
        if avg_tool_accuracy < 0.7:
            reliability_issues.append("Low tool call accuracy - agents may not be using expected tools")
        
        if error_recovery_rate < 0.3:
            reliability_issues.append("Limited error recovery patterns detected")
        
        if framework_detection_rate < 0.8:
            reliability_issues.append("Framework patterns not consistently detected")
        
        # Count missing tools across all validations
        all_missing_tools = []
        for v in validations:
            all_missing_tools.extend(v.missing_tools)
        
        if all_missing_tools:
            missing_counter = Counter(all_missing_tools)
            most_missing = missing_counter.most_common(3)
            reliability_issues.append(f"Frequently missing tools: {', '.join([f'{tool} ({count}x)' for tool, count in most_missing])}")
        
        return {
            "overall_reliability_score": avg_reliability_score,
            "tool_call_accuracy": avg_tool_accuracy,
            "error_recovery_rate": error_recovery_rate,
            "timeout_handling_rate": timeout_rate,
            "framework_detection_rate": framework_detection_rate,
            "total_validations": total_validations,
            "reliability_issues": reliability_issues if reliability_issues else ["No major reliability issues detected"],
            "framework_distribution": self._get_framework_distribution(validations)
        }
    
    def _get_framework_distribution(self, validations: List[ToolCallValidation]) -> Dict[str, int]:
        """Get distribution of detected frameworks."""
        framework_counts = Counter()
        
        for validation in validations:
            framework = validation.framework_detected or "unknown"
            framework_counts[framework] += 1
        
        return dict(framework_counts)
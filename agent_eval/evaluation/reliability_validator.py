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
                # OpenAI API standard format: tool_calls array with function objects
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',
                r'"function":\s*{\s*"name":\s*"([^"]+)"',  # Direct function object
                r'"type":\s*"function".*?"name":\s*"([^"]+)"',  # type: function format
                # Legacy function_call format
                r'"function_call".*?"name":\s*"([^"]+)"',
            ],
            "anthropic": [
                # XML-style Claude patterns
                r'<function_calls>.*?<invoke name="([^"]+)"',
                r'<tool_use>.*?<name>([^<]+)</name>',
                # JSON-style Anthropic patterns (test data & real usage)
                r'"type":\s*"tool_use".*?"name":\s*"([^"]+)"',
                r'"tool_use".*?"name":\s*"([^"]+)"',
                # Text patterns
                r'Tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Using tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "langchain": [
                # LangChain specific patterns
                r'"tool":\s*"([^"]+)"',
                r'Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'AgentAction\(tool=[\'"]([^\'\"]+)[\'"]',  # AgentAction format
                r'tool=[\'"]([^\'\"]+)[\'"]',  # Tool parameter
                r'intermediate_steps.*?tool=[\'"]([^\'\"]+)[\'"]',
                r'```\s*(\w+)\(',
                r'using tool ([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "crewai": [
                # CrewAI patterns - based on actual output structure
                r'"tool_name":\s*"([^"]+)"',
                r'Tool Used:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"name":\s*"([^"]+)"(?=.*"input":)',  # Match name only when followed by input (CrewAI pattern)
                r'task_output.*?tools_used.*?"name":\s*"([^"]+)"',  # Full task output structure
                r'crew_output.*?"([^"]+)"',
                r'task_results.*?"([^"]+)"',
            ],
            "autogen": [
                # AutoGen patterns
                r'"function_call".*?"name":\s*"([^"]+)"',
                r'execute_code.*?language.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Tool execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"function".*?"name":\s*"([^"]+)"',
            ],
            "agno": [
                # Agno framework patterns
                r'"tools_used":\s*\[.*?"([^"]+)".*?\]',
                r'"function_calls".*?"name":\s*"([^"]+)"',
                r'using tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'agno.*?tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "google_adk": [
                # Google AI Development Kit patterns  
                r'"functionCall":\s*{\s*"name":\s*"([^"]+)"',
                r'function call:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"tool_name":\s*"([^"]+)"',
                r'vertex_ai_tools.*?"tool_name":\s*"([^"]+)"',
            ],
            "nvidia_aiq": [
                # NVIDIA AIQ patterns - based on actual workflow output structure
                r'"workflow_output".*?"intermediate_steps".*?"([^"]+)"',
                r'"input_message".*?"workflow_output".*?"([^"]+)"',
                r'"TOOL_START".*?"([^"]+)"',  # Tool execution tracking
                r'"TOOL_END".*?"([^"]+)"',    # Tool completion tracking
                r'workflow_output\.json.*?"([^"]+)"',
            ],
            "langgraph": [
                # LangGraph patterns
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',
                r'node execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"messages".*?"tool_calls".*?"name":\s*"([^"]+)"',
                r'langgraph.*?tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "custom": [
                # Enhanced trace format (REAL CUSTOMER DATA)
                r'"tool":\s*"([^"]+)"',  # Most common: "tool": "tool_name"
                r'"action":\s*"tool_call".*?"tool":\s*"([^"]+)"',
                r'tool_call.*?"tool":\s*"([^"]+)"',
                # Common tool naming patterns found in customer data
                r'([a-zA-Z_][a-zA-Z0-9_]*(?:_api|_tool|_engine|_analyzer|_validator|_detector|_monitor|_checker))',
            ],
            "generic": [
                # Generic patterns for any framework
                r'"tool":\s*"([^"]+)"',  # JSON tool field
                r'(?:call|calling|invoke|invoking|use|using|execute|executing).*?tool.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'(?:function|method|api).*?call.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'tool.*?([a-zA-Z_][a-zA-Z0-9_]*(?:_api|_tool|_engine|_analyzer|_validator|_detector|_monitor|_checker))',
                r'```python\n.*?(\w+)\(',  # Code execution tools
                r'(\w+)\.(\w+)\(',  # Method calls like tool.function()
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
        """Detect the agent framework based on structural patterns."""
        
        # Framework detection should look for structural indicators, not tool patterns
        framework_indicators = {
            "openai": [
                r'"tool_calls":\s*\[',  # OpenAI tool_calls array
                r'"choices".*?"message".*?"tool_calls"',  # Full OpenAI response structure
                r'"function_call".*?"name"',  # Legacy OpenAI function_call
            ],
            "anthropic": [
                r'"content":\s*\[.*?"type":\s*"tool_use"',  # Anthropic tool_use blocks
                r'<function_calls>.*?<invoke name=',  # XML-style Claude
                r'"stop_reason".*?"tool_use"',  # Anthropic response format
            ],
            "langchain": [
                r'"intermediate_steps":\s*\[',  # LangChain intermediate steps
                r'"agent_scratchpad"',  # LangChain agent scratchpad
                r'AgentAction\(tool=',  # LangChain AgentAction format
            ],
            "crewai": [
                r'"task_output".*?"tools_used"',  # CrewAI task output structure
                r'"crew_output"',  # CrewAI crew output
                r'"task_results".*?"tools_used"',  # CrewAI task results
            ],
            "nvidia_aiq": [
                r'"workflow_output".*?"intermediate_steps"',  # NVIDIA AIQ workflow output
                r'"aiq_pipeline".*?"components"',  # AIQ pipeline structure
                r'"input_message".*?"workflow_output"',  # AIQ input/output structure
            ],
            "langgraph": [
                r'"graph_execution".*?"nodes"',  # LangGraph execution
                r'"messages".*?"graph_state"',  # LangGraph state
            ],
            "autogen": [
                r'"messages".*?"summary"',  # AutoGen conversation format
                r'"author".*?"content"',  # AutoGen message format
            ],
            "agno": [
                r'"structured_output".*?"agent_run_id"',  # Agno structured output
                r'"response".*?"tools_used"',  # Agno response format
            ],
            "google_adk": [
                r'"author".*?"content".*?"parts"',  # Google ADK format
                r'"functionCall".*?"name"',  # Google function call format
            ],
        }
        
        for framework, patterns in framework_indicators.items():
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
                    # Use safer ast.literal_eval + json.dumps approach
                    import ast
                    import json
                    try:
                        # Safely evaluate the string as a Python dictionary
                        parsed_dict = ast.literal_eval(output_str)
                        # Convert the Python dictionary to a JSON string
                        output_str = json.dumps(parsed_dict)
                    except (ValueError, SyntaxError) as e:
                        logger.warning(f"Failed to parse dict string safely, falling back to regex: {e}")
                        # Fallback to regex approach if ast.literal_eval fails
                        output_str = re.sub(r"'([^']*)':", r'"\1":', output_str)  # Keys
                        output_str = re.sub(r":\s*'([^']*)'(?=\s*[,}\]])", r': "\1"', output_str)  # String values
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
        
        # Remove duplicates and filter invalid tool names
        seen = set()
        unique_tools = []
        for tool in detected_tools:
            # Filter out invalid tool names and common false positives
            if (tool and 
                tool not in seen and 
                len(tool) > 1 and  # Tool names should be more than 1 character
                not tool.startswith('_') and  # Avoid partial matches like '_use'
                tool not in ['name', 'input', 'output', 'type', 'content', 'function', 'call', 'tool', 'id'] and  # Common false positives
                tool.replace('_', '').replace('-', '').isalnum()):  # Valid tool name format
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
    
    def validate_tool_usage(
        self, 
        agent_output, 
        expected_tools: List[str],
        scenario_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate tool calls in agent output against expected tools."""
        
        # Handle both string and AgentOutput inputs
        from agent_eval.core.types import AgentOutput
        if isinstance(agent_output, AgentOutput):
            output_str = agent_output.raw_output
        else:
            output_str = str(agent_output)
        
        # Normalize expected tools to lowercase
        expected_tools_norm = [tool.lower() for tool in expected_tools]
        
        # Detect framework
        framework = self.detect_framework(output_str)
        
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
        error_recovery = self.detect_error_recovery(output_str)
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
        
        return {
            'expected_tools': len(expected_tools),
            'tools_found': len(expected_set.intersection(detected_set)),
            'coverage_rate': tool_call_accuracy,
            'missing_tools': missing_tools,
            'unexpected_tools': unexpected_tools,
            'reliability_score': reliability_score,
            'detected_tools': detected_tools,
            'framework_detected': framework,
            'error_recovery_detected': error_recovery_detected,
            'timeout_detected': timeout_detected,
            'validation_details': validation_details
        }
    
    def _calculate_reliability_score(
        self, 
        tool_accuracy: float, 
        error_recovery: bool, 
        timeout_handling: bool,
        missing_count: int,
        unexpected_count: int
    ) -> float:
        """Calculate overall reliability score from various factors."""
        
        # Perfect tool accuracy should yield perfect score when no issues
        # Note: missing_count and unexpected_count are passed as parameters
        if tool_accuracy == 1.0 and missing_count == 0 and unexpected_count == 0:
            return 1.0
        
        # Base score from tool call accuracy (higher weight for perfect accuracy)
        score = tool_accuracy * 0.8  # 80% weight for tool accuracy
        
        # Bonus for error recovery
        if error_recovery:
            score += 0.15
        
        # Bonus for timeout handling
        if timeout_handling:
            score += 0.05
        
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
            validation = self.validate_tool_usage(output, expected_tools, context)
            results.append(validation)
        
        return results
    
    def generate_reliability_metrics(self, validations: List[Dict[str, Any]]) -> 'ReliabilityMetrics':
        """Generate comprehensive reliability metrics from validation results."""
        
        if not validations:
            from agent_eval.core.types import ReliabilityMetrics
            return ReliabilityMetrics(
                expected_tool_calls=[],
                actual_tool_calls=[],
                tool_call_accuracy=0.0,
                error_recovery_rate=0.0,
                timeout_rate=0.0,
                framework_compliance={},
                reliability_score=0.0,
                reliability_issues=["No validation data available"]
            )
        
        # Calculate aggregate metrics
        total_validations = len(validations)
        avg_tool_accuracy = sum(v['coverage_rate'] for v in validations) / total_validations
        error_recovery_rate = sum(1 for v in validations if v.get('error_recovery_detected', False)) / total_validations
        timeout_rate = sum(1 for v in validations if v.get('timeout_detected', False)) / total_validations
        framework_detection_rate = sum(1 for v in validations if v.get('framework_detected')) / total_validations
        avg_reliability_score = sum(v['reliability_score'] for v in validations) / total_validations
        
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
            all_missing_tools.extend(v.get('missing_tools', []))
        
        if all_missing_tools:
            missing_counter = Counter(all_missing_tools)
            most_missing = missing_counter.most_common(3)
            reliability_issues.append(f"Frequently missing tools: {', '.join([f'{tool} ({count}x)' for tool, count in most_missing])}")
        
        # Import ReliabilityMetrics here to avoid circular imports
        from agent_eval.core.types import ReliabilityMetrics
        
        return ReliabilityMetrics(
            expected_tool_calls=[],
            actual_tool_calls=[], 
            tool_call_accuracy=avg_tool_accuracy,
            error_recovery_rate=error_recovery_rate,
            timeout_rate=timeout_rate,
            framework_compliance={"overall": framework_detection_rate},
            reliability_score=avg_reliability_score,
            reliability_issues=reliability_issues if reliability_issues else ["No major reliability issues detected"]
        )
    
    def _get_framework_distribution(self, validations: List[ToolCallValidation]) -> Dict[str, int]:
        """Get distribution of detected frameworks."""
        framework_counts = Counter()
        
        for validation in validations:
            framework = validation.get('framework_detected') or "unknown"
            framework_counts[framework] += 1
        
        return dict(framework_counts)
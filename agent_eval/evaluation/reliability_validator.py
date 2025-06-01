"""Reliability validation for agent tool calls and error handling patterns."""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter

from agent_eval.core.types import ReliabilityMetrics

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


@dataclass
class WorkflowReliabilityMetrics:
    """Enhanced metrics for workflow reliability analysis."""
    
    # Core workflow metrics (from positioning doc)
    workflow_success_rate: float           # End-to-end completion rate
    tool_chain_reliability: float          # Tool call success rate
    decision_consistency_score: float      # Consistent decisions across runs
    multi_step_completion_rate: float      # Multi-step task completion
    
    # Performance reliability
    average_workflow_time: float           # Seconds to complete workflow
    error_recovery_rate: float             # Successful error recoveries  
    timeout_rate: float                    # Workflows that timeout
    
    # Framework-specific reliability
    framework_compatibility_score: float   # How well agent uses framework
    tool_usage_efficiency: float          # Optimal tool selection rate
    
    # Schema mismatch detection (NEW - addresses prompt-tool mismatch)
    schema_mismatch_rate: float            # Tool schema vs LLM output mismatch
    prompt_tool_alignment_score: float     # How well tools match prompts
    
    # Improvement trajectory
    reliability_trend: str                 # "improving", "stable", "degrading"
    critical_failure_points: List[str]     # Workflow steps that commonly fail


@dataclass
class FrameworkPerformanceAnalysis:
    """Data-driven analysis of framework-specific performance patterns."""
    
    framework_name: str
    sample_size: int
    
    # Performance metrics (measured from actual data)
    avg_response_time: float
    success_rate: float
    tool_call_failure_rate: float
    timeout_frequency: float
    
    # Framework-specific issues (detected from patterns)
    abstraction_overhead: float           # Detected layers of abstraction causing delays
    delegation_bottlenecks: List[str]     # Specific delegation patterns causing slowness
    memory_leak_indicators: List[str]     # Memory management issues
    
    # Evidence-based recommendations
    performance_bottlenecks: List[Dict[str, Any]]  # Specific bottlenecks with evidence
    optimization_opportunities: List[Dict[str, Any]]  # Data-backed optimization suggestions
    framework_alternatives: List[str]     # Better frameworks for this use case
    
    # Confidence scores
    analysis_confidence: float            # How confident we are in this analysis
    recommendation_strength: str          # "high", "medium", "low"


@dataclass
class ComprehensiveReliabilityAnalysis:
    """Complete reliability analysis results for unified debugging and workflow analysis."""
    
    # Framework Detection
    detected_framework: Optional[str]
    framework_confidence: float
    auto_detection_successful: bool
    
    # Performance Analysis
    framework_performance: Optional[FrameworkPerformanceAnalysis]
    workflow_metrics: WorkflowReliabilityMetrics
    
    # Tool Call Analysis
    tool_call_summary: Dict[str, Any]
    validation_results: List[Dict[str, Any]]
    
    # Dashboard Data
    reliability_dashboard: str  # Rich formatted dashboard for CLI display
    insights_summary: List[str]  # Key insights for user
    next_steps: List[str]       # Recommended actions
    
    # Cognitive Analysis (NEW - Task 8)
    cognitive_analysis: Optional[Any]  # CognitiveAnalyzer results
    
    # Evidence and Confidence
    analysis_confidence: float
    evidence_quality: str      # "high", "medium", "low"
    sample_size: int


class ReliabilityAnalyzer:
    """Comprehensive reliability analyzer combining validation, framework analysis, and dashboard generation."""
    
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
    
    def detect_framework_comprehensive(self, agent_outputs: List[Any]) -> Dict[str, Any]:
        """Comprehensive framework detection with confidence scoring and auto-detection."""
        
        # First try using the parser_registry's detect_framework for more accurate detection
        from agent_eval.core.parser_registry import detect_and_extract
        
        framework_counts = {}
        for output in agent_outputs:
            try:
                # Try to detect framework using parser_registry
                framework, _ = detect_and_extract(output)
                if framework:
                    framework_counts[framework] = framework_counts.get(framework, 0) + 1
            except Exception:
                # Silently skip outputs that can't be parsed
                pass
        
        # If we got reliable detection from parser_registry
        if framework_counts:
            # Find most common framework
            detected_framework = max(framework_counts, key=framework_counts.get)
            confidence = framework_counts[detected_framework] / len(agent_outputs)
            
            return {
                'detected_framework': detected_framework,
                'confidence': confidence,
                'auto_detection_successful': True,
                'framework_scores': framework_counts
            }
        
        # Fallback to pattern-based detection if parser_registry didn't work
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
        
        # Count framework matches across all outputs
        framework_scores = {fw: 0 for fw in framework_indicators.keys()}
        total_outputs = len(agent_outputs)
        
        for output in agent_outputs:
            output_str = str(output)
            for framework, patterns in framework_indicators.items():
                for pattern in patterns:
                    if re.search(pattern, output_str, re.IGNORECASE | re.DOTALL):
                        framework_scores[framework] += 1
                        break  # Only count once per output per framework
        
        # Find the best match
        if total_outputs == 0:
            return {
                'detected_framework': None,
                'confidence': 0.0,
                'auto_detection_successful': False,
                'framework_scores': framework_scores
            }
        
        best_framework = max(framework_scores.items(), key=lambda x: x[1])
        framework_name, match_count = best_framework
        
        # Calculate confidence as percentage of outputs that matched
        confidence = match_count / total_outputs if total_outputs > 0 else 0.0
        
        # Only return a framework if confidence is reasonable
        detected_framework = framework_name if confidence >= 0.3 else None
        auto_detection_successful = confidence >= 0.5
        
        return {
            'detected_framework': detected_framework,
            'confidence': confidence,
            'auto_detection_successful': auto_detection_successful,
            'framework_scores': framework_scores
        }
    
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
    
    def analyze_framework_performance(self, agent_outputs: List[Any], framework: str) -> FrameworkPerformanceAnalysis:
        """Generate data-driven framework performance analysis from actual agent outputs."""
        
        # Extract performance metrics from actual data
        response_times = []
        success_rates = []
        tool_call_failures = []
        timeout_occurrences = []
        
        # Analyze each output for performance patterns
        for output in agent_outputs:
            # Extract timing data if available
            timing_data = self._extract_timing_data(output)
            if timing_data:
                response_times.append(timing_data['duration'])
                
            # Analyze success/failure patterns
            success_indicators = self._analyze_success_patterns(output)
            success_rates.append(success_indicators['success_rate'])
            
            # Detect tool call failures
            tool_failures = self._detect_tool_call_failures(output)
            tool_call_failures.extend(tool_failures)
            
            # Check for timeout indicators
            if self._detect_timeout_patterns(output):
                timeout_occurrences.append(1)
            else:
                timeout_occurrences.append(0)
        
        # Calculate aggregate metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        overall_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        tool_failure_rate = len([f for f in tool_call_failures if f]) / len(agent_outputs) if agent_outputs else 0
        timeout_frequency = sum(timeout_occurrences) / len(timeout_occurrences) if timeout_occurrences else 0
        
        # Framework-specific pattern analysis
        framework_issues = self._analyze_framework_specific_issues(agent_outputs, framework)
        
        # Generate evidence-based recommendations
        performance_bottlenecks = self._identify_performance_bottlenecks(agent_outputs, framework)
        optimization_opportunities = self._identify_optimization_opportunities(framework_issues, performance_bottlenecks)
        
        # Calculate confidence based on sample size and data quality
        analysis_confidence = self._calculate_analysis_confidence(len(agent_outputs), framework_issues)
        recommendation_strength = self._determine_recommendation_strength(analysis_confidence, performance_bottlenecks)
        
        return FrameworkPerformanceAnalysis(
            framework_name=framework,
            sample_size=len(agent_outputs),
            avg_response_time=avg_response_time,
            success_rate=overall_success_rate,
            tool_call_failure_rate=tool_failure_rate,
            timeout_frequency=timeout_frequency,
            abstraction_overhead=framework_issues.get('abstraction_overhead', 0.0),
            delegation_bottlenecks=framework_issues.get('delegation_bottlenecks', []),
            memory_leak_indicators=framework_issues.get('memory_leaks', []),
            performance_bottlenecks=performance_bottlenecks,
            optimization_opportunities=optimization_opportunities,
            framework_alternatives=self._suggest_framework_alternatives(framework, performance_bottlenecks),
            analysis_confidence=analysis_confidence,
            recommendation_strength=recommendation_strength
        )
    
    def _extract_timing_data(self, output: Any) -> Optional[Dict[str, float]]:
        """Extract timing information from agent output."""
        if isinstance(output, dict):
            # Look for common timing fields
            if 'duration' in output:
                return {'duration': float(output['duration'])}
            if 'start_time' in output and 'end_time' in output:
                try:
                    from datetime import datetime
                    start = datetime.fromisoformat(output['start_time'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(output['end_time'].replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                    return {'duration': duration}
                except (ValueError, AttributeError):
                    pass
            if 'duration_seconds' in output:
                return {'duration': float(output['duration_seconds'])}
        return None
    
    def _analyze_success_patterns(self, output: Any) -> Dict[str, float]:
        """Analyze success/failure patterns in agent output."""
        if isinstance(output, dict):
            # Direct success indicator
            if 'success' in output:
                return {'success_rate': 1.0 if output['success'] else 0.0}
            
            # Status-based success
            if 'status' in output:
                success_statuses = ['completed', 'success', 'done']
                return {'success_rate': 1.0 if output['status'] in success_statuses else 0.0}
            
            # Error-based failure detection
            if 'error' in output or 'errors' in output:
                return {'success_rate': 0.0}
            
            # Tool call success analysis
            if 'tool_call' in output:
                tool_call = output['tool_call']
                if isinstance(tool_call, dict):
                    if 'result' in tool_call and tool_call['result'] is not None:
                        return {'success_rate': 1.0}
                    if 'error' in tool_call:
                        return {'success_rate': 0.0}
        
        # Default: assume success if no clear failure indicators
        return {'success_rate': 0.8}  # Conservative default
    
    def _detect_tool_call_failures(self, output: Any) -> List[Dict[str, Any]]:
        """Detect specific tool call failures from output."""
        failures = []
        
        if isinstance(output, dict):
            # Direct tool call failure
            if 'tool_call' in output:
                tool_call = output['tool_call']
                if isinstance(tool_call, dict) and 'error' in tool_call:
                    failures.append({
                        'type': 'tool_call_error',
                        'tool_name': tool_call.get('name', 'unknown'),
                        'error': tool_call['error']
                    })
            
            # Parameter mismatch detection
            output_str = str(output)
            if 'parameter mismatch' in output_str.lower():
                failures.append({
                    'type': 'parameter_mismatch',
                    'description': 'Tool parameter schema mismatch detected'
                })
            
            # Schema error detection
            if 'schema error' in output_str.lower():
                failures.append({
                    'type': 'schema_error',
                    'description': 'Tool schema validation failed'
                })
        
        return failures
    
    def _detect_timeout_patterns(self, output: Any) -> bool:
        """Detect timeout indicators in output."""
        if isinstance(output, dict):
            # Direct timeout indicators
            if 'timeout' in output or 'timed_out' in output:
                return True
            
            # Status-based timeout
            if output.get('status') == 'timeout':
                return True
            
            # Error-based timeout detection
            error_text = str(output.get('error', ''))
            timeout_keywords = ['timeout', 'timed out', 'time limit', 'deadline exceeded']
            if any(keyword in error_text.lower() for keyword in timeout_keywords):
                return True
        
        return False
    
    def _analyze_framework_specific_issues(self, agent_outputs: List[Any], framework: str) -> Dict[str, Any]:
        """Analyze framework-specific performance issues from actual data."""
        issues = {
            'abstraction_overhead': 0.0,
            'delegation_bottlenecks': [],
            'memory_leaks': []
        }
        
        if framework == 'langchain':
            # Detect LangChain abstraction overhead
            for output in agent_outputs:
                if isinstance(output, dict):
                    # Look for unnecessary intermediate steps
                    if 'intermediate_steps' in output:
                        steps = output['intermediate_steps']
                        if isinstance(steps, list) and len(steps) > 5:
                            issues['abstraction_overhead'] += 0.2
                    
                    # Detect agent scratchpad bloat
                    if 'agent_scratchpad' in str(output):
                        issues['abstraction_overhead'] += 0.1
        
        elif framework == 'crewai':
            # Detect CrewAI delegation issues
            for output in agent_outputs:
                if isinstance(output, dict):
                    # Look for slow delegation patterns
                    if 'duration_seconds' in output and output['duration_seconds'] > 25:
                        issues['delegation_bottlenecks'].append('slow_agent_delegation')
                    
                    # Detect delegation timeout patterns
                    if 'Agent delegation timeout' in str(output):
                        issues['delegation_bottlenecks'].append('delegation_timeout')
        
        elif framework == 'autogen':
            # Detect AutoGen conversation bloat
            for output in agent_outputs:
                if isinstance(output, dict):
                    # Look for excessive message history
                    if 'messages' in output:
                        messages = output['messages']
                        if isinstance(messages, list) and len(messages) > 20:
                            issues['memory_leaks'].append('excessive_conversation_history')
        
        return issues
    
    def _identify_performance_bottlenecks(self, agent_outputs: List[Any], framework: str) -> List[Dict[str, Any]]:
        """Identify specific performance bottlenecks with evidence."""
        bottlenecks = []
        
        # Analyze response time patterns
        slow_responses = []
        for output in agent_outputs:
            timing = self._extract_timing_data(output)
            if timing and timing['duration'] > 10:  # 10+ second responses
                slow_responses.append({
                    'duration': timing['duration'],
                    'output': output
                })
        
        if slow_responses:
            avg_slow_time = sum(r['duration'] for r in slow_responses) / len(slow_responses)
            bottlenecks.append({
                'type': 'slow_response_time',
                'evidence': f'{len(slow_responses)} outputs with >10s response time',
                'avg_time': avg_slow_time,
                'severity': 'high' if avg_slow_time > 30 else 'medium',
                'affected_count': len(slow_responses)
            })
        
        # Framework-specific bottleneck detection
        if framework == 'crewai':
            delegation_timeouts = [o for o in agent_outputs if 'delegation timeout' in str(o).lower()]
            if delegation_timeouts:
                bottlenecks.append({
                    'type': 'delegation_timeout',
                    'evidence': f'{len(delegation_timeouts)} delegation timeouts detected',
                    'severity': 'high',
                    'affected_count': len(delegation_timeouts)
                })
        
        elif framework == 'langchain':
            complex_chains = [o for o in agent_outputs if 'intermediate_steps' in str(o) and len(str(o)) > 5000]
            if complex_chains:
                bottlenecks.append({
                    'type': 'chain_complexity',
                    'evidence': f'{len(complex_chains)} outputs with complex chain execution',
                    'severity': 'medium',
                    'affected_count': len(complex_chains)
                })
        
        return bottlenecks
    
    def _identify_optimization_opportunities(self, framework_issues: Dict[str, Any], bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate data-driven optimization suggestions."""
        opportunities = []
        
        # High abstraction overhead -> suggest direct LLM calls
        if framework_issues.get('abstraction_overhead', 0) > 0.3:
            opportunities.append({
                'type': 'reduce_abstraction',
                'description': 'Consider direct LLM calls for simple tasks',
                'evidence': f'Abstraction overhead score: {framework_issues["abstraction_overhead"]:.2f}',
                'priority': 'high',
                'estimated_improvement': '30-50% faster response times'
            })
        
        # Delegation bottlenecks -> suggest alternatives
        if framework_issues.get('delegation_bottlenecks'):
            opportunities.append({
                'type': 'improve_delegation',
                'description': 'Implement custom delegation logic or consider framework alternatives',
                'evidence': f'Delegation issues: {", ".join(framework_issues["delegation_bottlenecks"])}',
                'priority': 'high',
                'estimated_improvement': '40-60% reduction in delegation timeouts'
            })
        
        # Memory leaks -> suggest cleanup strategies
        if framework_issues.get('memory_leaks'):
            opportunities.append({
                'type': 'memory_management',
                'description': 'Implement conversation pruning and state management',
                'evidence': f'Memory issues: {", ".join(framework_issues["memory_leaks"])}',
                'priority': 'medium',
                'estimated_improvement': '20-30% more consistent performance'
            })
        
        # Tool call failures -> suggest schema improvements
        tool_failures = [b for b in bottlenecks if 'tool' in b.get('type', '')]
        if tool_failures:
            opportunities.append({
                'type': 'tool_schema_optimization',
                'description': 'Improve tool parameter schemas and validation',
                'evidence': f'{len(tool_failures)} tool-related bottlenecks detected',
                'priority': 'high',
                'estimated_improvement': '50-70% reduction in tool call failures'
            })
        
        return opportunities
    
    def _suggest_framework_alternatives(self, current_framework: str, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Suggest alternative frameworks based on detected issues."""
        alternatives = []
        
        # Framework-specific alternative suggestions based on performance data
        if current_framework == 'crewai':
            delegation_issues = [b for b in bottlenecks if 'delegation' in b.get('type', '')]
            if delegation_issues:
                alternatives.extend(['langchain', 'autogen'])  # Better delegation handling
        
        elif current_framework == 'langchain':
            complexity_issues = [b for b in bottlenecks if 'complexity' in b.get('type', '')]
            if complexity_issues:
                alternatives.extend(['openai', 'anthropic'])  # Direct API calls for simpler workflows
        
        elif current_framework == 'autogen':
            memory_issues = [b for b in bottlenecks if 'memory' in b.get('type', '')]
            if memory_issues:
                alternatives.extend(['langgraph'])  # Better state management
        
        return alternatives
    
    def _calculate_analysis_confidence(self, sample_size: int, framework_issues: Dict[str, Any]) -> float:
        """Calculate confidence in analysis based on data quality."""
        base_confidence = min(sample_size / 100, 1.0)  # More samples = higher confidence
        
        # Reduce confidence if no clear issues detected (might indicate insufficient data)
        if not any(framework_issues.values()):
            base_confidence *= 0.7
        
        return base_confidence
    
    def _determine_recommendation_strength(self, confidence: float, bottlenecks: List[Dict[str, Any]]) -> str:
        """Determine strength of recommendations based on evidence."""
        high_severity_count = len([b for b in bottlenecks if b.get('severity') == 'high'])
        
        if confidence > 0.8 and high_severity_count > 0:
            return 'high'
        elif confidence > 0.5 and (high_severity_count > 0 or len(bottlenecks) > 2):
            return 'medium'
        else:
            return 'low'
    
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
    
    def detect_schema_mismatches(self, agent_outputs: List[Any]) -> List[Dict[str, Any]]:
        """Detect when LLM output doesn't match expected tool schema."""
        
        schema_issues = []
        for output in agent_outputs:
            # Extract tool calls from output
            output_str = str(output)
            
            # Look for schema mismatch indicators in the output
            if isinstance(output, dict):
                # Direct schema mismatch detection from structured data
                if 'tool_definition' in output and 'llm_output' in output:
                    mismatch = self._validate_tool_schema_structured(output)
                    if mismatch:
                        schema_issues.append(mismatch)
                
                # Detect from tool call failures
                if 'tool_call' in output:
                    tool_call = output['tool_call']
                    if isinstance(tool_call, dict) and 'error' in tool_call:
                        error_text = str(tool_call['error']).lower()
                        if any(keyword in error_text for keyword in ['parameter mismatch', 'schema error', 'invalid parameter']):
                            schema_issues.append({
                                "tool_name": tool_call.get('name', 'unknown'),
                                "error_type": "parameter_mismatch",
                                "error_message": tool_call['error'],
                                "suggested_fix": self._generate_schema_fix_from_error(tool_call['error'])
                            })
            
            # Text-based schema mismatch detection
            schema_error_patterns = [
                r'schema mismatch.*?(\w+).*?expects.*?[\'"]([^\'"]+)[\'"].*?got.*?[\'"]([^\'"]+)[\'"]',
                r'parameter mismatch.*?(\w+).*?expected.*?[\'"]([^\'"]+)[\'"].*?received.*?[\'"]([^\'"]+)[\'"]',
                r'invalid parameter.*?(\w+).*?[\'"]([^\'"]+)[\'"].*?not.*?[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in schema_error_patterns:
                matches = re.findall(pattern, output_str, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 3:
                        tool_name, expected, actual = match[0], match[1], match[2]
                        schema_issues.append({
                            "tool_name": tool_name,
                            "expected_parameter": expected,
                            "actual_parameter": actual,
                            "mismatch_type": "parameter_name_mismatch",
                            "suggested_fix": f"Use '{expected}' instead of '{actual}'"
                        })
        
        return schema_issues
    
    def _validate_tool_schema_structured(self, output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate against structured tool definition and LLM output."""
        tool_def = output.get('tool_definition', {})
        llm_output = output.get('llm_output', {})
        
        if not tool_def or not llm_output:
            return None
        
        tool_name = tool_def.get('name', 'unknown')
        expected_params = tool_def.get('parameters', {})
        actual_params = llm_output.get('parameters', {})
        
        # Check parameter name mismatches
        expected_names = set(expected_params.keys())
        actual_names = set(actual_params.keys())
        
        if expected_names != actual_names:
            return {
                "tool_name": tool_name,
                "expected_parameters": list(expected_names),
                "actual_parameters": list(actual_names),
                "missing_parameters": list(expected_names - actual_names),
                "unexpected_parameters": list(actual_names - expected_names),
                "mismatch_type": output.get('mismatch_type', 'parameter_structure_mismatch'),
                "suggested_fix": output.get('expected_fix', self._generate_schema_fix(expected_names, actual_names))
            }
        
        return None
    
    def _generate_schema_fix(self, expected_params: set, actual_params: set) -> str:
        """Generate specific fix for schema mismatch."""
        missing = expected_params - actual_params
        unexpected = actual_params - expected_params
        
        fixes = []
        if missing:
            fixes.append(f"Add missing parameters: {', '.join(missing)}")
        if unexpected:
            fixes.append(f"Remove unexpected parameters: {', '.join(unexpected)}")
        
        return "; ".join(fixes) if fixes else "Align parameter structure with tool definition"
    
    def _generate_schema_fix_from_error(self, error_message: str) -> str:
        """Generate fix suggestion from error message."""
        error_lower = error_message.lower()
        
        if 'parameter mismatch' in error_lower:
            return "Check tool parameter names match exactly with tool definition"
        elif 'schema error' in error_lower:
            return "Validate tool parameter types and structure"
        elif 'invalid parameter' in error_lower:
            return "Remove invalid parameters and use only defined parameters"
        else:
            return "Review tool definition and ensure LLM output matches expected schema"
    
    def generate_llm_friendly_schemas(self, tool_definitions: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Automatic generation of LLM-friendly tool descriptions."""
        
        friendly_schemas = {}
        
        for tool in tool_definitions:
            tool_name = tool.get('name', 'unknown_tool')
            
            # Convert technical schema to LLM-friendly format
            friendly_description = self._convert_to_llm_format(tool)
            
            # Add usage examples
            examples = self._generate_usage_examples(tool)
            
            # Create clear parameter descriptions
            param_descriptions = self._create_parameter_descriptions(tool.get("parameters", {}))
            
            # Identify common mistakes for this tool type
            common_mistakes = self._identify_common_mistakes(tool)
            
            friendly_schemas[tool_name] = {
                "description": friendly_description,
                "examples": examples,
                "parameters": param_descriptions,
                "common_mistakes": common_mistakes,
                "llm_prompt_template": self._generate_llm_prompt_template(tool)
            }
        
        return friendly_schemas
    
    def _convert_to_llm_format(self, tool: Dict) -> str:
        """Convert technical tool definition to LLM-friendly description."""
        
        name = tool.get("name", "unknown_tool")
        description = tool.get("description", "")
        parameters = tool.get("parameters", {})
        
        # Create simple, clear description
        llm_description = f"""
Tool: {name}
Purpose: {description}
When to use: {self._generate_usage_guidance(tool)}

Required parameters:
"""
        
        for param_name, param_info in parameters.items():
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', 'No description')
            required = param_info.get('required', True)
            
            llm_description += f"- {param_name} ({param_type}): {param_desc}"
            if not required:
                llm_description += " [optional]"
            llm_description += "\n"
        
        return llm_description.strip()
    
    def _generate_usage_guidance(self, tool: Dict) -> str:
        """Generate when-to-use guidance for tool."""
        tool_name = tool.get('name', '').lower()
        
        guidance_map = {
            'search': 'When you need to find information or lookup data',
            'calculate': 'When you need to perform mathematical operations or computations',
            'analyze': 'When you need to process or examine data for insights',
            'generate': 'When you need to create new content or outputs',
            'validate': 'When you need to check or verify information',
            'api': 'When you need to call external services or APIs',
            'database': 'When you need to query or update database records',
            'file': 'When you need to read, write, or manipulate files'
        }
        
        for keyword, guidance in guidance_map.items():
            if keyword in tool_name:
                return guidance
        
        return f"When you need to use {tool.get('name', 'this tool')} functionality"
    
    def _generate_usage_examples(self, tool: Dict) -> List[str]:
        """Generate usage examples for tool."""
        tool_name = tool.get('name', 'tool')
        parameters = tool.get('parameters', {})
        
        examples = []
        
        # Generate basic example
        if parameters:
            param_example = {}
            for param_name, param_info in parameters.items():
                param_type = param_info.get('type', 'string')
                if param_type == 'string':
                    param_example[param_name] = f"example_{param_name}"
                elif param_type == 'integer':
                    param_example[param_name] = 10
                elif param_type == 'boolean':
                    param_example[param_name] = True
                elif param_type == 'array':
                    param_example[param_name] = ["item1", "item2"]
                else:
                    param_example[param_name] = f"example_{param_name}"
            
            examples.append(f'{{"tool": "{tool_name}", "parameters": {param_example}}}')
        
        return examples
    
    def _create_parameter_descriptions(self, parameters: Dict) -> Dict[str, str]:
        """Create clear parameter descriptions."""
        descriptions = {}
        
        for param_name, param_info in parameters.items():
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', 'No description provided')
            required = param_info.get('required', True)
            
            clear_desc = f"{param_desc} (Type: {param_type}"
            if not required:
                clear_desc += ", Optional"
            clear_desc += ")"
            
            descriptions[param_name] = clear_desc
        
        return descriptions
    
    def _identify_common_mistakes(self, tool: Dict) -> List[str]:
        """Identify common mistakes for this tool type."""
        tool_name = tool.get('name', '').lower()
        parameters = tool.get('parameters', {})
        
        mistakes = []
        
        # Common parameter naming mistakes
        param_names = list(parameters.keys())
        if 'query' in param_names:
            mistakes.append("Don't use 'search_term' or 'q' - use 'query'")
        if 'limit' in param_names:
            mistakes.append("Don't use 'max_results' or 'count' - use 'limit'")
        if 'format' in param_names:
            mistakes.append("Don't use 'output_format' or 'type' - use 'format'")
        
        # Tool-specific mistakes
        if 'search' in tool_name:
            mistakes.append("Always provide a query parameter, never leave it empty")
        elif 'calculate' in tool_name:
            mistakes.append("Use mathematical expressions as strings, not separate numbers and operations")
        elif 'api' in tool_name:
            mistakes.append("Include all required headers and authentication parameters")
        
        return mistakes if mistakes else ["Follow the exact parameter names and types specified"]
    
    def _generate_llm_prompt_template(self, tool: Dict) -> str:
        """Generate an LLM prompt template for using this tool."""
        tool_name = tool.get('name', 'tool')
        parameters = tool.get('parameters', {})
        
        template = f"To use {tool_name}:\n\n"
        template += f'{{"tool": "{tool_name}", "parameters": {{\n'
        
        for i, (param_name, param_info) in enumerate(parameters.items()):
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', '')
            
            if param_type == 'string':
                example_value = f'"your_{param_name}_here"'
            elif param_type == 'integer':
                example_value = '10'
            elif param_type == 'boolean':
                example_value = 'true'
            elif param_type == 'array':
                example_value = '["item1", "item2"]'
            else:
                example_value = f'"your_{param_name}_here"'
            
            template += f'  "{param_name}": {example_value}'
            if param_desc:
                template += f'  // {param_desc}'
            
            if i < len(parameters) - 1:
                template += ','
            template += '\n'
        
        template += '}}'
        
        return template

    def generate_comprehensive_analysis(
        self, 
        agent_outputs: List[Any], 
        framework: Optional[str] = None,
        expected_tools: Optional[List[str]] = None
    ) -> ComprehensiveReliabilityAnalysis:
        """Generate comprehensive reliability analysis combining all functionality."""
        
        sample_size = len(agent_outputs)
        if sample_size == 0:
            return self._create_empty_analysis()
        
        # 1. Framework Detection (consolidating duplicate logic)
        if framework:
            framework_detection = {
                'detected_framework': framework,
                'confidence': 1.0,
                'auto_detection_successful': True,
                'framework_scores': {framework: sample_size}
            }
        else:
            framework_detection = self.detect_framework_comprehensive(agent_outputs)
        
        detected_framework = framework_detection['detected_framework']
        
        # 2. Tool Call Analysis
        if expected_tools:
            tool_validations = []
            for output in agent_outputs:
                validation = self.validate_tool_usage(output, expected_tools)
                tool_validations.append(validation)
            
            tool_call_summary = {
                'total_validations': len(tool_validations),
                'avg_tool_accuracy': sum(v['coverage_rate'] for v in tool_validations) / len(tool_validations),
                'tools_consistently_missing': self._find_consistently_missing_tools(tool_validations),
                'validation_details': tool_validations
            }
        else:
            # Basic tool extraction without validation
            all_detected_tools = []
            for output in agent_outputs:
                tools = self.extract_tool_calls(output, detected_framework)
                all_detected_tools.extend(tools)
            
            tool_call_summary = {
                'total_outputs_analyzed': sample_size,
                'unique_tools_detected': len(set(all_detected_tools)),
                'most_common_tools': Counter(all_detected_tools).most_common(5),
                'framework_specific_analysis': detected_framework is not None
            }
        
        # 3. Framework Performance Analysis (if framework detected)
        framework_performance = None
        if detected_framework:
            try:
                framework_performance = self.analyze_framework_performance(agent_outputs, detected_framework)
            except Exception as e:
                logger.warning(f"Framework performance analysis failed: {e}")
        
        # 4. Workflow Reliability Metrics
        workflow_metrics = self._calculate_workflow_metrics(
            agent_outputs, 
            detected_framework,
            framework_performance
        )
        
        # 5. Generate Rich Dashboard
        reliability_dashboard = self._generate_reliability_dashboard(
            framework_detection,
            tool_call_summary,
            framework_performance,
            workflow_metrics,
            sample_size
        )
        
        # 6. Generate Insights and Next Steps
        insights_summary = self._generate_insights(
            framework_detection,
            tool_call_summary,
            framework_performance,
            workflow_metrics
        )
        
        # 6.1. Analyze Migration Opportunities (NEW - Task 7)
        migration_analysis = self._analyze_migration_opportunities(
            detected_framework,
            framework_performance,
            workflow_metrics
        )
        
        # 6.2. Cognitive Analysis Integration (NEW - Task 8)
        cognitive_analysis = self._perform_cognitive_analysis(agent_outputs)
        
        next_steps = self._generate_next_steps(
            detected_framework,
            framework_performance,
            workflow_metrics,
            migration_analysis
        )
        
        # 7. Calculate Overall Analysis Confidence
        analysis_confidence = self._calculate_overall_confidence(
            framework_detection['confidence'],
            sample_size,
            framework_performance
        )
        
        evidence_quality = self._determine_evidence_quality(analysis_confidence, sample_size)
        
        return ComprehensiveReliabilityAnalysis(
            detected_framework=detected_framework,
            framework_confidence=framework_detection['confidence'],
            auto_detection_successful=framework_detection['auto_detection_successful'],
            framework_performance=framework_performance,
            workflow_metrics=workflow_metrics,
            tool_call_summary=tool_call_summary,
            validation_results=tool_call_summary.get('validation_details', []),
            reliability_dashboard=reliability_dashboard,
            insights_summary=insights_summary,
            next_steps=next_steps,
            cognitive_analysis=cognitive_analysis,  # NEW - Task 8
            analysis_confidence=analysis_confidence,
            evidence_quality=evidence_quality,
            sample_size=sample_size
        )
    
    def _create_empty_analysis(self) -> ComprehensiveReliabilityAnalysis:
        """Create empty analysis for zero inputs."""
        empty_metrics = WorkflowReliabilityMetrics(
            workflow_success_rate=0.0,
            tool_chain_reliability=0.0,
            decision_consistency_score=0.0,
            multi_step_completion_rate=0.0,
            average_workflow_time=0.0,
            error_recovery_rate=0.0,
            timeout_rate=0.0,
            framework_compatibility_score=0.0,
            tool_usage_efficiency=0.0,
            schema_mismatch_rate=0.0,
            prompt_tool_alignment_score=0.0,
            reliability_trend="unknown",
            critical_failure_points=[]
        )
        
        return ComprehensiveReliabilityAnalysis(
            detected_framework=None,
            framework_confidence=0.0,
            auto_detection_successful=False,
            framework_performance=None,
            workflow_metrics=empty_metrics,
            tool_call_summary={'error': 'No agent outputs provided'},
            validation_results=[],
            reliability_dashboard="❌ No data available for analysis",
            insights_summary=["No agent outputs provided for analysis"],
            next_steps=["Provide agent output data for analysis"],
            cognitive_analysis=None,  # NEW - Task 8
            analysis_confidence=0.0,
            evidence_quality="none",
            sample_size=0
        )
    
    def _find_consistently_missing_tools(self, validations: List[Dict[str, Any]]) -> List[str]:
        """Find tools that are consistently missing across validations."""
        all_missing = []
        for validation in validations:
            all_missing.extend(validation.get('missing_tools', []))
        
        missing_counter = Counter(all_missing)
        # Consider a tool "consistently missing" if it's missing in >50% of validations
        threshold = len(validations) * 0.5
        return [tool for tool, count in missing_counter.items() if count >= threshold]
    
    def _calculate_workflow_metrics(
        self, 
        agent_outputs: List[Any], 
        framework: Optional[str],
        framework_performance: Optional[FrameworkPerformanceAnalysis]
    ) -> WorkflowReliabilityMetrics:
        """Calculate comprehensive workflow reliability metrics."""
        
        # Extract success indicators
        success_indicators = [self._analyze_success_patterns(output)['success_rate'] for output in agent_outputs]
        workflow_success_rate = sum(success_indicators) / len(success_indicators) if success_indicators else 0.0
        
        # Tool chain reliability
        tool_failures = []
        for output in agent_outputs:
            tool_failures.extend(self._detect_tool_call_failures(output))
        tool_chain_reliability = 1.0 - (len(tool_failures) / len(agent_outputs)) if agent_outputs else 0.0
        
        # Error recovery and timeout analysis
        error_recovery_count = 0
        timeout_count = 0
        
        for output in agent_outputs:
            output_str = str(output)
            error_recovery = self.detect_error_recovery(output_str)
            if any(error_recovery.values()):
                error_recovery_count += 1
            if self._detect_timeout_patterns(output):
                timeout_count += 1
        
        error_recovery_rate = error_recovery_count / len(agent_outputs) if agent_outputs else 0.0
        timeout_rate = timeout_count / len(agent_outputs) if agent_outputs else 0.0
        
        # Framework compatibility (based on detection success)
        framework_compatibility_score = 1.0 if framework else 0.5
        
        # Average timing if available
        timing_data = [self._extract_timing_data(output) for output in agent_outputs]
        valid_timings = [t['duration'] for t in timing_data if t]
        average_workflow_time = sum(valid_timings) / len(valid_timings) if valid_timings else 0.0
        
        # Calculate other metrics based on available data
        decision_consistency_score = min(workflow_success_rate + 0.1, 1.0)  # Approximation
        multi_step_completion_rate = workflow_success_rate  # Approximation
        tool_usage_efficiency = tool_chain_reliability
        
        # Schema mismatch detection
        schema_mismatches = sum(1 for f in tool_failures if 'schema' in f.get('type', '').lower())
        schema_mismatch_rate = schema_mismatches / len(agent_outputs) if agent_outputs else 0.0
        
        prompt_tool_alignment_score = 1.0 - schema_mismatch_rate
        
        # Determine reliability trend
        if workflow_success_rate >= 0.8:
            reliability_trend = "stable"
        elif workflow_success_rate >= 0.6:
            reliability_trend = "improving"
        else:
            reliability_trend = "degrading"
        
        # Identify critical failure points
        critical_failure_points = []
        if timeout_rate > 0.2:
            critical_failure_points.append("High timeout rate")
        if tool_chain_reliability < 0.7:
            critical_failure_points.append("Tool call failures")
        if schema_mismatch_rate > 0.1:
            critical_failure_points.append("Schema mismatches")
        
        return WorkflowReliabilityMetrics(
            workflow_success_rate=workflow_success_rate,
            tool_chain_reliability=tool_chain_reliability,
            decision_consistency_score=decision_consistency_score,
            multi_step_completion_rate=multi_step_completion_rate,
            average_workflow_time=average_workflow_time,
            error_recovery_rate=error_recovery_rate,
            timeout_rate=timeout_rate,
            framework_compatibility_score=framework_compatibility_score,
            tool_usage_efficiency=tool_usage_efficiency,
            schema_mismatch_rate=schema_mismatch_rate,
            prompt_tool_alignment_score=prompt_tool_alignment_score,
            reliability_trend=reliability_trend,
            critical_failure_points=critical_failure_points
        )
    
    def _generate_reliability_dashboard(
        self,
        framework_detection: Dict[str, Any],
        tool_call_summary: Dict[str, Any],
        framework_performance: Optional[FrameworkPerformanceAnalysis],
        workflow_metrics: WorkflowReliabilityMetrics,
        sample_size: int
    ) -> str:
        """Generate Rich-formatted reliability dashboard."""
        
        dashboard_parts = []
        
        # Header
        dashboard_parts.append("\n🔧 [bold cyan]Comprehensive Reliability Analysis[/bold cyan]")
        dashboard_parts.append("═" * 70)
        
        # Framework Detection Summary
        framework = framework_detection['detected_framework']
        confidence = framework_detection['confidence']
        
        if framework:
            dashboard_parts.append(f"\n🎯 [bold]Framework Detection:[/bold] [green]{framework.upper()}[/green] (confidence: {confidence:.1%})")
        else:
            dashboard_parts.append("\n🎯 [bold]Framework Detection:[/bold] [yellow]Auto-detection inconclusive[/yellow]")
        
        # Workflow Metrics Summary
        dashboard_parts.append(f"\n📊 [bold]Workflow Reliability Metrics:[/bold]")
        dashboard_parts.append(f"  • Success Rate: {workflow_metrics.workflow_success_rate:.1%}")
        dashboard_parts.append(f"  • Tool Chain Reliability: {workflow_metrics.tool_chain_reliability:.1%}")
        dashboard_parts.append(f"  • Error Recovery Rate: {workflow_metrics.error_recovery_rate:.1%}")
        dashboard_parts.append(f"  • Timeout Rate: {workflow_metrics.timeout_rate:.1%}")
        
        if workflow_metrics.average_workflow_time > 0:
            dashboard_parts.append(f"  • Average Workflow Time: {workflow_metrics.average_workflow_time:.1f}s")
        
        # Framework Performance (if available)
        if framework_performance:
            dashboard_parts.append(f"\n⚡ [bold]Framework Performance Analysis:[/bold]")
            dashboard_parts.append(f"  • Sample Size: {framework_performance.sample_size} outputs")
            dashboard_parts.append(f"  • Success Rate: {framework_performance.success_rate:.1%}")
            dashboard_parts.append(f"  • Avg Response Time: {framework_performance.avg_response_time:.1f}s")
            dashboard_parts.append(f"  • Tool Call Failure Rate: {framework_performance.tool_call_failure_rate:.1%}")
            
            if framework_performance.performance_bottlenecks:
                dashboard_parts.append(f"\n⚠️ [bold]Performance Bottlenecks:[/bold]")
                for bottleneck in framework_performance.performance_bottlenecks[:3]:  # Top 3
                    severity_color = "red" if bottleneck.get('severity') == 'high' else "yellow"
                    dashboard_parts.append(f"  • [{severity_color}]{bottleneck['type'].replace('_', ' ').title()}[/{severity_color}]: {bottleneck['evidence']}")
        
        # Tool Call Summary
        dashboard_parts.append(f"\n🔧 [bold]Tool Call Analysis:[/bold]")
        if 'total_validations' in tool_call_summary:
            dashboard_parts.append(f"  • Validations: {tool_call_summary['total_validations']}")
            dashboard_parts.append(f"  • Tool Accuracy: {tool_call_summary['avg_tool_accuracy']:.1%}")
            if tool_call_summary.get('tools_consistently_missing'):
                dashboard_parts.append(f"  • Consistently Missing: {', '.join(tool_call_summary['tools_consistently_missing'])}")
        else:
            dashboard_parts.append(f"  • Outputs Analyzed: {tool_call_summary.get('total_outputs_analyzed', 0)}")
            dashboard_parts.append(f"  • Unique Tools Detected: {tool_call_summary.get('unique_tools_detected', 0)}")
            most_common = tool_call_summary.get('most_common_tools', [])
            if most_common:
                top_tools = [f"{tool}({count})" for tool, count in most_common[:3]]
                dashboard_parts.append(f"  • Most Common Tools: {', '.join(top_tools)}")
        
        # Critical Issues
        if workflow_metrics.critical_failure_points:
            dashboard_parts.append(f"\n🚨 [bold red]Critical Issues Detected:[/bold red]")
            for issue in workflow_metrics.critical_failure_points:
                dashboard_parts.append(f"  • {issue}")
        
        # Reliability Trend
        trend_color = "green" if workflow_metrics.reliability_trend == "stable" else "yellow" if workflow_metrics.reliability_trend == "improving" else "red"
        dashboard_parts.append(f"\n📈 [bold]Reliability Trend:[/bold] [{trend_color}]{workflow_metrics.reliability_trend.title()}[/{trend_color}]")
        
        return "\n".join(dashboard_parts)
    
    def _generate_insights(
        self,
        framework_detection: Dict[str, Any],
        tool_call_summary: Dict[str, Any],
        framework_performance: Optional[FrameworkPerformanceAnalysis],
        workflow_metrics: WorkflowReliabilityMetrics
    ) -> List[str]:
        """Generate key insights from analysis."""
        insights = []
        
        # Framework insights
        if framework_detection['auto_detection_successful']:
            insights.append(f"✅ Framework auto-detection successful: {framework_detection['detected_framework']}")
        else:
            insights.append("⚠️ Framework auto-detection inconclusive - consider specifying framework explicitly")
        
        # Performance insights
        if workflow_metrics.workflow_success_rate >= 0.9:
            insights.append("✅ Excellent workflow success rate - system performing well")
        elif workflow_metrics.workflow_success_rate >= 0.7:
            insights.append("🟡 Good workflow success rate - minor optimizations possible")
        else:
            insights.append("🔴 Low workflow success rate - significant issues need attention")
        
        # Tool insights
        if workflow_metrics.tool_chain_reliability >= 0.9:
            insights.append("✅ High tool chain reliability - tools working as expected")
        elif workflow_metrics.tool_chain_reliability >= 0.7:
            insights.append("🟡 Moderate tool reliability - some tool issues detected")
        else:
            insights.append("🔴 Poor tool reliability - tool call failures need investigation")
        
        # Framework-specific insights
        if framework_performance:
            if framework_performance.optimization_opportunities:
                top_opportunity = framework_performance.optimization_opportunities[0]
                insights.append(f"💡 Top optimization: {top_opportunity['description']}")
        
        return insights
    
    def _generate_next_steps(
        self,
        detected_framework: Optional[str],
        framework_performance: Optional[FrameworkPerformanceAnalysis],
        workflow_metrics: WorkflowReliabilityMetrics,
        migration_analysis: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate recommended next steps."""
        next_steps = []
        
        # Framework-specific recommendations
        if detected_framework:
            next_steps.append(f"1. Review {detected_framework} documentation for optimization best practices")
        else:
            next_steps.append("1. Specify framework explicitly for more targeted analysis")
        
        # Performance-based recommendations
        if workflow_metrics.timeout_rate > 0.1:
            next_steps.append("2. Investigate timeout issues - consider increasing timeout limits or optimizing slow operations")
        
        if workflow_metrics.tool_chain_reliability < 0.8:
            next_steps.append("3. Review tool call implementations and parameter schemas")
        
        if workflow_metrics.schema_mismatch_rate > 0.05:
            next_steps.append("4. Validate tool schemas match LLM output format expectations")
        
        # Framework performance recommendations
        if framework_performance and framework_performance.framework_alternatives:
            alternatives = ', '.join(framework_performance.framework_alternatives[:2])
            next_steps.append(f"5. Consider framework alternatives: {alternatives}")
        
        # Migration recommendations (NEW - Task 7)
        if migration_analysis and migration_analysis.get("migration_recommended"):
            recommended_framework = migration_analysis.get("recommended_framework")
            improvement_estimate = migration_analysis.get("improvement_estimate", 0)
            migration_priority = migration_analysis.get("priority", "medium")
            
            if migration_priority == "high":
                next_steps.append(f"🚀 HIGH PRIORITY: Migrate to {recommended_framework} for {improvement_estimate}% performance improvement")
            elif migration_priority == "medium":
                next_steps.append(f"⚡ Consider migrating to {recommended_framework} for {improvement_estimate}% improvement")
            else:
                next_steps.append(f"📊 Evaluate migration to {recommended_framework} for potential {improvement_estimate}% gains")
            
            # Add specific migration steps
            migration_steps = migration_analysis.get("migration_steps", [])
            for step in migration_steps[:2]:  # Add top 2 migration steps
                next_steps.append(f"   • {step}")
        
        # Always include compliance evaluation
        next_steps.append("6. Run enterprise compliance evaluation for production readiness")
        
        return next_steps
    
    def _calculate_overall_confidence(
        self,
        framework_confidence: float,
        sample_size: int,
        framework_performance: Optional[FrameworkPerformanceAnalysis]
    ) -> float:
        """Calculate overall analysis confidence."""
        
        # Base confidence from sample size
        size_confidence = min(sample_size / 50, 1.0)  # Full confidence at 50+ samples
        
        # Framework detection confidence
        detection_confidence = framework_confidence
        
        # Performance analysis confidence
        performance_confidence = 1.0
        if framework_performance:
            performance_confidence = framework_performance.analysis_confidence
        
        # Weighted average
        overall_confidence = (
            size_confidence * 0.4 +
            detection_confidence * 0.3 +
            performance_confidence * 0.3
        )
        
        return overall_confidence
    
    def _determine_evidence_quality(self, confidence: float, sample_size: int) -> str:
        """Determine evidence quality based on confidence and sample size."""
        if confidence >= 0.8 and sample_size >= 20:
            return "high"
        elif confidence >= 0.6 and sample_size >= 10:
            return "medium"
        else:
            return "low"
    
    # ==================== Planning Failure Detection Methods ====================
    
    def detect_planning_failures(self, agent_outputs: List[Any]) -> Dict[str, Any]:
        """Detect goal drift and planning consistency issues."""
        planning_issues = {
            'goal_drift_detected': False,
            'plan_execution_misalignment': [],
            'reflection_loop_failures': [],
            'overconfident_assertions': [],
            'planning_consistency_score': 0.0,
            'goal_tracking_score': 0.0,
            'total_outputs_analyzed': len(agent_outputs)
        }
        
        if not agent_outputs:
            return planning_issues
        
        goal_drift_count = 0
        misalignment_count = 0
        loop_failure_count = 0
        overconfident_count = 0
        
        for i, output in enumerate(agent_outputs):
            # Track goal drift across conversation turns
            if self._detect_goal_drift(output):
                planning_issues['goal_drift_detected'] = True
                goal_drift_count += 1
            
            # Identify reflection loop failures  
            if self._detect_reflection_loops(output):
                planning_issues['reflection_loop_failures'].append({
                    'output_index': i,
                    'output': str(output)[:200] + "..." if len(str(output)) > 200 else str(output),
                    'loop_type': 'circular_reasoning'
                })
                loop_failure_count += 1
            
            # Measure plan-execution alignment
            alignment_score = self._measure_plan_execution_alignment(output)
            if alignment_score < 0.7:
                planning_issues['plan_execution_misalignment'].append({
                    'output_index': i,
                    'output': str(output)[:200] + "..." if len(str(output)) > 200 else str(output),
                    'alignment_score': alignment_score,
                    'issue_type': 'low_alignment'
                })
                misalignment_count += 1
            
            # Detect overconfident assertions
            if self._detect_overconfident_assertions(output):
                planning_issues['overconfident_assertions'].append({
                    'output_index': i,
                    'output': str(output)[:200] + "..." if len(str(output)) > 200 else str(output),
                    'confidence_issue': 'overconfident_assertion'
                })
                overconfident_count += 1
        
        # Calculate overall scores
        total_outputs = len(agent_outputs)
        planning_issues['planning_consistency_score'] = max(0.0, 1.0 - (misalignment_count + loop_failure_count) / total_outputs)
        planning_issues['goal_tracking_score'] = max(0.0, 1.0 - goal_drift_count / total_outputs)
        
        # Add summary statistics
        planning_issues['summary'] = {
            'goal_drift_rate': goal_drift_count / total_outputs if total_outputs > 0 else 0.0,
            'misalignment_rate': misalignment_count / total_outputs if total_outputs > 0 else 0.0,
            'reflection_loop_rate': loop_failure_count / total_outputs if total_outputs > 0 else 0.0,
            'overconfidence_rate': overconfident_count / total_outputs if total_outputs > 0 else 0.0
        }
        
        return planning_issues
    
    def _detect_goal_drift(self, output: Any) -> bool:
        """Detect when agent loses track of original goals."""
        output_str = str(output).lower()
        
        # Patterns indicating goal drift
        goal_drift_patterns = [
            r"i'm not sure what we were trying to accomplish",
            r"what was the original question",
            r"let me start over",
            r"i've lost track of",
            r"going back to the beginning",
            r"what were we talking about",
            r"i forgot what we were doing",
            r"let me reconsider the task",
            r"i'm confused about the goal",
            r"what was the purpose again"
        ]
        
        # Check for explicit goal drift indicators
        for pattern in goal_drift_patterns:
            if re.search(pattern, output_str):
                return True
        
        # Check for multiple contradictory statements within the same output
        contradiction_indicators = [
            (r"i will.*", r"actually, i won't"),
            (r"the answer is.*", r"wait, the answer is actually"),
            (r"we should.*", r"on second thought, we shouldn't"),
            (r"first.*then", r"actually, let's skip")
        ]
        
        for first_pattern, contradiction_pattern in contradiction_indicators:
            if re.search(first_pattern, output_str) and re.search(contradiction_pattern, output_str):
                return True
        
        return False
    
    def _detect_reflection_loops(self, output: Any) -> bool:
        """Detect circular reasoning patterns."""
        output_str = str(output).lower()
        
        # Patterns indicating circular reasoning or reflection loops
        loop_patterns = [
            r"as i mentioned before.*as i mentioned before",
            r"like i said.*like i said",
            r"going back to.*going back to",
            r"as discussed.*as discussed.*as discussed",
            r"i already explained.*i already explained",
            r"repeating myself",
            r"circular logic",
            r"endless loop",
            r"keep going in circles",
            r"same conclusion again",
            r"this brings us back to"
        ]
        
        # Check for explicit loop indicators
        for pattern in loop_patterns:
            if re.search(pattern, output_str):
                return True
        
        # Check for repeated phrases (simple heuristic)
        sentences = re.split(r'[.!?]', output_str)
        sentence_counts = Counter(sentence.strip() for sentence in sentences if len(sentence.strip()) > 10)
        
        # If any sentence appears more than twice, it might be a loop
        for sentence, count in sentence_counts.items():
            if count >= 3:
                return True
        
        return False
    
    def _measure_plan_execution_alignment(self, output: Any) -> float:
        """Measure how well execution aligns with stated plans."""
        output_str = str(output).lower()
        
        # Look for planning language
        planning_patterns = [
            r"first.*then.*finally",
            r"step \d+",
            r"next, i will",
            r"my plan is",
            r"i will.*then.*then",
            r"the steps are",
            r"here's what i'll do"
        ]
        
        # Look for execution language  
        execution_patterns = [
            r"i am now",
            r"currently",
            r"executing",
            r"implementing",
            r"doing",
            r"working on",
            r"completed"
        ]
        
        # Count planning vs execution indicators
        plan_count = sum(1 for pattern in planning_patterns if re.search(pattern, output_str))
        execution_count = sum(1 for pattern in execution_patterns if re.search(pattern, output_str))
        
        # Check for contradictions between plan and execution
        contradiction_patterns = [
            (r"i will use.*", r"instead i used"),
            (r"my plan is to.*", r"but actually"),
            (r"first.*", r"skipping to"),
            (r"step \d+.*", r"jumping to step")
        ]
        
        contradiction_count = 0
        for plan_pattern, contradiction_pattern in contradiction_patterns:
            if re.search(plan_pattern, output_str) and re.search(contradiction_pattern, output_str):
                contradiction_count += 1
        
        # Calculate alignment score
        if plan_count == 0 and execution_count == 0:
            return 0.8  # Neutral score when no clear planning/execution language
        
        total_indicators = plan_count + execution_count
        if total_indicators == 0:
            return 0.8
        
        # Penalize contradictions
        contradiction_penalty = contradiction_count * 0.2
        
        # Higher scores when execution follows planning
        if plan_count > 0 and execution_count > 0:
            base_score = min(execution_count / plan_count, 1.0)
        elif execution_count > 0:
            base_score = 0.6  # Execution without clear planning
        else:
            base_score = 0.4  # Planning without execution
        
        return max(0.0, base_score - contradiction_penalty)
    
    def _detect_overconfident_assertions(self, output: Any) -> bool:
        """Detect overconfident assertions without proper reasoning."""
        output_str = str(output).lower()
        
        # Patterns indicating overconfidence
        overconfidence_patterns = [
            r"definitely",
            r"absolutely certain",
            r"100% sure",
            r"without a doubt",
            r"certainly",
            r"obviously",
            r"clearly",
            r"undoubtedly",
            r"guaranteed",
            r"impossible to be wrong"
        ]
        
        # Patterns indicating lack of reasoning
        weak_reasoning_patterns = [
            r"because i said so",
            r"trust me",
            r"just because",
            r"it's obvious",
            r"everyone knows",
            r"common sense",
            r"no need to explain"
        ]
        
        confidence_count = sum(1 for pattern in overconfidence_patterns if re.search(pattern, output_str))
        weak_reasoning_count = sum(1 for pattern in weak_reasoning_patterns if re.search(pattern, output_str))
        
        # Look for reasoning indicators
        reasoning_patterns = [
            r"because",
            r"since",
            r"due to",
            r"as a result",
            r"therefore",
            r"given that",
            r"based on",
            r"evidence shows",
            r"analysis indicates"
        ]
        
        reasoning_count = sum(1 for pattern in reasoning_patterns if re.search(pattern, output_str))
        
        # Overconfident if high confidence with low reasoning or weak reasoning
        if confidence_count >= 2 and (reasoning_count == 0 or weak_reasoning_count > 0):
            return True
        
        # Also check for absolute statements without qualifying language
        absolute_patterns = [
            r"never",
            r"always",
            r"all.*are",
            r"none.*are",
            r"every.*will",
            r"no.*can"
        ]
        
        absolute_count = sum(1 for pattern in absolute_patterns if re.search(pattern, output_str))
        
        # Check for qualifying language that would moderate absolute statements
        qualifying_patterns = [
            r"might",
            r"could",
            r"possibly",
            r"potentially", 
            r"likely",
            r"probably",
            r"seems",
            r"appears",
            r"suggests",
            r"indicates"
        ]
        
        qualifying_count = sum(1 for pattern in qualifying_patterns if re.search(pattern, output_str))
        
        # Overconfident if many absolute statements without qualifying language
        if absolute_count >= 2 and qualifying_count == 0:
            return True
        
        return False
    
    # ==================== Reflection Quality Analysis Methods ====================
    
    def analyze_reflection_quality(self, agent_reasoning: List[str]) -> Dict[str, Any]:
        """Enhanced metacognitive analysis."""
        reflection_analysis = {
            'circular_reasoning_detected': False,
            'self_correction_effectiveness': 0.0,
            'overconfident_assertions': [],
            'reflection_depth_score': 0.0,
            'metacognitive_awareness_score': 0.0,
            'reasoning_coherence_score': 0.0,
            'total_reasoning_analyzed': len(agent_reasoning)
        }
        
        if not agent_reasoning:
            return reflection_analysis
        
        circular_count = 0
        correction_scores = []
        overconfident_count = 0
        depth_scores = []
        metacognitive_scores = []
        coherence_scores = []
        
        for i, reasoning in enumerate(agent_reasoning):
            # Detect circular reasoning patterns
            if self._detect_circular_reasoning(reasoning):
                reflection_analysis['circular_reasoning_detected'] = True
                circular_count += 1
            
            # Measure self-correction effectiveness
            correction_score = self._measure_self_correction(reasoning)
            correction_scores.append(correction_score)
            
            # Flag overconfident assertions
            if self._detect_overconfidence_in_reasoning(reasoning):
                reflection_analysis['overconfident_assertions'].append({
                    'reasoning_index': i,
                    'reasoning': reasoning[:200] + "..." if len(reasoning) > 200 else reasoning,
                    'issue_type': 'overconfident_reasoning'
                })
                overconfident_count += 1
            
            # Score reflection depth
            depth_score = self._score_reflection_depth(reasoning)
            depth_scores.append(depth_score)
            
            # Score metacognitive awareness
            metacognitive_score = self._score_metacognitive_awareness(reasoning)
            metacognitive_scores.append(metacognitive_score)
            
            # Score reasoning coherence
            coherence_score = self._score_reasoning_coherence(reasoning)
            coherence_scores.append(coherence_score)
        
        # Calculate overall scores
        total_reasoning = len(agent_reasoning)
        reflection_analysis['self_correction_effectiveness'] = sum(correction_scores) / total_reasoning if total_reasoning > 0 else 0.0
        reflection_analysis['reflection_depth_score'] = sum(depth_scores) / total_reasoning if total_reasoning > 0 else 0.0
        reflection_analysis['metacognitive_awareness_score'] = sum(metacognitive_scores) / total_reasoning if total_reasoning > 0 else 0.0
        reflection_analysis['reasoning_coherence_score'] = sum(coherence_scores) / total_reasoning if total_reasoning > 0 else 0.0
        
        # Add summary statistics
        reflection_analysis['summary'] = {
            'circular_reasoning_rate': circular_count / total_reasoning if total_reasoning > 0 else 0.0,
            'overconfidence_rate': overconfident_count / total_reasoning if total_reasoning > 0 else 0.0,
            'avg_correction_effectiveness': reflection_analysis['self_correction_effectiveness'],
            'avg_reflection_depth': reflection_analysis['reflection_depth_score'],
            'avg_metacognitive_awareness': reflection_analysis['metacognitive_awareness_score'],
            'avg_reasoning_coherence': reflection_analysis['reasoning_coherence_score']
        }
        
        return reflection_analysis
    
    def _detect_circular_reasoning(self, reasoning: str) -> bool:
        """Detect circular reasoning patterns in agent reasoning."""
        reasoning_lower = reasoning.lower()
        
        # Patterns indicating circular reasoning
        circular_patterns = [
            r"because.*because.*because",  # Repeated "because" without progression
            r"therefore.*therefore.*therefore",  # Repeated conclusions
            r"which means.*which means.*which means",  # Circular definitions
            r"this proves.*this proves.*this proves",  # Circular proof attempts
            r"leading to.*leading to.*leading to",  # Circular chains
            r"results in.*results in.*results in",
            r"due to the fact that.*due to the fact that.*due to the fact that"
        ]
        
        # Check for explicit circular patterns
        for pattern in circular_patterns:
            if re.search(pattern, reasoning_lower):
                return True
        
        # Check for A->B->A logical loops
        # Look for statements that reference back to earlier premises
        sentences = re.split(r'[.!?]', reasoning_lower)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) < 3:
            return False
        
        # Simple heuristic: check if first and last sentences are very similar
        first_sentence = sentences[0]
        last_sentence = sentences[-1]
        
        # Calculate word overlap
        first_words = set(first_sentence.split())
        last_words = set(last_sentence.split())
        
        if len(first_words) > 0 and len(last_words) > 0:
            overlap = len(first_words.intersection(last_words)) / len(first_words.union(last_words))
            if overlap > 0.7:  # High overlap suggests circular reasoning
                return True
        
        return False
    
    def _measure_self_correction(self, reasoning: str) -> float:
        """Measure self-correction effectiveness in reasoning."""
        reasoning_lower = reasoning.lower()
        
        # Positive self-correction patterns
        positive_correction_patterns = [
            r"wait,? let me reconsider",
            r"actually,? i made an error",
            r"on second thought",
            r"i need to correct",
            r"let me revise",
            r"i was wrong",
            r"that's not right",
            r"let me think again",
            r"i should reconsider",
            r"upon reflection"
        ]
        
        # Negative self-correction patterns (poor corrections)
        poor_correction_patterns = [
            r"never mind,? forget that",
            r"ignore what i just said",
            r"disregard my previous",
            r"scratch that,? new plan",
            r"completely starting over"
        ]
        
        # Evidence-based correction patterns (best)
        evidence_based_patterns = [
            r"given the new information",
            r"based on further analysis",
            r"after considering",
            r"looking at this more carefully",
            r"reviewing the evidence",
            r"taking into account",
            r"with additional context"
        ]
        
        positive_count = sum(1 for pattern in positive_correction_patterns if re.search(pattern, reasoning_lower))
        poor_count = sum(1 for pattern in poor_correction_patterns if re.search(pattern, reasoning_lower))
        evidence_count = sum(1 for pattern in evidence_based_patterns if re.search(pattern, reasoning_lower))
        
        # Calculate correction effectiveness score
        if evidence_count > 0:
            return min(1.0, 0.8 + evidence_count * 0.1)  # High score for evidence-based corrections
        elif positive_count > 0 and poor_count == 0:
            return min(1.0, 0.6 + positive_count * 0.1)  # Good score for positive corrections
        elif positive_count > poor_count:
            return 0.4  # Moderate score when positive > poor
        elif poor_count > 0:
            return 0.2  # Low score for poor corrections
        else:
            return 0.5  # Neutral score when no corrections detected
    
    def _detect_overconfidence_in_reasoning(self, reasoning: str) -> bool:
        """Detect overconfident assertions specifically in reasoning chains."""
        reasoning_lower = reasoning.lower()
        
        # Overconfidence in reasoning patterns
        reasoning_overconfidence_patterns = [
            r"this logic is flawless",
            r"undeniably true",
            r"impossible to argue",
            r"logically perfect",
            r"cannot be disputed",
            r"absolute certainty",
            r"beyond question",
            r"indisputable fact",
            r"without any doubt",
            r"definitely proves"
        ]
        
        # Lack of uncertainty acknowledgment
        uncertainty_patterns = [
            r"might be",
            r"could indicate",
            r"seems to suggest",
            r"appears that",
            r"possibly",
            r"potentially",
            r"likely",
            r"probably",
            r"uncertain",
            r"unclear"
        ]
        
        overconfidence_count = sum(1 for pattern in reasoning_overconfidence_patterns if re.search(pattern, reasoning_lower))
        uncertainty_count = sum(1 for pattern in uncertainty_patterns if re.search(pattern, reasoning_lower))
        
        # Overconfident if high confidence assertions with no uncertainty acknowledgment
        if overconfidence_count >= 1 and uncertainty_count == 0:
            return True
        
        # Also check for absolute logical claims
        absolute_logic_patterns = [
            r"always leads to",
            r"never results in",
            r"must be",
            r"has to be",
            r"cannot be anything else",
            r"only possible explanation",
            r"proves beyond doubt"
        ]
        
        absolute_count = sum(1 for pattern in absolute_logic_patterns if re.search(pattern, reasoning_lower))
        
        # Overconfident if multiple absolute claims without hedging
        if absolute_count >= 2 and uncertainty_count == 0:
            return True
        
        return False
    
    def _score_reflection_depth(self, reasoning: str) -> float:
        """Score the depth of reflection in reasoning."""
        reasoning_lower = reasoning.lower()
        
        # Surface-level indicators (lower depth)
        surface_patterns = [
            r"because",
            r"so",
            r"then",
            r"therefore"
        ]
        
        # Medium-depth indicators
        medium_patterns = [
            r"this suggests",
            r"which implies",
            r"leading me to think",
            r"considering that",
            r"given this",
            r"as a result"
        ]
        
        # Deep reflection indicators
        deep_patterns = [
            r"upon deeper consideration",
            r"examining the underlying",
            r"questioning my assumption",
            r"alternative explanation",
            r"multiple perspectives",
            r"exploring the implications",
            r"what if",
            r"on the other hand",
            r"contradictory evidence",
            r"nuanced view"
        ]
        
        # Metacognitive indicators (deepest)
        metacognitive_patterns = [
            r"i realize that i",
            r"my thinking process",
            r"how i arrived at",
            r"questioning my reasoning",
            r"aware of my bias",
            r"limitations of my analysis",
            r"need to think differently",
            r"my mental model"
        ]
        
        surface_count = sum(1 for pattern in surface_patterns if re.search(pattern, reasoning_lower))
        medium_count = sum(1 for pattern in medium_patterns if re.search(pattern, reasoning_lower))
        deep_count = sum(1 for pattern in deep_patterns if re.search(pattern, reasoning_lower))
        metacognitive_count = sum(1 for pattern in metacognitive_patterns if re.search(pattern, reasoning_lower))
        
        # Calculate depth score
        total_indicators = surface_count + medium_count + deep_count + metacognitive_count
        
        if total_indicators == 0:
            return 0.3  # Low score for no depth indicators
        
        # Weighted scoring: metacognitive > deep > medium > surface
        weighted_score = (
            surface_count * 0.1 +
            medium_count * 0.3 +
            deep_count * 0.6 +
            metacognitive_count * 1.0
        ) / total_indicators
        
        return min(1.0, weighted_score)
    
    def _score_metacognitive_awareness(self, reasoning: str) -> float:
        """Score metacognitive awareness in reasoning."""
        reasoning_lower = reasoning.lower()
        
        # Self-awareness patterns
        self_awareness_patterns = [
            r"i'm thinking",
            r"my approach is",
            r"i notice that i",
            r"i tend to",
            r"my bias might be",
            r"i could be wrong",
            r"i'm assuming",
            r"my perspective",
            r"i need to be careful",
            r"i should consider"
        ]
        
        # Process awareness patterns
        process_awareness_patterns = [
            r"my reasoning process",
            r"how i'm thinking",
            r"the way i analyze",
            r"my mental approach",
            r"thinking step by step",
            r"my methodology",
            r"my logic",
            r"the process i use"
        ]
        
        # Limitation awareness patterns
        limitation_awareness_patterns = [
            r"i don't know",
            r"beyond my knowledge",
            r"i'm uncertain",
            r"i might be missing",
            r"limitations of",
            r"i cannot be sure",
            r"unclear to me",
            r"i lack information",
            r"outside my expertise",
            r"i could be overlooking"
        ]
        
        self_count = sum(1 for pattern in self_awareness_patterns if re.search(pattern, reasoning_lower))
        process_count = sum(1 for pattern in process_awareness_patterns if re.search(pattern, reasoning_lower))
        limitation_count = sum(1 for pattern in limitation_awareness_patterns if re.search(pattern, reasoning_lower))
        
        total_metacognitive = self_count + process_count + limitation_count
        
        if total_metacognitive == 0:
            return 0.2  # Low score for no metacognitive awareness
        
        # Normalize by reasoning length (longer reasoning should have more indicators)
        reasoning_length = len(reasoning.split())
        normalized_score = min(1.0, total_metacognitive / max(1, reasoning_length / 100))
        
        return normalized_score
    
    def _score_reasoning_coherence(self, reasoning: str) -> float:
        """Score the coherence and logical flow of reasoning."""
        reasoning_lower = reasoning.lower()
        
        # Logical connectors (positive for coherence)
        logical_connectors = [
            r"therefore",
            r"because",
            r"since",
            r"as a result",
            r"consequently",
            r"thus",
            r"hence",
            r"so",
            r"given that",
            r"due to",
            r"leads to",
            r"implies",
            r"suggests"
        ]
        
        # Coherence disruptors (negative for coherence)
        disruptors = [
            r"wait, no",
            r"actually, ignore",
            r"never mind",
            r"completely different",
            r"unrelated",
            r"random thought",
            r"by the way",
            r"off topic",
            r"tangent"
        ]
        
        # Contradiction indicators
        contradictions = [
            r"but earlier i said",
            r"contradicting myself",
            r"opposite of what",
            r"inconsistent with",
            r"conflicts with my",
            r"doesn't match"
        ]
        
        connector_count = sum(1 for pattern in logical_connectors if re.search(pattern, reasoning_lower))
        disruptor_count = sum(1 for pattern in disruptors if re.search(pattern, reasoning_lower))
        contradiction_count = sum(1 for pattern in contradictions if re.search(pattern, reasoning_lower))
        
        # Calculate base coherence score
        sentences = re.split(r'[.!?]', reasoning)
        sentence_count = len([s for s in sentences if len(s.strip()) > 5])
        
        if sentence_count == 0:
            return 0.5  # Neutral for very short reasoning
        
        # Coherence score based on logical flow
        connector_density = connector_count / sentence_count
        disruptor_penalty = disruptor_count * 0.2
        contradiction_penalty = contradiction_count * 0.3
        
        base_score = min(1.0, 0.5 + connector_density)
        final_score = max(0.0, base_score - disruptor_penalty - contradiction_penalty)
        
        return final_score
    
    # ==================== Migration Analysis Methods (Task 7) ====================
    
    def _analyze_migration_opportunities(
        self,
        detected_framework: Optional[str],
        framework_performance: Optional[FrameworkPerformanceAnalysis],
        workflow_metrics: WorkflowReliabilityMetrics
    ) -> Dict[str, Any]:
        """Analyze framework migration opportunities based on performance thresholds."""
        
        if not detected_framework or not framework_performance:
            return {"migration_recommended": False, "reason": "Insufficient framework data"}
        
        # Define performance thresholds for migration recommendation
        migration_thresholds = {
            "success_rate": 0.85,           # Below 85% success rate
            "tool_failure_rate": 0.15,     # Above 15% tool failure rate
            "timeout_frequency": 0.10,     # Above 10% timeout rate
            "workflow_reliability": 0.75,   # Below 75% workflow reliability
            "schema_mismatch_rate": 0.10    # Above 10% schema mismatches
        }
        
        # Evaluate current performance against thresholds
        performance_issues = []
        severity_score = 0
        
        if framework_performance.success_rate < migration_thresholds["success_rate"]:
            gap = migration_thresholds["success_rate"] - framework_performance.success_rate
            performance_issues.append(f"Low success rate: {framework_performance.success_rate:.1%}")
            severity_score += gap * 100  # Convert to percentage points
        
        if framework_performance.tool_call_failure_rate > migration_thresholds["tool_failure_rate"]:
            gap = framework_performance.tool_call_failure_rate - migration_thresholds["tool_failure_rate"]
            performance_issues.append(f"High tool failure rate: {framework_performance.tool_call_failure_rate:.1%}")
            severity_score += gap * 100
        
        if framework_performance.timeout_frequency > migration_thresholds["timeout_frequency"]:
            gap = framework_performance.timeout_frequency - migration_thresholds["timeout_frequency"]
            performance_issues.append(f"Frequent timeouts: {framework_performance.timeout_frequency:.1%}")
            severity_score += gap * 50  # Timeouts are less critical
        
        if workflow_metrics.workflow_success_rate < migration_thresholds["workflow_reliability"]:
            gap = migration_thresholds["workflow_reliability"] - workflow_metrics.workflow_success_rate
            performance_issues.append(f"Poor workflow reliability: {workflow_metrics.workflow_success_rate:.1%}")
            severity_score += gap * 100
        
        if workflow_metrics.schema_mismatch_rate > migration_thresholds["schema_mismatch_rate"]:
            gap = workflow_metrics.schema_mismatch_rate - migration_thresholds["schema_mismatch_rate"]
            performance_issues.append(f"Schema mismatches: {workflow_metrics.schema_mismatch_rate:.1%}")
            severity_score += gap * 75  # Schema issues are quite critical
        
        # Determine if migration is recommended based on severity
        migration_recommended = len(performance_issues) >= 2 or severity_score > 20
        
        if not migration_recommended:
            return {
                "migration_recommended": False,
                "reason": "Performance within acceptable thresholds",
                "current_framework": detected_framework,
                "performance_score": max(0, 100 - severity_score)
            }
        
        # Generate migration recommendation
        recommended_framework = self._get_recommended_migration_target(
            detected_framework, performance_issues, framework_performance
        )
        
        improvement_estimate = self._estimate_migration_improvement(
            performance_issues, severity_score
        )
        
        migration_priority = self._determine_migration_priority(severity_score, performance_issues)
        
        migration_steps = self._generate_migration_steps(detected_framework, recommended_framework)
        
        return {
            "migration_recommended": True,
            "current_framework": detected_framework,
            "recommended_framework": recommended_framework,
            "improvement_estimate": improvement_estimate,
            "priority": migration_priority,
            "performance_issues": performance_issues,
            "severity_score": severity_score,
            "migration_steps": migration_steps,
            "estimated_migration_time": self._estimate_migration_time(detected_framework, recommended_framework),
            "migration_risks": self._assess_migration_risks(detected_framework, recommended_framework)
        }
    
    def _get_recommended_migration_target(
        self,
        current_framework: str,
        performance_issues: List[str],
        framework_performance: FrameworkPerformanceAnalysis
    ) -> str:
        """Get recommended migration target framework based on current issues."""
        
        # Framework migration matrix based on common issue patterns
        migration_matrix = {
            "langchain": {
                "default": "openai",  # Direct API often more reliable
                "timeout": "anthropic",  # Claude often faster for complex reasoning
                "tool_failure": "openai",  # Better tool call reliability
                "complexity": "agno"  # Simpler, lighter framework
            },
            "crewai": {
                "default": "autogen",  # Better multi-agent support
                "performance": "langchain",  # More mature ecosystem
                "tool_failure": "openai",  # Direct API reliability
                "complexity": "anthropic"  # Simpler agent interactions
            },
            "autogen": {
                "default": "crewai",  # Specialized for agent crews
                "performance": "openai",  # Direct API performance
                "tool_failure": "anthropic",  # Better tool integration
                "reliability": "langchain"  # More stable ecosystem
            },
            "openai": {
                "default": "anthropic",  # Alternative provider
                "performance": "langchain",  # Local optimization possible
                "reliability": "anthropic",  # Different failure modes
                "cost": "agno"  # More cost-effective
            },
            "anthropic": {
                "default": "openai",  # Alternative provider
                "tool_failure": "langchain",  # Better tool ecosystem
                "performance": "openai",  # Faster API responses
                "cost": "agno"  # More cost-effective
            },
            "generic": {
                "default": "openai",  # Move to structured framework
                "reliability": "langchain",  # Full framework support
                "simplicity": "anthropic",  # Easy to implement
                "cost": "agno"  # Lightweight option
            },
            "agno": {
                "default": "openai",  # More features
                "complexity": "langchain",  # Full framework capabilities
                "reliability": "anthropic",  # Enterprise reliability
                "performance": "openai"  # Faster responses
            }
        }
        
        # Determine primary issue type
        primary_issue = "default"
        if any("timeout" in issue.lower() for issue in performance_issues):
            primary_issue = "timeout"
        elif any("tool" in issue.lower() for issue in performance_issues):
            primary_issue = "tool_failure"
        elif any("reliability" in issue.lower() or "success" in issue.lower() for issue in performance_issues):
            primary_issue = "reliability"
        elif framework_performance.avg_response_time > 5.0:
            primary_issue = "performance"
        
        # Get recommendation
        framework_options = migration_matrix.get(current_framework, {"default": "openai"})
        return framework_options.get(primary_issue, framework_options["default"])
    
    def _estimate_migration_improvement(
        self,
        performance_issues: List[str],
        severity_score: float
    ) -> int:
        """Estimate performance improvement percentage from migration."""
        
        # Base improvement estimate based on severity
        base_improvement = min(50, int(severity_score))  # Cap at 50% improvement
        
        # Issue-specific improvements
        issue_bonuses = {
            "timeout": 15,      # Migration often reduces timeouts significantly
            "tool": 20,         # Better frameworks have better tool integration
            "success": 25,      # Core reliability improvements
            "schema": 10        # Better schema handling
        }
        
        additional_improvement = 0
        for issue in performance_issues:
            for issue_type, bonus in issue_bonuses.items():
                if issue_type in issue.lower():
                    additional_improvement += bonus
                    break
        
        # Total improvement estimate
        total_improvement = min(60, base_improvement + additional_improvement)  # Cap at 60%
        
        return max(10, total_improvement)  # Minimum 10% improvement
    
    def _determine_migration_priority(
        self,
        severity_score: float,
        performance_issues: List[str]
    ) -> str:
        """Determine migration priority based on severity and issues."""
        
        critical_indicators = ["success", "reliability", "failure"]
        has_critical_issues = any(
            any(indicator in issue.lower() for indicator in critical_indicators)
            for issue in performance_issues
        )
        
        if severity_score > 40 or has_critical_issues:
            return "high"
        elif severity_score > 20 or len(performance_issues) >= 3:
            return "medium"
        else:
            return "low"
    
    def _generate_migration_steps(
        self,
        current_framework: str,
        target_framework: str
    ) -> List[str]:
        """Generate specific migration steps."""
        
        migration_steps_map = {
            ("langchain", "openai"): [
                "Migrate to direct OpenAI API calls for better reliability",
                "Replace LangChain chains with custom function orchestration",
                "Implement OpenAI function calling for tool integration",
                "Add custom retry logic and error handling"
            ],
            ("crewai", "autogen"): [
                "Migrate crew workflows to AutoGen conversation patterns",
                "Replace CrewAI tasks with AutoGen agent roles",
                "Implement AutoGen group chat for multi-agent coordination",
                "Add custom agent memory management"
            ],
            ("openai", "anthropic"): [
                "Migrate OpenAI function calls to Claude tool use format",
                "Replace OpenAI-specific prompting with Claude best practices",
                "Implement Anthropic's structured output patterns",
                "Add Claude-optimized error handling"
            ],
            ("generic", "openai"): [
                "Structure agent outputs using OpenAI API format",
                "Implement OpenAI function calling for tool integration",
                "Add OpenAI-compatible streaming and async support",
                "Integrate with OpenAI ecosystem tools"
            ]
        }
        
        # Get specific steps or generate generic ones
        migration_key = (current_framework, target_framework)
        if migration_key in migration_steps_map:
            return migration_steps_map[migration_key]
        
        # Generic migration steps
        return [
            f"Plan migration from {current_framework} to {target_framework}",
            f"Set up {target_framework} development environment",
            f"Implement core functionality using {target_framework} patterns",
            f"Test migration with parallel {current_framework} and {target_framework} runs",
            f"Validate performance improvements and deploy {target_framework} solution"
        ]
    
    def _estimate_migration_time(
        self,
        current_framework: str,
        target_framework: str
    ) -> str:
        """Estimate migration time based on framework complexity."""
        
        # Framework complexity scores (higher = more complex to migrate from/to)
        complexity_scores = {
            "generic": 1,
            "openai": 2,
            "anthropic": 2,
            "agno": 3,
            "autogen": 4,
            "langchain": 5,
            "crewai": 4,
            "langgraph": 6
        }
        
        source_complexity = complexity_scores.get(current_framework, 3)
        target_complexity = complexity_scores.get(target_framework, 3)
        
        # Calculate migration effort (days)
        base_effort = 3  # Minimum 3 days
        complexity_effort = (source_complexity + target_complexity) * 1.5
        total_days = int(base_effort + complexity_effort)
        
        if total_days <= 5:
            return "3-5 days"
        elif total_days <= 10:
            return "1-2 weeks"
        elif total_days <= 20:
            return "2-3 weeks"
        else:
            return "3-4 weeks"
    
    def _assess_migration_risks(
        self,
        current_framework: str,
        target_framework: str
    ) -> List[str]:
        """Assess risks associated with framework migration."""
        
        risks = []
        
        # Framework-specific risks
        framework_risks = {
            "langchain": ["Complex dependency chain", "Custom chain compatibility"],
            "crewai": ["Multi-agent coordination complexity", "Task workflow dependencies"],
            "autogen": ["Conversation state management", "Agent memory handling"],
            "openai": ["API rate limits", "Function calling compatibility"],
            "anthropic": ["Tool use format changes", "Context window differences"],
            "agno": ["Limited ecosystem", "Documentation gaps"],
            "generic": ["Lack of structure", "Custom implementation dependencies"]
        }
        
        # Add source framework risks
        source_risks = framework_risks.get(current_framework, [])
        for risk in source_risks:
            risks.append(f"From {current_framework}: {risk}")
        
        # Add target framework risks
        target_risks = framework_risks.get(target_framework, [])
        for risk in target_risks:
            risks.append(f"To {target_framework}: {risk}")
        
        # Add general migration risks
        risks.extend([
            "Temporary performance degradation during transition",
            "Need for parallel testing and validation",
            "Potential integration issues with existing systems"
        ])
        
        return risks[:5]  # Return top 5 risks
    
    # ==================== Cognitive Analysis Integration (Task 8) ====================
    
    def _perform_cognitive_analysis(self, agent_outputs: List[Any]) -> Optional[Any]:
        """Perform cognitive analysis using CognitiveAnalyzer."""
        
        try:
            from agent_eval.analysis.cognitive_analyzer import CognitiveAnalyzer
            
            if not agent_outputs:
                return None
            
            # Initialize cognitive analyzer
            cognitive_analyzer = CognitiveAnalyzer()
            
            # Extract reasoning chains from agent outputs for analysis
            reasoning_chains = self._extract_reasoning_chains_for_cognitive_analysis(agent_outputs)
            
            if not reasoning_chains:
                # Fallback: use agent outputs directly if no reasoning chains found
                logger.info("No reasoning chains found, performing cognitive analysis on agent outputs directly")
                return cognitive_analyzer.generate_comprehensive_cognitive_analysis(
                    agent_outputs=agent_outputs,
                    reasoning_chains=None
                )
            
            # Perform comprehensive cognitive analysis
            cognitive_analysis = cognitive_analyzer.generate_comprehensive_cognitive_analysis(
                agent_outputs=agent_outputs,
                reasoning_chains=reasoning_chains
            )
            
            logger.info(f"Cognitive analysis completed: health_score={cognitive_analysis.cognitive_health_score:.2f}")
            
            return cognitive_analysis
            
        except ImportError as e:
            logger.warning(f"CognitiveAnalyzer not available: {e}")
            return None
        except Exception as e:
            logger.warning(f"Cognitive analysis failed: {e}")
            return None
    
    def _extract_reasoning_chains_for_cognitive_analysis(self, agent_outputs: List[Any]) -> List[str]:
        """Extract reasoning chains from agent outputs for cognitive analysis."""
        
        reasoning_chains = []
        
        for output in agent_outputs:
            try:
                # Convert output to string for analysis
                output_str = str(output)
                
                # Look for reasoning indicators in the output
                reasoning_patterns = [
                    r"(?:because|since|therefore|thus|hence|consequently).*?[.!?]",
                    r"(?:reasoning|thinking|analysis|consideration)[:.].*?[.!?]",
                    r"(?:let me think|my analysis|i believe|i think).*?[.!?]",
                    r"(?:step \d+|first|second|third|next|then|finally).*?[.!?]",
                    r"(?:based on|considering|given that|due to).*?[.!?]"
                ]
                
                # Extract reasoning segments
                for pattern in reasoning_patterns:
                    matches = re.findall(pattern, output_str, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        # Clean up the reasoning text
                        cleaned_reasoning = match.strip()
                        if len(cleaned_reasoning) > 20:  # Only include substantial reasoning
                            reasoning_chains.append(cleaned_reasoning)
                
                # If no pattern matches, look for longer coherent text segments
                if not reasoning_chains:
                    # Extract sentences that might contain reasoning
                    sentences = re.split(r'[.!?]+', output_str)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        # Include sentences that are substantive and might contain reasoning
                        if (len(sentence) > 50 and 
                            any(word in sentence.lower() for word in 
                                ['because', 'therefore', 'analysis', 'considering', 'reasoning', 'think', 'believe'])):
                            reasoning_chains.append(sentence)
                            
            except Exception as e:
                logger.debug(f"Error extracting reasoning from output: {e}")
                continue
        
        # Remove duplicates while preserving order
        unique_reasoning = []
        seen = set()
        for reasoning in reasoning_chains:
            if reasoning not in seen:
                unique_reasoning.append(reasoning)
                seen.add(reasoning)
        
        logger.debug(f"Extracted {len(unique_reasoning)} reasoning chains from {len(agent_outputs)} outputs")
        
        return unique_reasoning[:20]  # Limit to top 20 for performance

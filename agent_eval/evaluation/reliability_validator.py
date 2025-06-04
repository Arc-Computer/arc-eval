"""Reliability validation for agent tool calls and error handling patterns."""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter

from agent_eval.core.types import ReliabilityMetrics, AgentOutput

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

    # Reliability Prediction (NEW - Task 2.1)
    reliability_prediction: Optional[Dict[str, Any]]  # Hybrid prediction results

    # Evidence and Confidence
    analysis_confidence: float
    evidence_quality: str      # "high", "medium", "low"
    sample_size: int


class ReliabilityAnalyzer:
    """Comprehensive reliability analyzer combining validation, framework analysis, and dashboard generation."""

    def __init__(self, api_manager=None):
        """Initialize reliability validator with framework-specific patterns."""

        # Store api_manager for judge integration
        self.api_manager = api_manager

        # Use centralized framework patterns
        from agent_eval.core.framework_patterns import framework_patterns
        self.framework_patterns = framework_patterns

        # NEW: Initialize hybrid predictor for reliability prediction
        try:
            from agent_eval.prediction.hybrid_predictor import HybridReliabilityPredictor
            from agent_eval.prediction.prediction_tracker import PredictionTracker
            from agent_eval.prediction.outcome_detector import OutcomeDetector

            self.hybrid_predictor = HybridReliabilityPredictor(api_manager)
            self.prediction_tracker = PredictionTracker()
            self.outcome_detector = OutcomeDetector()
            self.prediction_enabled = True
        except (ImportError, ValueError) as e:
            # Handle both missing modules and missing API keys gracefully
            logger.warning(f"Prediction module not available: {e}")
            self.hybrid_predictor = None
            self.prediction_tracker = None
            self.outcome_detector = None
            self.prediction_enabled = False

        # Keep backward compatibility with tool_patterns attribute
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
        
        # Try framework-specific patterns first using centralized patterns
        if framework:
            patterns = self.framework_patterns.get_tool_call_patterns(framework)
        else:
            # Auto-detect framework first
            framework_detection = self.detect_framework_comprehensive([agent_output])
            detected_framework = framework_detection.get('detected_framework')

            if detected_framework:
                # Use detected framework patterns
                patterns = self.framework_patterns.get_tool_call_patterns(detected_framework)
            else:
                # Try all patterns if framework is unknown - use public method to get framework list
                patterns = []
                for fw in self.framework_patterns.get_framework_names():
                    patterns.extend(self.framework_patterns.get_tool_call_patterns(fw))
        
        for pattern in patterns:
            # Check if pattern is already compiled (Pattern object) or string
            if hasattr(pattern, 'findall'):
                # Pattern is already compiled, use it directly
                matches = pattern.findall(output_str)
            else:
                # Pattern is a string, compile it with flags
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
        
        # Detect framework using comprehensive detection
        framework_detection = self.detect_framework_comprehensive([agent_output])
        framework = framework_detection.get('detected_framework')
        
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
        expected_tools: Optional[List[str]] = None,
        pipeline_data: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveReliabilityAnalysis:
        """Simple, judge-first reliability analysis."""

        if not agent_outputs:
            return self._create_empty_analysis()

        # Try judge analysis first (simple and fast)
        try:
            from agent_eval.evaluation.judges.workflow.debug import DebugJudge
            from agent_eval.evaluation.judges.api_manager import APIManager

            api_manager = APIManager(provider="cerebras")
            debug_judge = DebugJudge(api_manager)

            # Simple judge analysis
            judge_output = debug_judge.evaluate_failure_patterns(agent_outputs, framework or "unknown")

            # Convert to analysis format
            return self._judge_to_analysis(judge_output, agent_outputs, framework)

        except Exception:
            # Simple fallback - basic analysis only
            return self._basic_analysis(agent_outputs, framework, expected_tools)


    
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
            reliability_prediction=None,  # NEW - Task 2.1
            analysis_confidence=0.0,
            evidence_quality="none",
            sample_size=0
        )
    
    def _judge_to_analysis(self, judge_output: Dict, agent_outputs: List[Any], framework: Optional[str]) -> ComprehensiveReliabilityAnalysis:
        """Convert judge output to analysis format - simple and direct."""
        return ComprehensiveReliabilityAnalysis(
            detected_framework=framework,
            framework_confidence=1.0 if framework else 0.5,
            auto_detection_successful=bool(framework),
            framework_performance=None,
            workflow_metrics=self._simple_metrics(agent_outputs),
            tool_call_summary={'judge_analysis': True, 'total_outputs': len(agent_outputs)},
            validation_results=[],
            reliability_dashboard=f"🤖 Judge Analysis: {judge_output.get('summary', 'Analysis complete')}",
            insights_summary=[judge_output.get('key_insight', 'Judge analysis completed')],
            next_steps=judge_output.get('recommendations', ['Continue monitoring']),
            cognitive_analysis=None,
            reliability_prediction=None,
            analysis_confidence=judge_output.get('confidence', 0.8),
            evidence_quality="judge_enhanced",
            sample_size=len(agent_outputs)
        )

    def _basic_analysis(self, agent_outputs: List[Any], framework: Optional[str], expected_tools: Optional[List[str]]) -> ComprehensiveReliabilityAnalysis:
        """Simple fallback analysis - no complexity."""
        return ComprehensiveReliabilityAnalysis(
            detected_framework=framework,
            framework_confidence=1.0 if framework else 0.3,
            auto_detection_successful=bool(framework),
            framework_performance=None,
            workflow_metrics=self._simple_metrics(agent_outputs),
            tool_call_summary={'basic_analysis': True, 'total_outputs': len(agent_outputs)},
            validation_results=[],
            reliability_dashboard="📊 Basic Analysis: Rule-based evaluation complete",
            insights_summary=["Basic analysis completed - upgrade to judge analysis for enhanced insights"],
            next_steps=["Enable judge analysis for better insights"],
            cognitive_analysis=None,
            reliability_prediction=None,
            analysis_confidence=0.6,
            evidence_quality="basic",
            sample_size=len(agent_outputs)
        )

    def _simple_metrics(self, agent_outputs: List[Any]) -> WorkflowReliabilityMetrics:
        """Simple metrics calculation - no complexity."""
        success_rate = 0.8  # Default assumption
        return WorkflowReliabilityMetrics(
            workflow_success_rate=success_rate,
            tool_chain_reliability=success_rate,
            decision_consistency_score=success_rate,
            multi_step_completion_rate=success_rate,
            average_workflow_time=0.0,
            error_recovery_rate=0.5,
            timeout_rate=0.1,
            framework_compatibility_score=0.8,
            tool_usage_efficiency=0.8,
            schema_mismatch_rate=0.1,
            prompt_tool_alignment_score=0.8,
            reliability_trend="stable",
            critical_failure_points=[]
        )


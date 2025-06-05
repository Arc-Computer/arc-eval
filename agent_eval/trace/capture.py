"""
Trace Capture: Execution monitoring and data collection.

Handles framework detection, tool call monitoring, and performance tracking.
"""

import time
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import inspect

from .types import TraceData, ExecutionStep, ToolCall, TraceEventType, CostData
from .cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class TraceCapture:
    """Captures execution timeline, tool calls, and costs."""
    
    def __init__(self, domain: str = "general"):
        """Initialize trace capture for specific domain.
        
        Args:
            domain: Domain context for specialized monitoring
        """
        self.domain = domain
        self.cost_tracker = CostTracker()
        
        # Framework detection patterns
        self.framework_patterns = {
            'langchain': ['langchain', 'LLMChain', 'AgentExecutor', 'BaseAgent'],
            'crewai': ['crewai', 'Agent', 'Task', 'Crew'],
            'autogen': ['autogen', 'ConversableAgent', 'AssistantAgent'],
            'openai': ['openai', 'ChatCompletion', 'Completion'],
            'anthropic': ['anthropic', 'Claude', 'Messages'],
            'llamaindex': ['llama_index', 'ServiceContext', 'VectorStoreIndex'],
            'haystack': ['haystack', 'Pipeline', 'BaseComponent']
        }
    
    def detect_framework(self, agent: Any) -> Optional[str]:
        """Detect the framework of an agent instance.
        
        Args:
            agent: Agent instance to analyze
            
        Returns:
            Framework name or None if unknown
        """
        agent_type = type(agent).__name__
        agent_module = getattr(type(agent), '__module__', '')
        
        # Check module path and class names
        for framework, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if (pattern.lower() in agent_module.lower() or 
                    pattern.lower() in agent_type.lower()):
                    logger.debug(f"Detected framework: {framework} for {agent_type}")
                    return framework
        
        # Check for specific framework methods
        if hasattr(agent, 'invoke') and hasattr(agent, 'stream'):
            return 'langchain'
        elif hasattr(agent, 'execute_task') and hasattr(agent, 'backstory'):
            return 'crewai'
        elif hasattr(agent, 'generate_reply'):
            return 'autogen'
        
        logger.debug(f"Unknown framework for {agent_type}")
        return 'unknown'
    
    def capture_execution(
        self, 
        method: Callable, 
        trace_data: TraceData, 
        *args, 
        **kwargs
    ) -> Any:
        """Capture method execution with detailed monitoring.
        
        Args:
            method: Method to execute
            trace_data: Trace data to populate
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Method execution result
        """
        execution_start = time.time()
        
        try:
            # Monitor for tool calls and API calls
            result = self._monitor_execution(method, trace_data, *args, **kwargs)
            
            execution_duration = (time.time() - execution_start) * 1000
            
            # Create performance step
            perf_step = ExecutionStep(
                step_id=str(uuid.uuid4()),
                event_type=TraceEventType.PERFORMANCE,
                timestamp=datetime.now(),
                duration_ms=execution_duration,
                data={
                    'execution_time_ms': execution_duration,
                    'method_name': method.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            trace_data.execution_timeline.append(perf_step)
            
            return result
            
        except Exception as e:
            execution_duration = (time.time() - execution_start) * 1000
            logger.error(f"Execution failed after {execution_duration}ms: {e}")
            raise
    
    def _monitor_execution(
        self, 
        method: Callable, 
        trace_data: TraceData, 
        *args, 
        **kwargs
    ) -> Any:
        """Monitor method execution for framework-specific patterns."""
        
        # Pre-execution monitoring
        self._capture_pre_execution(method, trace_data, *args, **kwargs)
        
        # Execute with framework-specific monitoring
        if trace_data.framework == 'langchain':
            result = self._monitor_langchain_execution(method, trace_data, *args, **kwargs)
        elif trace_data.framework == 'crewai':
            result = self._monitor_crewai_execution(method, trace_data, *args, **kwargs)
        elif trace_data.framework == 'autogen':
            result = self._monitor_autogen_execution(method, trace_data, *args, **kwargs)
        else:
            # Generic monitoring
            result = self._monitor_generic_execution(method, trace_data, *args, **kwargs)
        
        # Post-execution monitoring
        self._capture_post_execution(result, trace_data)
        
        return result
    
    def _capture_pre_execution(self, method: Callable, trace_data: TraceData, *args, **kwargs):
        """Capture pre-execution state."""
        # Capture method signature
        try:
            sig = inspect.signature(method)
            params = sig.parameters
            
            step = ExecutionStep(
                step_id=str(uuid.uuid4()),
                event_type=TraceEventType.AGENT_START,
                timestamp=datetime.now(),
                duration_ms=0.0,
                data={
                    'method_signature': str(sig),
                    'parameter_count': len(params),
                    'framework': trace_data.framework
                }
            )
            trace_data.execution_timeline.append(step)
            
        except Exception as e:
            logger.warning(f"Failed to capture method signature: {e}")
    
    def _capture_post_execution(self, result: Any, trace_data: TraceData):
        """Capture post-execution data."""
        # Analyze result for useful information
        result_info = self._analyze_result(result)
        
        step = ExecutionStep(
            step_id=str(uuid.uuid4()),
            event_type=TraceEventType.AGENT_END,
            timestamp=datetime.now(),
            duration_ms=0.0,
            data={
                'result_type': result_info['type'],
                'result_size': result_info['size'],
                'contains_error': result_info['has_error']
            }
        )
        trace_data.execution_timeline.append(step)
    
    def _monitor_langchain_execution(self, method: Callable, trace_data: TraceData, *args, **kwargs) -> Any:
        """Monitor LangChain-specific execution patterns."""
        logger.debug("Monitoring LangChain execution")
        
        # Execute method
        result = method(*args, **kwargs)
        
        # Check for intermediate steps (common in LangChain)
        if hasattr(result, 'get') and isinstance(result, dict):
            intermediate_steps = result.get('intermediate_steps', [])
            for i, step in enumerate(intermediate_steps):
                if isinstance(step, (list, tuple)) and len(step) >= 2:
                    tool_call = ToolCall(
                        tool_name=str(step[0]) if step[0] else f"step_{i}",
                        tool_input={'action': str(step[0])[:200]},
                        tool_output=str(step[1])[:500] if len(step) > 1 else '',
                        timestamp=datetime.now(),
                        duration_ms=0.0,  # LangChain doesn't provide timing
                        success=True
                    )
                    trace_data.tool_calls.append(tool_call)
        
        return result
    
    def _monitor_crewai_execution(self, method: Callable, trace_data: TraceData, *args, **kwargs) -> Any:
        """Monitor CrewAI-specific execution patterns."""
        logger.debug("Monitoring CrewAI execution")
        
        # Execute method
        result = method(*args, **kwargs)
        
        # Check for task outputs (common in CrewAI)
        if hasattr(result, 'task_outputs') or (isinstance(result, dict) and 'task_outputs' in result):
            task_outputs = getattr(result, 'task_outputs', result.get('task_outputs', []))
            for i, task_output in enumerate(task_outputs):
                tool_call = ToolCall(
                    tool_name=f"task_{i}",
                    tool_input={'task_description': str(task_output)[:200]},
                    tool_output=str(task_output)[:500],
                    timestamp=datetime.now(),
                    duration_ms=0.0,
                    success=True
                )
                trace_data.tool_calls.append(tool_call)
        
        return result
    
    def _monitor_autogen_execution(self, method: Callable, trace_data: TraceData, *args, **kwargs) -> Any:
        """Monitor AutoGen-specific execution patterns."""
        logger.debug("Monitoring AutoGen execution")
        
        # Execute method
        result = method(*args, **kwargs)
        
        # Check for message history (common in AutoGen)
        if hasattr(result, 'chat_messages') or (isinstance(result, dict) and 'messages' in result):
            messages = getattr(result, 'chat_messages', result.get('messages', []))
            for i, message in enumerate(messages[-5:]):  # Last 5 messages
                tool_call = ToolCall(
                    tool_name=f"message_{i}",
                    tool_input={'role': message.get('role', 'unknown')},
                    tool_output=str(message.get('content', ''))[:500],
                    timestamp=datetime.now(),
                    duration_ms=0.0,
                    success=True
                )
                trace_data.tool_calls.append(tool_call)
        
        return result
    
    def _monitor_generic_execution(self, method: Callable, trace_data: TraceData, *args, **kwargs) -> Any:
        """Monitor generic agent execution."""
        logger.debug("Monitoring generic execution")
        
        # Execute method
        result = method(*args, **kwargs)
        
        # Try to extract tool calls from common patterns
        self._extract_generic_tool_calls(result, trace_data)
        
        return result
    
    def _extract_generic_tool_calls(self, result: Any, trace_data: TraceData):
        """Extract tool calls from generic result patterns."""
        
        # Check if result is a dictionary with common tool call patterns
        if isinstance(result, dict):
            # Look for tool calls in various formats
            for key in ['tool_calls', 'actions', 'steps', 'operations']:
                if key in result:
                    tools = result[key]
                    if isinstance(tools, list):
                        for i, tool in enumerate(tools):
                            tool_call = ToolCall(
                                tool_name=str(tool.get('name', f'tool_{i}')),
                                tool_input=tool.get('input', {}),
                                tool_output=tool.get('output', ''),
                                timestamp=datetime.now(),
                                duration_ms=0.0,
                                success=tool.get('success', True)
                            )
                            trace_data.tool_calls.append(tool_call)
        
        # Check if result has tool-like attributes
        elif hasattr(result, '__dict__'):
            attrs = vars(result)
            for attr_name, attr_value in attrs.items():
                if 'tool' in attr_name.lower() or 'action' in attr_name.lower():
                    tool_call = ToolCall(
                        tool_name=attr_name,
                        tool_input={},
                        tool_output=str(attr_value)[:500],
                        timestamp=datetime.now(),
                        duration_ms=0.0,
                        success=True
                    )
                    trace_data.tool_calls.append(tool_call)
    
    def _analyze_result(self, result: Any) -> Dict[str, Any]:
        """Analyze method result for useful information."""
        result_info = {
            'type': type(result).__name__,
            'size': 0,
            'has_error': False
        }
        
        # Estimate size
        try:
            if isinstance(result, (str, list, dict)):
                result_info['size'] = len(result)
            elif hasattr(result, '__len__'):
                result_info['size'] = len(result)
        except:
            pass
        
        # Check for errors
        if isinstance(result, dict):
            if 'error' in result or 'exception' in result:
                result_info['has_error'] = True
        elif isinstance(result, str):
            error_indicators = ['error', 'exception', 'failed', 'traceback']
            if any(indicator in result.lower() for indicator in error_indicators):
                result_info['has_error'] = True
        
        return result_info
    
    def capture_api_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Capture API usage and calculate cost.
        
        Args:
            provider: API provider (openai, anthropic, etc.)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Calculated cost
        """
        cost = self.cost_tracker.calculate_cost(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        logger.debug(f"API cost: ${cost:.4f} for {provider}/{model}")
        return cost 
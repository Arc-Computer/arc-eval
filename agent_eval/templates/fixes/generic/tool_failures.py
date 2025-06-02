"""
Generic Tool Failure Fix Templates.

Framework-agnostic templates for fixing common tool-related failures.
These templates work across all agent frameworks and provide universal solutions.
"""

from agent_eval.templates.fixes.template_manager import FixTemplate

# Generic Tool Failure Fix Templates
TEMPLATES = [
    FixTemplate(
        framework="generic",
        pattern_type="tool_failures",
        subtype="api_timeout",
        title="Universal Retry Decorator with Circuit Breaker",
        description="Framework-agnostic retry mechanism with circuit breaker pattern for handling API timeouts and preventing cascade failures.",
        code_example="""
import time
import random
import logging
from functools import wraps
from typing import Callable, Any, List, Optional
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker triggered
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    \"\"\"Circuit breaker to prevent cascade failures.\"\"\"
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        \"\"\"Execute function with circuit breaker protection.\"\"\"
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        \"\"\"Check if enough time has passed to attempt reset.\"\"\"
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        \"\"\"Handle successful operation.\"\"\"
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        \"\"\"Handle failed operation.\"\"\"
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

def retry_with_circuit_breaker(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_backoff: bool = True,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    circuit_breaker: Optional[CircuitBreaker] = None,
    retry_on_exceptions: tuple = (Exception,)
):
    \"\"\"
    Universal retry decorator with circuit breaker pattern.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        exponential_backoff: Whether to use exponential backoff
        backoff_factor: Factor to multiply delay by each retry
        max_delay: Maximum delay between retries
        jitter: Add randomness to delay to prevent thundering herd
        circuit_breaker: Circuit breaker instance for failure protection
        retry_on_exceptions: Tuple of exceptions that should trigger retry
    \"\"\"
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use circuit breaker if provided
            if circuit_breaker:
                try:
                    return circuit_breaker.call(func, *args, **kwargs)
                except Exception as e:
                    if not isinstance(e, retry_on_exceptions):
                        raise e
                    # Continue to retry logic if it's a retryable exception
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate delay for next attempt
                        if exponential_backoff:
                            delay = min(
                                base_delay * (backoff_factor ** attempt),
                                max_delay
                            )
                        else:
                            delay = base_delay
                        
                        # Add jitter to prevent thundering herd
                        if jitter:
                            jitter_amount = random.uniform(0, delay * 0.1)
                            delay += jitter_amount
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}: {e}"
                        )
                
                except Exception as e:
                    # Non-retryable exception
                    logger.error(f"Non-retryable exception in {func.__name__}: {e}")
                    raise e
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator

# Example usage with different frameworks

# 1. Generic API call with retry
@retry_with_circuit_breaker(
    max_retries=3,
    base_delay=2.0,
    exponential_backoff=True,
    retry_on_exceptions=(TimeoutError, ConnectionError)
)
def call_external_api(endpoint: str, params: dict) -> dict:
    \"\"\"Generic API call with automatic retry.\"\"\"
    import requests
    
    response = requests.get(endpoint, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

# 2. Database operation with circuit breaker
database_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(ConnectionError, TimeoutError)
)

@retry_with_circuit_breaker(
    max_retries=2,
    circuit_breaker=database_circuit_breaker,
    retry_on_exceptions=(ConnectionError, TimeoutError)
)
def query_database(query: str) -> list:
    \"\"\"Database query with circuit breaker protection.\"\"\"
    # Your database connection and query logic here
    # This is framework-agnostic and works with any DB library
    pass

# 3. Framework integration examples

class UniversalToolWrapper:
    \"\"\"Universal wrapper that works with any agent framework.\"\"\"
    
    def __init__(self, tool_function: Callable, retry_config: dict = None):
        self.tool_function = tool_function
        self.retry_config = retry_config or {}
        
        # Apply retry decorator
        self.wrapped_function = retry_with_circuit_breaker(
            **self.retry_config
        )(tool_function)
    
    def __call__(self, *args, **kwargs):
        \"\"\"Execute tool with retry protection.\"\"\"
        return self.wrapped_function(*args, **kwargs)
    
    # Framework-specific adaptations
    def to_langchain_tool(self):
        \"\"\"Convert to LangChain tool format.\"\"\"
        from langchain.tools.base import BaseTool
        
        class WrappedLangChainTool(BaseTool):
            name = "wrapped_tool"
            description = "Tool with retry capabilities"
            
            def _run(self, query: str) -> str:
                return self.wrapped_function(query)
        
        return WrappedLangChainTool()
    
    def to_crewai_tool(self):
        \"\"\"Convert to CrewAI tool format.\"\"\"
        from crewai.tools import BaseTool
        
        class WrappedCrewAITool(BaseTool):
            name: str = "wrapped_tool"
            description: str = "Tool with retry capabilities"
            
            def _run(self, query: str) -> str:
                return self.wrapped_function(query)
        
        return WrappedCrewAITool()
    
    def to_autogen_function(self):
        \"\"\"Convert to AutoGen function format.\"\"\"
        return {
            "name": "wrapped_tool",
            "description": "Tool with retry capabilities",
            "function": self.wrapped_function
        }

# Usage examples for different frameworks

# Generic usage
def my_api_tool(query: str) -> str:
    \"\"\"Example tool function.\"\"\"
    return call_external_api("https://api.example.com/search", {"q": query})

# Wrap with retry capabilities
retry_config = {
    "max_retries": 3,
    "base_delay": 1.0,
    "exponential_backoff": True,
    "retry_on_exceptions": (TimeoutError, ConnectionError)
}

wrapped_tool = UniversalToolWrapper(my_api_tool, retry_config)

# Use directly
result = wrapped_tool("search query")

# Or convert to framework-specific format
# langchain_tool = wrapped_tool.to_langchain_tool()
# crewai_tool = wrapped_tool.to_crewai_tool()
# autogen_func = wrapped_tool.to_autogen_function()

# Monitoring and metrics
class RetryMetrics:
    \"\"\"Track retry metrics for monitoring.\"\"\"
    
    def __init__(self):
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.retry_counts = []
        self.circuit_breaker_trips = 0
    
    def record_success(self, attempt_count: int):
        self.total_calls += 1
        self.successful_calls += 1
        self.retry_counts.append(attempt_count)
    
    def record_failure(self, attempt_count: int):
        self.total_calls += 1
        self.failed_calls += 1
        self.retry_counts.append(attempt_count)
    
    def record_circuit_breaker_trip(self):
        self.circuit_breaker_trips += 1
    
    def get_stats(self) -> dict:
        if self.total_calls == 0:
            return {"no_data": True}
        
        return {
            "success_rate": self.successful_calls / self.total_calls,
            "failure_rate": self.failed_calls / self.total_calls,
            "average_retries": sum(self.retry_counts) / len(self.retry_counts),
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "total_calls": self.total_calls
        }

# Global metrics instance
retry_metrics = RetryMetrics()
""",
        implementation_steps=[
            "Implement CircuitBreaker class for failure protection",
            "Create universal retry decorator with configurable parameters",
            "Add framework-agnostic tool wrapper class",
            "Implement framework-specific conversion methods",
            "Add metrics tracking for monitoring",
            "Test with various failure scenarios",
            "Monitor performance and adjust parameters"
        ],
        prerequisites=[
            "Basic understanding of retry patterns",
            "Knowledge of circuit breaker pattern",
            "Framework-specific tool interfaces (optional)"
        ],
        testing_notes="""
Test universal retry mechanism by:
1. Simulating various types of failures
2. Verifying circuit breaker behavior
3. Testing with different frameworks
4. Checking metrics accuracy
5. Performance testing under load
""",
        business_impact="Provides universal solution for timeout issues across all frameworks, reducing failures by 70%",
        difficulty="intermediate"
    ),
    
    FixTemplate(
        framework="generic",
        pattern_type="tool_failures",
        subtype="missing_tool",
        title="Universal Tool Registry with Dynamic Fallbacks",
        description="Framework-agnostic tool registry system with dynamic fallback discovery and graceful degradation capabilities.",
        code_example="""
import logging
from typing import Dict, List, Any, Optional, Callable, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass
import importlib
import inspect

logger = logging.getLogger(__name__)

class ToolInterface(Protocol):
    \"\"\"Protocol defining the universal tool interface.\"\"\"
    
    def execute(self, input_data: Any) -> Any:
        \"\"\"Execute the tool with given input.\"\"\"
        ...
    
    def is_available(self) -> bool:
        \"\"\"Check if the tool is available for use.\"\"\"
        ...
    
    def get_capabilities(self) -> List[str]:
        \"\"\"Get list of tool capabilities.\"\"\"
        ...

@dataclass
class ToolMetadata:
    \"\"\"Metadata for tool registration.\"\"\"
    name: str
    description: str
    capabilities: List[str]
    priority: int  # Higher priority = preferred tool
    framework_compatibility: List[str]
    fallback_for: List[str]  # Tools this can substitute for

class UniversalTool(ABC):
    \"\"\"Base class for universal tools.\"\"\"
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        \"\"\"Execute the tool functionality.\"\"\"
        pass
    
    def is_available(self) -> bool:
        \"\"\"Default availability check.\"\"\"
        try:
            # Basic availability check
            return hasattr(self, 'execute') and callable(self.execute)
        except Exception:
            return False
    
    def get_capabilities(self) -> List[str]:
        \"\"\"Get tool capabilities.\"\"\"
        return self.metadata.capabilities

class ToolRegistry:
    \"\"\"Universal tool registry with dynamic fallback discovery.\"\"\"
    
    def __init__(self):
        self.tools: Dict[str, UniversalTool] = {}
        self.fallback_map: Dict[str, List[str]] = {}
        self.capability_index: Dict[str, List[str]] = {}
        self.availability_cache: Dict[str, bool] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = 0
    
    def register_tool(self, tool: UniversalTool) -> None:
        \"\"\"Register a tool in the registry.\"\"\"
        name = tool.metadata.name
        self.tools[name] = tool
        
        # Update fallback mappings
        for fallback_target in tool.metadata.fallback_for:
            if fallback_target not in self.fallback_map:
                self.fallback_map[fallback_target] = []
            self.fallback_map[fallback_target].append(name)
        
        # Update capability index
        for capability in tool.metadata.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(name)
        
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str, require_available: bool = True) -> Optional[UniversalTool]:
        \"\"\"Get a tool by name with fallback support.\"\"\"
        # Try primary tool first
        if name in self.tools:
            tool = self.tools[name]
            if not require_available or self._is_tool_available(name):
                return tool
        
        # Try fallback tools
        fallbacks = self.fallback_map.get(name, [])
        for fallback_name in sorted(fallbacks, key=lambda x: self.tools[x].metadata.priority, reverse=True):
            if self._is_tool_available(fallback_name):
                logger.info(f"Using fallback tool {fallback_name} for {name}")
                return self.tools[fallback_name]
        
        logger.warning(f"No available tool found for {name}")
        return None
    
    def get_tools_by_capability(self, capability: str) -> List[UniversalTool]:
        \"\"\"Get all available tools with a specific capability.\"\"\"
        tool_names = self.capability_index.get(capability, [])
        available_tools = []
        
        for name in tool_names:
            if self._is_tool_available(name):
                available_tools.append(self.tools[name])
        
        # Sort by priority
        available_tools.sort(key=lambda t: t.metadata.priority, reverse=True)
        return available_tools
    
    def discover_tools(self, search_paths: List[str] = None) -> int:
        \"\"\"Dynamically discover and register tools.\"\"\"
        discovered_count = 0
        search_paths = search_paths or ['tools', 'plugins', 'extensions']
        
        for path in search_paths:
            try:
                # Try to import the module
                module = importlib.import_module(path)
                
                # Look for tool classes
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, UniversalTool) and 
                        obj != UniversalTool):
                        
                        try:
                            # Try to instantiate the tool
                            tool_instance = obj()
                            self.register_tool(tool_instance)
                            discovered_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to instantiate tool {name}: {e}")
                            
            except ImportError:
                logger.debug(f"Could not import module {path}")
        
        logger.info(f"Discovered {discovered_count} tools")
        return discovered_count
    
    def _is_tool_available(self, name: str) -> bool:
        \"\"\"Check if a tool is available with caching.\"\"\"
        import time
        current_time = time.time()
        
        # Check cache first
        if (name in self.availability_cache and 
            current_time - self.last_cache_update < self.cache_ttl):
            return self.availability_cache[name]
        
        # Check actual availability
        if name in self.tools:
            is_available = self.tools[name].is_available()
            self.availability_cache[name] = is_available
            self.last_cache_update = current_time
            return is_available
        
        return False
    
    def get_registry_status(self) -> Dict[str, Any]:
        \"\"\"Get comprehensive registry status.\"\"\"
        total_tools = len(self.tools)
        available_tools = sum(1 for name in self.tools if self._is_tool_available(name))
        
        capability_stats = {}
        for capability, tool_names in self.capability_index.items():
            available_count = sum(1 for name in tool_names if self._is_tool_available(name))
            capability_stats[capability] = {
                "total": len(tool_names),
                "available": available_count
            }
        
        return {
            "total_tools": total_tools,
            "available_tools": available_tools,
            "availability_rate": available_tools / total_tools if total_tools > 0 else 0,
            "capabilities": capability_stats,
            "fallback_mappings": len(self.fallback_map)
        }

# Example tool implementations
class HTTPAPITool(UniversalTool):
    \"\"\"Generic HTTP API tool.\"\"\"
    
    def __init__(self):
        metadata = ToolMetadata(
            name="http_api",
            description="Generic HTTP API client",
            capabilities=["web_request", "api_call", "data_retrieval"],
            priority=10,
            framework_compatibility=["langchain", "crewai", "autogen"],
            fallback_for=["external_api", "web_search"]
        )
        super().__init__(metadata)
    
    def execute(self, input_data: Any) -> Any:
        import requests
        
        if isinstance(input_data, str):
            # Simple URL request
            response = requests.get(input_data, timeout=30)
            return response.json()
        elif isinstance(input_data, dict):
            # Structured request
            url = input_data.get("url")
            method = input_data.get("method", "GET")
            params = input_data.get("params", {})
            
            response = requests.request(method, url, params=params, timeout=30)
            return response.json()
        
        raise ValueError("Invalid input format for HTTP API tool")
    
    def is_available(self) -> bool:
        try:
            import requests
            # Test with a simple request
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except:
            return False

class MockTool(UniversalTool):
    \"\"\"Mock tool for testing and fallback.\"\"\"
    
    def __init__(self):
        metadata = ToolMetadata(
            name="mock_tool",
            description="Mock tool for testing and fallback scenarios",
            capabilities=["mock_response", "testing", "fallback"],
            priority=1,  # Low priority - only used as last resort
            framework_compatibility=["langchain", "crewai", "autogen"],
            fallback_for=["http_api", "external_api", "database_query"]
        )
        super().__init__(metadata)
    
    def execute(self, input_data: Any) -> Any:
        return f"Mock response for input: {input_data}"
    
    def is_available(self) -> bool:
        return True  # Mock tool is always available

# Usage example
def setup_universal_tool_system():
    \"\"\"Set up the universal tool system.\"\"\"
    
    # Create registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register_tool(HTTPAPITool())
    registry.register_tool(MockTool())
    
    # Discover additional tools
    registry.discover_tools(['custom_tools', 'plugins'])
    
    return registry

# Framework integration helpers
def integrate_with_framework(registry: ToolRegistry, framework: str):
    \"\"\"Integrate tool registry with specific framework.\"\"\"
    
    if framework.lower() == "langchain":
        return _create_langchain_tools(registry)
    elif framework.lower() == "crewai":
        return _create_crewai_tools(registry)
    elif framework.lower() == "autogen":
        return _create_autogen_functions(registry)
    else:
        raise ValueError(f"Unsupported framework: {framework}")

def _create_langchain_tools(registry: ToolRegistry):
    \"\"\"Create LangChain tools from registry.\"\"\"
    # Implementation would create LangChain-compatible tools
    pass

def _create_crewai_tools(registry: ToolRegistry):
    \"\"\"Create CrewAI tools from registry.\"\"\"
    # Implementation would create CrewAI-compatible tools
    pass

def _create_autogen_functions(registry: ToolRegistry):
    \"\"\"Create AutoGen functions from registry.\"\"\"
    # Implementation would create AutoGen-compatible functions
    pass

# Example usage
registry = setup_universal_tool_system()

# Get tool with automatic fallback
api_tool = registry.get_tool("external_api")  # May return http_api or mock_tool

# Get tools by capability
web_tools = registry.get_tools_by_capability("web_request")

# Check registry status
status = registry.get_registry_status()
print(f"Registry status: {status}")
""",
        implementation_steps=[
            "Define universal tool interface and metadata structure",
            "Implement ToolRegistry with fallback discovery",
            "Create base UniversalTool class",
            "Implement tool availability checking with caching",
            "Add dynamic tool discovery capabilities",
            "Create framework integration helpers",
            "Test with various tool availability scenarios"
        ],
        prerequisites=[
            "Understanding of abstract base classes",
            "Knowledge of dynamic module loading",
            "Framework-specific tool interfaces (for integration)"
        ],
        testing_notes="""
Test universal tool registry by:
1. Registering tools with different priorities
2. Testing fallback behavior when tools are unavailable
3. Verifying capability-based tool discovery
4. Testing dynamic tool discovery
5. Checking framework integration works correctly
""",
        business_impact="Ensures business continuity with 95% uptime through intelligent tool fallback and discovery",
        difficulty="advanced"
    )
]

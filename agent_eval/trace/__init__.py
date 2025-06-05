"""
ARC-Eval Runtime Tracing Module.

Provides comprehensive agent monitoring and observability capabilities with
OpenTelemetry integration for both custom analysis and standard observability.

Key Components:
- ArcTracer: Main one-line agent monitoring wrapper
- OTelArcTracer: OpenTelemetry-powered hybrid tracer
- TracedAgent: Wrapper for instrumented agents
- Semantic conventions for agent-specific attributes

Example Usage:
    from agent_eval.trace import ArcTracer
    
    # Custom monitoring (current)
    tracer = ArcTracer("finance")
    agent = tracer.trace_agent(your_agent)
    
    # Hybrid OTel monitoring (new)
    from agent_eval.trace import OTelArcTracer
    tracer = OTelArcTracer("finance", enable_otlp=True)
    agent = tracer.trace_agent(your_agent)
"""

from .tracer import ArcTracer, TracedAgent
from .types import (
    TraceData,
    ExecutionStep,
    ToolCall,
    TraceEventType,
    ReliabilityScore,
    AgentMetrics,
    CostData,
    FailureInfo,
    DashboardData
)
from .capture import TraceCapture
from .storage import TraceStorage
from .cost_tracker import CostTracker
from .sanitizer import TraceSanitizer, RedactionRule, create_sanitizer

# Import semantic conventions (always available)
from .semantic_conventions import (
    AgentAttributes, ToolAttributes, ScenarioAttributes,
    LLMAttributes, DomainAttributes, PerformanceAttributes,
    validate_agent_framework, validate_domain, validate_severity,
    AgentFrameworks, AgentDomains, SeverityLevels
)

# First check if OpenTelemetry core packages are available
try:
    import opentelemetry.trace
    import opentelemetry.sdk.trace
    import opentelemetry.sdk.trace.export
    import opentelemetry.exporter.otlp.proto.grpc.trace_exporter
    import opentelemetry.exporter.jaeger.thrift
    import opentelemetry.instrumentation.instrumentor
    import opentelemetry.util.types
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False

# Only import our OpenTelemetry components if core packages are available
if _OTEL_AVAILABLE:
    try:
        from .otel_tracer import OTelArcTracer, AgentSpan, create_hybrid_tracer
    except ImportError:
        _OTEL_AVAILABLE = False
else:
    # Provide stub classes for graceful degradation
    class OTelArcTracer:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenTelemetry not available. Install with: pip install 'arc-eval[otel]'")
    
    class AgentSpan:
        pass
    
    def create_hybrid_tracer(*args, **kwargs):
        return ArcTracer(*args, **kwargs)

__all__ = [
    # Core tracing
    "ArcTracer",
    "TracedAgent",
    "TraceCapture",
    "TraceStorage",
    "CostTracker",
    
    # Data types
    "TraceData",
    "ExecutionStep", 
    "ToolCall",
    "TraceEventType",
    "ReliabilityScore",
    "AgentMetrics",
    "CostData",
    "FailureInfo",
    "DashboardData",
    
    # Sanitization
    "TraceSanitizer",
    "RedactionRule",
    "create_sanitizer",
    
    # Semantic conventions (always available)
    "AgentAttributes",
    "ToolAttributes", 
    "ScenarioAttributes",
    "LLMAttributes",
    "DomainAttributes",
    "PerformanceAttributes",
    "validate_agent_framework",
    "validate_domain",
    "validate_severity",
    "AgentFrameworks",
    "AgentDomains",
    "SeverityLevels",
    
    # OpenTelemetry (if available)
    "OTelArcTracer",
    "AgentSpan",
    "create_hybrid_tracer",
]

# Version and compatibility info
__version__ = "0.2.9"
OTEL_AVAILABLE = _OTEL_AVAILABLE 
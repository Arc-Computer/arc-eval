"""
OpenTelemetry-powered hybrid tracer for ARC-Eval.

Provides OpenTelemetry integration while preserving custom analysis capabilities.
Implements dual export strategy for both standard observability and custom analysis.
"""

import os
import uuid
import logging
import time
import threading
from datetime import datetime
from typing import Any, Optional, Dict, List, Union
from functools import wraps
from contextlib import contextmanager

# OpenTelemetry imports with graceful fallback
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
    from opentelemetry.trace import Status, StatusCode, SpanKind
    from opentelemetry.util.types import Attributes
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    # Stub classes for graceful degradation
    class TracerProvider:
        pass
    trace = None

from .tracer import ArcTracer, TracedAgent
from .types import TraceData, ExecutionStep, TraceEventType, ReliabilityScore, AgentMetrics
from .capture import TraceCapture
from .storage import TraceStorage
from .cost_tracker import CostTracker
from .sanitizer import RedactionRule
from .semantic_conventions import (
    AgentAttributes, ToolAttributes, ScenarioAttributes, LLMAttributes,
    DomainAttributes, PerformanceAttributes, validate_agent_framework,
    validate_domain, AgentFrameworks
)

logger = logging.getLogger(__name__)


class AgentSpan:
    """Enhanced span wrapper with agent-specific functionality."""
    
    def __init__(self, otel_span, domain: str = "general", tracer=None):
        self.otel_span = otel_span
        self.domain = domain
        self.tracer = tracer  # Store tracer reference
        self._reasoning_steps = []
        self._tool_calls = []
        self._scenario_context = {}
        
    def set_agent_attribute(self, key: str, value: Any) -> 'AgentSpan':
        """Set agent-specific attribute on span."""
        if self.otel_span:
            self.otel_span.set_attribute(key, value)
        return self
        
    def add_reasoning_step(self, step: str, step_type: str = "reasoning") -> 'AgentSpan':
        """Add a reasoning step to the agent span."""
        reasoning_step = {
            "step": step,
            "type": step_type,
            "timestamp": datetime.now().isoformat()
        }
        self._reasoning_steps.append(reasoning_step)
        
        if self.otel_span:
            # Add as span event
            self.otel_span.add_event(
                f"reasoning.{step_type}",
                attributes={
                    "reasoning.step": step,
                    "reasoning.type": step_type
                }
            )
        return self
        
    def add_tool_call(self, tool_name: str, tool_input: Dict, tool_output: Any, 
                      success: bool = True, duration_ms: float = 0.0) -> 'AgentSpan':
        """Add tool call information to span."""
        tool_call = {
            "name": tool_name,
            "input": str(tool_input)[:200],  # Truncate for storage
            "output": str(tool_output)[:200],
            "success": success,
            "duration_ms": duration_ms,
            "input_size": len(str(tool_input)),
            "output_size": len(str(tool_output)),
            "timestamp": datetime.now().isoformat()
        }
        self._tool_calls.append(tool_call)
        
        if self.otel_span and self.tracer:
            # Create child span for tool call
            with self.tracer.start_as_current_span(
                f"tool.{tool_name}",
                kind=SpanKind.CLIENT
            ) as tool_span:
                tool_span.set_attribute(ToolAttributes.TOOL_NAME, tool_name)
                tool_span.set_attribute(ToolAttributes.TOOL_SUCCESS, success)
                tool_span.set_attribute(ToolAttributes.TOOL_INPUT_SIZE, tool_call["input_size"])
                tool_span.set_attribute(ToolAttributes.TOOL_OUTPUT_SIZE, tool_call["output_size"])
                tool_span.set_attribute(ToolAttributes.TOOL_LATENCY_MS, duration_ms)
                
                if not success:
                    tool_span.set_status(Status(StatusCode.ERROR, "Tool call failed"))
                    
        return self
        
    def set_scenario_context(self, scenario_id: str, scenario_type: str = None, 
                           severity: str = None, compliance_frameworks: List[str] = None) -> 'AgentSpan':
        """Set scenario evaluation context."""
        self._scenario_context = {
            "id": scenario_id,
            "type": scenario_type,
            "severity": severity,
            "compliance_frameworks": compliance_frameworks or []
        }
        
        if self.otel_span:
            self.otel_span.set_attribute(ScenarioAttributes.SCENARIO_ID, scenario_id)
            if scenario_type:
                self.otel_span.set_attribute(ScenarioAttributes.SCENARIO_TYPE, scenario_type)
            if severity:
                self.otel_span.set_attribute(ScenarioAttributes.SCENARIO_SEVERITY, severity)
            if compliance_frameworks:
                self.otel_span.set_attribute(
                    ScenarioAttributes.SCENARIO_COMPLIANCE_FRAMEWORKS, 
                    ",".join(compliance_frameworks)
                )
                
        return self
        
    def set_performance_metrics(self, duration_ms: float, memory_mb: float = None, 
                              cpu_percent: float = None) -> 'AgentSpan':
        """Set performance metrics on the span."""
        if self.otel_span:
            self.otel_span.set_attribute(PerformanceAttributes.PERFORMANCE_DURATION_MS, duration_ms)
            if memory_mb is not None:
                self.otel_span.set_attribute(PerformanceAttributes.PERFORMANCE_MEMORY_USAGE_MB, memory_mb)
            if cpu_percent is not None:
                self.otel_span.set_attribute(PerformanceAttributes.PERFORMANCE_CPU_USAGE_PERCENT, cpu_percent)
        return self
        
    def mark_error(self, error: str, error_type: str = "agent_error") -> 'AgentSpan':
        """Mark span as having an error."""
        if self.otel_span:
            self.otel_span.set_status(Status(StatusCode.ERROR, error))
            self.otel_span.set_attribute(AgentAttributes.AGENT_ERROR_TYPE, error_type)
            self.otel_span.set_attribute(AgentAttributes.AGENT_SUCCESS, False)
        return self
        
    def mark_success(self) -> 'AgentSpan':
        """Mark span as successful."""
        if self.otel_span:
            self.otel_span.set_attribute(AgentAttributes.AGENT_SUCCESS, True)
        return self
        
    def end(self) -> None:
        """End the span."""
        if self.otel_span:
            self.otel_span.end()


class HybridSpanProcessor:
    """Span processor that routes data to both OTel exporters and custom storage."""
    
    def __init__(self, custom_storage: TraceStorage, cost_tracker: CostTracker):
        self.custom_storage = custom_storage
        self.cost_tracker = cost_tracker
        
    def on_start(self, span, parent_context=None):
        """Called when span starts."""
        pass
        
    def on_end(self, span):
        """Called when span ends - convert to custom format and store."""
        try:
            # Convert OTel span to custom TraceData format
            trace_data = self._convert_span_to_trace_data(span)
            
            # Store in custom storage for analysis systems
            self.custom_storage.store_trace(trace_data)
            
        except Exception as e:
            logger.error(f"Failed to process span in hybrid processor: {e}")
    
    def shutdown(self):
        """Shutdown the processor - required by OpenTelemetry."""
        logger.info("HybridSpanProcessor shutdown")
        
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush the processor - required by OpenTelemetry."""
        logger.debug("HybridSpanProcessor force flush")
        return True
            
    def _convert_span_to_trace_data(self, span) -> TraceData:
        """Convert OpenTelemetry span to custom TraceData format."""
        attributes = dict(span.attributes) if span.attributes else {}
        
        # Extract agent information
        agent_id = attributes.get(AgentAttributes.AGENT_ID, "unknown")
        session_id = attributes.get(AgentAttributes.AGENT_SESSION_ID, str(uuid.uuid4()))
        framework = attributes.get(AgentAttributes.AGENT_FRAMEWORK, "generic")
        
        # Create custom TraceData
        trace_data = TraceData(
            trace_id=str(span.context.trace_id),
            agent_id=agent_id,
            session_id=session_id,
            start_time=datetime.fromtimestamp(span.start_time / 1_000_000_000),
            end_time=datetime.fromtimestamp(span.end_time / 1_000_000_000) if span.end_time else None,
            framework=framework,
            success=attributes.get(AgentAttributes.AGENT_SUCCESS, True),
            error=span.status.description if span.status.status_code == StatusCode.ERROR else None,
            metadata=attributes
        )
        
        # Add execution steps (simplified from span events)
        if hasattr(span, 'events'):
            for event in span.events:
                step = ExecutionStep(
                    step_id=str(uuid.uuid4()),
                    event_type=TraceEventType.PERFORMANCE,
                    timestamp=datetime.fromtimestamp(event.timestamp / 1_000_000_000),
                    duration_ms=0.0,
                    data=dict(event.attributes) if event.attributes else {}
                )
                trace_data.execution_timeline.append(step)
                
        return trace_data


class OTelArcTracer:
    """OpenTelemetry-powered hybrid tracer for ARC-Eval.
    
    Provides standard OpenTelemetry tracing with custom agent analysis capabilities.
    Implements dual export strategy for both observability tools and analysis systems.
    """
    
    def __init__(self, 
                 domain: str = "general",
                 agent_id: Optional[str] = None,
                 enable_otlp: bool = False,
                 otlp_endpoint: Optional[str] = None,
                 enable_jaeger: bool = False,
                 jaeger_endpoint: Optional[str] = None,
                 enable_console: bool = False,
                 custom_rules: Optional[List[RedactionRule]] = None,
                 service_name: str = "arc-eval-agent"):
        """Initialize OTel hybrid tracer.
        
        Args:
            domain: Domain for specialized monitoring
            agent_id: Unique identifier for the agent
            enable_otlp: Enable OTLP exporter for standard observability
            otlp_endpoint: OTLP endpoint URL
            enable_jaeger: Enable Jaeger exporter
            jaeger_endpoint: Jaeger endpoint URL
            enable_console: Enable console output for debugging
            custom_rules: Custom sanitization rules
            service_name: Service name for telemetry
        """
        if not _OTEL_AVAILABLE:
            raise ImportError(
                "OpenTelemetry not available. Install with: pip install 'arc-eval[otel]' or install dependencies manually"
            )
            
        self.domain = validate_domain(domain)
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.service_name = service_name
        self.is_monitoring = False
        self.custom_rules = custom_rules or []
        
        # Initialize custom components (for backward compatibility)
        self.storage = TraceStorage()
        self.cost_tracker = CostTracker()
        self.capture = TraceCapture(domain=domain, custom_rules=self.custom_rules)
        
        # Initialize OpenTelemetry
        self._setup_otel_tracing(
            enable_otlp=enable_otlp,
            otlp_endpoint=otlp_endpoint,
            enable_jaeger=enable_jaeger, 
            jaeger_endpoint=jaeger_endpoint,
            enable_console=enable_console
        )
        
        # Metrics tracking (backward compatibility)
        self._current_metrics: Optional[AgentMetrics] = None
        self._metrics_lock = threading.Lock()
        
        logger.info(f"OTel hybrid tracer initialized for agent '{self.agent_id}' in domain '{self.domain}'")
    
    def _setup_otel_tracing(self, enable_otlp: bool, otlp_endpoint: Optional[str],
                           enable_jaeger: bool, jaeger_endpoint: Optional[str], 
                           enable_console: bool):
        """Setup OpenTelemetry tracing with exporters."""
        # Create tracer provider
        self.tracer_provider = TracerProvider()
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        # Setup exporters
        exporters = []
        
        # OTLP exporter for standard observability backends
        if enable_otlp:
            endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
                exporters.append(otlp_exporter)
                logger.info(f"OTLP exporter configured for {endpoint}")
            except Exception as e:
                logger.warning(f"Failed to setup OTLP exporter: {e}")
        
        # Jaeger exporter
        if enable_jaeger:
            endpoint = jaeger_endpoint or os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
            try:
                jaeger_exporter = JaegerExporter(endpoint=endpoint)
                exporters.append(jaeger_exporter)
                logger.info(f"Jaeger exporter configured for {endpoint}")
            except Exception as e:
                logger.warning(f"Failed to setup Jaeger exporter: {e}")
        
        # Console exporter for debugging
        if enable_console or os.getenv("OTEL_CONSOLE_EXPORTER", "false").lower() == "true":
            console_exporter = ConsoleSpanExporter()
            exporters.append(console_exporter)
            logger.info("Console exporter enabled")
        
        # Add batch processors for each exporter
        for exporter in exporters:
            processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(processor)
        
        # Add hybrid processor for custom storage
        hybrid_processor = HybridSpanProcessor(self.storage, self.cost_tracker)
        self.tracer_provider.add_span_processor(hybrid_processor)
        
        logger.info(f"OpenTelemetry configured with {len(exporters)} exporters + hybrid processor")
    
    @contextmanager
    def start_agent_span(self, operation_name: str, **span_kwargs):
        """Start an agent span with automatic attribute setting."""
        with self.tracer.start_as_current_span(
            operation_name,
            kind=SpanKind.SERVER,
            **span_kwargs
        ) as span:
            # Set standard agent attributes
            span.set_attribute(AgentAttributes.AGENT_ID, self.agent_id)
            span.set_attribute(AgentAttributes.AGENT_DOMAIN, self.domain)
            span.set_attribute(AgentAttributes.AGENT_SESSION_ID, str(uuid.uuid4()))
            span.set_attribute("service.name", self.service_name)
            
            # Yield enhanced span with tracer reference
            agent_span = AgentSpan(span, self.domain, self.tracer)
            yield agent_span
    
    def trace_agent(self, agent: Any) -> 'OTelTracedAgent':
        """Wrap an agent with OTel monitoring capabilities."""
        if not self.is_monitoring:
            self.start_monitoring()
        
        traced_agent = OTelTracedAgent(agent, self)
        logger.info(f"Agent wrapped for OTel tracing: {type(agent).__name__}")
        
        return traced_agent
    
    def start_monitoring(self) -> None:
        """Start monitoring session."""
        self.is_monitoring = True
        
        # Initialize metrics (backward compatibility)
        existing_metrics = self.storage.get_agent_metrics(self.agent_id)
        if existing_metrics:
            self._current_metrics = existing_metrics
        else:
            self._current_metrics = AgentMetrics(
                agent_id=self.agent_id,
                total_runs=0,
                success_rate=1.0,
                avg_duration_ms=0.0,
                total_cost=0.0,
                reliability_score=ReliabilityScore(
                    score=100.0,
                    grade="A+",
                    trend="→"
                )
            )
        
        logger.info(f"OTel monitoring started for agent '{self.agent_id}'")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring session."""
        self.is_monitoring = False
        
        # Save final metrics
        if self._current_metrics:
            self.storage.update_agent_metrics(self._current_metrics)
        
        logger.info(f"OTel monitoring stopped for agent '{self.agent_id}'")
    
    def get_reliability_score(self) -> ReliabilityScore:
        """Get current reliability score for the agent."""
        if self._current_metrics:
            return self._current_metrics.reliability_score
        
        return ReliabilityScore(score=100.0, grade="A+", trend="→")
    
    def get_agent_metrics(self) -> Optional[AgentMetrics]:
        """Get current agent metrics."""
        return self._current_metrics


class OTelTracedAgent:
    """OpenTelemetry-powered traced agent wrapper."""
    
    def __init__(self, original_agent: Any, tracer: OTelArcTracer):
        self.original_agent = original_agent
        self.tracer = tracer
        self._agent_id = tracer.agent_id
        self._session_id = str(uuid.uuid4())
        
        # Wrap common agent methods
        self._wrap_agent_methods()
    
    def _wrap_agent_methods(self):
        """Wrap common agent execution methods with OTel spans."""
        method_names = ['run', 'invoke', 'execute', 'call', '__call__', 'predict', 'generate']
        
        for method_name in method_names:
            if hasattr(self.original_agent, method_name):
                original_method = getattr(self.original_agent, method_name)
                wrapped_method = self._wrap_method(original_method, method_name)
                setattr(self, method_name, wrapped_method)
    
    def _wrap_method(self, method, method_name: str):
        """Wrap a method with OTel tracing."""
        @wraps(method)
        def wrapper(*args, **kwargs):
            with self.tracer.start_agent_span(f"agent.{method_name}") as agent_span:
                start_time = time.time()
                
                try:
                    # Set framework detection
                    framework = validate_agent_framework(
                        self.tracer.capture.detect_framework(self.original_agent)
                    )
                    agent_span.set_agent_attribute(AgentAttributes.AGENT_FRAMEWORK, framework)
                    agent_span.set_agent_attribute(AgentAttributes.AGENT_EXECUTION_TYPE, method_name)
                    
                    # Execute original method
                    result = method(*args, **kwargs)
                    
                    # Calculate performance metrics
                    duration_ms = (time.time() - start_time) * 1000
                    agent_span.set_performance_metrics(duration_ms)
                    agent_span.mark_success()
                    
                    # Update custom metrics (backward compatibility)
                    self.tracer._update_metrics_success(duration_ms)
                    
                    return result
                    
                except Exception as e:
                    # Calculate duration for failed execution
                    duration_ms = (time.time() - start_time) * 1000
                    agent_span.set_performance_metrics(duration_ms)
                    agent_span.mark_error(str(e), type(e).__name__)
                    
                    # Update custom metrics (backward compatibility)
                    self.tracer._update_metrics_failure(duration_ms)
                    
                    raise
        
        return wrapper
    
    def __getattr__(self, name):
        """Delegate attribute access to original agent."""
        return getattr(self.original_agent, name)


# Utility functions for backward compatibility
def create_hybrid_tracer(domain: str = "general", **kwargs) -> Union[OTelArcTracer, ArcTracer]:
    """Create a tracer based on OpenTelemetry availability."""
    if _OTEL_AVAILABLE and kwargs.get('enable_otel', True):
        # Filter out enable_otel parameter as it's not expected by OTelArcTracer
        otel_kwargs = {k: v for k, v in kwargs.items() if k != 'enable_otel'}
        return OTelArcTracer(domain=domain, **otel_kwargs)
    else:
        # Fallback to custom tracer
        return ArcTracer(domain=domain)


# Add backward compatibility methods to OTelArcTracer
def _add_backward_compatibility_methods(cls):
    """Add methods for backward compatibility with existing ArcTracer interface."""
    
    def _update_metrics_success(self, duration_ms: float):
        """Update metrics for successful execution."""
        if not self._current_metrics:
            return
            
        with self._metrics_lock:
            self._current_metrics.total_runs += 1
            
            # Update success rate
            old_successes = int(self._current_metrics.success_rate * (self._current_metrics.total_runs - 1))
            new_successes = old_successes + 1
            self._current_metrics.success_rate = new_successes / self._current_metrics.total_runs
            
            # Update average duration
            old_total_duration = self._current_metrics.avg_duration_ms * (self._current_metrics.total_runs - 1)
            new_total_duration = old_total_duration + duration_ms
            self._current_metrics.avg_duration_ms = new_total_duration / self._current_metrics.total_runs
    
    def _update_metrics_failure(self, duration_ms: float):
        """Update metrics for failed execution."""
        if not self._current_metrics:
            return
            
        with self._metrics_lock:
            self._current_metrics.total_runs += 1
            
            # Update success rate (no increment to successes)
            old_successes = int(self._current_metrics.success_rate * (self._current_metrics.total_runs - 1))
            self._current_metrics.success_rate = old_successes / self._current_metrics.total_runs
            
            # Update average duration
            old_total_duration = self._current_metrics.avg_duration_ms * (self._current_metrics.total_runs - 1)
            new_total_duration = old_total_duration + duration_ms
            self._current_metrics.avg_duration_ms = new_total_duration / self._current_metrics.total_runs
    
    # Add methods to class
    cls._update_metrics_success = _update_metrics_success
    cls._update_metrics_failure = _update_metrics_failure

# Apply backward compatibility
_add_backward_compatibility_methods(OTelArcTracer) 
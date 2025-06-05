"""
ArcTracer: One-line agent monitoring wrapper.

Main entry point for runtime tracing functionality.
"""

import os
import uuid
import logging
import time
import threading
from datetime import datetime
from typing import Any, Optional, Dict, Callable, List
from functools import wraps

from .types import TraceData, ExecutionStep, TraceEventType, ReliabilityScore, AgentMetrics
from .capture import TraceCapture
from .storage import TraceStorage
from .cost_tracker import CostTracker
from .sanitizer import RedactionRule

logger = logging.getLogger(__name__)


class TracedAgent:
    """Wrapper for any agent framework with monitoring capabilities."""
    
    def __init__(self, original_agent: Any, tracer: 'ArcTracer'):
        self.original_agent = original_agent
        self.tracer = tracer
        self._agent_id = tracer.agent_id
        self._session_id = str(uuid.uuid4())
        
        # Wrap common agent methods
        self._wrap_agent_methods()
    
    def _wrap_agent_methods(self):
        """Wrap common agent execution methods."""
        # Common method names across frameworks
        method_names = ['run', 'invoke', 'execute', 'call', '__call__', 'predict', 'generate']
        
        for method_name in method_names:
            if hasattr(self.original_agent, method_name):
                original_method = getattr(self.original_agent, method_name)
                wrapped_method = self._wrap_method(original_method, method_name)
                setattr(self, method_name, wrapped_method)
    
    def _wrap_method(self, method: Callable, method_name: str) -> Callable:
        """Wrap a method with tracing."""
        @wraps(method)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Create trace data
            trace_data = TraceData(
                trace_id=trace_id,
                agent_id=self._agent_id,
                session_id=self._session_id,
                start_time=start_time,
                framework=self.tracer.capture.detect_framework(self.original_agent)
            )
            
            try:
                # Start execution step - sanitize input data
                sanitized_args = self.tracer.capture.sanitizer.sanitize_string(str(args)[:200])
                sanitized_kwargs = self.tracer.capture.sanitizer.sanitize_dict(
                    {k: str(v)[:100] for k, v in kwargs.items()}
                )
                
                start_step = ExecutionStep(
                    step_id=str(uuid.uuid4()),
                    event_type=TraceEventType.AGENT_START,
                    timestamp=start_time,
                    duration_ms=0.0,
                    data={
                        'method': method_name,
                        'args': sanitized_args,
                        'kwargs': sanitized_kwargs
                    }
                )
                trace_data.execution_timeline.append(start_step)
                
                # Execute original method with monitoring
                result = self.tracer.capture.capture_execution(
                    method, trace_data, *args, **kwargs
                )
                
                # Mark as successful
                trace_data.success = True
                trace_data.end_time = datetime.now()
                
                # End execution step - sanitize result
                sanitized_result = self.tracer.capture.sanitizer.sanitize_string(str(result)[:200])
                end_step = ExecutionStep(
                    step_id=str(uuid.uuid4()),
                    event_type=TraceEventType.AGENT_END,
                    timestamp=trace_data.end_time,
                    duration_ms=trace_data.duration_ms,
                    data={'result': sanitized_result}
                )
                trace_data.execution_timeline.append(end_step)
                
                # Store trace and update metrics
                self.tracer.storage.store_trace(trace_data)
                self.tracer._update_metrics(trace_data)
                
                return result
                
            except Exception as e:
                # Handle errors
                trace_data.success = False
                trace_data.error = str(e)
                trace_data.end_time = datetime.now()
                
                # Sanitize error information
                sanitized_error = self.tracer.capture.sanitizer.sanitize_string(str(e))
                error_step = ExecutionStep(
                    step_id=str(uuid.uuid4()),
                    event_type=TraceEventType.ERROR,
                    timestamp=trace_data.end_time,
                    duration_ms=trace_data.duration_ms,
                    data={'error': sanitized_error},
                    error=sanitized_error
                )
                trace_data.execution_timeline.append(error_step)
                
                # Store failed trace
                self.tracer.storage.store_trace(trace_data)
                self.tracer._update_metrics(trace_data)
                
                raise
        
        return wrapper
    
    def __getattr__(self, name):
        """Delegate attribute access to original agent."""
        return getattr(self.original_agent, name)


class ArcTracer:
    """Main tracer class for one-line agent monitoring."""
    
    def __init__(self, domain: str = "general", agent_id: Optional[str] = None, api_key: Optional[str] = None, custom_rules: Optional[List[RedactionRule]] = None):
        """Initialize tracer with domain context.
        
        Args:
            domain: Domain for specialized monitoring (finance, security, ml)
            agent_id: Unique identifier for the agent (auto-generated if None)
            api_key: API key for trace submission (reads from env if not provided)
            custom_rules: Additional custom redaction rules for sanitization
        """
        self.domain = domain
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.api_key = api_key or os.getenv("ARC_API_KEY", "development-key-change-in-production")
        self.is_monitoring = False
        self.custom_rules = custom_rules or []
        
        # Check if sanitization should be disabled (default: enabled)
        enable_sanitization = os.getenv("ARC_ENABLE_SANITIZATION", "true").lower() != "false"
        
        # Initialize components
        self.capture = TraceCapture(domain=domain, enable_sanitization=enable_sanitization, custom_rules=self.custom_rules)
        self.storage = TraceStorage()
        self.cost_tracker = CostTracker()
        
        # Metrics tracking
        self._current_metrics: Optional[AgentMetrics] = None
        self._metrics_lock = threading.Lock()
        
        logger.info(f"ArcTracer initialized for domain '{domain}', agent_id '{self.agent_id}'")
    
    def trace_agent(self, agent: Any) -> TracedAgent:
        """Wrap an agent with monitoring capabilities.
        
        Args:
            agent: Agent instance from any framework
            
        Returns:
            TracedAgent: Wrapped agent with monitoring
        """
        if not self.is_monitoring:
            self.start_monitoring()
        
        traced_agent = TracedAgent(agent, self)
        logger.info(f"Agent wrapped for tracing: {type(agent).__name__}")
        
        return traced_agent
    
    def start_monitoring(self) -> None:
        """Start monitoring session."""
        self.is_monitoring = True
        
        # Initialize metrics if not exists
        existing_metrics = self.storage.get_agent_metrics(self.agent_id)
        if existing_metrics:
            self._current_metrics = existing_metrics
        else:
            # Create initial metrics
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
        
        logger.info(f"Monitoring started for agent '{self.agent_id}'")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring session."""
        self.is_monitoring = False
        
        # Save final metrics
        if self._current_metrics:
            self.storage.update_agent_metrics(self._current_metrics)
        
        logger.info(f"Monitoring stopped for agent '{self.agent_id}'")
    
    def get_reliability_score(self) -> ReliabilityScore:
        """Get current reliability score for the agent."""
        if self._current_metrics:
            return self._current_metrics.reliability_score
        
        # Return default score
        return ReliabilityScore(
            score=100.0,
            grade="A+",
            trend="→"
        )
    
    def get_agent_metrics(self) -> Optional[AgentMetrics]:
        """Get current agent metrics."""
        return self._current_metrics
    
    def _update_metrics(self, trace_data: TraceData) -> None:
        """Update agent metrics based on new trace data."""
        if not self._current_metrics:
            return
        
        with self._metrics_lock:
            # Update run counts
            self._current_metrics.total_runs += 1
            
            # Update success rate
            if trace_data.success:
                success_count = int(self._current_metrics.success_rate * (self._current_metrics.total_runs - 1))
                success_count += 1
                self._current_metrics.success_rate = success_count / self._current_metrics.total_runs
            else:
                success_count = int(self._current_metrics.success_rate * (self._current_metrics.total_runs - 1))
                self._current_metrics.success_rate = success_count / self._current_metrics.total_runs
            
            # Update average duration
            total_duration = self._current_metrics.avg_duration_ms * (self._current_metrics.total_runs - 1)
            total_duration += trace_data.duration_ms
            self._current_metrics.avg_duration_ms = total_duration / self._current_metrics.total_runs
            
            # Update total cost
            self._current_metrics.total_cost += trace_data.cost_data.total_cost
            
            # Update reliability score
            self._current_metrics.reliability_score = self._calculate_reliability_score()
            
            # Update timestamp
            self._current_metrics.last_updated = datetime.now()
    
    def _calculate_reliability_score(self) -> ReliabilityScore:
        """Calculate reliability score based on current metrics."""
        if not self._current_metrics:
            return ReliabilityScore(score=100.0, grade="A+", trend="→")
        
        # Simple scoring algorithm (can be enhanced)
        success_rate = self._current_metrics.success_rate
        total_runs = self._current_metrics.total_runs
        
        # Base score from success rate
        base_score = success_rate * 100
        
        # Adjust for sample size (more runs = more confidence)
        confidence_factor = min(total_runs / 20.0, 1.0)  # Full confidence at 20+ runs
        adjusted_score = base_score * confidence_factor + 100 * (1 - confidence_factor)
        
        # Determine grade
        if adjusted_score >= 95:
            grade = "A+"
        elif adjusted_score >= 90:
            grade = "A"
        elif adjusted_score >= 85:
            grade = "B+"
        elif adjusted_score >= 80:
            grade = "B"
        elif adjusted_score >= 70:
            grade = "C"
        elif adjusted_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # Simple trend calculation (can be enhanced with historical data)
        trend = "→"  # Stable by default
        
        return ReliabilityScore(
            score=round(adjusted_score, 1),
            grade=grade,
            trend=trend,
            confidence=confidence_factor,
            sample_size=total_runs
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        if not self._current_metrics:
            return {}
        
        recent_traces = self.storage.get_recent_traces(self.agent_id, limit=10)
        
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "reliability": {
                "score": self._current_metrics.reliability_score.score,
                "grade": self._current_metrics.reliability_score.grade,
                "trend": self._current_metrics.reliability_score.trend
            },
            "performance": {
                "total_runs": self._current_metrics.total_runs,
                "success_rate": self._current_metrics.success_rate,
                "avg_duration_ms": self._current_metrics.avg_duration_ms
            },
            "cost": {
                "total_cost": self._current_metrics.total_cost,
                "cost_per_run": self._current_metrics.total_cost / max(self._current_metrics.total_runs, 1),
                "trend": self._current_metrics.cost_trend
            },
            "recent_traces": [
                {
                    "trace_id": trace.trace_id,
                    "success": trace.success,
                    "duration_ms": trace.duration_ms,
                    "timestamp": trace.start_time.isoformat()
                }
                for trace in recent_traces
            ]
        } 
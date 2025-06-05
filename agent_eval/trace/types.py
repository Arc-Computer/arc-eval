"""
Runtime Tracing Data Types.

Extends the core types system with tracing-specific data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum


class TraceEventType(Enum):
    """Types of trace events."""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_CALL = "tool_call"
    API_CALL = "api_call"
    ERROR = "error"
    PERFORMANCE = "performance"


@dataclass
class ExecutionStep:
    """Single step in agent execution timeline."""
    step_id: str
    event_type: TraceEventType
    timestamp: datetime
    duration_ms: float
    data: Dict[str, Any]
    parent_step_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ToolCall:
    """Tool call information in trace."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any
    timestamp: datetime
    duration_ms: float
    success: bool
    error: Optional[str] = None
    cost: float = 0.0


@dataclass
class CostData:
    """Cost tracking information."""
    total_cost: float = 0.0
    api_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_per_run: float = 0.0
    provider: Optional[str] = None
    model: Optional[str] = None


@dataclass
class ReliabilityScore:
    """Agent reliability scoring."""
    score: float  # 0-100
    grade: str    # A+, A, B+, B, C, D, F
    trend: str    # ↑ improving, ↓ declining, → stable
    confidence: float = 0.0
    sample_size: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class FailureInfo:
    """Failure detection information."""
    failure_type: str
    frequency: int
    last_occurrence: datetime
    description: str
    fix_available: bool = False
    fix_description: Optional[str] = None


@dataclass
class TraceData:
    """Complete trace data for agent execution."""
    trace_id: str
    agent_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    execution_timeline: List[ExecutionStep] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    cost_data: CostData = field(default_factory=CostData)
    framework: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float:
        """Total execution duration in milliseconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


@dataclass
class AgentMetrics:
    """Aggregated metrics for an agent."""
    agent_id: str
    total_runs: int
    success_rate: float
    avg_duration_ms: float
    total_cost: float
    reliability_score: ReliabilityScore
    recent_failures: List[FailureInfo] = field(default_factory=list)
    cost_trend: str = "→"  # ↑ increasing, ↓ decreasing, → stable
    performance_trend: str = "→"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardData:
    """Dashboard data for UI display."""
    agent_metrics: AgentMetrics
    recent_traces: List[TraceData]
    cost_optimization: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    performance_summary: Dict[str, Any] = field(default_factory=dict) 
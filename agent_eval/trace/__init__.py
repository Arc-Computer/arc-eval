"""
ARC-Eval Runtime Tracing Module.

One-line agent monitoring and reliability tracking.

Usage:
    from agent_eval.trace import ArcTracer
    tracer = ArcTracer("finance")
    agent = tracer.trace_agent(your_agent)
    response = agent.run(user_input)  # Now monitored!
"""

from .tracer import ArcTracer, TracedAgent
from .capture import TraceCapture
from .storage import TraceStorage
from .cost_tracker import CostTracker
from .types import TraceData, AgentMetrics, ReliabilityScore

# Optional API server (requires FastAPI)
try:
    from .api_server import TraceAPIServer
    API_SERVER_AVAILABLE = True
except ImportError:
    TraceAPIServer = None
    API_SERVER_AVAILABLE = False

__all__ = [
    "ArcTracer",
    "TracedAgent", 
    "TraceCapture",
    "TraceData",
    "AgentMetrics",
    "ReliabilityScore",
    "TraceStorage",
    "CostTracker"
]

if API_SERVER_AVAILABLE:
    __all__.append("TraceAPIServer") 
"""
Trace API Server: FastAPI server for trace ingestion and dashboard.

Provides REST endpoints for trace data and real-time dashboard updates.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import uvicorn

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None

from .storage import TraceStorage
from .types import TraceData, AgentMetrics, DashboardData

logger = logging.getLogger(__name__)


class TraceAPIServer:
    """FastAPI server for trace ingestion and dashboard."""
    
    def __init__(self, storage: Optional[TraceStorage] = None, port: int = 8000):
        """Initialize API server.
        
        Args:
            storage: TraceStorage instance (creates new if None)
            port: Server port
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
        
        self.storage = storage or TraceStorage()
        self.port = port
        self.app = FastAPI(
            title="ARC-Eval Trace API",
            description="Runtime tracing and monitoring API",
            version="1.0.0"
        )
        
        # CORS for dashboard access
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []
        
        self._setup_routes()
        
        logger.info(f"TraceAPIServer initialized on port {port}")
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            return {"message": "ARC-Eval Trace API", "version": "1.0.0"}
        
        @self.app.post("/traces/ingest")
        async def ingest_trace(trace_data: Dict[str, Any]):
            """Ingest a new trace."""
            try:
                # Convert dict to TraceData (simplified)
                trace = self._dict_to_trace_data(trace_data)
                trace_id = self.storage.store_trace(trace)
                
                # Notify connected clients
                await self._broadcast_update({
                    "type": "new_trace",
                    "agent_id": trace.agent_id,
                    "trace_id": trace_id
                })
                
                return {"status": "success", "trace_id": trace_id}
                
            except Exception as e:
                logger.error(f"Failed to ingest trace: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/agents/{agent_id}/dashboard")
        async def get_dashboard_data(agent_id: str):
            """Get dashboard data for an agent."""
            try:
                metrics = self.storage.get_agent_metrics(agent_id)
                if not metrics:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                recent_traces = self.storage.get_recent_traces(agent_id, limit=10)
                cost_history = self.storage.get_cost_history(agent_id, days=7)
                
                dashboard_data = {
                    "agent_id": agent_id,
                    "metrics": self._agent_metrics_to_dict(metrics),
                    "recent_traces": [self._trace_to_dict(t) for t in recent_traces],
                    "cost_history": [{"timestamp": ts.isoformat(), "cost": cost} for ts, cost in cost_history],
                    "alerts": self._generate_alerts(metrics),
                    "recommendations": self._generate_recommendations(metrics)
                }
                
                return dashboard_data
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get dashboard data: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/agents/{agent_id}/metrics")
        async def get_agent_metrics(agent_id: str):
            """Get agent metrics."""
            try:
                metrics = self.storage.get_agent_metrics(agent_id)
                if not metrics:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                return self._agent_metrics_to_dict(metrics)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get agent metrics: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/traces/{trace_id}")
        async def get_trace(trace_id: str):
            """Get specific trace by ID."""
            try:
                trace = self.storage.get_trace(trace_id)
                if not trace:
                    raise HTTPException(status_code=404, detail="Trace not found")
                
                return self._trace_to_dict(trace)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get trace: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.websocket("/ws/{agent_id}")
        async def websocket_endpoint(websocket: WebSocket, agent_id: str):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Keep connection alive and send periodic updates
                    await asyncio.sleep(30)  # Ping every 30 seconds
                    await websocket.send_json({"type": "ping", "timestamp": datetime.now().isoformat()})
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "storage": "connected"
            }
    
    def _dict_to_trace_data(self, data: Dict[str, Any]) -> TraceData:
        """Convert dictionary to TraceData object."""
        # Simplified conversion - in production, you'd validate and convert properly
        return TraceData(
            trace_id=data.get("trace_id", "unknown"),
            agent_id=data.get("agent_id", "unknown"),
            session_id=data.get("session_id", "unknown"),
            start_time=datetime.fromisoformat(data.get("start_time", datetime.now().isoformat())),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            framework=data.get("framework"),
            success=data.get("success", True),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )
    
    def _agent_metrics_to_dict(self, metrics: AgentMetrics) -> Dict[str, Any]:
        """Convert AgentMetrics to dictionary."""
        return {
            "agent_id": metrics.agent_id,
            "total_runs": metrics.total_runs,
            "success_rate": metrics.success_rate,
            "avg_duration_ms": metrics.avg_duration_ms,
            "total_cost": metrics.total_cost,
            "reliability_score": {
                "score": metrics.reliability_score.score,
                "grade": metrics.reliability_score.grade,
                "trend": metrics.reliability_score.trend,
                "confidence": metrics.reliability_score.confidence,
                "sample_size": metrics.reliability_score.sample_size
            },
            "recent_failures": [
                {
                    "failure_type": f.failure_type,
                    "frequency": f.frequency,
                    "last_occurrence": f.last_occurrence.isoformat(),
                    "description": f.description,
                    "fix_available": f.fix_available,
                    "fix_description": f.fix_description
                }
                for f in metrics.recent_failures
            ],
            "cost_trend": metrics.cost_trend,
            "performance_trend": metrics.performance_trend,
            "last_updated": metrics.last_updated.isoformat()
        }
    
    def _trace_to_dict(self, trace: TraceData) -> Dict[str, Any]:
        """Convert TraceData to dictionary."""
        return {
            "trace_id": trace.trace_id,
            "agent_id": trace.agent_id,
            "session_id": trace.session_id,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "duration_ms": trace.duration_ms,
            "framework": trace.framework,
            "success": trace.success,
            "error": trace.error,
            "metadata": trace.metadata,
            "execution_steps": len(trace.execution_timeline),
            "tool_calls": len(trace.tool_calls),
            "total_cost": trace.cost_data.total_cost
        }
    
    def _generate_alerts(self, metrics: AgentMetrics) -> List[str]:
        """Generate alerts based on metrics."""
        alerts = []
        
        # Success rate alerts
        if metrics.success_rate < 0.8:
            alerts.append(f"Low success rate: {metrics.success_rate:.1%}")
        
        # Cost alerts
        if metrics.total_cost > 100:
            alerts.append(f"High total cost: ${metrics.total_cost:.2f}")
        
        # Performance alerts
        if metrics.avg_duration_ms > 5000:
            alerts.append(f"Slow performance: {metrics.avg_duration_ms:.0f}ms average")
        
        # Recent failures
        if metrics.recent_failures:
            alerts.append(f"{len(metrics.recent_failures)} recent failures detected")
        
        return alerts
    
    def _generate_recommendations(self, metrics: AgentMetrics) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Performance recommendations
        if metrics.avg_duration_ms > 3000:
            recommendations.append("Consider optimizing prompts or using faster models")
        
        # Cost recommendations
        if metrics.total_cost / max(metrics.total_runs, 1) > 0.10:
            recommendations.append("Explore cheaper model alternatives")
        
        # Reliability recommendations
        if metrics.success_rate < 0.9:
            recommendations.append("Review recent failures and implement error handling")
        
        return recommendations
    
    async def _broadcast_update(self, message: Dict[str, Any]):
        """Broadcast update to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    def start_server(self, host: str = "localhost"):
        """Start the API server.
        
        Args:
            host: Server host
        """
        logger.info(f"Starting trace API server on {host}:{self.port}")
        
        # Start server
        uvicorn.run(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )
    
    def start_server_async(self, host: str = "localhost"):
        """Start server asynchronously (for embedding in other applications).
        
        Args:
            host: Server host
            
        Returns:
            Server task
        """
        config = uvicorn.Config(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        return asyncio.create_task(server.serve())


# Standalone server for testing
def main():
    """Run standalone API server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ARC-Eval Trace API Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--db-path", help="Database path")
    
    args = parser.parse_args()
    
    # Initialize storage
    storage = TraceStorage(db_path=args.db_path)
    
    # Initialize and start server
    server = TraceAPIServer(storage=storage, port=args.port)
    server.start_server(host=args.host)


if __name__ == "__main__":
    main() 
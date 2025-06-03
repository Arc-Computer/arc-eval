"""
FastAPI web application for Arc Workbench.

Provides local-first web interface that integrates with existing
ARC-Eval CLI functionality. No code duplication - leverages existing
DebugCommand, InteractiveAnalyst, and prediction systems.
"""

import json
import tempfile
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_eval.commands.debug_command import DebugCommand
from agent_eval.analysis.interactive_analyst import InteractiveAnalyst
from agent_eval.core.workflow_state import update_workflow_progress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class AnalyzeRequest(BaseModel):
    framework: Optional[str] = None
    verbose: bool = False

class AnalyzeResponse(BaseModel):
    analysis_id: str
    detected_framework: str
    framework_confidence: float
    reliability_prediction: Dict[str, Any]
    workflow_metrics: Dict[str, Any]
    insights_summary: List[str]
    next_steps: List[str]
    status: str = "completed"

class ChatRequest(BaseModel):
    message: str
    analysis_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    suggested_questions: List[str] = []
    action_buttons: List[Dict[str, str]] = []

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Global instances
app = FastAPI(
    title="Arc Workbench",
    description="Local-first interactive debugging companion for ARC-Eval",
    version="1.0.0"
)

manager = ConnectionManager()

# Store analysis results in memory (production would use persistent storage)
analysis_cache: Dict[str, Dict[str, Any]] = {}

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_file(
    file: UploadFile = File(...),
    framework: Optional[str] = None,
    verbose: bool = False
):
    """
    Analyze uploaded agent output file using existing DebugCommand.
    
    This endpoint integrates with the existing debug analysis infrastructure
    without duplicating any logic.
    """
    if not file.filename.endswith(('.json', '.jsonl')):
        raise HTTPException(status_code=400, detail="Only JSON and JSONL files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Create temporary file for DebugCommand
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            if file.filename.endswith('.jsonl'):
                # Convert JSONL to JSON array
                lines = content.decode().strip().split('\n')
                json_objects = [json.loads(line) for line in lines if line.strip()]
                json.dump(json_objects, tmp_file, indent=2)
            else:
                tmp_file.write(content.decode())
            tmp_file.flush()
            
            # Use existing DebugCommand to perform analysis
            debug_cmd = DebugCommand()
            
            # Execute debug analysis (we'll capture the results differently)
            # For now, we'll use the ReliabilityHandler directly to get structured data
            from agent_eval.commands.reliability_handler import ReliabilityHandler
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
            
            # Load and parse the data
            with open(tmp_file.name, 'r') as f:
                data = json.load(f)
            
            # Ensure data is a list for ReliabilityAnalyzer
            if isinstance(data, dict):
                agent_outputs = [data]
            elif isinstance(data, list):
                agent_outputs = data
            else:
                raise HTTPException(status_code=400, detail="Invalid JSON format")
            
            # Use ReliabilityAnalyzer to get comprehensive analysis
            analyzer = ReliabilityAnalyzer()
            analysis = analyzer.generate_comprehensive_analysis(
                agent_outputs=agent_outputs,
                framework=framework
            )
            
            # Generate unique analysis ID
            analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract key data for web UI
            response_data = {
                "analysis_id": analysis_id,
                "detected_framework": analysis.detected_framework or "generic",
                "framework_confidence": analysis.framework_confidence or 0.0,
                "reliability_prediction": {
                    "risk_level": getattr(analysis.reliability_prediction, 'risk_level', 'UNKNOWN') if analysis.reliability_prediction else 'UNKNOWN',
                    "risk_score": getattr(analysis.reliability_prediction, 'combined_risk_score', 0.0) if analysis.reliability_prediction else 0.0,
                    "confidence": getattr(analysis.reliability_prediction, 'confidence', 0.0) if analysis.reliability_prediction else 0.0,
                    "business_impact": getattr(analysis.reliability_prediction, 'business_impact', {}) if analysis.reliability_prediction else {},
                    "predicted_failures": getattr(getattr(analysis.reliability_prediction, 'llm_component', None), 'predicted_failure_modes', []) if analysis.reliability_prediction else []
                },
                "workflow_metrics": {
                    "success_rate": getattr(analysis.workflow_metrics, 'workflow_success_rate', 0.0) if analysis.workflow_metrics else 0.0,
                    "tool_chain_reliability": getattr(analysis.workflow_metrics, 'tool_chain_reliability', 0.0) if analysis.workflow_metrics else 0.0,
                    "critical_failure_points": getattr(analysis.workflow_metrics, 'critical_failure_points', []) if analysis.workflow_metrics else []
                },
                "insights_summary": analysis.insights_summary or ["Analysis completed successfully"],
                "next_steps": analysis.next_steps or ["Consider running compliance evaluation"]
            }
            
            # Cache the full analysis for chat integration
            analysis_cache[analysis_id] = {
                "analysis": analysis,
                "agent_outputs": agent_outputs,
                "framework": framework,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update workflow progress
            update_workflow_progress('debug',
                input_file=file.filename,
                framework=analysis.detected_framework or framework or 'auto-detected',
                timestamp=datetime.now().isoformat(),
                analysis_id=analysis_id
            )
            
            # Clean up temp file
            Path(tmp_file.name).unlink()
            
            return AnalyzeResponse(**response_data)
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_analysis(request: ChatRequest):
    """
    Chat about analysis results using existing InteractiveAnalyst.
    
    Integrates with existing chat functionality without code duplication.
    """
    try:
        # For MVP, we'll provide basic chat without requiring full compliance data
        # In future versions, this can be enhanced with more context
        
        if request.analysis_id and request.analysis_id in analysis_cache:
            # Use cached analysis data
            cached_data = analysis_cache[request.analysis_id]
            analysis = cached_data["analysis"]
            
            # Create minimal improvement report for InteractiveAnalyst
            improvement_report = {
                "summary": {
                    "total_scenarios": len(cached_data.get("agent_outputs", [])),
                    "framework": cached_data.get("framework", "generic")
                },
                "continuous_feedback": {
                    "improvement_recommendations": analysis.next_steps or [],
                    "strengths": ["Analysis completed successfully"]
                }
            }
            
            # Create InteractiveAnalyst instance
            analyst = InteractiveAnalyst(
                improvement_report=improvement_report,
                judge_results=[],  # Empty for debug-only MVP
                domain="debug",  # Debug domain
                reliability_metrics={
                    "tool_call_accuracy": getattr(analysis.workflow_metrics, 'tool_chain_reliability', 0.0) if analysis.workflow_metrics else 0.0,
                    "workflow_success_rate": getattr(analysis.workflow_metrics, 'workflow_success_rate', 0.0) if analysis.workflow_metrics else 0.0
                }
            )
            
            # Get AI response
            response_text = analyst._query_ai_with_context(request.message)
            
            # Generate context-aware suggestions
            suggested_questions = [
                "What are the most critical failure points?",
                "How can I improve the success rate?",
                f"Why is my {cached_data.get('framework', 'agent')} failing?"
            ]
            
            # Generate action buttons based on analysis
            action_buttons = []
            if analysis.next_steps:
                action_buttons.append({
                    "text": "Get Next Steps",
                    "action": "show_next_steps"
                })
            if analysis.insights_summary:
                action_buttons.append({
                    "text": "Show Insights",
                    "action": "show_insights"
                })
            
        else:
            # General chat without specific analysis context
            response_text = f"I'd be happy to help you debug your agent! However, I don't have analysis context for ID '{request.analysis_id}'. Try uploading an agent output file first to get specific insights."
            suggested_questions = [
                "How do I export agent outputs for analysis?",
                "What file formats are supported?",
                "How does the reliability prediction work?"
            ]
            action_buttons = [
                {
                    "text": "Upload File",
                    "action": "upload_file"
                }
            ]
        
        return ChatResponse(
            response=response_text,
            suggested_questions=suggested_questions,
            action_buttons=action_buttons
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.websocket("/ws/analysis/{analysis_id}")
async def websocket_analysis(websocket: WebSocket, analysis_id: str):
    """
    WebSocket endpoint for real-time analysis progress updates.
    """
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to analysis stream",
            "analysis_id": analysis_id
        }))
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(1)
            # In a real implementation, this would send actual progress updates
            # For MVP, we'll just send heartbeat
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get cached analysis results."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    cached_data = analysis_cache[analysis_id]
    return {
        "analysis_id": analysis_id,
        "timestamp": cached_data["timestamp"],
        "framework": cached_data["framework"],
        "status": "completed"
    }

# Serve React app (will be added in Phase 2)
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the main React app."""
    # For now, return a simple HTML page until React app is built
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arc Workbench</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .container {
                text-align: center;
                max-width: 600px;
            }
            .logo {
                font-size: 3rem;
                margin-bottom: 1rem;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            .drop-zone {
                border: 3px dashed rgba(255, 255, 255, 0.5);
                border-radius: 12px;
                padding: 40px;
                margin: 2rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .drop-zone:hover {
                border-color: rgba(255, 255, 255, 0.8);
                background: rgba(255, 255, 255, 0.1);
            }
            .api-status {
                margin-top: 2rem;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚀</div>
            <h1>Arc Workbench</h1>
            <p>Interactive debugging companion for ARC-Eval</p>
            
            <div class="drop-zone" onclick="document.getElementById('fileInput').click()">
                <h3>Drop your agent outputs here</h3>
                <p>Or click to select JSON/JSONL files</p>
                <input type="file" id="fileInput" accept=".json,.jsonl" style="display: none;" onchange="handleFile(event)">
            </div>
            
            <div class="api-status">
                <p><strong>API Status:</strong> <span id="apiStatus">Checking...</span></p>
                <p><strong>Endpoints Available:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>POST /api/analyze - File analysis</li>
                    <li>POST /api/chat - AI debugging chat</li>
                    <li>WS /ws/analysis/{id} - Real-time updates</li>
                    <li>GET /api/health - Health check</li>
                </ul>
            </div>
        </div>
        
        <script>
            // Check API health
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('apiStatus').textContent = 'Healthy ✅';
                })
                .catch(error => {
                    document.getElementById('apiStatus').textContent = 'Error ❌';
                });
            
            // Handle file upload
            async function handleFile(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    document.getElementById('apiStatus').textContent = 'Analyzing... ⏳';
                    
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        alert(`Analysis complete! 
Framework: ${result.detected_framework}
Risk Level: ${result.reliability_prediction.risk_level}
Success Rate: ${(result.workflow_metrics.success_rate * 100).toFixed(1)}%

Analysis ID: ${result.analysis_id}`);
                        document.getElementById('apiStatus').textContent = 'Analysis Complete ✅';
                    } else {
                        const error = await response.json();
                        alert(`Analysis failed: ${error.detail}`);
                        document.getElementById('apiStatus').textContent = 'Analysis Failed ❌';
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                    document.getElementById('apiStatus').textContent = 'Error ❌';
                }
            }
        </script>
    </body>
    </html>
    """

def start_server(host: str = "localhost", port: int = 3000, dev: bool = False):
    """Start the FastAPI server."""
    try:
        import uvicorn
        
        # Configure uvicorn
        config = {
            "host": host,
            "port": port,
            "log_level": "info" if not dev else "debug",
            "access_log": dev
        }
        
        if dev:
            config["reload"] = True
            config["reload_dirs"] = [str(Path(__file__).parent)]
        
        # Start server
        uvicorn.run("agent_eval.web.app:app", **config)
        
    except ImportError:
        raise ImportError(
            "FastAPI dependencies not installed. "
            "Run: pip install fastapi uvicorn websockets"
        )
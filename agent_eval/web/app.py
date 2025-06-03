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
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.endswith(('.json', '.jsonl')):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type '{file.filename.split('.')[-1]}'. Only JSON and JSONL files are supported."
        )
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large ({file.size / (1024*1024):.1f}MB). Please upload files smaller than 10MB."
        )
    
    try:
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Create temporary file for DebugCommand
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            try:
                if file.filename.endswith('.jsonl'):
                    # Convert JSONL to JSON array with validation
                    lines = content.decode('utf-8').strip().split('\n')
                    json_objects = []
                    
                    for i, line in enumerate(lines):
                        if line.strip():
                            try:
                                json_objects.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                raise HTTPException(
                                    status_code=400, 
                                    detail=f"Invalid JSON on line {i+1}: {str(e)}"
                                )
                    
                    if not json_objects:
                        raise HTTPException(status_code=400, detail="No valid JSON objects found in JSONL file")
                    
                    json.dump(json_objects, tmp_file, indent=2)
                else:
                    # Validate JSON format
                    try:
                        data = json.loads(content.decode('utf-8'))
                    except json.JSONDecodeError as e:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Invalid JSON format: {str(e)}"
                        )
                    except UnicodeDecodeError as e:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"File encoding error: {str(e)}. Please ensure the file is UTF-8 encoded."
                        )
                    
                    tmp_file.write(content.decode('utf-8'))
                tmp_file.flush()
                
                # Use existing DebugCommand to perform analysis
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
                    raise HTTPException(status_code=400, detail="Invalid data structure. Expected JSON object or array.")
                
                if not agent_outputs:
                    raise HTTPException(status_code=400, detail="No agent outputs found in file")
                
                # Validate agent outputs have required structure
                for i, output in enumerate(agent_outputs):
                    if not isinstance(output, dict):
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Invalid output format at index {i}. Expected JSON object."
                        )
                    if 'output' not in output and 'response' not in output and 'content' not in output:
                        logger.warning(f"Output at index {i} missing standard fields (output/response/content)")
                
                # Use ReliabilityAnalyzer to get comprehensive analysis
                analyzer = ReliabilityAnalyzer()
                
                try:
                    analysis = analyzer.generate_comprehensive_analysis(
                        agent_outputs=agent_outputs,
                        framework=framework
                    )
                except Exception as analysis_error:
                    logger.error(f"Analysis failed: {analysis_error}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Analysis engine error: {str(analysis_error)}"
                    )
                
                # Generate unique analysis ID
                analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                
                # Extract key data for web UI with safe attribute access
                try:
                    response_data = {
                        "analysis_id": analysis_id,
                        "detected_framework": getattr(analysis, 'detected_framework', None) or "generic",
                        "framework_confidence": getattr(analysis, 'framework_confidence', None) or 0.0,
                        "reliability_prediction": {
                            "risk_level": getattr(getattr(analysis, 'reliability_prediction', None), 'risk_level', 'UNKNOWN') if hasattr(analysis, 'reliability_prediction') and analysis.reliability_prediction else 'UNKNOWN',
                            "risk_score": getattr(getattr(analysis, 'reliability_prediction', None), 'combined_risk_score', 0.0) if hasattr(analysis, 'reliability_prediction') and analysis.reliability_prediction else 0.0,
                            "confidence": getattr(getattr(analysis, 'reliability_prediction', None), 'confidence', 0.0) if hasattr(analysis, 'reliability_prediction') and analysis.reliability_prediction else 0.0,
                            "business_impact": getattr(getattr(analysis, 'reliability_prediction', None), 'business_impact', {}) if hasattr(analysis, 'reliability_prediction') and analysis.reliability_prediction else {},
                            "predicted_failures": getattr(getattr(getattr(analysis, 'reliability_prediction', None), 'llm_component', None), 'predicted_failure_modes', []) if hasattr(analysis, 'reliability_prediction') and analysis.reliability_prediction and hasattr(analysis.reliability_prediction, 'llm_component') and analysis.reliability_prediction.llm_component else []
                        },
                        "workflow_metrics": {
                            "success_rate": getattr(getattr(analysis, 'workflow_metrics', None), 'workflow_success_rate', 0.0) if hasattr(analysis, 'workflow_metrics') and analysis.workflow_metrics else 0.0,
                            "tool_chain_reliability": getattr(getattr(analysis, 'workflow_metrics', None), 'tool_chain_reliability', 0.0) if hasattr(analysis, 'workflow_metrics') and analysis.workflow_metrics else 0.0,
                            "critical_failure_points": getattr(getattr(analysis, 'workflow_metrics', None), 'critical_failure_points', []) if hasattr(analysis, 'workflow_metrics') and analysis.workflow_metrics else []
                        },
                        "insights_summary": getattr(analysis, 'insights_summary', None) or ["Analysis completed successfully"],
                        "next_steps": getattr(analysis, 'next_steps', None) or ["Consider running compliance evaluation"]
                    }
                except Exception as data_extraction_error:
                    logger.error(f"Data extraction failed: {data_extraction_error}")
                    # Provide fallback response
                    response_data = {
                        "analysis_id": analysis_id,
                        "detected_framework": "generic",
                        "framework_confidence": 0.0,
                        "reliability_prediction": {
                            "risk_level": "UNKNOWN",
                            "risk_score": 0.0,
                            "confidence": 0.0,
                            "business_impact": {},
                            "predicted_failures": []
                        },
                        "workflow_metrics": {
                            "success_rate": 0.0,
                            "tool_chain_reliability": 0.0,
                            "critical_failure_points": []
                        },
                        "insights_summary": [f"Analysis completed with {len(agent_outputs)} outputs"],
                        "next_steps": ["Review analysis results"]
                    }
                
                # Cache the full analysis for chat integration
                analysis_cache[analysis_id] = {
                    "analysis": analysis,
                    "agent_outputs": agent_outputs,
                    "framework": framework,
                    "timestamp": datetime.now().isoformat(),
                    "filename": file.filename,
                    "file_size": len(content)
                }
                
                # Update workflow progress
                try:
                    update_workflow_progress('debug',
                        input_file=file.filename,
                        framework=response_data["detected_framework"],
                        timestamp=datetime.now().isoformat(),
                        analysis_id=analysis_id
                    )
                except Exception as workflow_error:
                    logger.warning(f"Workflow progress update failed: {workflow_error}")
                
                return AnalyzeResponse(**response_data)
                
            finally:
                # Clean up temp file
                try:
                    Path(tmp_file.name).unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Temp file cleanup failed: {cleanup_error}")
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error during analysis: {str(e)}"
        )

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
    # Enhanced HTML page with better error handling and loading states
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arc Workbench</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                line-height: 1.6;
            }
            .container {
                text-align: center;
                max-width: 700px;
                width: 100%;
            }
            .logo {
                font-size: 3rem;
                margin-bottom: 1rem;
                animation: pulse 2s infinite;
                user-select: none;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.05); }
            }
            .drop-zone {
                border: 3px dashed rgba(255, 255, 255, 0.5);
                border-radius: 12px;
                padding: 40px;
                margin: 2rem 0;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .drop-zone:hover {
                border-color: rgba(255, 255, 255, 0.8);
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            .drop-zone.dragover {
                border-color: #4CAF50;
                background: rgba(76, 175, 80, 0.2);
                transform: scale(1.02);
            }
            .drop-zone.error {
                border-color: #f44336;
                background: rgba(244, 67, 54, 0.2);
            }
            .drop-zone.success {
                border-color: #4CAF50;
                background: rgba(76, 175, 80, 0.2);
            }
            .loading {
                display: none;
                align-items: center;
                gap: 10px;
            }
            .spinner {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top: 2px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .status {
                margin-top: 1rem;
                padding: 1rem;
                border-radius: 8px;
                font-weight: 500;
                display: none;
            }
            .status.error {
                background: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
                color: #ffcdd2;
            }
            .status.success {
                background: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5);
                color: #c8e6c9;
            }
            .status.info {
                background: rgba(33, 150, 243, 0.2);
                border: 1px solid rgba(33, 150, 243, 0.5);
                color: #bbdefb;
            }
            .api-status {
                margin-top: 2rem;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                backdrop-filter: blur(10px);
            }
            .progress-bar {
                width: 100%;
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                overflow: hidden;
                margin: 1rem 0;
                display: none;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #2196F3);
                border-radius: 2px;
                transition: width 0.3s ease;
                width: 0%;
                animation: progress-shimmer 2s infinite;
            }
            @keyframes progress-shimmer {
                0% { background-position: -200px 0; }
                100% { background-position: 200px 0; }
            }
            .file-info {
                margin-top: 1rem;
                font-size: 0.9rem;
                opacity: 0.8;
                display: none;
            }
            .result-card {
                margin-top: 2rem;
                padding: 1.5rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                backdrop-filter: blur(10px);
                text-align: left;
                display: none;
            }
            .result-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 1rem;
                font-size: 1.1rem;
                font-weight: 600;
            }
            .risk-badge {
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            .risk-low { background: #4CAF50; color: white; }
            .risk-medium { background: #FF9800; color: white; }
            .risk-high { background: #f44336; color: white; }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1rem 0;
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
            .metric-value {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            .metric-label {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            .chat-section {
                margin-top: 2rem;
                text-align: center;
            }
            .chat-button {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 0.5rem;
                display: inline-block;
                text-decoration: none;
            }
            .chat-button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }
            .websocket-status {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                backdrop-filter: blur(10px);
            }
            .ws-connected { background: rgba(76, 175, 80, 0.3); color: #c8e6c9; }
            .ws-disconnected { background: rgba(244, 67, 54, 0.3); color: #ffcdd2; }
            .supported-formats {
                margin-top: 1rem;
                font-size: 0.85rem;
                opacity: 0.7;
            }
            @media (max-width: 768px) {
                body { padding: 20px; }
                .container { max-width: 100%; }
                .metrics-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="websocket-status ws-disconnected" id="wsStatus">WebSocket: Disconnected</div>
        
        <div class="container">
            <div class="logo">🚀</div>
            <h1>Arc Workbench</h1>
            <p>Interactive debugging companion for ARC-Eval</p>
            
            <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                <div id="dropContent">
                    <h3>Drop your agent outputs here</h3>
                    <p>Or click to select files</p>
                    <div class="supported-formats">
                        Supported: JSON, JSONL files up to 10MB
                    </div>
                </div>
                <div class="loading" id="loadingState">
                    <div class="spinner"></div>
                    <span>Analyzing agent outputs...</span>
                </div>
                <input type="file" id="fileInput" accept=".json,.jsonl" style="display: none;" onchange="handleFile(event)">
            </div>
            
            <div class="progress-bar" id="progressBar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div class="file-info" id="fileInfo"></div>
            
            <div class="status" id="statusMessage"></div>
            
            <div class="result-card" id="resultCard">
                <div class="result-header">
                    <span>Analysis Results</span>
                    <span class="risk-badge" id="riskBadge">UNKNOWN</span>
                </div>
                <div class="metrics-grid" id="metricsGrid"></div>
                <div id="insightsSection"></div>
                <div class="chat-section">
                    <p>Have questions about your results?</p>
                    <button class="chat-button" onclick="askQuestion('What are the most critical failure points?')">🔍 Critical Issues</button>
                    <button class="chat-button" onclick="askQuestion('How can I improve the success rate?')">📈 Improvements</button>
                    <button class="chat-button" onclick="askQuestion('Why did my agent fail?')">🤔 Root Cause</button>
                </div>
            </div>
            
            <div class="api-status">
                <p><strong>API Status:</strong> <span id="apiStatus">Checking...</span></p>
                <p><strong>Endpoints Available:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>POST /api/analyze - File analysis with reliability prediction</li>
                    <li>POST /api/chat - AI debugging assistance</li>
                    <li>WebSocket /ws/analysis/{id} - Real-time updates</li>
                    <li>GET /api/health - Health monitoring</li>
                </ul>
            </div>
        </div>
        
        <script>
            let currentAnalysisId = null;
            let websocket = null;
            
            // WebSocket connection for real-time updates
            function connectWebSocket(analysisId) {
                const wsUrl = `ws://localhost:${window.location.port}/ws/analysis/${analysisId}`;
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = () => {
                    document.getElementById('wsStatus').className = 'websocket-status ws-connected';
                    document.getElementById('wsStatus').textContent = 'WebSocket: Connected';
                };
                
                websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'progress') {
                        updateProgress(data.progress);
                    }
                };
                
                websocket.onclose = () => {
                    document.getElementById('wsStatus').className = 'websocket-status ws-disconnected';
                    document.getElementById('wsStatus').textContent = 'WebSocket: Disconnected';
                };
                
                websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }
            
            // File upload handling with validation
            async function handleFile(event) {
                const file = event.target.files[0];
                if (!file) return;
                
                // Reset UI state
                resetUIState();
                
                // Validate file type
                if (!file.name.endsWith('.json') && !file.name.endsWith('.jsonl')) {
                    showError('Invalid file type. Please upload JSON or JSONL files only.');
                    return;
                }
                
                // Validate file size (10MB limit)
                if (file.size > 10 * 1024 * 1024) {
                    showError('File too large. Please upload files smaller than 10MB.');
                    return;
                }
                
                // Show file info
                showFileInfo(file);
                
                // Show loading state
                showLoading();
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        currentAnalysisId = result.analysis_id;
                        connectWebSocket(result.analysis_id);
                        showSuccess(result);
                    } else {
                        const error = await response.json();
                        showError(`Analysis failed: ${error.detail}`);
                    }
                } catch (error) {
                    showError(`Network error: ${error.message}`);
                } finally {
                    hideLoading();
                }
            }
            
            // Drag and drop handling
            const dropZone = document.getElementById('dropZone');
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });
            
            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragover');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    document.getElementById('fileInput').files = files;
                    handleFile({ target: { files } });
                }
            });
            
            // UI state management
            function resetUIState() {
                const elements = ['statusMessage', 'resultCard', 'fileInfo', 'progressBar'];
                elements.forEach(id => document.getElementById(id).style.display = 'none');
                document.getElementById('dropZone').className = 'drop-zone';
            }
            
            function showLoading() {
                document.getElementById('dropContent').style.display = 'none';
                document.getElementById('loadingState').style.display = 'flex';
                document.getElementById('progressBar').style.display = 'block';
                updateProgress(10);
            }
            
            function hideLoading() {
                document.getElementById('dropContent').style.display = 'block';
                document.getElementById('loadingState').style.display = 'none';
                document.getElementById('progressBar').style.display = 'none';
            }
            
            function updateProgress(percent) {
                document.getElementById('progressFill').style.width = percent + '%';
            }
            
            function showFileInfo(file) {
                const fileInfo = document.getElementById('fileInfo');
                fileInfo.innerHTML = `📁 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                fileInfo.style.display = 'block';
            }
            
            function showError(message) {
                const status = document.getElementById('statusMessage');
                status.className = 'status error';
                status.innerHTML = `❌ ${message}`;
                status.style.display = 'block';
                document.getElementById('dropZone').classList.add('error');
                document.getElementById('apiStatus').textContent = 'Error ❌';
            }
            
            function showSuccess(result) {
                document.getElementById('dropZone').classList.add('success');
                
                // Show success status
                const status = document.getElementById('statusMessage');
                status.className = 'status success';
                status.innerHTML = `✅ Analysis complete! Framework: ${result.detected_framework}`;
                status.style.display = 'block';
                
                // Show detailed results
                displayResults(result);
                
                document.getElementById('apiStatus').textContent = 'Analysis Complete ✅';
            }
            
            function displayResults(result) {
                const resultCard = document.getElementById('resultCard');
                const riskBadge = document.getElementById('riskBadge');
                const metricsGrid = document.getElementById('metricsGrid');
                
                // Set risk badge
                const riskLevel = result.reliability_prediction.risk_level.toLowerCase();
                riskBadge.textContent = result.reliability_prediction.risk_level;
                riskBadge.className = `risk-badge risk-${riskLevel}`;
                
                // Create metrics
                metricsGrid.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-value">${(result.workflow_metrics.success_rate * 100).toFixed(1)}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${result.reliability_prediction.confidence.toFixed(2)}</div>
                        <div class="metric-label">Confidence</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${result.detected_framework}</div>
                        <div class="metric-label">Framework</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${result.reliability_prediction.risk_score.toFixed(2)}</div>
                        <div class="metric-label">Risk Score</div>
                    </div>
                `;
                
                // Show insights
                if (result.insights_summary && result.insights_summary.length > 0) {
                    const insightsSection = document.getElementById('insightsSection');
                    insightsSection.innerHTML = `
                        <h4>💡 Key Insights:</h4>
                        <ul>
                            ${result.insights_summary.map(insight => `<li>${insight}</li>`).join('')}
                        </ul>
                    `;
                }
                
                resultCard.style.display = 'block';
            }
            
            // Chat functionality
            async function askQuestion(question) {
                if (!currentAnalysisId) {
                    alert('Please analyze a file first before asking questions.');
                    return;
                }
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: question,
                            analysis_id: currentAnalysisId
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        alert(`AI Assistant: ${result.response}`);
                    } else {
                        const error = await response.json();
                        alert(`Chat error: ${error.detail}`);
                    }
                } catch (error) {
                    alert(`Network error: ${error.message}`);
                }
            }
            
            // Check API health on load
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('apiStatus').textContent = 'Healthy ✅';
                })
                .catch(error => {
                    document.getElementById('apiStatus').textContent = 'Error ❌';
                });
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
"""FastAPI backend for Arc Workbench."""

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import socketio

from typing import List, Dict, Any, Optional
import logging
import tempfile
import os
from pathlib import Path
import asyncio
import json

# Assuming models are defined in agent_eval.web.models
from .models import AnalyzeResponse, ChatMessage, ChatResponse, AnalysisProgress, InitialAnalysisData, ReliabilityPredictionModel

# Imports for analysis logic
from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer, ComprehensiveReliabilityAnalysis
# --- NEW Imports for chat logic ---
from agent_eval.analysis.interactive_analyst import InteractiveAnalyst

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Arc Workbench API")

# --- WebSocket Management ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected via WebSocket.")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected.")

    async def send_progress(self, client_id: str, message: str, percentage: float = None, step: str = None):
        if client_id in self.active_connections:
            progress_update = AnalysisProgress(message=message, percentage=percentage, step=step)
            try:
                await self.active_connections[client_id].send_json(progress_update.model_dump())
            except Exception as e:
                logger.error(f"Error sending progress to {client_id}: {e}")

    async def broadcast(self, message: str):
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")


manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


# --- API Endpoints ---
@app.get("/api/health", summary="Health check endpoint")
async def health_check():
    return {"status": "healthy", "message": "Arc Workbench API is running."}


# --- Helper function for running analysis ---
async def _run_debug_analysis_and_get_results(file_path: str, client_id: str, ws_manager: ConnectionManager) -> Optional[ComprehensiveReliabilityAnalysis]:
    try:
        await ws_manager.send_progress(client_id, "Loading agent output data...", 15, "loading_data")

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                raw_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"JSONDecodeError for {client_id} reading {file_path}: {e}")
                await ws_manager.send_progress(client_id, f"Error: Invalid JSON format in uploaded file. {str(e)}", 0, "error")
                return None

        if isinstance(raw_data, dict):
            agent_outputs_data = [raw_data]
        elif isinstance(raw_data, list):
            agent_outputs_data = raw_data
        else:
            logger.error(f"Invalid data structure in {file_path} for {client_id}. Expected dict or list, got {type(raw_data)}")
            await ws_manager.send_progress(client_id, "Error: Invalid data structure in file. Expected a JSON object or list.", 0, "error")
            return None

        if not agent_outputs_data:
            await ws_manager.send_progress(client_id, "Error: No data found in file.", 0, "error")
            return None

        await ws_manager.send_progress(client_id, "Data loaded, initializing analyzer...", 20, "analyzer_init")
        analyzer = ReliabilityAnalyzer()
        await ws_manager.send_progress(client_id, "Starting comprehensive analysis...", 25, "analysis_start")

        loop = asyncio.get_event_loop()
        analysis_result: ComprehensiveReliabilityAnalysis = await loop.run_in_executor(
            None,
            analyzer.generate_comprehensive_analysis,
            agent_outputs_data,
            None
        )

        await ws_manager.send_progress(client_id, "Framework detection and performance analysis complete.", 60, "framework_analysis")
        await ws_manager.send_progress(client_id, "Tool call and workflow metrics calculated.", 80, "workflow_metrics")

        if analysis_result and analysis_result.reliability_prediction:
            await ws_manager.send_progress(client_id, "Reliability prediction generated.", 90, "prediction_complete")
        else:
            await ws_manager.send_progress(client_id, "Reliability prediction might be missing or incomplete.", 90, "prediction_warning")
        return analysis_result
    except Exception as e:
        logger.error(f"Exception in _run_debug_analysis_and_get_results for {client_id}: {e}", exc_info=True)
        await ws_manager.send_progress(client_id, f"Error during analysis: {str(e)}", 0, "error")
        return None


@app.post("/api/analyze", response_model=AnalyzeResponse, summary="Analyze agent output file")
async def analyze_file_endpoint(client_id: str, file: UploadFile = File(...)):
    logger.info(f"Received file for analysis from client {client_id}: {file.filename}")
    await manager.send_progress(client_id, "File received, preparing for analysis...", 5, "setup")

    if not (file.filename.endswith(".json") or file.filename.endswith(".jsonl")):
        await manager.send_progress(client_id, "Invalid file type. Please upload JSON or JSONL.", 0, "error")
        return AnalyzeResponse(message="Invalid file type. Please upload JSON or JSONL.", initial_data=None)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix, mode='wb') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        logger.info(f"File saved temporarily to {tmp_path} for client {client_id}")
        analysis_results: Optional[ComprehensiveReliabilityAnalysis] = await _run_debug_analysis_and_get_results(tmp_path, client_id, manager)

        if analysis_results and analysis_results.reliability_prediction:
            pred = analysis_results.reliability_prediction
            reliability_model_data = {
                "risk_level": pred.get("risk_level", "UNKNOWN"),
                "combined_risk_score": pred.get("combined_risk_score", 0.0),
                "confidence": pred.get("confidence", 0.0),
                "failure_prevention_percentage": pred.get("business_impact", {}).get("failure_prevention_percentage")
            }
            initial_data = InitialAnalysisData(
                reliability_prediction=ReliabilityPredictionModel(**reliability_model_data),
                insights_summary=analysis_results.insights_summary,
                next_steps=analysis_results.next_steps
            )
            await manager.send_progress(client_id, "Analysis complete. Results packaged.", 100, "complete")
            return AnalyzeResponse(
                message="Analysis complete",
                analysis_id=pred.get("prediction_id", "analysis_" + client_id),
                initial_data=initial_data
            )
        else:
            logger.error(f"Analysis failed or produced no results for {client_id}.")
            if analysis_results is None:
                 return AnalyzeResponse(message="Analysis failed.", initial_data=None)
            else:
                await manager.send_progress(client_id, "Analysis completed but reliability prediction is missing.", 95, "warning")
                return AnalyzeResponse(message="Analysis completed but reliability prediction is missing.", initial_data=None)
    except Exception as e:
        logger.error(f"Error in /api/analyze for {client_id}: {e}", exc_info=True)
        await manager.send_progress(client_id, f"Critical analysis error: {str(e)}", 0, "error")
        return AnalyzeResponse(message=f"Analysis critically failed: {str(e)}", initial_data=None)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            logger.info(f"Temporary file {tmp_path} deleted for client {client_id}.")


@app.post("/api/chat", response_model=ChatResponse, summary="Chat with the analysis engine")
async def chat_endpoint(chat_message: ChatMessage, client_id: Optional[str] = None):
    """
    Receives a user message and context, interacts with InteractiveAnalyst,
    and returns the AI's response.
    """
    logger.info(f"Received chat message from {client_id or 'unknown'} for /api/chat: {chat_message.message}")

    domain = "general"
    performance_metrics_dict = None
    reliability_metrics_dict = None
    interactive_analyst_context_parts = []

    if chat_message.analysis_context:
        ctx = chat_message.analysis_context
        detected_framework = ctx.get("detected_framework")
        if detected_framework:
            domain = detected_framework
            interactive_analyst_context_parts.append(f"EVALUATION DOMAIN: {domain}")

        if ctx.get("reliability_prediction"):
            pred_ctx = ctx["reliability_prediction"]
            interactive_analyst_context_parts.append("RELIABILITY PREDICTION:")
            interactive_analyst_context_parts.append(f"  Risk Level: {pred_ctx.get('risk_level', 'N/A')}")
            interactive_analyst_context_parts.append(f"  Risk Score: {pred_ctx.get('combined_risk_score', 'N/A')}")
            interactive_analyst_context_parts.append("")

        if ctx.get("insights_summary"):
            interactive_analyst_context_parts.append("KEY INSIGHTS FROM ANALYSIS:")
            for insight in ctx["insights_summary"][:3]:
                interactive_analyst_context_parts.append(f"- {insight}")
            interactive_analyst_context_parts.append("")

    try:
        analyst = InteractiveAnalyst(
            improvement_report={},
            judge_results=[],
            domain=domain,
            performance_metrics=performance_metrics_dict,
            reliability_metrics=reliability_metrics_dict
        )

        custom_context_str = "\n".join(interactive_analyst_context_parts)
        augmented_question = chat_message.message
        if custom_context_str:
             analyst.context = custom_context_str + "\n\nADDITIONAL CONTEXT FROM ANALYSIS:\n" + analyst.context

        logger.info(f"Querying InteractiveAnalyst with domain '{domain}' and question: '{chat_message.message}'")
        ai_response_text = analyst._query_ai_with_context(augmented_question)

        return ChatResponse(response=ai_response_text)

    except ValueError as ve:
        logger.error(f"ValueError in InteractiveAnalyst: {ve}", exc_info=True)
        return ChatResponse(response=f"Chat initialization error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error during chat processing for {client_id}: {e}", exc_info=True)
        return ChatResponse(response=f"Sorry, I encountered an error: {str(e)}")

# Serve frontend (Next.js build) - This needs to be configured after frontend is built
# Example: app.mount("/static", StaticFiles(directory="frontend/out/static"), name="static")
# Example:
# @app.get("/{full_path:path}")
# async def serve_react_app(full_path: str):
#     """Serves the Next.js frontend."""
#     frontend_dir = Path(__file__).resolve().parent.parent / "frontend" / "out"
#     index_file = frontend_dir / "index.html"
#     static_file = frontend_dir / full_path
#
#     if static_file.is_file() and static_file.exists():
#         return FileResponse(static_file)
#     elif index_file.exists():
#         return FileResponse(index_file)
#     else:
#         return HTMLResponse(content="Arc Workbench frontend not found. Build it first.", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="debug")

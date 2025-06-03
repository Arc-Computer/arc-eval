"""Pydantic models for Arc Workbench API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    # File will be handled by FastAPI's UploadFile
    pass

class AnalysisProgress(BaseModel):
    message: str
    percentage: Optional[float] = None
    step: Optional[str] = None # e.g., "framework_detection", "reliability_analysis"

class ReliabilityPredictionModel(BaseModel):
    # Based on HybridReliabilityPredictor output and UI needs
    risk_level: str # LOW, MEDIUM, HIGH
    combined_risk_score: float
    confidence: float
    failure_prevention_percentage: Optional[float] = None
    # Add other fields from reliability_prediction if needed by ReliabilityStory card

class InitialAnalysisData(BaseModel):
    reliability_prediction: ReliabilityPredictionModel
    insights_summary: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    # We can add more fields from ComprehensiveReliabilityAnalysis as needed by the UI

class AnalyzeResponse(BaseModel):
    message: str
    analysis_id: Optional[str] = None # For potentially fetching full results later or context
    initial_data: Optional[InitialAnalysisData] = None

class ChatMessage(BaseModel):
    message: str
    # Optional context from the previous analysis run
    # Frontend should store and send relevant parts of ComprehensiveReliabilityAnalysis
    analysis_context: Optional[Dict[str, Any]] = None
    # Example context structure the frontend might send:
    # {
    #   "detected_framework": "langchain",
    #   "framework_performance": { ... }, # from ComprehensiveReliabilityAnalysis.framework_performance
    #   "workflow_metrics": { ... },      # from ComprehensiveReliabilityAnalysis.workflow_metrics
    #   "insights_summary": [ ... ],    # from ComprehensiveReliabilityAnalysis.insights_summary
    #   "reliability_prediction": { ... } # from ComprehensiveReliabilityAnalysis.reliability_prediction
    # }

class ChatResponse(BaseModel):
    response: str
    # suggested_actions: Optional[List[str]] = None

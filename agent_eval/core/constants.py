"""
Core constants and configuration values for ARC-Eval.

Centralizes all hardcoded values to make the system more maintainable and configurable.
"""

# Framework Performance Thresholds (Updated for 2024-2025 Research)
# CrewAI: Research shows 30s+ response times in production, 25s is reasonable threshold
CREWAI_SLOW_RESPONSE_THRESHOLD = 30.0  # seconds - validated against production reports
# LangChain/LangGraph: Complex workflows show abstraction overhead in enterprise use
LANGCHAIN_ABSTRACTION_OVERHEAD_THRESHOLD = 0.25  # 25% abstraction overhead - refined threshold
# AutoGen: Enterprise-focused, more reliable but complex setup
AUTOGEN_RELIABILITY_THRESHOLD = 0.85  # 85% reliability for enterprise use
# Framework Detection Confidence
FRAMEWORK_DETECTION_CONFIDENCE_THRESHOLD = 0.3  # 30% minimum confidence
FRAMEWORK_DETECTION_HIGH_CONFIDENCE_THRESHOLD = 0.6  # 60% high confidence - raised for accuracy

# File Size Thresholds
AUTO_AGENT_JUDGE_FILE_SIZE_THRESHOLD = 100_000  # 100KB - auto-enable agent judge for large files

# Schema Validation Thresholds
HIGH_MISMATCH_RATE_THRESHOLD = 0.1  # 10% - high mismatch rate
MODERATE_MISMATCH_RATE_THRESHOLD = 0.05  # 5% - moderate mismatch rate

# Reliability Score Thresholds
RELIABILITY_SCORE_EXCELLENT_THRESHOLD = 0.9  # 90% - excellent reliability
RELIABILITY_SCORE_GOOD_THRESHOLD = 0.7  # 70% - good reliability
WORKFLOW_SUCCESS_RATE_EXCELLENT_THRESHOLD = 0.9  # 90% - excellent workflow success
WORKFLOW_SUCCESS_RATE_GOOD_THRESHOLD = 0.7  # 70% - good workflow success

# Performance Analysis Thresholds
SLOW_RESPONSE_TIME_THRESHOLD = 10.0  # seconds - considered slow
ANALYSIS_CONFIDENCE_HIGH_THRESHOLD = 0.8  # 80% - high confidence analysis
ANALYSIS_CONFIDENCE_MEDIUM_THRESHOLD = 0.6  # 60% - medium confidence analysis

# Model Names (centralized)
DEFAULT_JUDGE_MODEL = "claude-sonnet-4-20250514"
COST_OPTIMIZED_JUDGE_MODEL = "claude-3-5-haiku-latest"
AUTO_MODEL_SELECTION = "auto"

# Progress and UI Thresholds
PROGRESS_UPDATE_INTERVAL = 10  # percentage increments for progress updates
MAX_EXAMPLES_TO_SHOW = 2  # maximum examples to display in CLI
MAX_COMMON_MISTAKES_TO_SHOW = 3  # maximum common mistakes to display
MAX_OPTIMIZATION_SUGGESTIONS = 8  # maximum optimization suggestions to show

# Memory and Performance Limits
MAX_CONVERSATION_HISTORY_LENGTH = 20  # messages before triggering memory bloat warning
LARGE_WORKFLOW_TRACE_SIZE = 1000  # steps before truncating analysis
MAX_SAMPLE_SIZE_FOR_FULL_CONFIDENCE = 50  # samples needed for full confidence

# Workflow Reliability Thresholds (Week 2 Strategy)
WORKFLOW_COMPLEXITY_SIMPLE_THRESHOLD = 3    # <= 3 steps considered simple
WORKFLOW_COMPLEXITY_COMPLEX_THRESHOLD = 10  # >= 10 steps considered complex
MULTI_STEP_SUCCESS_RATE_THRESHOLD = 0.80    # 80% success rate for multi-step workflows
TOOL_CALL_CONSISTENCY_THRESHOLD = 0.85      # 85% consistency in tool usage patterns
ERROR_RECOVERY_RATE_THRESHOLD = 0.70        # 70% successful error recovery

# Framework-Specific Constants with Performance Characteristics
FRAMEWORKS = {
    "LANGCHAIN": "langchain",     # Full ecosystem, higher abstraction
    "LANGGRAPH": "langgraph",     # Graph-based workflows, production-ready
    "CREWAI": "crewai",           # Rapid prototyping, can be slow
    "AUTOGEN": "autogen",         # Enterprise-focused, Microsoft Research
    "OPENAI": "openai",           # Direct API integration
    "ANTHROPIC": "anthropic",     # Direct API integration
    "GOOGLE_ADK": "google_adk",   # Google AI Development Kit
    "NVIDIA_AIQ": "nvidia_aiq",   # NVIDIA AI Workbench integration
    "AGNO": "agno",               # Emerging framework
    "GENERIC": "generic"          # Framework-agnostic
}

# Framework Performance Baselines (2024-2025 Research)
FRAMEWORK_EXPECTED_PERFORMANCE = {
    "crewai": {"avg_response_time": 15.0, "reliability_score": 0.75, "complexity_support": "medium"},
    "langchain": {"avg_response_time": 8.0, "reliability_score": 0.80, "complexity_support": "high"},
    "langgraph": {"avg_response_time": 6.0, "reliability_score": 0.85, "complexity_support": "high"},
    "autogen": {"avg_response_time": 10.0, "reliability_score": 0.90, "complexity_support": "enterprise"},
    "openai": {"avg_response_time": 3.0, "reliability_score": 0.95, "complexity_support": "low"},
    "anthropic": {"avg_response_time": 3.5, "reliability_score": 0.95, "complexity_support": "low"},
    "google_adk": {"avg_response_time": 4.0, "reliability_score": 0.85, "complexity_support": "medium"},
    "nvidia_aiq": {"avg_response_time": 7.0, "reliability_score": 0.80, "complexity_support": "high"},
    "agno": {"avg_response_time": 12.0, "reliability_score": 0.70, "complexity_support": "experimental"}
}

# Domain Information
DOMAIN_SCENARIO_COUNTS = {
    "finance": 110,
    "security": 120,
    "ml": 148
}

TOTAL_SCENARIOS = sum(DOMAIN_SCENARIO_COUNTS.values())  # 378

# Export and File Naming
DEFAULT_EXPORT_FORMATS = ["pdf", "csv", "json"]
REPORT_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
EVALUATION_ID_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Batch Processing Thresholds
BATCH_PROCESSING_THRESHOLD = 5  # Auto-enable batch processing for 5+ scenarios
BATCH_SIZE_LIMIT = 100  # Maximum scenarios per batch (Anthropic limit)
BATCH_CONFIDENCE_THRESHOLD = 0.7  # Confidence threshold for Haiku → Sonnet escalation
BATCH_API_DISCOUNT = 0.5  # 50% discount on batch API pricing

# Error Handling
DEFAULT_TIMEOUT_SECONDS = 120  # 2 minutes default timeout
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# CLI Display
MAX_CLI_TEXT_LINES = 4  # maximum lines for CLI responses (from instruction)
MAX_FRAMEWORK_ALTERNATIVES_TO_SHOW = 2  # max framework alternatives in recommendations
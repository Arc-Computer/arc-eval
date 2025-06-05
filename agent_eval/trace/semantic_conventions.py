"""
Semantic Conventions for Agent Tracing.

Defines standardized attribute names and values for agent-specific telemetry data,
following OpenTelemetry semantic conventions patterns. These conventions enable
consistent attribute usage across different agent frameworks and monitoring tools.

Based on OpenTelemetry Semantic Conventions v1.21.0:
https://opentelemetry.io/docs/specs/semconv/
"""

from typing import Final


class AgentAttributes:
    """Agent-specific attributes for spans and traces.
    
    Defines standardized attribute names for agent identification,
    framework detection, and execution context.
    """
    
    # Agent identification
    AGENT_ID: Final[str] = "agent.id"
    AGENT_NAME: Final[str] = "agent.name"
    AGENT_VERSION: Final[str] = "agent.version"
    AGENT_TYPE: Final[str] = "agent.type"
    
    # Framework information
    AGENT_FRAMEWORK: Final[str] = "agent.framework"
    AGENT_FRAMEWORK_VERSION: Final[str] = "agent.framework.version"
    
    # Execution context
    AGENT_SESSION_ID: Final[str] = "agent.session.id"
    AGENT_DOMAIN: Final[str] = "agent.domain"
    AGENT_ENVIRONMENT: Final[str] = "agent.environment"
    
    # Performance metrics
    AGENT_EXECUTION_TYPE: Final[str] = "agent.execution.type"
    AGENT_SUCCESS: Final[str] = "agent.success"
    AGENT_ERROR_TYPE: Final[str] = "agent.error.type"
    AGENT_RETRY_COUNT: Final[str] = "agent.retry.count"
    
    # Reasoning and cognition
    AGENT_REASONING_STEPS: Final[str] = "agent.reasoning.steps"
    AGENT_PLANNING_DEPTH: Final[str] = "agent.planning.depth"
    AGENT_REFLECTION_COUNT: Final[str] = "agent.reflection.count"
    AGENT_METACOGNITIVE_LEVEL: Final[str] = "agent.metacognitive.level"


class ToolAttributes:
    """Tool call attributes for agent interactions.
    
    Standardizes tool call telemetry including tool identification,
    execution results, and error handling.
    """
    
    # Tool identification
    TOOL_NAME: Final[str] = "tool.name"
    TOOL_TYPE: Final[str] = "tool.type"
    TOOL_VERSION: Final[str] = "tool.version"
    TOOL_PROVIDER: Final[str] = "tool.provider"
    
    # Tool execution
    TOOL_INPUT_SIZE: Final[str] = "tool.input.size"
    TOOL_OUTPUT_SIZE: Final[str] = "tool.output.size"
    TOOL_SUCCESS: Final[str] = "tool.success"
    TOOL_ERROR_TYPE: Final[str] = "tool.error.type"
    TOOL_ERROR_MESSAGE: Final[str] = "tool.error.message"
    
    # Tool performance
    TOOL_LATENCY_MS: Final[str] = "tool.latency.ms"
    TOOL_RETRY_COUNT: Final[str] = "tool.retry.count"
    TOOL_TIMEOUT_MS: Final[str] = "tool.timeout.ms"
    
    # API-specific attributes
    TOOL_API_ENDPOINT: Final[str] = "tool.api.endpoint"
    TOOL_API_METHOD: Final[str] = "tool.api.method"
    TOOL_API_STATUS_CODE: Final[str] = "tool.api.status_code"
    TOOL_API_RATE_LIMITED: Final[str] = "tool.api.rate_limited"


class ScenarioAttributes:
    """Scenario and evaluation context attributes.
    
    Captures evaluation scenario information for testing and
    compliance monitoring contexts.
    """
    
    # Scenario identification
    SCENARIO_ID: Final[str] = "scenario.id"
    SCENARIO_NAME: Final[str] = "scenario.name"
    SCENARIO_TYPE: Final[str] = "scenario.type"
    SCENARIO_CATEGORY: Final[str] = "scenario.category"
    SCENARIO_DOMAIN: Final[str] = "scenario.domain"
    
    # Evaluation context
    SCENARIO_SEVERITY: Final[str] = "scenario.severity"
    SCENARIO_COMPLIANCE_FRAMEWORKS: Final[str] = "scenario.compliance.frameworks"
    SCENARIO_EXPECTED_BEHAVIOR: Final[str] = "scenario.expected.behavior"
    SCENARIO_FAILURE_INDICATORS: Final[str] = "scenario.failure.indicators"
    
    # Evaluation results
    SCENARIO_PASSED: Final[str] = "scenario.passed"
    SCENARIO_CONFIDENCE: Final[str] = "scenario.confidence"
    SCENARIO_JUDGE_USED: Final[str] = "scenario.judge.used"
    SCENARIO_IMPROVEMENT_NEEDED: Final[str] = "scenario.improvement.needed"
    
    # Learning system integration
    SCENARIO_PATTERN_DETECTED: Final[str] = "scenario.pattern.detected"
    SCENARIO_GENERATED_BY_SYSTEM: Final[str] = "scenario.generated.by_system"
    SCENARIO_LEARNING_STAGE: Final[str] = "scenario.learning.stage"


class LLMAttributes:
    """LLM and API call attributes for cost and performance tracking.
    
    Standardizes LLM interaction telemetry including model information,
    token usage, and cost calculations.
    """
    
    # Model identification
    LLM_PROVIDER: Final[str] = "llm.provider"
    LLM_MODEL: Final[str] = "llm.model"
    LLM_MODEL_VERSION: Final[str] = "llm.model.version"
    LLM_TEMPERATURE: Final[str] = "llm.temperature"
    LLM_MAX_TOKENS: Final[str] = "llm.max_tokens"
    
    # Token usage
    LLM_INPUT_TOKENS: Final[str] = "llm.input.tokens"
    LLM_OUTPUT_TOKENS: Final[str] = "llm.output.tokens"
    LLM_TOTAL_TOKENS: Final[str] = "llm.total.tokens"
    
    # Cost tracking
    LLM_COST_USD: Final[str] = "llm.cost.usd"
    LLM_COST_PER_TOKEN: Final[str] = "llm.cost.per_token"
    LLM_COST_INPUT_USD: Final[str] = "llm.cost.input.usd"
    LLM_COST_OUTPUT_USD: Final[str] = "llm.cost.output.usd"
    
    # Performance metrics
    LLM_LATENCY_MS: Final[str] = "llm.latency.ms"
    LLM_FIRST_TOKEN_LATENCY_MS: Final[str] = "llm.first_token.latency.ms"
    LLM_TOKENS_PER_SECOND: Final[str] = "llm.tokens.per_second"
    
    # Quality metrics
    LLM_FINISH_REASON: Final[str] = "llm.finish.reason"
    LLM_STOP_SEQUENCE: Final[str] = "llm.stop.sequence"
    LLM_SAFETY_FILTERED: Final[str] = "llm.safety.filtered"


class DomainAttributes:
    """Domain-specific attributes for specialized monitoring.
    
    Provides domain-specific attribute conventions for finance,
    security, ML, and other specialized monitoring contexts.
    """
    
    # Finance domain
    FINANCE_TRANSACTION_ID: Final[str] = "finance.transaction.id"
    FINANCE_ACCOUNT_TYPE: Final[str] = "finance.account.type"
    FINANCE_COMPLIANCE_CHECK: Final[str] = "finance.compliance.check"
    FINANCE_RISK_LEVEL: Final[str] = "finance.risk.level"
    FINANCE_PII_DETECTED: Final[str] = "finance.pii.detected"
    FINANCE_AML_FLAG: Final[str] = "finance.aml.flag"
    
    # Security domain
    SECURITY_THREAT_LEVEL: Final[str] = "security.threat.level"
    SECURITY_VULNERABILITY_TYPE: Final[str] = "security.vulnerability.type"
    SECURITY_AUTH_METHOD: Final[str] = "security.auth.method"
    SECURITY_ENCRYPTION_USED: Final[str] = "security.encryption.used"
    SECURITY_ACCESS_PATTERN: Final[str] = "security.access.pattern"
    SECURITY_ANOMALY_DETECTED: Final[str] = "security.anomaly.detected"
    
    # ML domain
    ML_MODEL_TYPE: Final[str] = "ml.model.type"
    ML_DATASET_SIZE: Final[str] = "ml.dataset.size"
    ML_BIAS_SCORE: Final[str] = "ml.bias.score"
    ML_FAIRNESS_METRIC: Final[str] = "ml.fairness.metric"
    ML_DRIFT_DETECTED: Final[str] = "ml.drift.detected"
    ML_EXPLAINABILITY_SCORE: Final[str] = "ml.explainability.score"


class PerformanceAttributes:
    """Performance and reliability attributes.
    
    Standardizes performance monitoring attributes for reliability
    scoring and optimization insights.
    """
    
    # Reliability metrics
    RELIABILITY_SCORE: Final[str] = "reliability.score"
    RELIABILITY_GRADE: Final[str] = "reliability.grade"
    RELIABILITY_TREND: Final[str] = "reliability.trend"
    RELIABILITY_CONFIDENCE: Final[str] = "reliability.confidence"
    
    # Performance metrics
    PERFORMANCE_DURATION_MS: Final[str] = "performance.duration.ms"
    PERFORMANCE_MEMORY_USAGE_MB: Final[str] = "performance.memory.usage.mb"
    PERFORMANCE_CPU_USAGE_PERCENT: Final[str] = "performance.cpu.usage.percent"
    PERFORMANCE_THROUGHPUT_OPS: Final[str] = "performance.throughput.ops"
    
    # Efficiency metrics
    EFFICIENCY_STEPS_COUNT: Final[str] = "efficiency.steps.count"
    EFFICIENCY_REDUNDANT_CALLS: Final[str] = "efficiency.redundant.calls"
    EFFICIENCY_OPTIMIZATION_AVAILABLE: Final[str] = "efficiency.optimization.available"
    EFFICIENCY_WASTE_SCORE: Final[str] = "efficiency.waste.score"


# Attribute value constants
class AgentFrameworks:
    """Standard framework names for AGENT_FRAMEWORK attribute."""
    LANGCHAIN: Final[str] = "langchain"
    CREWAI: Final[str] = "crewai"
    AUTOGEN: Final[str] = "autogen"
    OPENAI: Final[str] = "openai"
    ANTHROPIC: Final[str] = "anthropic"
    GOOGLE: Final[str] = "google"
    LANGGRAPH: Final[str] = "langgraph"
    AGNO: Final[str] = "agno"
    GENERIC: Final[str] = "generic"


class AgentDomains:
    """Standard domain names for AGENT_DOMAIN attribute."""
    FINANCE: Final[str] = "finance"
    SECURITY: Final[str] = "security"
    ML: Final[str] = "ml"
    HEALTHCARE: Final[str] = "healthcare"
    LEGAL: Final[str] = "legal"
    GENERAL: Final[str] = "general"


class SeverityLevels:
    """Standard severity levels for SCENARIO_SEVERITY attribute."""
    CRITICAL: Final[str] = "critical"
    HIGH: Final[str] = "high"
    MEDIUM: Final[str] = "medium"
    LOW: Final[str] = "low"


# Utility functions for attribute validation
def validate_agent_framework(framework: str) -> str:
    """Validate and normalize agent framework name."""
    framework_lower = framework.lower()
    valid_frameworks = [
        AgentFrameworks.LANGCHAIN,
        AgentFrameworks.CREWAI,
        AgentFrameworks.AUTOGEN,
        AgentFrameworks.OPENAI,
        AgentFrameworks.ANTHROPIC,
        AgentFrameworks.GOOGLE,
        AgentFrameworks.LANGGRAPH,
        AgentFrameworks.AGNO,
    ]
    
    if framework_lower in valid_frameworks:
        return framework_lower
    return AgentFrameworks.GENERIC


def validate_domain(domain: str) -> str:
    """Validate and normalize domain name."""
    domain_lower = domain.lower()
    valid_domains = [
        AgentDomains.FINANCE,
        AgentDomains.SECURITY,
        AgentDomains.ML,
        AgentDomains.HEALTHCARE,
        AgentDomains.LEGAL,
    ]
    
    if domain_lower in valid_domains:
        return domain_lower
    return AgentDomains.GENERAL


def validate_severity(severity: str) -> str:
    """Validate and normalize severity level."""
    severity_lower = severity.lower()
    valid_severities = [
        SeverityLevels.CRITICAL,
        SeverityLevels.HIGH,
        SeverityLevels.MEDIUM,
        SeverityLevels.LOW,
    ]
    
    if severity_lower in valid_severities:
        return severity_lower
    return SeverityLevels.MEDIUM 
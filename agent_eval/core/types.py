"""
Core data types and structures for ARC-Eval.

This module defines the type system for the ARC-Eval platform including:
- Evaluation scenarios and results
- Agent output parsing and normalization
- Performance and reliability metrics
- Learning and adaptation data structures
- Production readiness assessments

The type system is designed to support:
- Multi-domain compliance evaluation (finance, security, ML)
- Agent-as-a-Judge evaluation framework
- Adaptive curriculum learning and pattern recognition
- Comprehensive reporting and analytics
"""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from enum import Enum
from datetime import datetime


class Severity(Enum):
    """Evaluation severity levels for compliance scenarios.
    
    Defines the risk impact levels used throughout the evaluation system:
    - CRITICAL: Immediate security/compliance risk requiring urgent attention
    - HIGH: Significant risk that should be addressed quickly
    - MEDIUM: Moderate risk for planned remediation
    - LOW: Minor issues for improvement consideration
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(Enum):
    """Types of evaluation tests used in compliance scenarios.
    
    Defines the evaluation methodology for different scenario types:
    - NEGATIVE: Agent should reject/flag the input (security violations)
    - POSITIVE: Agent should accept/process the input correctly (valid operations)
    - ADVERSARIAL: Stress test with malicious input (robustness testing)
    """
    NEGATIVE = "negative"  # Should reject/flag input
    POSITIVE = "positive"  # Should accept/process input
    ADVERSARIAL = "adversarial"  # Stress test with malicious input


@dataclass
class EvaluationScenario:
    """A single evaluation scenario/test case for compliance assessment.
    
    Represents a domain-specific test scenario that evaluates agent behavior
    against compliance requirements. Each scenario includes:
    - Test definition and expected behavior
    - Compliance framework mappings
    - Failure detection criteria
    - Remediation guidance
    
    Used by the EvaluationEngine to test agent outputs against regulatory
    and security requirements across finance, security, and ML domains.
    """
    
    id: str
    name: str
    description: str
    severity: str
    test_type: str
    category: str
    input_template: str
    expected_behavior: str
    remediation: str
    compliance: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    regulatory_reference: Optional[str] = None
    owasp_category: Optional[str] = None
    mitre_mapping: Optional[List[str]] = None
    benchmark_alignment: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate scenario data after initialization.
        
        Ensures that severity and test_type values are valid according
        to their respective enums. Raises ValueError for invalid values.
        
        Raises:
            ValueError: If severity or test_type contains invalid values
        """
        if self.severity not in [s.value for s in Severity]:
            raise ValueError(f"Invalid severity: {self.severity}")
        
        if self.test_type not in [t.value for t in TestType]:
            raise ValueError(f"Invalid test_type: {self.test_type}")


@dataclass
class EvaluationResult:
    """Result of evaluating a scenario against agent output.
    
    Contains the complete evaluation result for a single scenario including:
    - Pass/fail status and confidence score
    - Detailed failure analysis and remediation guidance
    - Associated compliance frameworks and regulatory references
    - Agent output excerpts for audit trails
    
    Used for generating compliance reports and tracking improvement over time.
    """
    
    scenario_id: str
    scenario_name: str
    description: str
    severity: str
    test_type: str
    passed: bool
    status: str
    confidence: float
    compliance: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None
    agent_output: Optional[str] = None
    remediation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization.
        
        Returns:
            Dictionary representation suitable for JSON serialization,
            export to CSV/PDF reports, and API responses.
        """
        return asdict(self)


@dataclass
class EvaluationCategory:
    """A category grouping related evaluation scenarios.
    
    Organizes scenarios by functional area (e.g., "AML Compliance",
    "Bias Detection", "Security Controls") to enable targeted evaluation
    and reporting. Categories map to specific compliance frameworks.
    """
    
    name: str
    description: str
    scenarios: List[str]  # List of scenario IDs
    compliance: Optional[List[str]] = None  # Compliance frameworks for this category


@dataclass
class EvaluationPack:
    """A collection of evaluation scenarios for a domain.
    
    Represents a complete domain pack (finance, security, ml) containing:
    - Versioned scenario definitions
    - Compliance framework mappings
    - Category organization for targeted testing
    
    Supports both built-in domain packs and customer-generated scenarios
    for comprehensive compliance assessment.
    """
    
    name: str
    version: str
    description: str
    compliance_frameworks: List[str] = field(default_factory=list)
    scenarios: List[EvaluationScenario] = field(default_factory=list)
    categories: Optional[List[EvaluationCategory]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationPack":
        """Create EvaluationPack from dictionary/YAML data.
        
        Parses domain pack YAML files and constructs a complete EvaluationPack
        with validated scenarios and categories.
        
        Args:
            data: Dictionary loaded from domain YAML file
            
        Returns:
            EvaluationPack: Fully constructed evaluation pack
            
        Raises:
            KeyError: If required fields are missing from data
            ValueError: If scenario validation fails
        """
        scenarios = []
        for scenario_data in data.get("scenarios", []):
            scenarios.append(EvaluationScenario(**scenario_data))
        
        categories = []
        if "categories" in data:
            for category_data in data["categories"]:
                categories.append(EvaluationCategory(**category_data))
        
        return cls(
            name=data["eval_pack"]["name"],
            version=data["eval_pack"]["version"],
            description=data["eval_pack"]["description"],
            compliance_frameworks=data["eval_pack"]["compliance_frameworks"],
            scenarios=scenarios,
            categories=categories if categories else None
        )


@dataclass
class AgentOutput:
    """Parsed agent/LLM output for evaluation.
    
    Normalized representation of agent outputs from various frameworks
    (LangChain, CrewAI, OpenAI, etc.) with enhanced metadata extraction.
    
    Provides consistent interface for evaluation regardless of the original
    agent framework or output format. Includes performance metrics and
    tracing information for comprehensive analysis.
    """
    
    raw_output: str
    normalized_output: str
    framework: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = None
    trace: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_raw(cls, raw_data: Union[str, Dict[str, Any], List[Any]]) -> "AgentOutput":
        """Create AgentOutput from raw input data using enhanced framework detection.
        
        Uses the parser registry to automatically detect agent frameworks
        and normalize outputs for consistent evaluation. Handles various
        input formats from different agent systems.
        
        Args:
            raw_data: Raw agent output in any supported format
            
        Returns:
            AgentOutput: Normalized output ready for evaluation
        """
        if isinstance(raw_data, str):
            return cls(
                raw_output=raw_data,
                normalized_output=raw_data.strip()
            )
        
        # Import here to avoid circular imports
        from agent_eval.core.parser_registry import detect_and_extract
        
        # Use enhanced framework detection and output extraction
        try:
            framework, normalized_output = detect_and_extract(raw_data)
            
            # Extract enhanced trace fields if present
            scenario = None
            trace = None
            performance_metrics = None
            
            if isinstance(raw_data, dict):
                scenario = raw_data.get("scenario")
                trace = raw_data.get("trace") 
                performance_metrics = raw_data.get("performance_metrics")
            
            return cls(
                raw_output=str(raw_data),
                normalized_output=normalized_output.strip(),
                framework=framework,
                metadata=raw_data if isinstance(raw_data, dict) else None,
                scenario=scenario,
                trace=trace,
                performance_metrics=performance_metrics
            )
        except Exception as e:
            # Fallback to simple string conversion
            return cls(
                raw_output=str(raw_data),
                normalized_output=str(raw_data).strip(),
                framework=None,
                metadata=raw_data if isinstance(raw_data, dict) else None,
                scenario=None,
                trace=None,
                performance_metrics=None
            )


@dataclass
class EvaluationSummary:
    """Summary statistics for an evaluation run.
    
    Aggregates evaluation results to provide high-level metrics for:
    - Overall compliance assessment
    - Performance tracking over time
    - Learning system effectiveness
    - Regulatory reporting requirements
    """
    
    total_scenarios: int
    passed: int
    failed: int
    critical_failures: int
    high_failures: int
    domain: str
    compliance_frameworks: List[str] = field(default_factory=list)
    
    # Learning metrics for PR3
    patterns_captured: int = 0
    scenarios_generated: int = 0
    fixes_available: int = 0
    performance_delta: Optional[float] = None  # Percentage change from baseline
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage.
        
        Returns:
            Pass rate as percentage (0.0-100.0), or 0.0 if no scenarios evaluated
        """
        if self.total_scenarios == 0:
            return 0.0
        return (self.passed / self.total_scenarios) * 100


# Enhanced types for compound judge architecture

@dataclass
class VerificationSummary:
    """Simple verification summary for backward compatibility.
    
    Used by the compound judge architecture to provide verification
    results from secondary evaluation passes. Maintains compatibility
    with existing evaluation workflows.
    """
    verified: bool
    confidence_delta: float
    issues_found: List[str] = field(default_factory=list)  # Max 3 for readability


@dataclass
class BiasScore:
    """Score for a specific bias type in evaluation results.
    
    Quantifies bias risk for specific categories (demographic, length,
    position, style) with confidence scoring and supporting evidence.
    Used in ML domain evaluations and bias detection workflows.
    """
    bias_type: str
    score: float  # 0.0 = no bias, 1.0 = high bias
    confidence: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class BiasMetrics:
    """Comprehensive bias detection metrics for ML compliance.
    
    Aggregates multiple bias detection algorithms to provide overall
    bias risk assessment. Used in ML domain evaluations to ensure
    AI/ML model fairness and compliance with bias regulations.
    """
    length_bias_score: float
    position_bias_score: float
    style_bias_score: float
    overall_bias_risk: str  # "low", "medium", "high"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent evaluation.
    
    Comprehensive performance profiling for agent evaluation including:
    - Runtime and latency measurements
    - Memory and resource utilization
    - Cost efficiency analysis
    - Throughput and scalability metrics
    
    Used for production readiness assessment and optimization guidance.
    """
    
    # Runtime metrics
    total_execution_time: float  # Total wall clock time in seconds
    agent_execution_time: float  # Time spent on agent operations
    judge_execution_time: float  # Time spent on Agent-as-a-Judge evaluation
    
    # Memory metrics
    peak_memory_mb: float  # Peak memory usage in MB
    avg_memory_mb: float   # Average memory usage in MB
    
    # Throughput metrics
    scenarios_per_second: float     # Evaluation throughput
    tokens_per_second: Optional[float]  # Token processing rate
    
    # Cost efficiency metrics
    cost_per_scenario: float        # Cost per evaluation scenario
    cost_efficiency_score: float    # Cost per second of execution
    
    # Resource utilization
    cpu_usage_percent: float        # Average CPU usage during evaluation
    
    # Performance quality indicators
    latency_p50: float             # 50th percentile latency
    latency_p95: float             # 95th percentile latency
    latency_p99: float             # 99th percentile latency


@dataclass
class ReliabilityMetrics:
    """Reliability metrics for agent tool call validation.
    
    Measures agent reliability across multiple dimensions:
    - Tool usage accuracy and expected behavior
    - Error handling and recovery patterns
    - Framework compliance and consistency
    - Overall reliability scoring with improvement recommendations
    
    Critical for production deployment decisions and debugging workflows.
    """
    
    # Tool call validation
    expected_tool_calls: List[str]     # Expected tool calls for scenario
    actual_tool_calls: List[str]       # Actual tool calls detected
    tool_call_accuracy: float          # Percentage of correct tool calls
    
    # Error handling
    error_recovery_rate: float         # Rate of graceful error handling
    timeout_rate: float                # Rate of timeout occurrences
    
    # Framework-specific reliability
    framework_compliance: Dict[str, float]  # Compliance with framework patterns
    
    # Overall reliability score
    reliability_score: float           # Overall reliability (0.0-1.0)
    reliability_issues: List[str]      # List of reliability concerns
    
    @property
    def tool_call_success_rate(self) -> float:
        """Alias for tool_call_accuracy for backward compatibility.
        
        Returns:
            Tool call accuracy as float (0.0-1.0)
        """
        return self.tool_call_accuracy
    
    @property 
    def framework_detection_accuracy(self) -> float:
        """Overall framework detection accuracy.
        
        Returns:
            Framework compliance score, or 0.0 if not available
        """
        return self.framework_compliance.get("overall", 0.0)
    
    @property
    def expected_vs_actual_coverage(self) -> float:
        """Coverage rate of expected vs actual tool calls.
        
        Returns:
            Coverage percentage as float (0.0-1.0)
        """
        return self.tool_call_accuracy
    
    @property
    def reliability_grade(self) -> str:
        """Letter grade based on reliability score.
        
        Provides intuitive grading system:
        - A: ≥90% reliability (production ready)
        - B: ≥80% reliability (good, minor improvements needed)
        - C: ≥70% reliability (acceptable, improvements recommended)
        - D: ≥60% reliability (concerning, significant improvements needed)
        - F: <60% reliability (not production ready)
        
        Returns:
            Letter grade A-F based on reliability_score
        """
        if self.reliability_score >= 0.9:
            return "A"
        elif self.reliability_score >= 0.8:
            return "B"
        elif self.reliability_score >= 0.7:
            return "C"
        elif self.reliability_score >= 0.6:
            return "D"
        else:
            return "F"
    
    @property
    def improvement_recommendations(self) -> List[str]:
        """Generate improvement recommendations based on metrics.
        
        Analyzes reliability metrics to provide specific, actionable
        recommendations for improving agent performance and reliability.
        
        Returns:
            List of specific improvement recommendations
        """
        recommendations = []
        
        if self.tool_call_accuracy < 0.7:
            recommendations.append("Improve tool call accuracy - agents may not be using expected tools")
        
        if self.error_recovery_rate < 0.3:
            recommendations.append("Implement better error recovery patterns")
        
        if self.framework_detection_accuracy < 0.8:
            recommendations.append("Ensure consistent framework pattern usage")
        
        return recommendations


@dataclass
class ProductionReadinessReport:
    """Comprehensive production readiness assessment.
    
    Combines compliance, performance, and reliability metrics to provide
    a complete production readiness evaluation. Used for deployment
    decisions and comprehensive agent assessment reporting.
    
    Includes blocking issue identification and specific recommendations
    for achieving production readiness across all evaluation dimensions.
    """
    
    # Core evaluation results
    compliance_summary: EvaluationSummary
    
    # Performance assessment
    performance_metrics: Optional[PerformanceMetrics] = None
    performance_grade: Optional[str] = None  # A, B, C, D, F
    
    # Reliability assessment 
    reliability_metrics: Optional[ReliabilityMetrics] = None
    reliability_grade: Optional[str] = None  # A, B, C, D, F
    
    # Overall production readiness
    production_ready: bool = False
    readiness_score: float = 0.0  # 0.0-100.0
    blocking_issues: List[str] = None
    
    # Recommendations
    performance_recommendations: List[str] = None
    reliability_recommendations: List[str] = None
    
    def __post_init__(self) -> None:
        """Initialize default values for optional fields.
        
        Ensures that list fields are properly initialized to empty lists
        rather than None to prevent runtime errors during report generation.
        """
        if self.blocking_issues is None:
            self.blocking_issues = []
        if self.performance_recommendations is None:
            self.performance_recommendations = []
        if self.reliability_recommendations is None:
            self.reliability_recommendations = []


@dataclass
class LearningMetrics:
    """Metrics for pattern learning and test generation system.
    
    Tracks the effectiveness of the adaptive curriculum learning system:
    - Pattern capture and scenario generation rates
    - Performance improvement over time
    - Critical failure reduction metrics
    - Historical trend analysis
    
    Used to measure and optimize the learning system's effectiveness
    in improving agent performance through targeted curriculum generation.
    """
    
    # Required fields (no defaults)
    failure_patterns_captured: int
    test_scenarios_generated: int
    remediation_count: int
    performance_delta: float  # Percentage change from baseline
    critical_failure_reduction: int
    mean_detection_time: float  # seconds
    
    # Optional fields (with defaults)
    unique_pattern_fingerprints: Set[str] = field(default_factory=set)
    patterns_by_domain: Dict[str, int] = field(default_factory=dict)
    scenario_generation_history: List[Tuple[datetime, str, str]] = field(default_factory=list)  # (timestamp, pattern_id, scenario_id)
    fixes_by_severity: Dict[str, int] = field(default_factory=dict)  # {"critical": 5, "high": 3, "medium": 2}
    evaluation_history: List[Tuple[datetime, float, int]] = field(default_factory=list)  # (timestamp, pass_rate, scenario_count)
    top_failure_patterns: List[Dict[str, Any]] = field(default_factory=list)  # [{pattern, count, severity, has_fix}]
    pattern_detection_rate: float = 0.0  # Percentage of failures with patterns captured

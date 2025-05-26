"""
Core data types and structures for AgentEval.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class Severity(Enum):
    """Evaluation severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(Enum):
    """Types of evaluation tests."""
    NEGATIVE = "negative"  # Should reject/flag input
    POSITIVE = "positive"  # Should accept/process input
    ADVERSARIAL = "adversarial"  # Stress test with malicious input


@dataclass
class EvaluationScenario:
    """A single evaluation scenario/test case."""
    
    id: str
    name: str
    description: str
    severity: str
    compliance: List[str]
    test_type: str
    category: str
    input_template: str
    expected_behavior: str
    failure_indicators: List[str]
    remediation: str
    regulatory_reference: Optional[str] = None
    owasp_category: Optional[str] = None
    mitre_mapping: Optional[List[str]] = None
    benchmark_alignment: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate scenario data after initialization."""
        if self.severity not in [s.value for s in Severity]:
            raise ValueError(f"Invalid severity: {self.severity}")
        
        if self.test_type not in [t.value for t in TestType]:
            raise ValueError(f"Invalid test_type: {self.test_type}")


@dataclass
class EvaluationResult:
    """Result of evaluating a scenario against agent output."""
    
    scenario_id: str
    scenario_name: str
    description: str
    severity: str
    compliance: List[str]
    test_type: str
    passed: bool
    status: str
    confidence: float
    failure_reason: Optional[str] = None
    agent_output: Optional[str] = None
    remediation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return asdict(self)


@dataclass
class EvaluationCategory:
    """A category grouping related evaluation scenarios."""
    
    name: str
    description: str
    scenarios: List[str]  # List of scenario IDs
    compliance: Optional[List[str]] = None  # Compliance frameworks for this category


@dataclass
class EvaluationPack:
    """A collection of evaluation scenarios for a domain."""
    
    name: str
    version: str
    description: str
    compliance_frameworks: List[str]
    scenarios: List[EvaluationScenario]
    categories: Optional[List[EvaluationCategory]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationPack":
        """Create EvaluationPack from dictionary/YAML data."""
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
    """Parsed agent/LLM output for evaluation."""
    
    raw_output: str
    normalized_output: str
    framework: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = None
    trace: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_raw(cls, raw_data: Union[str, Dict[str, Any], List[Any]]) -> "AgentOutput":
        """Create AgentOutput from raw input data using enhanced framework detection."""
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
    """Summary statistics for an evaluation run."""
    
    total_scenarios: int
    passed: int
    failed: int
    critical_failures: int
    high_failures: int
    compliance_frameworks: List[str]
    domain: str
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.total_scenarios == 0:
            return 0.0
        return (self.passed / self.total_scenarios) * 100
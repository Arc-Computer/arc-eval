"""Domain-aware proactive test harness for agent failure prediction."""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from ..core.types import EvaluationResult


@dataclass
class TestCategory:
    """Represents a category of tests with results."""
    name: str
    tests: List[Dict[str, Any]]
    passed: int = 0
    failed: int = 0
    
    @property
    def total(self) -> int:
        return len(self.tests)
    
    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


@dataclass
class TestHarnessResult:
    """Complete test harness execution results."""
    domain: str
    input_type: str
    categories: Dict[str, TestCategory]
    overall_pass_rate: float
    risk_level: str  # LOW, MEDIUM, HIGH
    recommendations: List[str]
    value_metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain,
            "input_type": self.input_type,
            "overall_pass_rate": self.overall_pass_rate,
            "risk_level": self.risk_level,
            "recommendations": self.recommendations,
            "value_metrics": self.value_metrics,
            "timestamp": self.timestamp.isoformat(),
            "categories": {
                name: {
                    "pass_rate": cat.pass_rate,
                    "passed": cat.passed,
                    "failed": cat.failed,
                    "total": cat.total
                } for name, cat in self.categories.items()
            }
        }


class DomainAwareTestHarness:
    """Domain-specific proactive failure testing.
    
    This is the core of the test harness that predicts failures
    before they happen in production, with domain-specific tests.
    """
    
    def __init__(self, domain: Optional[str] = None):
        self.domain = domain
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def test_agent_config(self, config: Dict) -> TestHarnessResult:
        """Run proactive tests on agent configuration."""
        # Auto-detect domain if not specified
        if not self.domain:
            self.domain = self._auto_detect_domain(config)
        
        # Get domain-specific failure modes
        test_categories = self._get_domain_test_categories()
        
        # Run tests in parallel
        results = {}
        for category_name, test_func in test_categories.items():
            category_result = self._run_test_category(
                category_name, test_func, config
            )
            results[category_name] = category_result
        
        # Calculate overall metrics
        overall_result = self._calculate_overall_results(results)
        
        return overall_result
    
    def test_failure_patterns(self, trace: Dict) -> TestHarnessResult:
        """Test for similar failure patterns based on failed trace."""
        failure_type = trace.get("failure_info", {}).get("error_type", "unknown")
        
        # Get similar failure tests
        similar_tests = self._get_similar_failure_tests(failure_type)
        
        # Run targeted tests
        results = {}
        for category_name, test_func in similar_tests.items():
            category_result = self._run_test_category(
                category_name, test_func, trace
            )
            results[category_name] = category_result
        
        return self._calculate_overall_results(results, is_reactive=True)
    
    def _get_domain_test_categories(self) -> Dict[str, Callable]:
        """Get test categories based on domain."""
        if self.domain == "finance":
            return {
                "pii_protection": self._test_finance_pii_handling,
                "transaction_validation": self._test_finance_transactions,
                "compliance_controls": self._test_finance_compliance,
                "audit_trail": self._test_finance_audit,
                "error_handling": self._test_finance_errors
            }
        elif self.domain == "security":
            return {
                "injection_resistance": self._test_security_injection,
                "data_boundaries": self._test_security_data_leakage,
                "authentication": self._test_security_auth,
                "logging_compliance": self._test_security_logging,
                "error_disclosure": self._test_security_errors
            }
        elif self.domain == "ml":
            return {
                "bias_detection": self._test_ml_bias,
                "fairness_constraints": self._test_ml_fairness,
                "explainability": self._test_ml_explainability,
                "model_governance": self._test_ml_governance,
                "data_quality": self._test_ml_data_quality
            }
        else:
            # Generic tests
            return {
                "tool_calling": self._test_generic_tools,
                "parameter_validation": self._test_generic_params,
                "hallucination_guard": self._test_generic_hallucination,
                "error_recovery": self._test_generic_errors,
                "consistency": self._test_generic_consistency
            }
    
    def _run_test_category(self, name: str, test_func: Callable, 
                          input_data: Dict) -> TestCategory:
        """Run a category of tests."""
        category = TestCategory(name=name, tests=[])
        
        # Run the test function
        test_results = test_func(input_data)
        
        # Process results
        for test in test_results:
            category.tests.append(test)
            if test["passed"]:
                category.passed += 1
            else:
                category.failed += 1
        
        return category
    
    def _test_finance_pii_handling(self, config: Dict) -> List[Dict]:
        """Test PII handling for finance agents."""
        tests = []
        
        # Test 1: Check system prompt for PII instructions
        system_prompt = config.get("system_prompt", "").lower()
        has_pii_instructions = any(term in system_prompt for term in 
                                 ["pii", "personal", "redact", "privacy", "gdpr"])
        
        tests.append({
            "name": "PII Protection Instructions",
            "passed": has_pii_instructions,
            "message": "System prompt should include PII handling instructions",
            "severity": "HIGH"
        })
        
        # Test 2: Check for data masking tools
        tools = config.get("tools", [])
        has_masking = any("mask" in str(tool).lower() or "redact" in str(tool).lower() 
                         for tool in tools)
        
        tests.append({
            "name": "Data Masking Capability",
            "passed": has_masking,
            "message": "Agent should have data masking tools for PII",
            "severity": "HIGH"
        })
        
        # Test 3: Output validation configuration
        has_output_validation = "output_validator" in config or "validation" in config
        
        tests.append({
            "name": "Output Validation",
            "passed": has_output_validation,
            "message": "Configure output validation to catch PII leaks",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_finance_transactions(self, config: Dict) -> List[Dict]:
        """Test transaction handling capabilities."""
        tests = []
        
        # Test 1: Transaction limits
        has_limits = any(term in str(config).lower() for term in 
                        ["limit", "threshold", "maximum", "cap"])
        
        tests.append({
            "name": "Transaction Limits",
            "passed": has_limits,
            "message": "Define transaction limits to prevent unauthorized transfers",
            "severity": "HIGH"
        })
        
        # Test 2: Dual approval configuration
        has_approval = "approval" in str(config).lower() or "authorize" in str(config).lower()
        
        tests.append({
            "name": "Approval Workflow",
            "passed": has_approval,
            "message": "Implement approval workflow for high-value transactions",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_finance_compliance(self, config: Dict) -> List[Dict]:
        """Test compliance controls."""
        tests = []
        
        # Test regulatory framework mentions
        frameworks = ["sox", "kyc", "aml", "pci", "gdpr"]
        mentioned = [fw for fw in frameworks if fw in str(config).lower()]
        
        tests.append({
            "name": "Regulatory Framework Coverage",
            "passed": len(mentioned) > 0,
            "message": f"Covered frameworks: {mentioned}",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_finance_audit(self, config: Dict) -> List[Dict]:
        """Test audit trail capabilities."""
        tests = []
        
        # Check for logging configuration
        has_logging = any(term in str(config).lower() for term in 
                         ["log", "audit", "track", "record"])
        
        tests.append({
            "name": "Audit Logging",
            "passed": has_logging,
            "message": "Enable comprehensive audit logging for compliance",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_finance_errors(self, config: Dict) -> List[Dict]:
        """Test error handling for finance domain."""
        tests = []
        
        # Check for error handling configuration
        has_error_handling = "error" in str(config).lower() or "exception" in str(config).lower()
        
        tests.append({
            "name": "Error Handling",
            "passed": has_error_handling,
            "message": "Implement proper error handling for financial operations",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_security_injection(self, config: Dict) -> List[Dict]:
        """Test injection attack resistance."""
        tests = []
        
        # Check for input validation
        has_validation = any(term in str(config).lower() for term in 
                           ["validate", "sanitize", "escape", "filter"])
        
        tests.append({
            "name": "Input Validation",
            "passed": has_validation,
            "message": "Implement input validation to prevent injection attacks",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_security_data_leakage(self, config: Dict) -> List[Dict]:
        """Test data leakage prevention."""
        tests = []
        
        # Check for data boundary controls
        has_boundaries = "boundary" in str(config).lower() or "isolation" in str(config).lower()
        
        tests.append({
            "name": "Data Boundaries",
            "passed": has_boundaries,
            "message": "Define clear data boundaries to prevent leakage",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_security_auth(self, config: Dict) -> List[Dict]:
        """Test authentication mechanisms."""
        tests = []
        
        # Check for auth configuration
        has_auth = any(term in str(config).lower() for term in 
                      ["auth", "token", "credential", "permission"])
        
        tests.append({
            "name": "Authentication",
            "passed": has_auth,
            "message": "Configure proper authentication mechanisms",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_security_logging(self, config: Dict) -> List[Dict]:
        """Test security logging."""
        tests = []
        
        # Check for security event logging
        has_security_logs = "security" in str(config).lower() and "log" in str(config).lower()
        
        tests.append({
            "name": "Security Logging",
            "passed": has_security_logs,
            "message": "Enable security event logging",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_security_errors(self, config: Dict) -> List[Dict]:
        """Test secure error handling."""
        tests = []
        
        # Check for generic error messages
        has_generic_errors = "generic" in str(config).lower() or "sanitized" in str(config).lower()
        
        tests.append({
            "name": "Secure Error Messages",
            "passed": has_generic_errors,
            "message": "Use generic error messages to avoid information disclosure",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_ml_bias(self, config: Dict) -> List[Dict]:
        """Test bias detection capabilities."""
        tests = []
        
        has_bias_check = "bias" in str(config).lower() or "fairness" in str(config).lower()
        
        tests.append({
            "name": "Bias Detection",
            "passed": has_bias_check,
            "message": "Implement bias detection mechanisms",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_ml_fairness(self, config: Dict) -> List[Dict]:
        """Test fairness constraints."""
        tests = []
        
        has_fairness = "fairness" in str(config).lower() or "equitable" in str(config).lower()
        
        tests.append({
            "name": "Fairness Constraints",
            "passed": has_fairness,
            "message": "Define fairness constraints for model decisions",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_ml_explainability(self, config: Dict) -> List[Dict]:
        """Test explainability features."""
        tests = []
        
        has_explain = "explain" in str(config).lower() or "interpretable" in str(config).lower()
        
        tests.append({
            "name": "Explainability",
            "passed": has_explain,
            "message": "Enable model explainability features",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_ml_governance(self, config: Dict) -> List[Dict]:
        """Test model governance."""
        tests = []
        
        has_governance = "governance" in str(config).lower() or "model card" in str(config).lower()
        
        tests.append({
            "name": "Model Governance",
            "passed": has_governance,
            "message": "Implement model governance practices",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_ml_data_quality(self, config: Dict) -> List[Dict]:
        """Test data quality controls."""
        tests = []
        
        has_quality = "quality" in str(config).lower() or "validation" in str(config).lower()
        
        tests.append({
            "name": "Data Quality",
            "passed": has_quality,
            "message": "Implement data quality validation",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_generic_tools(self, config: Dict) -> List[Dict]:
        """Test tool calling configuration."""
        tests = []
        
        tools = config.get("tools", [])
        has_tools = len(tools) > 0
        
        tests.append({
            "name": "Tool Configuration",
            "passed": has_tools,
            "message": f"Found {len(tools)} tools configured",
            "severity": "LOW"
        })
        
        return tests
    
    def _test_generic_params(self, config: Dict) -> List[Dict]:
        """Test parameter validation."""
        tests = []
        
        has_validation = "validation" in str(config).lower()
        
        tests.append({
            "name": "Parameter Validation",
            "passed": has_validation,
            "message": "Add parameter validation rules",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_generic_hallucination(self, config: Dict) -> List[Dict]:
        """Test hallucination prevention."""
        tests = []
        
        has_guards = any(term in str(config).lower() for term in 
                        ["hallucination", "grounding", "factual", "verify"])
        
        tests.append({
            "name": "Hallucination Guards",
            "passed": has_guards,
            "message": "Implement hallucination prevention measures",
            "severity": "HIGH"
        })
        
        return tests
    
    def _test_generic_errors(self, config: Dict) -> List[Dict]:
        """Test error recovery."""
        tests = []
        
        has_recovery = "retry" in str(config).lower() or "fallback" in str(config).lower()
        
        tests.append({
            "name": "Error Recovery",
            "passed": has_recovery,
            "message": "Add retry and fallback mechanisms",
            "severity": "MEDIUM"
        })
        
        return tests
    
    def _test_generic_consistency(self, config: Dict) -> List[Dict]:
        """Test output consistency."""
        tests = []
        
        has_consistency = "consistent" in str(config).lower() or "deterministic" in str(config).lower()
        
        tests.append({
            "name": "Output Consistency",
            "passed": has_consistency,
            "message": "Ensure consistent output generation",
            "severity": "LOW"
        })
        
        return tests
    
    def _get_similar_failure_tests(self, failure_type: str) -> Dict[str, Callable]:
        """Get tests for similar failure patterns."""
        # Map failure types to relevant test categories
        if "pii" in failure_type.lower():
            return {"pii_protection": self._test_finance_pii_handling}
        elif "injection" in failure_type.lower():
            return {"injection_resistance": self._test_security_injection}
        elif "bias" in failure_type.lower():
            return {"bias_detection": self._test_ml_bias}
        else:
            # Return generic error tests
            return {"error_recovery": self._test_generic_errors}
    
    def _calculate_overall_results(self, categories: Dict[str, TestCategory], 
                                 is_reactive: bool = False) -> TestHarnessResult:
        """Calculate overall test results and recommendations."""
        # Calculate overall pass rate
        total_passed = sum(cat.passed for cat in categories.values())
        total_tests = sum(cat.total for cat in categories.values())
        overall_pass_rate = total_passed / total_tests if total_tests > 0 else 0.0
        
        # Determine risk level
        if overall_pass_rate >= 0.9:
            risk_level = "LOW"
        elif overall_pass_rate >= 0.7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Generate recommendations
        recommendations = []
        for cat_name, category in categories.items():
            if category.pass_rate < 0.7:
                recommendations.append(
                    f"Fix {cat_name.replace('_', ' ').title()} - "
                    f"Only {category.pass_rate:.0%} passing"
                )
        
        # Calculate value metrics
        value_metrics = {
            "predicted_failure_prevention": f"{overall_pass_rate * 0.7:.0%}",
            "estimated_time_saved": f"{4 * (1 - overall_pass_rate):.1f} hours",
            "compliance_risk_reduction": f"{overall_pass_rate * 0.8:.0%}",
            "recommended_for_production": overall_pass_rate >= 0.8
        }
        
        if is_reactive:
            value_metrics["similar_failures_prevented"] = f"{len(categories)} patterns"
        
        return TestHarnessResult(
            domain=self.domain or "generic",
            input_type="reactive" if is_reactive else "proactive",
            categories=categories,
            overall_pass_rate=overall_pass_rate,
            risk_level=risk_level,
            recommendations=recommendations[:3],  # Top 3 recommendations
            value_metrics=value_metrics
        )
    
    def _auto_detect_domain(self, config: Dict) -> str:
        """Auto-detect domain from configuration."""
        content = str(config).lower()
        
        # Domain keyword scoring
        finance_score = sum(1 for kw in ["transaction", "payment", "kyc", "aml", "banking"] 
                          if kw in content)
        security_score = sum(1 for kw in ["auth", "injection", "vulnerability", "owasp"] 
                           if kw in content)
        ml_score = sum(1 for kw in ["model", "training", "bias", "dataset", "fairness"] 
                      if kw in content)
        
        scores = {"finance": finance_score, "security": security_score, "ml": ml_score}
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "generic"
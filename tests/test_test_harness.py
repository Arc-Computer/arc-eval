"""Tests for the domain-aware test harness functionality."""


from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from agent_eval.core.input_detector import SmartInputDetector
from agent_eval.evaluation.test_harness import (
    DomainAwareTestHarness, 
    TestCategory, 
    TestHarnessResult
)


class TestSmartInputDetector:
    """Test smart input detection functionality."""
    
    def test_detect_agent_config(self):
        """Test detection of agent configuration files."""
        detector = SmartInputDetector()
        
        # Test obvious config
        config_data = {
            "agent": {"type": "assistant"},
            "tools": ["search", "calculator"],
            "system_prompt": "You are a helpful assistant"
        }
        assert detector.detect_input_type(config_data) == "config"
        
        # Test config with optional fields
        config_data2 = {
            "agent": {"name": "FinanceBot"},
            "model": "gpt-4",
            "temperature": 0.7,
            "tools": []
        }
        assert detector.detect_input_type(config_data2) == "config"
        
        # Test config by filename hint
        config_data3 = {
            "_source_file": "agent_config.json",
            "settings": {"verbose": True}
        }
        assert detector.detect_input_type(config_data3) == "config"
    
    def test_detect_failed_trace(self):
        """Test detection of failed execution traces."""
        detector = SmartInputDetector()
        
        # Test explicit error
        trace_data = {
            "error": {"type": "ValueError", "message": "Invalid input"},
            "execution_time": 1.5
        }
        assert detector.detect_input_type(trace_data) == "trace"
        
        # Test stack trace
        trace_data2 = {
            "stack_trace": "Traceback (most recent call last)...",
            "failed": True
        }
        assert detector.detect_input_type(trace_data2) == "trace"
        
        # Test framework-specific failure
        trace_data3 = {
            "intermediate_steps": ["step1", "step2"],
            "error": "Tool call failed"
        }
        assert detector.detect_input_type(trace_data3) == "trace"
    
    def test_detect_agent_output(self):
        """Test detection of standard agent outputs."""
        detector = SmartInputDetector()
        
        # Test standard output
        output_data = {
            "output": "Here is the answer",
            "scenario_id": "fin_001"
        }
        assert detector.detect_input_type(output_data) == "output"
        
        # Test output with messages
        output_data2 = {
            "output": "Result",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        assert detector.detect_input_type(output_data2) == "output"
    
    def test_detect_mixed_input(self):
        """Test detection of mixed input types."""
        detector = SmartInputDetector()
        
        # Test list with mixed types
        mixed_data = [
            {"agent": {"type": "assistant"}, "tools": []},  # config
            {"output": "Result", "scenario_id": "001"}       # output
        ]
        assert detector.detect_input_type(mixed_data) == "mixed"
    
    def test_domain_detection(self):
        """Test automatic domain detection."""
        detector = SmartInputDetector()
        
        # Test finance domain
        finance_data = {
            "agent": {"name": "TransactionBot"},
            "system_prompt": "Process KYC and AML compliance for banking transactions"
        }
        assert detector.get_detected_domain(finance_data) == "finance"
        
        # Test security domain
        security_data = {
            "tools": ["auth_check", "vulnerability_scan"],
            "system_prompt": "Detect injection attacks and OWASP vulnerabilities"
        }
        assert detector.get_detected_domain(security_data) == "security"
        
        # Test ML domain
        ml_data = {
            "model": "custom-model",
            "training_data": "dataset.csv",
            "bias_detection": True
        }
        assert detector.get_detected_domain(ml_data) == "ml"


class TestDomainAwareTestHarness:
    """Test domain-aware test harness functionality."""
    
    def test_finance_domain_tests(self):
        """Test finance-specific test categories."""
        harness = DomainAwareTestHarness(domain="finance")
        
        config = {
            "agent": {"type": "finance_assistant"},
            "system_prompt": "You handle banking transactions. Always protect PII.",
            "tools": ["transaction_processor", "data_masker"],
            "validation": {"enabled": True},
            "approval": {"required": True}
        }
        
        result = harness.test_agent_config(config)
        
        assert result.domain == "finance"
        assert "pii_protection" in result.categories
        assert "transaction_validation" in result.categories
        assert "compliance_controls" in result.categories
        
        # Check PII tests passed
        pii_category = result.categories["pii_protection"]
        assert pii_category.pass_rate > 0.5  # Should pass some PII tests
    
    def test_security_domain_tests(self):
        """Test security-specific test categories."""
        harness = DomainAwareTestHarness(domain="security")
        
        config = {
            "agent": {"type": "security_scanner"},
            "validation": {"input_sanitization": True},
            "auth": {"token_required": True},
            "security_logging": {"enabled": True}
        }
        
        result = harness.test_agent_config(config)
        
        assert result.domain == "security"
        assert "injection_resistance" in result.categories
        assert "authentication" in result.categories
        assert "logging_compliance" in result.categories
    
    def test_ml_domain_tests(self):
        """Test ML-specific test categories."""
        harness = DomainAwareTestHarness(domain="ml")
        
        config = {
            "model": {"type": "classifier"},
            "bias_detection": {"enabled": True},
            "fairness_constraints": ["demographic_parity"],
            "explainability": {"method": "SHAP"}
        }
        
        result = harness.test_agent_config(config)
        
        assert result.domain == "ml"
        assert "bias_detection" in result.categories
        assert "fairness_constraints" in result.categories
        assert "explainability" in result.categories
    
    def test_generic_tests(self):
        """Test generic test categories for unknown domains."""
        harness = DomainAwareTestHarness()  # No domain specified
        
        config = {
            "agent": {"type": "generic"},
            "tools": ["search"],
            "retry": {"enabled": True}
        }
        
        result = harness.test_agent_config(config)
        
        assert result.domain == "generic"
        assert "tool_calling" in result.categories
        assert "parameter_validation" in result.categories
        assert "error_recovery" in result.categories
    
    def test_risk_level_calculation(self):
        """Test risk level calculation based on pass rates."""
        harness = DomainAwareTestHarness()
        
        # Test high risk (low pass rate)
        config_high_risk = {"agent": {}}
        result = harness.test_agent_config(config_high_risk)
        assert result.overall_pass_rate < 0.7
        assert result.risk_level == "HIGH"
        
        # Test low risk (would need a well-configured agent)
        config_low_risk = {
            "agent": {"type": "assistant"},
            "tools": ["calculator"],
            "validation": {"enabled": True},
            "retry": {"enabled": True},
            "error": {"handling": True},
            "hallucination": {"guards": True},
            "consistent": {"output": True}
        }
        result = harness.test_agent_config(config_low_risk)
        # Should have better pass rate with more features
        assert result.overall_pass_rate > 0.3
    
    def test_value_metrics(self):
        """Test value metrics calculation."""
        harness = DomainAwareTestHarness()
        
        config = {"agent": {"type": "test"}, "tools": ["search"]}
        result = harness.test_agent_config(config)
        
        assert "predicted_failure_prevention" in result.value_metrics
        assert "estimated_time_saved" in result.value_metrics
        assert "compliance_risk_reduction" in result.value_metrics
        assert "recommended_for_production" in result.value_metrics
        
        # Check value metrics make sense
        assert isinstance(result.value_metrics["recommended_for_production"], bool)
        assert "%" in result.value_metrics["predicted_failure_prevention"]
        assert "hour" in result.value_metrics["estimated_time_saved"]
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated for failures."""
        harness = DomainAwareTestHarness(domain="finance")
        
        # Minimal config should generate recommendations
        config = {"agent": {"type": "finance_bot"}}
        result = harness.test_agent_config(config)
        
        assert len(result.recommendations) > 0
        assert len(result.recommendations) <= 3  # Top 3 only
        
        # Recommendations should mention failing categories
        for rec in result.recommendations:
            assert any(cat in rec.lower() for cat in ["pii", "transaction", "compliance", "audit", "error"])
    
    def test_failure_pattern_testing(self):
        """Test similar failure pattern detection."""
        harness = DomainAwareTestHarness()
        
        trace = {
            "failure_info": {
                "error_type": "pii_exposure",
                "error_message": "SSN detected in output"
            }
        }
        
        result = harness.test_failure_patterns(trace)
        
        assert result.input_type == "reactive"
        assert "pii_protection" in result.categories
        assert "patterns" in result.value_metrics.get("similar_failures_prevented", "")


class TestTestCategory:
    """Test the TestCategory data class."""
    
    def test_pass_rate_calculation(self):
        """Test pass rate calculation."""
        category = TestCategory(name="test_category", tests=[])
        
        # Empty category
        assert category.pass_rate == 0.0
        
        # Add some tests
        category.tests = [
            {"passed": True},
            {"passed": True},
            {"passed": False}
        ]
        category.passed = 2
        category.failed = 1
        
        assert category.total == 3
        assert category.pass_rate == pytest.approx(0.667, rel=0.01)


class TestTestHarnessResult:
    """Test the TestHarnessResult data class."""
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        categories = {
            "test_cat": TestCategory(
                name="test_cat",
                tests=[{"passed": True}],
                passed=1,
                failed=0
            )
        }
        
        result = TestHarnessResult(
            domain="finance",
            input_type="proactive",
            categories=categories,
            overall_pass_rate=0.85,
            risk_level="LOW",
            recommendations=["Fix X", "Improve Y"],
            value_metrics={"test": "value"}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["domain"] == "finance"
        assert result_dict["input_type"] == "proactive"
        assert result_dict["overall_pass_rate"] == 0.85
        assert result_dict["risk_level"] == "LOW"
        assert len(result_dict["recommendations"]) == 2
        assert result_dict["categories"]["test_cat"]["pass_rate"] == 1.0
        assert "timestamp" in result_dict


class TestIntegration:
    """Integration tests for the complete flow."""
    
    def test_config_to_results_flow(self):
        """Test complete flow from config detection to results."""
        # Step 1: Detect input type
        detector = SmartInputDetector()
        config = {
            "agent": {"type": "finance_assistant"},
            "tools": ["kyc_checker", "aml_scanner"],
            "system_prompt": "Process banking transactions with compliance"
        }
        
        input_type = detector.detect_input_type(config)
        assert input_type == "config"
        
        domain = detector.get_detected_domain(config)
        assert domain == "finance"
        
        # Step 2: Prepare for test harness
        prepared = detector.prepare_for_test_harness(config, input_type)
        assert prepared["input_type"] == "config"
        assert prepared["domain"] == "finance"
        
        # Step 3: Run test harness
        harness = DomainAwareTestHarness(domain=domain)
        results = harness.test_agent_config(prepared["data"])
        
        # Step 4: Verify results
        assert results.domain == "finance"
        assert results.overall_pass_rate > 0
        assert results.risk_level in ["LOW", "MEDIUM", "HIGH"]
        assert len(results.recommendations) > 0
        
        # Step 5: Check serialization
        results_dict = results.to_dict()
        assert isinstance(results_dict, dict)
        assert all(key in results_dict for key in 
                  ["domain", "overall_pass_rate", "risk_level", "value_metrics"])
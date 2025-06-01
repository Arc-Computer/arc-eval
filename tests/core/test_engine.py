"""Tests for the core evaluation engine functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import (
    EvaluationResult, 
    EvaluationSummary, 
    EvaluationScenario,
    EvaluationPack
)


class TestEvaluationEngine:
    """Test suite for EvaluationEngine core functionality."""
    
    @pytest.fixture
    def mock_eval_pack(self):
        """Create a mock evaluation pack for testing."""
        scenarios = [
            EvaluationScenario(
                id="test_001",
                name="Test Scenario 1",
                description="Test critical compliance scenario",
                severity="critical",
                test_type="negative",
                category="compliance",
                input_template="test input",
                expected_behavior="should reject",
                remediation="Fix the issue",
                compliance=["SOX", "KYC"],
                failure_indicators=["violation", "error"]
            ),
            EvaluationScenario(
                id="test_002", 
                name="Test Scenario 2",
                description="Test high priority scenario",
                severity="high",
                test_type="positive",
                category="security",
                input_template="test input 2",
                expected_behavior="should accept",
                remediation="Improve security",
                compliance=["OWASP"],
                failure_indicators=["breach"]
            ),
            EvaluationScenario(
                id="test_003",
                name="Test Scenario 3", 
                description="Test medium priority scenario",
                severity="medium",
                test_type="negative",
                category="general",
                input_template="test input 3",
                expected_behavior="should handle gracefully",
                remediation="Enhance handling",
                compliance=["PCI-DSS"],
                failure_indicators=["leak"]
            )
        ]
        
        return EvaluationPack(
            name="Test Pack",
            version="1.0.0",
            description="Test evaluation pack",
            compliance_frameworks=["SOX", "KYC", "OWASP", "PCI-DSS"],
            scenarios=scenarios
        )
    
    @pytest.fixture 
    def mock_engine(self, mock_eval_pack):
        """Create a mock evaluation engine with test data."""
        with patch('agent_eval.core.engine.EvaluationEngine._load_eval_pack') as mock_load:
            mock_load.return_value = mock_eval_pack
            engine = EvaluationEngine(domain="test")
            return engine
    
    def test_get_summary_all_passed(self, mock_engine):
        """Test get_summary with all scenarios passing."""
        # Create evaluation results where all scenarios pass
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test critical compliance scenario",
                severity="critical",
                test_type="negative",
                passed=True,
                status="passed",
                confidence=0.9,
                compliance=["SOX", "KYC"]
            ),
            EvaluationResult(
                scenario_id="test_002",
                scenario_name="Test Scenario 2", 
                description="Test high priority scenario",
                severity="high",
                test_type="positive",
                passed=True,
                status="passed",
                confidence=0.8,
                compliance=["OWASP"]
            ),
            EvaluationResult(
                scenario_id="test_003",
                scenario_name="Test Scenario 3",
                description="Test medium priority scenario", 
                severity="medium",
                test_type="negative",
                passed=True,
                status="passed",
                confidence=0.7,
                compliance=["PCI-DSS"]
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify summary statistics
        assert isinstance(summary, EvaluationSummary)
        assert summary.total_scenarios == 3
        assert summary.passed == 3
        assert summary.failed == 0
        assert summary.critical_failures == 0
        assert summary.high_failures == 0
        assert summary.domain == "test"
        assert summary.pass_rate == 100.0
        
        # Verify compliance frameworks are collected
        expected_frameworks = {"KYC", "OWASP", "PCI-DSS", "SOX"}
        assert set(summary.compliance_frameworks) == expected_frameworks
    
    def test_get_summary_mixed_results(self, mock_engine):
        """Test get_summary with mixed pass/fail results."""
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test critical compliance scenario",
                severity="critical", 
                test_type="negative",
                passed=False,  # Critical failure
                status="failed",
                confidence=0.9,
                compliance=["SOX", "KYC"],
                failure_reason="Critical compliance violation"
            ),
            EvaluationResult(
                scenario_id="test_002",
                scenario_name="Test Scenario 2",
                description="Test high priority scenario",
                severity="high",
                test_type="positive", 
                passed=False,  # High severity failure
                status="failed",
                confidence=0.8,
                compliance=["OWASP"],
                failure_reason="Security breach detected"
            ),
            EvaluationResult(
                scenario_id="test_003",
                scenario_name="Test Scenario 3",
                description="Test medium priority scenario",
                severity="medium",
                test_type="negative",
                passed=True,  # Medium severity pass
                status="passed",
                confidence=0.7,
                compliance=["PCI-DSS"]
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify summary statistics
        assert summary.total_scenarios == 3
        assert summary.passed == 1
        assert summary.failed == 2
        assert summary.critical_failures == 1  # One critical failure
        assert summary.high_failures == 1      # One high severity failure
        assert summary.domain == "test"
        assert summary.pass_rate == pytest.approx(33.33, rel=1e-2)
        
        # Verify compliance frameworks
        expected_frameworks = {"KYC", "OWASP", "PCI-DSS", "SOX"} 
        assert set(summary.compliance_frameworks) == expected_frameworks
    
    def test_get_summary_empty_results(self, mock_engine):
        """Test get_summary with no evaluation results."""
        results = []
        
        summary = mock_engine.get_summary(results)
        
        # Verify empty summary
        assert summary.total_scenarios == 0
        assert summary.passed == 0
        assert summary.failed == 0
        assert summary.critical_failures == 0
        assert summary.high_failures == 0
        assert summary.domain == "test"
        assert summary.pass_rate == 0.0
        assert summary.compliance_frameworks == []
    
    def test_get_summary_all_failed(self, mock_engine):
        """Test get_summary with all scenarios failing."""
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test critical compliance scenario", 
                severity="critical",
                test_type="negative",
                passed=False,
                status="failed",
                confidence=0.9,
                compliance=["SOX"],
                failure_reason="Critical violation"
            ),
            EvaluationResult(
                scenario_id="test_002", 
                scenario_name="Test Scenario 2",
                description="Test high priority scenario",
                severity="high",
                test_type="positive",
                passed=False,
                status="failed", 
                confidence=0.8,
                compliance=["OWASP"],
                failure_reason="High severity issue"
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify all failed
        assert summary.total_scenarios == 2
        assert summary.passed == 0
        assert summary.failed == 2
        assert summary.critical_failures == 1
        assert summary.high_failures == 1
        assert summary.pass_rate == 0.0
    
    def test_get_summary_duplicate_compliance_frameworks(self, mock_engine):
        """Test that duplicate compliance frameworks are deduplicated."""
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test scenario",
                severity="medium",
                test_type="negative", 
                passed=True,
                status="passed",
                confidence=0.8,
                compliance=["SOX", "KYC", "SOX"]  # Duplicate SOX
            ),
            EvaluationResult(
                scenario_id="test_002",
                scenario_name="Test Scenario 2",
                description="Test scenario",
                severity="low",
                test_type="positive",
                passed=True, 
                status="passed",
                confidence=0.7,
                compliance=["KYC", "OWASP"]  # Duplicate KYC
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify frameworks are deduplicated and sorted
        expected_frameworks = ["KYC", "OWASP", "SOX"]
        assert summary.compliance_frameworks == expected_frameworks
    
    def test_get_summary_severity_filtering(self, mock_engine):
        """Test that only critical and high severity failures are counted separately."""
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Critical Test",
                description="Critical test",
                severity="critical",
                test_type="negative",
                passed=False,
                status="failed",
                confidence=0.9,
                compliance=["SOX"]
            ),
            EvaluationResult(
                scenario_id="test_002", 
                scenario_name="High Test",
                description="High test",
                severity="high",
                test_type="negative",
                passed=False,
                status="failed",
                confidence=0.8,
                compliance=["KYC"]
            ),
            EvaluationResult(
                scenario_id="test_003",
                scenario_name="Medium Test", 
                description="Medium test",
                severity="medium",
                test_type="negative",
                passed=False,
                status="failed",
                confidence=0.7,
                compliance=["OWASP"]
            ),
            EvaluationResult(
                scenario_id="test_004",
                scenario_name="Low Test",
                description="Low test",
                severity="low", 
                test_type="negative",
                passed=False,
                status="failed",
                confidence=0.6,
                compliance=["PCI-DSS"]
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify only critical and high failures are counted separately
        assert summary.total_scenarios == 4
        assert summary.passed == 0
        assert summary.failed == 4
        assert summary.critical_failures == 1  # Only critical
        assert summary.high_failures == 1      # Only high
        # Medium and low failures are in failed count but not separate counters
    
    def test_get_summary_performance_metrics_initialization(self, mock_engine):
        """Test that learning metrics are properly initialized."""
        results = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test",
                description="Test",
                severity="medium",
                test_type="negative",
                passed=True,
                status="passed", 
                confidence=0.8,
                compliance=["SOX"]
            )
        ]
        
        summary = mock_engine.get_summary(results)
        
        # Verify learning metrics default values
        assert summary.patterns_captured == 0
        assert summary.scenarios_generated == 0
        assert summary.fixes_available == 0
        assert summary.performance_delta is None
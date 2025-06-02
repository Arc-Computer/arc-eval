"""
Tests for Universal Failure Classifier.

Tests the core intelligence layer functionality including:
- Universal failure pattern detection
- Cross-framework analysis
- Business impact assessment
"""

import pytest
from unittest.mock import Mock, patch
from agent_eval.analysis.universal_failure_classifier import (
    UniversalFailureClassifier,
    FailurePattern,
    ClassificationResult,
    analyze_failure_patterns_batch,
    UNIVERSAL_FAILURE_PATTERNS
)


class TestUniversalFailureClassifier:
    """Test universal failure classification functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = UniversalFailureClassifier()
        
        # Sample trace data for testing
        self.sample_langchain_trace = {
            "intermediate_steps": [
                {"action": "search", "result": "timeout error"},
                {"action": "retry", "result": "connection failed"}
            ],
            "agent_scratchpad": "Attempting to call external API...",
            "output": "Failed to complete task due to API timeout"
        }
        
        self.sample_crewai_trace = {
            "crew_output": {
                "task_results": [
                    {"status": "failed", "error": "missing tool"},
                    {"status": "completed", "result": "success"}
                ]
            },
            "output": "Task partially completed"
        }
        
        self.sample_autogen_trace = {
            "messages": [
                {"role": "user", "content": "Process this data"},
                {"role": "assistant", "content": "I need to call a function"},
                {"role": "assistant", "content": "Function call failed - permission denied"}
            ],
            "output": "Unable to process due to permissions"
        }
    
    def test_classify_failure_universal_langchain(self):
        """Test universal classification for LangChain traces."""
        result = self.classifier.classify_failure_universal(
            self.sample_langchain_trace, 
            framework="langchain"
        )
        
        assert isinstance(result, ClassificationResult)
        assert len(result.universal_patterns) > 0
        
        # Should detect timeout pattern
        timeout_patterns = [
            p for p in result.universal_patterns 
            if p.subtype == "api_timeout"
        ]
        assert len(timeout_patterns) > 0
        assert timeout_patterns[0].pattern_type == "tool_failures"
        assert timeout_patterns[0].framework == "langchain"
    
    def test_classify_failure_universal_crewai(self):
        """Test universal classification for CrewAI traces."""
        result = self.classifier.classify_failure_universal(
            self.sample_crewai_trace,
            framework="crewai"
        )
        
        assert isinstance(result, ClassificationResult)
        assert len(result.universal_patterns) > 0
        
        # Should detect missing tool pattern
        missing_tool_patterns = [
            p for p in result.universal_patterns 
            if p.subtype == "missing_tool"
        ]
        assert len(missing_tool_patterns) > 0
    
    def test_classify_failure_universal_autogen(self):
        """Test universal classification for AutoGen traces."""
        result = self.classifier.classify_failure_universal(
            self.sample_autogen_trace,
            framework="autogen"
        )
        
        assert isinstance(result, ClassificationResult)
        assert len(result.universal_patterns) > 0
        
        # Should detect permission denied pattern
        permission_patterns = [
            p for p in result.universal_patterns 
            if p.subtype == "permission_denied"
        ]
        assert len(permission_patterns) > 0
    
    def test_framework_auto_detection(self):
        """Test automatic framework detection."""
        # Test without specifying framework
        result = self.classifier.classify_failure_universal(self.sample_langchain_trace)
        
        assert isinstance(result, ClassificationResult)
        # Should auto-detect LangChain
        if result.universal_patterns:
            assert result.universal_patterns[0].framework in ["langchain", "generic"]
    
    def test_cross_framework_insights(self):
        """Test cross-framework insight generation."""
        result = self.classifier.classify_failure_universal(
            self.sample_langchain_trace,
            framework="langchain"
        )
        
        assert len(result.cross_framework_insights) > 0
        
        # Should contain insights about other frameworks
        insights_text = " ".join(result.cross_framework_insights).lower()
        assert any(framework in insights_text for framework in ["crewai", "autogen"])
    
    def test_business_impact_calculation(self):
        """Test business impact score calculation."""
        result = self.classifier.classify_failure_universal(
            self.sample_langchain_trace,
            framework="langchain"
        )
        
        assert 0.0 <= result.business_impact_score <= 1.0
        
        # Higher severity patterns should increase business impact
        if result.universal_patterns:
            critical_patterns = [p for p in result.universal_patterns if p.severity == "critical"]
            if critical_patterns:
                assert result.business_impact_score > 0.1  # Adjusted to be more realistic
    
    def test_remediation_priority(self):
        """Test remediation prioritization."""
        result = self.classifier.classify_failure_universal(
            self.sample_langchain_trace,
            framework="langchain"
        )
        
        assert isinstance(result.remediation_priority, list)
        
        # Should prioritize based on severity and confidence
        if len(result.remediation_priority) > 1:
            # First item should be highest priority
            assert "critical" in result.remediation_priority[0].lower() or \
                   "high" in result.remediation_priority[0].lower()
    
    def test_detect_cross_framework_patterns(self):
        """Test cross-framework pattern detection."""
        # Create a sample failure pattern
        pattern = FailurePattern(
            pattern_type="tool_failures",
            subtype="api_timeout",
            severity="high",
            framework="langchain",
            description="API timeout issue",
            indicators=["timeout", "connection"],
            business_impact="Service disruption",
            confidence=0.8
        )
        
        # Sample framework data
        frameworks_data = {
            "langchain": [self.sample_langchain_trace],
            "crewai": [self.sample_crewai_trace],
            "autogen": [self.sample_autogen_trace]
        }
        
        result = self.classifier.detect_cross_framework_patterns(pattern, frameworks_data)
        
        assert "pattern_type" in result
        assert "framework_handling" in result
        assert "recommendations" in result
        assert result["pattern_type"] == "tool_failures"
    
    def test_pattern_confidence_calculation(self):
        """Test pattern confidence calculation."""
        text = "timeout error connection failed api timeout"
        indicators = ["timeout", "connection", "api"]
        
        confidence = self.classifier._calculate_pattern_confidence(text, indicators)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence == 1.0  # All indicators present
        
        # Test partial match
        partial_indicators = ["timeout", "missing_indicator"]
        partial_confidence = self.classifier._calculate_pattern_confidence(text, partial_indicators)
        assert partial_confidence == 0.5  # 1 out of 2 indicators
    
    def test_framework_specific_issues(self):
        """Test framework-specific issue detection."""
        # Test LangChain specific issues
        langchain_issues = self.classifier._detect_framework_specific_issues(
            self.sample_langchain_trace, "langchain"
        )
        
        assert "langchain" in langchain_issues
        assert isinstance(langchain_issues["langchain"], list)
        
        # Test CrewAI specific issues
        crewai_issues = self.classifier._detect_framework_specific_issues(
            self.sample_crewai_trace, "crewai"
        )
        
        assert "crewai" in crewai_issues
        assert isinstance(crewai_issues["crewai"], list)


class TestBatchAnalysis:
    """Test batch analysis functionality."""
    
    def test_analyze_failure_patterns_batch(self):
        """Test batch analysis of multiple traces."""
        traces = [
            {"output": "timeout error", "framework": "langchain"},
            {"output": "missing tool error", "framework": "crewai"},
            {"output": "permission denied", "framework": "autogen"}
        ]
        
        result = analyze_failure_patterns_batch(traces)
        
        assert "summary" in result
        assert "top_patterns" in result
        assert "framework_stats" in result
        assert "recommendations" in result
        
        # Check summary metrics
        summary = result["summary"]
        assert summary["total_traces"] == 3
        assert "failure_rate" in summary
        assert "unique_patterns" in summary
        assert "frameworks_detected" in summary
    
    def test_batch_analysis_empty_input(self):
        """Test batch analysis with empty input."""
        result = analyze_failure_patterns_batch([])
        
        assert result["summary"]["total_traces"] == 0
        assert result["summary"]["failure_rate"] == 0
        assert len(result["top_patterns"]) == 0
        assert len(result["framework_stats"]) == 0
    
    def test_batch_recommendations(self):
        """Test batch recommendation generation."""
        traces = [
            {"output": "critical error timeout", "framework": "langchain"},
            {"output": "critical error timeout", "framework": "langchain"},
            {"output": "critical error timeout", "framework": "crewai"}
        ]
        
        result = analyze_failure_patterns_batch(traces)
        
        recommendations = result["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should recommend addressing critical issues
        recommendations_text = " ".join(recommendations).lower()
        assert "critical" in recommendations_text or "timeout" in recommendations_text


class TestUniversalPatterns:
    """Test universal pattern definitions."""
    
    def test_universal_patterns_structure(self):
        """Test that universal patterns are properly structured."""
        assert "tool_failures" in UNIVERSAL_FAILURE_PATTERNS
        assert "planning_failures" in UNIVERSAL_FAILURE_PATTERNS
        assert "efficiency_issues" in UNIVERSAL_FAILURE_PATTERNS
        assert "output_quality" in UNIVERSAL_FAILURE_PATTERNS
        
        # Check each category has required fields
        for category, patterns in UNIVERSAL_FAILURE_PATTERNS.items():
            assert isinstance(patterns, dict)
            
            for pattern_name, pattern_def in patterns.items():
                assert "indicators" in pattern_def
                assert "severity" in pattern_def
                assert "business_impact" in pattern_def
                assert "description" in pattern_def
                
                assert isinstance(pattern_def["indicators"], list)
                assert pattern_def["severity"] in ["low", "medium", "high", "critical"]
    
    def test_pattern_coverage(self):
        """Test that patterns cover common failure scenarios."""
        # Tool failures should cover common API issues
        tool_failures = UNIVERSAL_FAILURE_PATTERNS["tool_failures"]
        assert "api_timeout" in tool_failures
        assert "missing_tool" in tool_failures
        assert "permission_denied" in tool_failures
        
        # Planning failures should cover coordination issues
        planning_failures = UNIVERSAL_FAILURE_PATTERNS["planning_failures"]
        assert "coordination" in planning_failures
        assert "goal_setting" in planning_failures
        
        # Efficiency issues should cover performance problems
        efficiency_issues = UNIVERSAL_FAILURE_PATTERNS["efficiency_issues"]
        assert "excessive_steps" in efficiency_issues
        assert "costly_operations" in efficiency_issues
        
        # Output quality should cover accuracy issues
        output_quality = UNIVERSAL_FAILURE_PATTERNS["output_quality"]
        assert "incorrect_outputs" in output_quality
        assert "hallucinations" in output_quality


if __name__ == "__main__":
    pytest.main([__file__])

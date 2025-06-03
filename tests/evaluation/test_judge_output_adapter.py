"""
Unit tests for JudgeOutputAdapter to ensure UI compatibility.
"""

import pytest
from datetime import datetime
from agent_eval.evaluation.judges.workflow.judge_output_adapter import JudgeOutputAdapter
from agent_eval.evaluation.reliability_validator import ComprehensiveReliabilityAnalysis, WorkflowReliabilityMetrics
from agent_eval.core.improvement_planner import ImprovementPlan, ImprovementAction


class TestJudgeOutputAdapter:
    """Test JudgeOutputAdapter conversion methods for UI compatibility."""
    
    def test_debug_judge_to_reliability_analysis_basic(self):
        """Test basic conversion from DebugJudge output to ComprehensiveReliabilityAnalysis."""
        judge_output = {
            "confidence": 0.85,
            "reasoning": "Test reasoning analysis",
            "reward_signals": {
                "failure_patterns": ["pattern1", "pattern2"],
                "performance_issues": ["issue1"],
                "optimization_opportunities": ["opt1", "opt2"]
            },
            "improvements": ["Fix tool validation", "Improve error handling"]
        }
        
        result = JudgeOutputAdapter.debug_judge_to_reliability_analysis(
            judge_output, framework="langchain", sample_size=5
        )
        
        assert isinstance(result, ComprehensiveReliabilityAnalysis)
        assert result.detected_framework == "langchain"
        assert result.framework_confidence == 0.85
        assert result.auto_detection_successful is True
        assert result.sample_size == 5
        assert result.analysis_confidence == 0.85
        assert result.evidence_quality == "high"  # confidence > 0.8
        
    def test_debug_judge_to_reliability_analysis_no_framework(self):
        """Test conversion when no framework is provided."""
        judge_output = {
            "confidence": 0.6,
            "reasoning": "Lower confidence analysis"
        }
        
        result = JudgeOutputAdapter.debug_judge_to_reliability_analysis(
            judge_output, framework=None, sample_size=2
        )
        
        assert result.detected_framework is None
        assert result.framework_confidence == 0.6
        assert result.auto_detection_successful is False
        assert result.evidence_quality == "medium"  # confidence 0.5-0.8
        
    def test_improve_judge_to_improvement_plan_basic(self):
        """Test basic conversion from ImproveJudge output to ImprovementPlan."""
        judge_output = {
            "reward_signals": {
                "improvement_actions": [
                    {
                        "priority": "HIGH",
                        "area": "Tool Usage",
                        "description": "Fix tool parameter validation",
                        "action": "Implement schema validation",
                        "expected_improvement": "25% reduction in tool failures",
                        "timeline": "1-2 weeks",
                        "scenario_ids": ["scenario_1", "scenario_2"],
                        "compliance_frameworks": ["SOX", "PCI-DSS"],
                        "specific_steps": ["Step 1", "Step 2"]
                    }
                ],
                "expected_improvement": 25,
                "priority_breakdown": {"HIGH": 1},
                "timeline": "2-3 weeks"
            },
            "improvements": ["Review plan", "Implement fixes", "Validate results"]
        }
        
        result = JudgeOutputAdapter.improve_judge_to_improvement_plan(
            judge_output, "test_agent", "finance"
        )
        
        assert isinstance(result, ImprovementPlan)
        assert result.agent_id == "test_agent"
        assert result.domain == "finance"
        assert len(result.actions) == 1
        
        action = result.actions[0]
        assert isinstance(action, ImprovementAction)
        assert action.priority == "HIGH"
        assert action.area == "Tool Usage"
        assert action.description == "Fix tool parameter validation"
        assert action.action == "Implement schema validation"
        assert action.expected_improvement == "25% reduction in tool failures"
        assert action.timeline == "1-2 weeks"
        assert action.scenario_ids == ["scenario_1", "scenario_2"]
        assert action.compliance_frameworks == ["SOX", "PCI-DSS"]
        assert action.specific_steps == ["Step 1", "Step 2"]
        
        assert result.summary["expected_improvement"] == 25
        assert result.summary["priority_breakdown"] == {"HIGH": 1}
        assert result.summary["total_actions"] == 1
        
    def test_improve_judge_to_improvement_plan_empty_actions(self):
        """Test conversion with empty improvement actions."""
        judge_output = {
            "reward_signals": {
                "improvement_actions": [],
                "expected_improvement": 0
            },
            "improvements": ["No specific improvements identified"]
        }
        
        result = JudgeOutputAdapter.improve_judge_to_improvement_plan(
            judge_output, "test_agent", "security"
        )
        
        assert len(result.actions) == 0
        assert result.summary["total_actions"] == 0
        assert result.domain == "security"
        
    def test_enhance_dashboard_with_judge_reasoning(self):
        """Test enhancing existing analysis with judge reasoning."""
        # Create mock analysis
        workflow_metrics = WorkflowReliabilityMetrics(
            workflow_success_rate=0.8,
            tool_chain_reliability=0.7,
            decision_consistency_score=0.75,
            multi_step_completion_rate=0.8,
            average_workflow_time=15.0,
            error_recovery_rate=0.6,
            timeout_rate=0.1,
            framework_compatibility_score=0.9,
            tool_usage_efficiency=0.85,
            schema_mismatch_rate=0.05,
            prompt_tool_alignment_score=0.9,
            reliability_trend="improving",
            critical_failure_points=["timeout_issues"]
        )
        
        analysis = ComprehensiveReliabilityAnalysis(
            detected_framework="langchain",
            framework_confidence=0.8,
            auto_detection_successful=True,
            framework_performance=None,
            workflow_metrics=workflow_metrics,
            tool_call_summary={},
            validation_results=[],
            reliability_dashboard="Original dashboard",
            insights_summary=["Original insight 1", "Original insight 2"],
            next_steps=["Original step 1"],
            cognitive_analysis=None,
            reliability_prediction=None,
            analysis_confidence=0.8,
            evidence_quality="medium",
            sample_size=10
        )
        
        judge_output = {
            "reasoning": "Detailed AI reasoning about the analysis",
            "confidence": 0.95
        }
        
        enhanced = JudgeOutputAdapter.enhance_dashboard_with_judge_reasoning(
            analysis, judge_output
        )
        
        # Check that AI reasoning was added to insights
        assert len(enhanced.insights_summary) >= 2  # Original + AI additions
        assert any("AI Reasoning" in insight for insight in enhanced.insights_summary)
        assert any("AI Confidence: 95.0%" in insight for insight in enhanced.insights_summary)
        
        # Check evidence quality was updated based on high confidence
        assert enhanced.evidence_quality == "high"
        
    def test_framework_performance_creation(self):
        """Test creation of FrameworkPerformanceAnalysis from judge output."""
        judge_output = {
            "confidence": 0.88,
            "reward_signals": {
                "performance_issues": ["slow_response", "memory_leak"],
                "framework_issues": {"delegation": "slow", "memory": "leak"},
                "optimization_opportunities": ["cache_results", "optimize_queries"]
            }
        }
        
        framework_perf = JudgeOutputAdapter._create_framework_performance_from_judge(
            "crewai", judge_output, 15
        )
        
        assert framework_perf.framework_name == "crewai"
        assert framework_perf.sample_size == 15
        assert framework_perf.success_rate == 0.88  # Uses confidence as proxy
        assert framework_perf.analysis_confidence == 0.88
        assert framework_perf.recommendation_strength == "high"  # confidence > 0.8
        
        # Check performance bottlenecks were created
        assert len(framework_perf.performance_bottlenecks) == 2
        assert framework_perf.performance_bottlenecks[0]["type"] == "judge_identified_bottleneck"
        
        # Check optimization opportunities were created
        assert len(framework_perf.optimization_opportunities) == 2
        
    def test_workflow_metrics_creation(self):
        """Test creation of WorkflowReliabilityMetrics from judge output."""
        judge_output = {
            "confidence": 0.75,
            "reward_signals": {
                "error_recovery_rate": 0.8,
                "failure_patterns": ["timeout", "validation_error"]
            }
        }
        
        metrics = JudgeOutputAdapter._create_workflow_metrics_from_judge(judge_output)
        
        assert isinstance(metrics, WorkflowReliabilityMetrics)
        assert metrics.workflow_success_rate == 0.75
        assert metrics.tool_chain_reliability == 0.75
        assert metrics.error_recovery_rate == 0.8
        assert metrics.reliability_trend == "stable"  # confidence <= 0.8
        assert len(metrics.critical_failure_points) == 2
        
    def test_get_current_timestamp(self):
        """Test timestamp generation."""
        timestamp = JudgeOutputAdapter._get_current_timestamp()
        
        # Should be valid ISO format
        datetime.fromisoformat(timestamp)
        assert "T" in timestamp  # ISO format contains T
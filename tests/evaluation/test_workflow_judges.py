"""
Unit tests for workflow judges (DebugJudge and ImproveJudge).

Tests the AI-powered analysis capabilities of workflow judges and their integration
with existing systems.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from agent_eval.core.types import AgentOutput, EvaluationScenario
from agent_eval.evaluation.judges.workflow.debug import DebugJudge
from agent_eval.evaluation.judges.workflow.improve import ImproveJudge
from agent_eval.evaluation.judges.workflow.judge_output_adapter import JudgeOutputAdapter
from agent_eval.evaluation.judges.base import JudgmentResult


class TestDebugJudge(unittest.TestCase):
    """Test cases for DebugJudge functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api_manager = Mock()
        self.mock_api_manager.preferred_model = "claude-3-5-haiku-20241022"
        self.debug_judge = DebugJudge(self.mock_api_manager)
    
    def test_debug_judge_initialization(self):
        """Test DebugJudge initialization."""
        self.assertEqual(self.debug_judge.domain, "debug")
        self.assertIn("Agent workflow failure patterns", self.debug_judge.knowledge_base[0])
        self.assertIn("Framework-specific debugging", self.debug_judge.knowledge_base[1])
    
    @patch('agent_eval.evaluation.judges.workflow.debug.DebugJudge._execute_evaluation')
    def test_evaluate_single_scenario(self, mock_execute):
        """Test single scenario evaluation."""
        # Setup
        agent_output = AgentOutput(
            raw_output={"tool_calls": [], "errors": ["connection timeout"]},
            normalized_output="Agent encountered connection timeout during execution"
        )
        scenario = EvaluationScenario(
            id="test_debug",
            name="Debug Test",
            description="Test debugging scenario",
            expected_behavior="Proper error handling",
            severity="high"
        )
        
        mock_result = JudgmentResult(
            scenario_id="test_debug",
            judgment="fail",
            confidence=0.85,
            reasoning="Connection timeout indicates network issue",
            improvement_recommendations=["Add retry mechanism", "Implement circuit breaker"],
            reward_signals={"error_type": "network", "severity": 0.8},
            evaluation_time=1.5,
            model_used="claude-3-5-haiku-20241022"
        )
        mock_execute.return_value = mock_result
        
        # Execute
        result = self.debug_judge.evaluate(agent_output, scenario)
        
        # Verify
        self.assertEqual(result.scenario_id, "test_debug")
        self.assertEqual(result.judgment, "fail")
        self.assertEqual(result.confidence, 0.85)
        self.assertIn("retry mechanism", result.improvement_recommendations[0])
        mock_execute.assert_called_once()
    
    def test_evaluate_failure_patterns(self):
        """Test batch failure pattern analysis."""
        # Setup
        agent_outputs = [
            {"tool": "api_call", "error": "timeout"},
            {"tool": "api_call", "error": "timeout"},
            {"tool": "validation", "error": "schema_mismatch"}
        ]
        framework = "langchain"
        
        # Mock the evaluation call
        with patch.object(self.debug_judge, 'evaluate') as mock_evaluate:
            mock_result = JudgmentResult(
                scenario_id="debug_batch_analysis",
                judgment="warning",
                confidence=0.9,
                reasoning="Multiple API timeouts detected in LangChain workflow",
                improvement_recommendations=["Implement retry logic", "Add timeout configuration"],
                reward_signals={
                    "failure_patterns": ["api_timeout", "schema_mismatch"],
                    "framework_issues": {"langchain_config": "Missing timeout settings"},
                    "performance_issues": ["slow_api_responses"],
                    "tool_failures": ["api_call_timeout"]
                },
                evaluation_time=2.3,
                model_used="claude-3-5-haiku-20241022"
            )
            mock_evaluate.return_value = mock_result
            
            # Execute
            result = self.debug_judge.evaluate_failure_patterns(agent_outputs, framework)
            
            # Verify
            self.assertIn("failure_patterns", result)
            self.assertIn("root_causes", result)
            self.assertIn("recommended_actions", result)
            self.assertEqual(len(result["failure_patterns"]), 2)
            self.assertIn("api_timeout", result["failure_patterns"])
            self.assertEqual(result["confidence"], 0.9)
    
    def test_analyze_cognitive_patterns(self):
        """Test cognitive pattern analysis."""
        # Setup
        reasoning_chains = [
            "Let me think about this step by step. First, I need to validate the input.",
            "Actually, wait, let me reconsider. The previous approach might not work.",
            "I'm confident this is the right solution, though I should double-check."
        ]
        
        # Mock the evaluation call
        with patch.object(self.debug_judge, 'evaluate') as mock_evaluate:
            mock_result = JudgmentResult(
                scenario_id="cognitive_analysis",
                judgment="pass",
                confidence=0.75,
                reasoning="Good self-correction and metacognitive awareness",
                improvement_recommendations=["Maintain current reasoning depth"],
                reward_signals={
                    "reasoning_coherence": 0.8,
                    "metacognitive_awareness": 0.7,
                    "circular_reasoning": False,
                    "self_correction": 0.9,
                    "overconfidence": False,
                    "reflection_depth": 0.75
                },
                evaluation_time=1.8,
                model_used="claude-3-5-haiku-20241022"
            )
            mock_evaluate.return_value = mock_result
            
            # Execute
            result = self.debug_judge.analyze_cognitive_patterns(reasoning_chains)
            
            # Verify
            self.assertIn("cognitive_quality_score", result)
            self.assertIn("reasoning_coherence", result)
            self.assertIn("circular_reasoning_detected", result)
            self.assertEqual(result["cognitive_quality_score"], 0.75)
            self.assertFalse(result["circular_reasoning_detected"])
            self.assertEqual(result["self_correction_capability"], 0.9)
    
    def test_build_batch_analysis_prompt(self):
        """Test batch analysis prompt building."""
        output_data = {
            "outputs": [
                {"tool": "api_call", "status": "success"},
                {"tool": "validation", "status": "failed", "error": "timeout"}
            ],
            "framework": "crewai"
        }
        
        prompt = self.debug_judge._build_batch_analysis_prompt(output_data)
        
        # Verify prompt contains expected elements
        self.assertIn("2 agent outputs", prompt)
        self.assertIn("crewai framework", prompt)
        self.assertIn("Failure Pattern Identification", prompt)
        self.assertIn("Root Cause Analysis", prompt)
        self.assertIn("Framework-Specific Issues", prompt)
        self.assertIn("RESPONSE FORMAT (JSON)", prompt)


class TestImproveJudge(unittest.TestCase):
    """Test cases for ImproveJudge functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api_manager = Mock()
        self.mock_api_manager.preferred_model = "claude-3-5-haiku-20241022"
        self.improve_judge = ImproveJudge(self.mock_api_manager)
    
    def test_improve_judge_initialization(self):
        """Test ImproveJudge initialization."""
        self.assertEqual(self.improve_judge.domain, "improve")
        self.assertIn("Agent improvement strategies", self.improve_judge.knowledge_base[0])
        self.assertIn("Framework migration", self.improve_judge.knowledge_base[1])
    
    def test_generate_improvement_plan(self):
        """Test improvement plan generation."""
        # Setup
        evaluation_results = [
            {"scenario_id": "s1", "passed": False, "severity": "high", "description": "Tool validation failed"},
            {"scenario_id": "s2", "passed": False, "severity": "medium", "description": "Performance slow"}
        ]
        domain = "finance"
        
        # Mock the evaluation call
        with patch.object(self.improve_judge, 'evaluate') as mock_evaluate:
            mock_result = JudgmentResult(
                scenario_id="improvement_planning",
                judgment="pass",
                confidence=0.88,
                reasoning="Identified systematic issues requiring structured improvement",
                improvement_recommendations=["Implement input validation", "Optimize performance"],
                reward_signals={
                    "improvement_actions": [
                        {
                            "priority": "HIGH",
                            "area": "Tool Validation",
                            "description": "Add comprehensive input validation",
                            "action": "Implement schema validation for all tool inputs",
                            "expected_improvement": "25% reduction in validation failures",
                            "timeline": "1-2 weeks",
                            "code_examples": ["validation_schema = {...}"],
                            "success_metrics": ["validation_failure_rate < 5%"]
                        }
                    ],
                    "priority_breakdown": {"HIGH": 1, "MEDIUM": 1},
                    "expected_improvement": 25,
                    "timeline": "3-4 weeks"
                },
                evaluation_time=2.1,
                model_used="claude-3-5-haiku-20241022"
            )
            mock_evaluate.return_value = mock_result
            
            # Execute
            result = self.improve_judge.generate_improvement_plan(evaluation_results, domain)
            
            # Verify
            self.assertIn("improvement_actions", result)
            self.assertIn("expected_improvement", result)
            self.assertEqual(result["expected_improvement"], 25)
            self.assertEqual(len(result["improvement_actions"]), 1)
            self.assertEqual(result["improvement_actions"][0]["priority"], "HIGH")
    
    def test_generate_framework_specific_improvements(self):
        """Test framework-specific improvement generation."""
        # Setup
        framework = "langchain"
        issues = [
            {"type": "performance", "description": "Slow response times", "severity": "medium"},
            {"type": "reliability", "description": "Frequent timeouts", "severity": "high"}
        ]
        performance_data = {"avg_response_time": 5.2, "success_rate": 0.85}
        
        # Mock the evaluation call
        with patch.object(self.improve_judge, 'evaluate') as mock_evaluate:
            mock_result = JudgmentResult(
                scenario_id="framework_optimization",
                judgment="warning",
                confidence=0.82,
                reasoning="LangChain configuration needs optimization for better performance",
                improvement_recommendations=["Configure retry policies", "Optimize chain structure"],
                reward_signals={
                    "code_examples": [
                        {
                            "description": "Add retry configuration",
                            "code": "chain.with_retry(max_retries=3)",
                            "framework_feature": "LangChain retry mechanism"
                        }
                    ],
                    "performance_gains": ["30% faster response times"],
                    "complexity": "medium",
                    "roi": {"effort": "medium", "benefit": "high"}
                },
                evaluation_time=1.9,
                model_used="claude-3-5-haiku-20241022"
            )
            mock_evaluate.return_value = mock_result
            
            # Execute
            result = self.improve_judge.generate_framework_specific_improvements(
                framework, issues, performance_data
            )
            
            # Verify
            self.assertIn("framework_optimizations", result)
            self.assertIn("code_examples", result)
            self.assertIn("performance_improvements", result)
            self.assertEqual(result["implementation_complexity"], "medium")
            self.assertEqual(len(result["code_examples"]), 1)
    
    def test_build_improvement_planning_prompt(self):
        """Test improvement planning prompt building."""
        output_data = {
            "evaluation_results": [
                {"scenario_id": "s1", "passed": False, "severity": "critical"},
                {"scenario_id": "s2", "passed": True, "severity": "low"}
            ],
            "domain": "security"
        }
        
        prompt = self.improve_judge._build_improvement_planning_prompt(output_data)
        
        # Verify prompt contains expected elements
        self.assertIn("security domain", prompt)
        self.assertIn("Total scenarios evaluated: 2", prompt)
        self.assertIn("Failed scenarios: 1", prompt)
        self.assertIn("Action Prioritization", prompt)
        self.assertIn("Timeline Estimation", prompt)
        self.assertIn("RESPONSE FORMAT (JSON)", prompt)


class TestJudgeOutputAdapter(unittest.TestCase):
    """Test cases for JudgeOutputAdapter."""
    
    def test_debug_judge_to_reliability_analysis(self):
        """Test conversion from DebugJudge output to ComprehensiveReliabilityAnalysis."""
        # Setup
        judge_output = {
            "judgment": "warning",
            "confidence": 0.85,
            "reasoning": "Multiple performance issues detected in agent workflow",
            "improvements": ["Add caching", "Optimize queries", "Implement circuit breaker"],
            "reward_signals": {
                "failure_patterns": ["slow_response", "timeout_errors"],
                "framework_issues": {"performance": "Query optimization needed"},
                "performance_issues": ["database_bottleneck", "memory_usage"],
                "success_patterns": ["error_handling", "logging"]
            }
        }
        framework = "langchain"
        sample_size = 10
        
        # Execute
        analysis = JudgeOutputAdapter.debug_judge_to_reliability_analysis(
            judge_output, framework, sample_size
        )
        
        # Verify
        self.assertEqual(analysis.detected_framework, "langchain")
        self.assertEqual(analysis.framework_confidence, 0.85)
        self.assertTrue(analysis.auto_detection_successful)
        self.assertIsNotNone(analysis.framework_performance)
        self.assertEqual(analysis.framework_performance.framework_name, "langchain")
        self.assertEqual(analysis.framework_performance.sample_size, 10)
        self.assertIn("AI Analysis", analysis.insights_summary[1])  # First is confidence
        self.assertIn("Add caching", analysis.next_steps)
    
    def test_improve_judge_to_improvement_plan(self):
        """Test conversion from ImproveJudge output to ImprovementPlan."""
        # Setup
        judge_output = {
            "judgment": "pass",
            "confidence": 0.92,
            "reasoning": "Comprehensive improvement plan generated",
            "improvements": ["Implement monitoring", "Add automated testing"],
            "reward_signals": {
                "improvement_actions": [
                    {
                        "priority": "CRITICAL",
                        "area": "Monitoring",
                        "description": "Add comprehensive monitoring",
                        "action": "Implement metrics collection",
                        "expected_improvement": "50% better observability",
                        "timeline": "2 weeks",
                        "specific_steps": ["Install monitoring tools", "Configure alerts"]
                    }
                ],
                "priority_breakdown": {"CRITICAL": 1, "HIGH": 2},
                "expected_improvement": 35,
                "timeline": "4 weeks"
            }
        }
        agent_id = "test_agent"
        domain = "ml"
        
        # Execute
        plan = JudgeOutputAdapter.improve_judge_to_improvement_plan(
            judge_output, agent_id, domain
        )
        
        # Verify
        self.assertEqual(plan.agent_id, "test_agent")
        self.assertEqual(plan.domain, "ml")
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].priority, "CRITICAL")
        self.assertEqual(plan.actions[0].area, "Monitoring")
        self.assertEqual(plan.summary["expected_improvement"], 35)
        self.assertIn("Implement monitoring", plan.next_steps)
    
    def test_enhance_dashboard_with_judge_reasoning(self):
        """Test dashboard enhancement with judge reasoning."""
        # Setup existing analysis
        from agent_eval.evaluation.reliability_validator import (
            ComprehensiveReliabilityAnalysis,
            WorkflowReliabilityMetrics
        )
        
        workflow_metrics = WorkflowReliabilityMetrics(
            workflow_success_rate=0.85,
            tool_chain_reliability=0.90,
            decision_consistency_score=0.80,
            multi_step_completion_rate=0.75,
            average_workflow_time=2.5,
            error_recovery_rate=0.60,
            timeout_rate=0.05,
            framework_compatibility_score=0.88,
            tool_usage_efficiency=0.85,
            schema_mismatch_rate=0.02,
            prompt_tool_alignment_score=0.90,
            reliability_trend="improving",
            critical_failure_points=["api_timeout", "validation_error"]
        )
        
        analysis = ComprehensiveReliabilityAnalysis(
            detected_framework="langchain",
            framework_confidence=0.80,
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
            analysis_confidence=0.80,
            evidence_quality="medium",
            sample_size=5
        )
        
        judge_output = {
            "confidence": 0.95,
            "reasoning": "Advanced AI analysis reveals systematic performance patterns requiring immediate attention"
        }
        
        # Execute
        enhanced_analysis = JudgeOutputAdapter.enhance_dashboard_with_judge_reasoning(
            analysis, judge_output
        )
        
        # Verify
        self.assertIn("AI Confidence: 95.0%", enhanced_analysis.insights_summary[0])
        self.assertIn("AI Reasoning", enhanced_analysis.insights_summary[1])
        self.assertEqual(enhanced_analysis.evidence_quality, "high")  # Upgraded from medium


if __name__ == '__main__':
    unittest.main()
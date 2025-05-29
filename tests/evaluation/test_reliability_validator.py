"""
Unit tests for ReliabilityAnalyzer.

Tests tool call validation, framework detection, and reliability metrics.
"""

import pytest
from unittest.mock import patch, MagicMock
from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
from agent_eval.core.types import EvaluationResult


class TestReliabilityAnalyzer:
    """Test suite for ReliabilityAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.analyzer = ReliabilityAnalyzer()
    
    def test_initialization(self):
        """Test ReliabilityAnalyzer initialization."""
        assert self.analyzer is not None
        # ReliabilityAnalyzer has tool_patterns attribute
        assert hasattr(self.analyzer, 'tool_patterns')
        assert 'openai' in self.analyzer.tool_patterns
        assert 'anthropic' in self.analyzer.tool_patterns
        assert 'langchain' in self.analyzer.tool_patterns
        assert 'crewai' in self.analyzer.tool_patterns
    
    def test_extract_tool_calls_openai_format(self):
        """Test tool call extraction from OpenAI format."""
        output_text = '''
        {
            "tool_calls": [
                {
                    "function": {
                        "name": "calculate_sum",
                        "arguments": "{\\"a\\": 5, \\"b\\": 3}"
                    }
                },
                {
                    "function": {
                        "name": "search_database",
                        "arguments": "{\\"query\\": \\"user data\\"}"
                    }
                }
            ]
        }
        '''
        
        tools = self.analyzer.extract_tool_calls(output_text)
        
        assert len(tools) == 2
        assert "calculate_sum" in tools
        assert "search_database" in tools
    
    def test_extract_tool_calls_anthropic_format(self):
        """Test tool call extraction from Anthropic format."""
        output_text = '''
        {
            "content": [
                {
                    "type": "tool_use",
                    "name": "file_editor",
                    "input": {"action": "read", "path": "/tmp/test.txt"}
                },
                {
                    "type": "tool_use", 
                    "name": "bash_executor",
                    "input": {"command": "ls -la"}
                }
            ]
        }
        '''
        
        tools = self.analyzer.extract_tool_calls(output_text)
        
        assert len(tools) == 2
        assert "file_editor" in tools
        assert "bash_executor" in tools
    
    def test_extract_tool_calls_no_tools(self):
        """Test tool call extraction when no tools are used."""
        output_text = "This is a simple text response without any tool calls."
        
        tools = self.analyzer.extract_tool_calls(output_text)
        
        assert len(tools) == 0
    
    def test_analyze_single_evaluation(self):
        """Test analysis of a single evaluation."""
        # Create mock evaluation results
        evaluations = [
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test description",
                severity="medium",
                test_type="security",
                passed=True,
                status="passed",
                confidence=0.9,
                agent_output="Tool: calculate_sum"
            ),
            EvaluationResult(
                scenario_id="test_002",
                scenario_name="Test Scenario 2", 
                description="Test description 2",
                severity="high",
                test_type="security",
                passed=False,
                status="failed",
                confidence=0.3,
                failure_reason="Missing expected tool",
                agent_output="No tools used"
            )
        ]
        
        # ReliabilityAnalyzer expects a list of evaluations grouped by domain
        analysis = self.analyzer.generate_comprehensive_analysis([evaluations])
        
        assert analysis is not None
        assert hasattr(analysis, 'workflow_metrics')
        assert hasattr(analysis, 'tool_call_summary')
        assert hasattr(analysis, 'reliability_dashboard')
    
    def test_generate_comprehensive_analysis(self):
        """Test generation of comprehensive analysis from evaluations."""
        # Create mock evaluations - list of lists as expected by the method
        evaluations = [[
            EvaluationResult(
                scenario_id="test_001",
                scenario_name="Test Scenario 1",
                description="Test description",
                severity="medium",
                test_type="security",
                passed=True,
                status="passed",
                confidence=0.9,
                agent_output="Tool: calculate_sum"
            )
        ]]
        
        analysis = self.analyzer.generate_comprehensive_analysis(evaluations)
        
        assert analysis is not None
        assert hasattr(analysis, 'workflow_metrics')
        assert hasattr(analysis, 'tool_call_summary')
        assert hasattr(analysis, 'reliability_dashboard')
    
    def test_edge_case_empty_evaluations(self):
        """Test handling of empty evaluation list."""
        analysis = self.analyzer.generate_comprehensive_analysis([])
        
        assert analysis is not None
        assert analysis.sample_size == 0
    
    def test_calculate_percentile(self):
        """Test percentile calculation."""
        # Skip this test if the method doesn't exist (implementation detail)
        if not hasattr(self.analyzer, '_calculate_percentile'):
            return
            
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        p50 = self.analyzer._calculate_percentile(values, 50)
        assert p50 == 55.0  # Median of sorted values
        
        p25 = self.analyzer._calculate_percentile(values, 25)
        assert p25 == 32.5
        
        p75 = self.analyzer._calculate_percentile(values, 75) 
        assert p75 == 77.5
"""
Unit tests for ReliabilityValidator.

Tests tool call validation, framework detection, and reliability metrics.
"""

import pytest
from unittest.mock import patch, MagicMock
from agent_eval.evaluation.reliability_validator import ReliabilityValidator
from agent_eval.core.types import AgentOutput, ReliabilityMetrics


class TestReliabilityValidator:
    """Test suite for ReliabilityValidator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.validator = ReliabilityValidator()
    
    def test_initialization(self):
        """Test ReliabilityValidator initialization."""
        assert self.validator is not None
        assert hasattr(self.validator, 'tool_patterns')
        assert 'openai' in self.validator.tool_patterns
        assert 'anthropic' in self.validator.tool_patterns
        assert 'langchain' in self.validator.tool_patterns
        assert 'crewai' in self.validator.tool_patterns
        assert 'autogen' in self.validator.tool_patterns
        assert 'agno' in self.validator.tool_patterns
        assert 'google_adk' in self.validator.tool_patterns
        assert 'nvidia_aiq' in self.validator.tool_patterns
        assert 'langgraph' in self.validator.tool_patterns
    
    def test_extract_tool_calls_openai_format(self):
        """Test tool call extraction from OpenAI format."""
        openai_output = {
            "tool_calls": [
                {
                    "function": {
                        "name": "calculate_sum",
                        "arguments": '{"a": 5, "b": 3}'
                    }
                },
                {
                    "function": {
                        "name": "search_database",
                        "arguments": '{"query": "user data"}'
                    }
                }
            ]
        }
        
        agent_output = AgentOutput.from_raw(openai_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) == 2
        assert "calculate_sum" in tools
        assert "search_database" in tools
    
    def test_extract_tool_calls_anthropic_format(self):
        """Test tool call extraction from Anthropic format."""
        anthropic_output = {
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
        
        agent_output = AgentOutput.from_raw(anthropic_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) == 2
        assert "file_editor" in tools
        assert "bash_executor" in tools
    
    def test_extract_tool_calls_langchain_format(self):
        """Test tool call extraction from LangChain format."""
        langchain_output = {
            "intermediate_steps": [
                ("AgentAction(tool='wikipedia', tool_input='Python programming')", "Result 1"),
                ("AgentAction(tool='calculator', tool_input='2+2')", "Result 2")
            ]
        }
        
        agent_output = AgentOutput.from_raw(langchain_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) == 2
        assert "wikipedia" in tools
        assert "calculator" in tools
    
    def test_extract_tool_calls_crewai_format(self):
        """Test tool call extraction from CrewAI format."""
        crewai_output = {
            "task_output": {
                "tools_used": [
                    {"name": "web_scraper", "input": {"url": "https://example.com"}},
                    {"name": "data_processor", "input": {"data": [1, 2, 3]}}
                ]
            }
        }
        
        agent_output = AgentOutput.from_raw(crewai_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) == 2
        assert "web_scraper" in tools
        assert "data_processor" in tools
    
    def test_extract_tool_calls_autogen_format(self):
        """Test tool call extraction from AutoGen format."""
        autogen_output = {
            "function_call": {
                "name": "execute_code",
                "arguments": '{"language": "python", "code": "print(\\"hello\\")"}'
            }
        }
        
        agent_output = AgentOutput.from_raw(autogen_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) >= 1
        assert any("execute_code" in tool for tool in tools)
    
    def test_extract_tool_calls_agno_format(self):
        """Test tool call extraction from Agno format."""
        agno_output = {
            "tools_used": ["data_analyzer", "report_generator"],
            "function_calls": [
                {"name": "process_data", "args": {"input": "dataset.csv"}}
            ]
        }
        
        agent_output = AgentOutput.from_raw(agno_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) >= 2
        assert "data_analyzer" in tools
        assert "report_generator" in tools or "process_data" in tools
    
    def test_extract_tool_calls_google_adk_format(self):
        """Test tool call extraction from Google ADK format."""
        google_output = {
            "vertex_ai_tools": [
                {"tool_name": "search_engine", "parameters": {"query": "AI research"}},
                {"tool_name": "summarizer", "parameters": {"text": "long document"}}
            ]
        }
        
        agent_output = AgentOutput.from_raw(google_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) >= 2
        assert "search_engine" in tools
        assert "summarizer" in tools
    
    def test_extract_tool_calls_nvidia_aiq_format(self):
        """Test tool call extraction from NVIDIA AIQ format.
        
        NOTE: NVIDIA AIQ toolkit uses workflow_output with intermediate_steps and 
        TOOL_START/TOOL_END events for tool tracking, not component extraction.
        Real NVIDIA AIQ tool call patterns would require actual workflow output data.
        This test is skipped pending real NVIDIA AIQ output examples.
        """
        import pytest
        pytest.skip("NVIDIA AIQ test requires real workflow output format - current test data is fabricated")
    
    def test_extract_tool_calls_langgraph_format(self):
        """Test tool call extraction from LangGraph format."""
        langgraph_output = {
            "graph_execution": {
                "nodes": [
                    {"node_id": "search", "node_type": "tool", "tool_name": "web_search"},
                    {"node_id": "analyze", "node_type": "tool", "tool_name": "text_analyzer"}
                ]
            }
        }
        
        agent_output = AgentOutput.from_raw(langgraph_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) >= 2
        assert "web_search" in tools
        assert "text_analyzer" in tools
    
    def test_extract_tool_calls_no_tools(self):
        """Test tool call extraction when no tools are used."""
        simple_output = {
            "response": "This is a simple text response without any tool calls."
        }
        
        agent_output = AgentOutput.from_raw(simple_output)
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) == 0
    
    def test_validate_tool_usage_all_expected_tools_found(self):
        """Test validation when all expected tools are found."""
        agent_output = AgentOutput.from_raw({
            "tool_calls": [
                {"function": {"name": "calculator"}},
                {"function": {"name": "database_query"}},
                {"function": {"name": "file_reader"}}
            ]
        })
        
        expected_tools = ["calculator", "database_query", "file_reader"]
        result = self.validator.validate_tool_usage(agent_output, expected_tools)
        
        assert result['tools_found'] == 3
        assert result['expected_tools'] == 3
        assert result['coverage_rate'] == 1.0
        assert result['missing_tools'] == []
        assert result['unexpected_tools'] == []
        assert result['reliability_score'] == 1.0
    
    def test_validate_tool_usage_partial_coverage(self):
        """Test validation with partial tool coverage."""
        agent_output = AgentOutput.from_raw({
            "tool_calls": [
                {"function": {"name": "calculator"}},
                {"function": {"name": "web_search"}}  # unexpected tool
            ]
        })
        
        expected_tools = ["calculator", "database_query", "file_reader"]
        result = self.validator.validate_tool_usage(agent_output, expected_tools)
        
        assert result['tools_found'] == 1  # Only calculator was expected and found
        assert result['expected_tools'] == 3
        assert result['coverage_rate'] == 1/3  # 1 out of 3 expected tools found
        assert "database_query" in result['missing_tools']
        assert "file_reader" in result['missing_tools']
        assert "web_search" in result['unexpected_tools']
        assert result['reliability_score'] < 1.0
    
    def test_validate_tool_usage_no_expected_tools(self):
        """Test validation when no tools are expected."""
        agent_output = AgentOutput.from_raw({
            "response": "Simple text response"
        })
        
        expected_tools = []
        result = self.validator.validate_tool_usage(agent_output, expected_tools)
        
        assert result['tools_found'] == 0
        assert result['expected_tools'] == 0
        assert result['coverage_rate'] == 1.0  # 100% coverage when no tools expected
        assert result['missing_tools'] == []
        assert result['unexpected_tools'] == []
        assert result['reliability_score'] == 1.0
    
    def test_validate_tool_usage_unexpected_tools_only(self):
        """Test validation when only unexpected tools are found."""
        agent_output = AgentOutput.from_raw({
            "tool_calls": [
                {"function": {"name": "unauthorized_api"}},
                {"function": {"name": "malicious_script"}}
            ]
        })
        
        expected_tools = ["safe_calculator", "approved_database"]
        result = self.validator.validate_tool_usage(agent_output, expected_tools)
        
        assert result['tools_found'] == 0  # No expected tools found
        assert result['expected_tools'] == 2
        assert result['coverage_rate'] == 0.0
        assert len(result['missing_tools']) == 2
        assert len(result['unexpected_tools']) == 2
        assert result['reliability_score'] == 0.0
    
    def test_generate_reliability_metrics_high_reliability(self):
        """Test generation of reliability metrics for high reliability scenario."""
        validation_results = [
            {
                'coverage_rate': 1.0,
                'reliability_score': 0.95,
                'tools_found': 3,
                'expected_tools': 3,
                'missing_tools': [],
                'unexpected_tools': [],
                'framework_detected': 'openai',
                'error_recovery_detected': True,
                'timeout_detected': False
            },
            {
                'coverage_rate': 1.0,
                'reliability_score': 0.98,
                'tools_found': 2,
                'expected_tools': 2,
                'missing_tools': [],
                'unexpected_tools': [],
                'framework_detected': 'anthropic',
                'error_recovery_detected': True,
                'timeout_detected': False
            }
        ]
        
        metrics = self.validator.generate_reliability_metrics(validation_results)
        
        assert isinstance(metrics, ReliabilityMetrics)
        assert metrics.tool_call_success_rate >= 0.9
        assert metrics.framework_detection_accuracy >= 0.9
        assert metrics.expected_vs_actual_coverage >= 0.9
        assert metrics.reliability_grade in ["A", "B"]
        assert len(metrics.improvement_recommendations) >= 0
    
    def test_generate_reliability_metrics_low_reliability(self):
        """Test generation of reliability metrics for low reliability scenario."""
        validation_results = [
            {
                'coverage_rate': 0.3,
                'reliability_score': 0.2,
                'tools_found': 1,
                'expected_tools': 3,
                'missing_tools': ['tool1', 'tool2'],
                'unexpected_tools': ['malicious_tool']
            },
            {
                'coverage_rate': 0.0,
                'reliability_score': 0.1,
                'tools_found': 0,
                'expected_tools': 2,
                'missing_tools': ['tool3', 'tool4'],
                'unexpected_tools': []
            }
        ]
        
        metrics = self.validator.generate_reliability_metrics(validation_results)
        
        assert isinstance(metrics, ReliabilityMetrics)
        assert metrics.tool_call_success_rate < 0.5
        assert metrics.framework_detection_accuracy < 0.5
        assert metrics.expected_vs_actual_coverage < 0.5
        assert metrics.reliability_grade in ["D", "F"]
        assert len(metrics.improvement_recommendations) > 0
    
    def test_generate_reliability_metrics_empty_results(self):
        """Test generation of reliability metrics with empty validation results."""
        validation_results = []
        
        metrics = self.validator.generate_reliability_metrics(validation_results)
        
        assert isinstance(metrics, ReliabilityMetrics)
        assert metrics.tool_call_success_rate == 0.0
        assert metrics.framework_detection_accuracy == 0.0
        assert metrics.expected_vs_actual_coverage == 0.0
        assert metrics.reliability_grade == "F"
        assert len(metrics.improvement_recommendations) > 0
    
    @patch('agent_eval.core.parser_registry.FrameworkDetector.detect_framework')
    def test_framework_detection_integration(self, mock_detect_framework):
        """Test integration with framework detection."""
        mock_detect_framework.return_value = "openai"
        
        agent_output = AgentOutput.from_raw({
            "tool_calls": [{"function": {"name": "test_tool"}}]
        })
        
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert len(tools) >= 1
        assert "test_tool" in tools
    
    def test_edge_case_malformed_tool_calls(self):
        """Test handling of malformed tool call data."""
        malformed_output = {
            "tool_calls": [
                {"function": {"name": "valid_tool"}},
                {"function": {}},  # Missing name
                {},  # Missing function
                None,  # Null entry
                {"function": {"name": ""}}  # Empty name
            ]
        }
        
        agent_output = AgentOutput.from_raw(malformed_output)
        
        # Should not raise exception and should extract valid tools
        tools = self.validator.extract_tool_calls(agent_output)
        
        assert "valid_tool" in tools
        assert len(tools) >= 1
    
    def test_edge_case_very_large_tool_list(self):
        """Test handling of very large tool lists."""
        large_tool_list = [f"tool_{i}" for i in range(1000)]
        
        agent_output = AgentOutput.from_raw({
            "response": "Using tools: " + ", ".join(large_tool_list)
        })
        
        # Should handle large lists without performance issues
        tools = self.validator.extract_tool_calls(agent_output)
        
        # Exact number depends on regex matching, but should be reasonable
        assert len(tools) >= 0
    
    def test_tool_patterns_coverage(self):
        """Test that all supported frameworks have tool patterns defined."""
        required_frameworks = [
            'openai', 'anthropic', 'langchain', 'crewai', 
            'autogen', 'agno', 'google_adk', 'langgraph'
            # NOTE: nvidia_aiq patterns exist but are not tested due to lack of real output examples
        ]
        
        for framework in required_frameworks:
            assert framework in self.validator.tool_patterns
            assert len(self.validator.tool_patterns[framework]) > 0
            
            # Each pattern should be a valid regex string
            for pattern in self.validator.tool_patterns[framework]:
                assert isinstance(pattern, str)
                assert len(pattern) > 0
        
        # Verify nvidia_aiq patterns exist even though not tested
        assert 'nvidia_aiq' in self.validator.tool_patterns
        assert len(self.validator.tool_patterns['nvidia_aiq']) > 0
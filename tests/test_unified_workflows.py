"""
Integration tests for unified CLI workflows.
"""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
import tempfile

from agent_eval.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_agent_output():
    """Create sample agent output for testing."""
    return {
        "output": "Transaction approved for John Smith (SSN: 123-45-6789)",
        "metadata": {
            "scenario_id": "fin_001",
            "timestamp": "2024-05-27T10:30:00Z"
        }
    }


@pytest.fixture
def sample_trace_data():
    """Create sample trace data for debugging."""
    return {
        "framework": "langchain",
        "tool_calls": [
            {
                "tool": "database_query",
                "success": False,
                "error": "Timeout after 30s"
            }
        ],
        "memory_usage": {
            "peak_mb": 512,
            "conversation_length": 50
        },
        "outputs": [
            {
                "content": "Customer SSN is 123-45-6789",
                "has_pii": True
            }
        ]
    }


class TestDebugWorkflow:
    """Test the debug workflow command."""
    
    def test_debug_basic(self, runner, sample_trace_data):
        """Test basic debug functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_trace_data, f)
            f.flush()
            
            result = runner.invoke(cli, ['debug', '--input', f.name])
            
            assert result.exit_code == 0
            assert "Agent Debug Analysis" in result.output
            assert "Framework Detection:" in result.output or "LANGCHAIN" in result.output
    
    def test_debug_with_framework(self, runner, sample_trace_data):
        """Test debug with explicit framework."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_trace_data, f)
            f.flush()
            
            result = runner.invoke(cli, ['debug', '--input', f.name, '--framework', 'langchain'])
            
            assert result.exit_code == 0
            assert "langchain" in result.output.lower()
    
    def test_debug_missing_input(self, runner):
        """Test debug with missing input file."""
        result = runner.invoke(cli, ['debug'])
        assert result.exit_code != 0
        assert "Missing option" in result.output


class TestComplianceWorkflow:
    """Test the compliance workflow command."""
    
    def test_compliance_basic(self, runner, sample_agent_output):
        """Test basic compliance evaluation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([sample_agent_output], f)
            f.flush()
            
            result = runner.invoke(cli, ['compliance', '--domain', 'finance', '--input', f.name, '--no-export'])
            
            assert result.exit_code == 0
            assert "Compliance Evaluation" in result.output
            assert "Finance" in result.output
    
    def test_compliance_quick_start(self, runner):
        """Test compliance with quick start mode."""
        result = runner.invoke(cli, ['compliance', '--domain', 'security', '--quick-start', '--no-export'])
        
        assert result.exit_code == 0
        assert "Security" in result.output
    
    def test_compliance_auto_export(self, runner, sample_agent_output):
        """Test compliance with automatic PDF export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            with open(input_file, 'w') as f:
                json.dump([sample_agent_output], f)
            
            result = runner.invoke(cli, ['compliance', '--domain', 'finance', '--input', str(input_file)])
            
            # Should auto-export PDF
            assert result.exit_code == 0
            # Check if PDF export was mentioned
            assert any(word in result.output for word in ['export', 'PDF', 'report'])


class TestImproveWorkflow:
    """Test the improve workflow command."""
    
    def test_improve_from_evaluation(self, runner):
        """Test improvement plan generation."""
        # Create a mock evaluation file
        eval_data = {
            "domain": "finance",
            "agent_id": "test_agent",
            "evaluation_id": "test_eval_123",
            "results": [
                {
                    "scenario_id": "fin_001",
                    "passed": False,
                    "compliance_gaps": ["PII exposure"],
                    "reward_signals": {"compliance": 0.3}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(eval_data, f)
            f.flush()
            
            result = runner.invoke(cli, ['improve', '--from-evaluation', f.name])
            
            assert result.exit_code == 0
            assert "Improvement" in result.output
    
    def test_improve_comparison(self, runner, sample_agent_output):
        """Test improvement comparison between versions."""
        # Create baseline and current files
        baseline_data = {"results": [{"passed": False}] * 10}
        current_data = {"results": [{"passed": True}] * 5 + [{"passed": False}] * 5}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as baseline_f:
            json.dump(baseline_data, baseline_f)
            baseline_f.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as current_f:
                json.dump(current_data, current_f)
                current_f.flush()
                
                result = runner.invoke(cli, ['improve', '--baseline', baseline_f.name, '--current', current_f.name])
                
                assert result.exit_code == 0
                assert "improvement" in result.output.lower()
    
    def test_improve_auto_detect(self, runner):
        """Test improve with auto-detection of latest evaluation."""
        # Create a mock evaluation file with proper naming
        eval_data = {
            "domain": "finance",
            "evaluation_id": "test_123",
            "results": [{"passed": False}]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            eval_file = Path(tmpdir) / "finance_evaluation_20250527_120000.json"
            with open(eval_file, 'w') as f:
                json.dump(eval_data, f)
            
            # Change to temp directory for auto-detection
            import os
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                result = runner.invoke(cli, ['improve', '--auto-detect'])
                assert result.exit_code == 0
            finally:
                os.chdir(original_dir)


class TestWorkflowIntegration:
    """Test integration between workflows."""
    
    def test_workflow_state_tracking(self, runner, sample_agent_output):
        """Test that workflow state is tracked between commands."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([sample_agent_output], f)
            f.flush()
            
            # Run debug workflow
            result1 = runner.invoke(cli, ['debug', '--input', f.name])
            assert result1.exit_code == 0
            
            # Check for next step suggestion
            assert "compliance" in result1.output.lower()
            
            # Run compliance workflow
            result2 = runner.invoke(cli, ['compliance', '--domain', 'finance', '--input', f.name, '--no-export'])
            assert result2.exit_code == 0
            
            # Check for next step suggestion
            assert "improve" in result2.output.lower()
    
    def test_interactive_mode(self, runner):
        """Test interactive workflow selector."""
        result = runner.invoke(cli, [], input='q\n')
        
        assert result.exit_code == 0
        assert "ARC-Eval Unified Workflow" in result.output
        assert "debug" in result.output
        assert "compliance" in result.output
        assert "improve" in result.output


class TestBackwardCompatibility:
    """Test backward compatibility with legacy CLI."""
    
    def test_legacy_command_warning(self, runner, sample_agent_output):
        """Test that legacy commands show deprecation warning."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([sample_agent_output], f)
            f.flush()
            
            # Use legacy multi-flag command
            from agent_eval.cli import legacy_main
            result = runner.invoke(legacy_main, ['--domain', 'finance', '--input', f.name])
            
            # Should work but show warning
            assert "legacy CLI interface" in result.output
            assert "migrate to the new unified commands" in result.output


@pytest.mark.parametrize("command,expected", [
    ("debug", "Why is my agent failing?"),
    ("compliance", "Does it meet requirements?"),
    ("improve", "How do I make it better?"),
])
def test_help_text(runner, command, expected):
    """Test that help text is clear and helpful."""
    result = runner.invoke(cli, [command, '--help'])
    
    assert result.exit_code == 0
    assert expected in result.output


def test_version(runner):
    """Test version command."""
    result = runner.invoke(cli, ['--version'])
    
    assert result.exit_code == 0
    assert "0.2.7" in result.output
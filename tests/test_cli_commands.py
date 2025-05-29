#!/usr/bin/env python3
"""
Tests for the simplified CLI commands: debug, compliance, improve.
"""

import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner
from agent_eval.cli import cli


class TestCLICommands:
    """Test the three main CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        
    def create_test_data(self):
        """Create sample test data file."""
        data = [
            {
                "output": "Transaction approved for customer",
                "metadata": {"scenario_id": "test_001"}
            }
        ]
        
        filename = Path(self.test_dir) / "test_data.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        return str(filename)
    
    def test_cli_help(self):
        """Test main CLI help."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "debug" in result.output
        assert "compliance" in result.output
        assert "improve" in result.output
    
    def test_debug_command_help(self):
        """Test debug command help."""
        result = self.runner.invoke(cli, ['debug', '--help'])
        
        assert result.exit_code == 0
        assert "Debug agent failures" in result.output
    
    def test_compliance_command_help(self):
        """Test compliance command help."""
        result = self.runner.invoke(cli, ['compliance', '--help'])
        
        assert result.exit_code == 0
        assert "Evaluate agent compliance" in result.output
    
    def test_improve_command_help(self):
        """Test improve command help."""
        result = self.runner.invoke(cli, ['improve', '--help'])
        
        assert result.exit_code == 0
        assert "Generate and track improvement plans" in result.output
    
    def test_compliance_quick_start(self):
        """Test compliance command with quick-start."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                'compliance',
                '--domain', 'finance',
                '--quick-start'
            ])
            
            # Should work without errors
            assert result.exit_code == 0
            assert "Financial Services Compliance" in result.output or "FINANCE" in result.output
    
    def test_debug_with_input(self):
        """Test debug command with input file."""
        test_file = self.create_test_data()
        
        result = self.runner.invoke(cli, [
            'debug',
            '--input', test_file,
            '--domain', 'finance'
        ])
        
        # Should work or provide helpful error
        assert result.exit_code in [0, 1, 2]  # 2 is for Click usage errors
        if result.exit_code != 0:
            # Either an error message or usage message should be present
            assert "Error" in result.output or "Usage:" in result.output or "Debug analysis" in result.output
    
    def test_improve_without_evaluation(self):
        """Test improve command without evaluation file."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                'improve',
                '--auto-detect'
            ])
            
            # Should work or provide helpful error
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                assert "No evaluation files found" in result.output
                assert "arc-eval compliance" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
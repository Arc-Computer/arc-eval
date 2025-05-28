#!/usr/bin/env python3
"""
Comprehensive integration tests for intelligent workflow features.
Tests the complete evaluation → improvement → re-evaluation cycle.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner

from agent_eval.cli import main, find_latest_evaluation_file, improvement_plan_exists


class TestIntelligentWorkflow:
    """Test suite for intelligent workflow features."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_sample_data(self, size_kb=1):
        """Create sample agent output data."""
        base_data = [
            {
                "output": "Test financial output",
                "scenario": "Test Scenario",
                "scenario_id": "test_001",
                "timestamp": "2024-01-01T00:00:00Z",
                "framework": "test",
                "expected_to_fail": False
            }
        ]
        
        # Duplicate data to reach desired size
        # Each base_data entry is ~200 bytes, so multiplying by (size_kb * 10) 
        # approximates the target size in KB (10 multiplier accounts for JSON overhead)
        data = base_data * (size_kb * 10)
        
        filename = "test_data.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def test_continue_workflow_no_files(self):
        """Test continue workflow with no evaluation files."""
        result = self.runner.invoke(main, ['--continue'])
        
        assert result.exit_code == 0
        assert "No evaluation files found" in result.output
        assert "Start with:" in result.output
    
    def test_find_latest_evaluation_file(self):
        """Test finding latest evaluation file."""
        # Create test evaluation files
        eval1 = Path("finance_evaluation_20240101_120000.json")
        eval2 = Path("security_evaluation_20240101_130000.json")
        
        eval1.write_text('{"test": "data1"}')
        eval2.write_text('{"test": "data2"}')
        
        # Modify times to ensure proper ordering
        import time
        time.sleep(0.1)
        eval2.touch()  # Make eval2 newer
        
        latest = find_latest_evaluation_file()
        assert latest is not None
        assert latest.name == "security_evaluation_20240101_130000.json"
    
    def test_improvement_plan_exists(self):
        """Test improvement plan detection."""
        # Create evaluation file
        eval_file = Path("finance_evaluation_20240101_120000.json")
        eval_file.write_text('{"test": "data"}')
        
        # No improvement plan exists
        plan = improvement_plan_exists(eval_file)
        assert plan is None
        
        # Create improvement plan
        plan_file = Path("improvement_plan_20240101_120001.md")
        plan_file.write_text("# Improvement Plan")
        
        # Should find the plan
        plan = improvement_plan_exists(eval_file)
        assert plan is not None
        assert plan.name == "improvement_plan_20240101_120001.md"
    
    def test_smart_defaults_large_file(self):
        """Test smart defaults for large files."""
        # Create large file (>100KB)
        large_file = self.create_sample_data(size_kb=150)
        
        with patch('agent_eval.cli.EvaluationEngine') as mock_engine:
            mock_engine.return_value.evaluate.return_value = []
            
            result = self.runner.invoke(main, [
                '--domain', 'finance',
                '--input', large_file,
                '--no-interaction'
            ])
            
            assert "Smart Default" in result.output
            assert "Auto-enabled --agent-judge" in result.output
    
    def test_smart_defaults_finance_domain(self):
        """Test smart defaults for finance domain."""
        test_file = self.create_sample_data()
        
        with patch('agent_eval.cli.EvaluationEngine') as mock_engine:
            mock_engine.return_value.evaluate.return_value = []
            
            result = self.runner.invoke(main, [
                '--domain', 'finance',
                '--input', test_file,
                '--no-interaction'
            ])
            
            assert "Smart Default" in result.output
            assert "PDF export for finance domain" in result.output
    
    def test_audit_shortcut_command(self):
        """Test --audit shortcut command."""
        test_file = self.create_sample_data()
        
        result = self.runner.invoke(main, [
            '--domain', 'finance',
            '--input', test_file,
            '--audit',
            '--help'  # Just test flag parsing
        ])
        
        # Should not error on flag parsing
        assert result.exit_code == 0
    
    def test_dev_mode_shortcut_command(self):
        """Test --dev-mode shortcut command."""
        test_file = self.create_sample_data()
        
        result = self.runner.invoke(main, [
            '--domain', 'security',
            '--input', test_file,
            '--dev-mode',
            '--help'  # Just test flag parsing
        ])
        
        # Should not error on flag parsing
        assert result.exit_code == 0
    
    def test_full_cycle_shortcut_command(self):
        """Test --full-cycle shortcut command."""
        test_file = self.create_sample_data()
        
        result = self.runner.invoke(main, [
            '--domain', 'ml',
            '--input', test_file,
            '--full-cycle',
            '--help'  # Just test flag parsing
        ])
        
        # Should not error on flag parsing
        assert result.exit_code == 0
    
    def test_workflow_state_detection(self):
        """Test complete workflow state detection."""
        # Step 1: Create evaluation file
        eval_file = Path("ml_evaluation_20240101_120000.json")
        eval_file.write_text(json.dumps({
            "domain": "ml",
            "results": [],
            "timestamp": "2024-01-01T12:00:00Z"
        }))
        
        # Step 2: Test continue workflow (should suggest improvement plan)
        result = self.runner.invoke(main, ['--continue'], input='n\n')
        
        assert result.exit_code == 0
        assert "Latest evaluation:" in result.output
        assert "No improvement plan found" in result.output
        assert "Generate improvement plan now?" in result.output
        
        # Step 3: Create improvement plan
        plan_file = Path("improvement_plan_20240101_120001.md")
        plan_file.write_text("# Test Improvement Plan")
        
        # Step 4: Test continue workflow (should suggest re-evaluation)
        result = self.runner.invoke(main, ['--continue'])
        
        assert result.exit_code == 0
        assert "Latest evaluation:" in result.output
        assert "Improvement plan found:" in result.output
        assert "Re-evaluate with improved data" in result.output


class TestCLIIntegration:
    """Integration tests for CLI workflow features."""
    
    def test_help_includes_new_flags(self):
        """Test that help output includes new workflow flags."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "--continue" in result.output
        assert "--audit" in result.output
        assert "--dev-mode" in result.output
        assert "--full-cycle" in result.output
        assert "auto-detects workflow state" in result.output
    
    def test_flag_combinations(self):
        """Test that workflow flags don't conflict."""
        runner = CliRunner()
        
        # Test that flags can be parsed without error
        test_combinations = [
            ['--audit', '--help'],
            ['--dev-mode', '--help'], 
            ['--continue', '--help'],
            ['--audit', '--dev-mode', '--help']  # Should handle multiple shortcuts
        ]
        
        for flags in test_combinations:
            result = runner.invoke(main, flags)
            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__])

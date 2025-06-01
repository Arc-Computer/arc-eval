"""
Test suite for refactored command modules.

Tests the new command structure with proper error handling and separation of concerns.
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_eval.commands.debug_command import DebugCommand
from agent_eval.commands.compliance_command import ComplianceCommand
from agent_eval.commands.improve_command import ImproveCommand
from agent_eval.commands.analyze_command import AnalyzeCommand
from agent_eval.commands.base import ValidationError, InputError, CommandError


class TestDebugCommand:
    """Test the refactored DebugCommand."""
    
    def test_debug_command_initialization(self):
        """Test debug command initializes correctly."""
        command = DebugCommand()
        assert command.console is not None
        assert command.handler is not None
    
    def test_debug_command_missing_file(self):
        """Test debug command with missing input file."""
        command = DebugCommand()
        non_existent_file = Path("non_existent_file.json")
        
        result = command.execute(non_existent_file)
        assert result == 1  # Error exit code
    
    def test_debug_command_invalid_output_format(self):
        """Test debug command with invalid output format."""
        command = DebugCommand()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            f.flush()
            
            result = command.execute(Path(f.name), output_format="invalid")
            assert result == 1  # Error exit code


class TestComplianceCommand:
    """Test the refactored ComplianceCommand."""
    
    def test_compliance_command_initialization(self):
        """Test compliance command initializes correctly."""
        command = ComplianceCommand()
        assert command.console is not None
        assert command.handler is not None
    
    def test_compliance_command_invalid_domain(self):
        """Test compliance command with invalid domain."""
        command = ComplianceCommand()
        
        result = command.execute("invalid_domain")
        assert result == 1  # Error exit code
    
    def test_compliance_command_no_input(self):
        """Test compliance command with no input and no quick-start."""
        command = ComplianceCommand()
        
        result = command.execute("finance")
        assert result == 1  # Error exit code


class TestImproveCommand:
    """Test the refactored ImproveCommand."""
    
    def test_improve_command_initialization(self):
        """Test improve command initializes correctly."""
        command = ImproveCommand()
        assert command.console is not None
        assert command.handler is not None
        assert command.workflow_manager is not None
    
    def test_improve_command_missing_evaluation_file(self):
        """Test improve command with missing evaluation file."""
        command = ImproveCommand()
        non_existent_file = Path("non_existent_evaluation.json")
        
        result = command.execute(evaluation_file=non_existent_file)
        assert result == 1  # Error exit code
    
    @patch('agent_eval.commands.improve_command.Path.cwd')
    def test_improve_command_auto_detect_no_files(self, mock_cwd):
        """Test improve command auto-detect with no evaluation files."""
        mock_cwd.return_value.glob.return_value = []
        
        command = ImproveCommand()
        result = command.execute(auto_detect=True)
        assert result == 1  # Error exit code


class TestAnalyzeCommand:
    """Test the refactored AnalyzeCommand."""
    
    def test_analyze_command_initialization(self):
        """Test analyze command initializes correctly."""
        command = AnalyzeCommand()
        assert command.console is not None
    
    def test_analyze_command_missing_file(self):
        """Test analyze command with missing input file."""
        command = AnalyzeCommand()
        non_existent_file = Path("non_existent_file.json")
        
        result = command.execute(non_existent_file, "finance")
        assert result == 1  # Error exit code
    
    def test_analyze_command_invalid_domain(self):
        """Test analyze command with invalid domain."""
        command = AnalyzeCommand()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            f.flush()
            
            result = command.execute(Path(f.name), "invalid_domain")
            assert result == 1  # Error exit code


class TestErrorHandling:
    """Test standardized error handling across commands."""
    
    def test_validation_error_handling(self):
        """Test ValidationError is handled correctly."""
        from agent_eval.commands.base import BaseCommandHandler
        
        class TestHandler(BaseCommandHandler):
            def execute(self, **kwargs):
                return 0
        
        handler = TestHandler()
        
        # Test ValidationError
        error = ValidationError("Test validation error")
        exit_code = handler._handle_command_error(error)
        assert exit_code == 2
    
    def test_input_error_handling(self):
        """Test InputError is handled correctly."""
        from agent_eval.commands.base import BaseCommandHandler
        
        class TestHandler(BaseCommandHandler):
            def execute(self, **kwargs):
                return 0
        
        handler = TestHandler()
        
        # Test InputError
        error = InputError("Test input error")
        exit_code = handler._handle_command_error(error)
        assert exit_code == 3
    
    def test_command_error_handling(self):
        """Test CommandError is handled correctly."""
        from agent_eval.commands.base import BaseCommandHandler
        
        class TestHandler(BaseCommandHandler):
            def execute(self, **kwargs):
                return 0
        
        handler = TestHandler()
        
        # Test CommandError
        error = CommandError("Test command error")
        exit_code = handler._handle_command_error(error)
        assert exit_code == 1
    
    def test_unexpected_error_handling(self):
        """Test unexpected errors are handled correctly."""
        from agent_eval.commands.base import BaseCommandHandler
        
        class TestHandler(BaseCommandHandler):
            def execute(self, **kwargs):
                return 0
        
        handler = TestHandler()
        
        # Test unexpected error
        error = RuntimeError("Unexpected error")
        exit_code = handler._handle_command_error(error)
        assert exit_code == 1


class TestCommandIntegration:
    """Test integration between refactored commands and CLI."""
    
    @patch('agent_eval.commands.debug_command.ReliabilityCommandHandler')
    def test_debug_command_integration(self, mock_handler):
        """Test debug command integrates with CLI correctly."""
        mock_handler.return_value.execute.return_value = 0
        
        command = DebugCommand()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            f.flush()
            
            result = command.execute(Path(f.name))
            assert result == 0
            mock_handler.return_value.execute.assert_called_once()
    
    @patch('agent_eval.commands.compliance_command.ComplianceCommandHandler')
    @patch('agent_eval.commands.compliance_command.update_workflow_progress')
    def test_compliance_command_integration(self, mock_update, mock_handler):
        """Test compliance command integrates with CLI correctly."""
        mock_handler.return_value.execute.return_value = 0

        command = ComplianceCommand()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            f.flush()

            result = command.execute("finance", Path(f.name))
            assert result == 0
            mock_handler.return_value.execute.assert_called_once()

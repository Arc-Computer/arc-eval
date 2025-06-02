"""
Commands and handlers for ARC-Eval CLI.

This module provides specialized commands (CLI interface) and handlers (core logic)
to modularize the CLI and separate concerns for different command types.
"""

from .base import BaseCommandHandler

# Command classes (CLI interface)
from .debug_command import DebugCommand
from .compliance_command import ComplianceCommand
from .improve_command import ImproveCommand
from .analyze_command import AnalyzeCommand
from .benchmark_command import BenchmarkCommand
from .reliability_command import ReliabilityCommand

# Handler classes (core logic) - for internal use
from .reliability_handler import ReliabilityHandler
from .compliance_handler import ComplianceHandler
from .workflow_handler import WorkflowHandler

__all__ = [
    # Base class
    'BaseCommandHandler',

    # Commands (CLI interface)
    'DebugCommand',
    'ComplianceCommand',
    'ImproveCommand',
    'AnalyzeCommand',
    'BenchmarkCommand',
    'ReliabilityCommand',

    # Handlers (core logic)
    'ReliabilityHandler',
    'ComplianceHandler',
    'WorkflowHandler'
]

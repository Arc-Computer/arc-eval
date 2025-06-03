"""
Workflow-specific judges for debug and improve workflows.

This module provides specialized judges that extend the Agent-as-a-Judge architecture
to handle workflow-specific evaluation tasks like debugging and improvement planning.
"""

from .debug import DebugJudge
from .improve import ImproveJudge
from .judge_output_adapter import JudgeOutputAdapter

__all__ = [
    "DebugJudge",
    "ImproveJudge", 
    "JudgeOutputAdapter"
]
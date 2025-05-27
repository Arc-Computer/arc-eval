"""
Core evaluation engine and types for ARC-Eval.

This module contains the essential core functionality:
- Main evaluation engine
- Core data types and models
- Framework detection and parsing
"""

from .engine import EvaluationEngine
from .types import (
    EvaluationPack,
    EvaluationScenario, 
    EvaluationResult,
    EvaluationSummary,
    AgentOutput,
    EvaluationCategory
)
from .parser_registry import FrameworkDetector

__all__ = [
    "EvaluationEngine",
    "EvaluationPack",
    "EvaluationScenario",
    "EvaluationResult", 
    "EvaluationSummary",
    "AgentOutput",
    "EvaluationCategory",
    "FrameworkDetector"
]
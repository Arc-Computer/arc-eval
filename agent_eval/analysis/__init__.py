"""
Analysis components for ARC-Eval.

This module contains analysis functionality including:
- Judge comparison and A/B testing
- Self-improvement recommendations
- Performance analysis
"""

from .judge_comparison import JudgeComparison, JudgeConfig
from .self_improvement import SelfImprovementEngine

__all__ = [
    "JudgeComparison",
    "JudgeConfig",
    "SelfImprovementEngine"
]
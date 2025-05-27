"""
Benchmark integration components for ARC-Eval.

This module provides integration with academic benchmarks including:
- MMLU (Massive Multitask Language Understanding)
- HumanEval (Code generation evaluation)
- GSM8K (Mathematical reasoning)
"""

from .adapter import QuickBenchmarkAdapter

__all__ = [
    "QuickBenchmarkAdapter"
]
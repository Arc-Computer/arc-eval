"""
Benchmark Adapters for ARC-Eval.

Provides specialized adapters for external benchmarks.
"""

from .mmlu import MMLUAdapter
from .humeval import HumanEvalAdapter  
from .gsm8k import GSM8KAdapter

__all__ = ["MMLUAdapter", "HumanEvalAdapter", "GSM8KAdapter"]
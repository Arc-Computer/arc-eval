"""
Quick Benchmark Integration for ARC-Eval.

Provides adapters for popular AI benchmarks (MMLU, HumanEval, GSM8K)
to integrate with existing ARC-Eval evaluation framework.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from agent_eval.core.types import EvaluationScenario


logger = logging.getLogger(__name__)


class QuickBenchmarkAdapter:
    """Quick integration for popular benchmarks - immediate utility."""
    
    def __init__(self):
        self.supported_benchmarks = {
            "mmlu": self._load_mmlu_subset,
            "humeval": self._load_humeval_subset,
            "gsm8k": self._load_gsm8k_subset
        }
    
    def load_benchmark(self, benchmark_name: str, subset: Optional[str] = None, limit: Optional[int] = 10) -> List[EvaluationScenario]:
        """Load benchmark and convert to EvaluationScenario format.
        
        Args:
            benchmark_name: Name of benchmark (mmlu, humeval, gsm8k)
            subset: Specific subset (e.g., 'anatomy' for MMLU)
            limit: Maximum number of scenarios to load
            
        Returns:
            List of EvaluationScenario objects
        """
        if benchmark_name not in self.supported_benchmarks:
            raise ValueError(f"Benchmark {benchmark_name} not supported. Available: {list(self.supported_benchmarks.keys())}")
        
        loader_func = self.supported_benchmarks[benchmark_name]
        return loader_func(subset=subset, limit=limit)
    
    def _load_mmlu_subset(self, subset: str = "anatomy", limit: int = 10) -> List[EvaluationScenario]:
        """Load MMLU subset and convert to EvaluationScenario format.
        
        Args:
            subset: MMLU subject (default: anatomy)
            limit: Number of questions to load
            
        Returns:
            List of EvaluationScenario objects
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for MMLU integration. Install with: pip install datasets")
        
        try:
            # Load MMLU dataset from HuggingFace
            dataset = load_dataset("cais/mmlu", subset, split="test")
            
            scenarios = []
            items = dataset[:limit] if limit else dataset
            
            # Convert to list format if needed
            if isinstance(items, dict):
                # Convert from dataset dict format to list
                num_items = len(items[list(items.keys())[0]])
                items_list = []
                for i in range(num_items):
                    item = {key: items[key][i] for key in items.keys()}
                    items_list.append(item)
                items = items_list
            
            for i, item in enumerate(items):
                scenario = EvaluationScenario(
                    id=f"mmlu_{subset}_{i}",
                    name=f"MMLU {subset.title()} Question {i+1}",
                    description=f"Multiple choice question from {subset} domain",
                    category="knowledge_reasoning",
                    severity="medium",
                    test_type="positive",
                    compliance=["academic_benchmark", "mmlu"],
                    input_template=f"Question: {item['question']}\nChoices: {', '.join(item['choices'])}",
                    expected_behavior="correct_answer",
                    failure_indicators=["incorrect_answer", "random_guess"],
                    remediation=f"Review {subset} knowledge and reasoning capabilities",
                    benchmark_alignment="MMLU"
                )
                scenarios.append(scenario)
            
            logger.info(f"Loaded {len(scenarios)} MMLU {subset} scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to load MMLU {subset}: {e}")
            # Return fallback scenarios for demo purposes
            return self._get_fallback_mmlu_scenarios(subset, limit)
    
    def _load_humeval_subset(self, subset: Optional[str] = None, limit: int = 10) -> List[EvaluationScenario]:
        """Load HumanEval subset and convert to EvaluationScenario format.
        
        Args:
            subset: Not used for HumanEval (single dataset)
            limit: Number of problems to load
            
        Returns:
            List of EvaluationScenario objects
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for HumanEval integration. Install with: pip install datasets")
        
        try:
            # Load HumanEval dataset
            dataset = load_dataset("openai_humaneval", split="test")
            
            scenarios = []
            items = dataset[:limit] if limit else dataset
            
            # Convert to list format if needed
            if isinstance(items, dict):
                num_items = len(items[list(items.keys())[0]])
                items_list = []
                for i in range(num_items):
                    item = {key: items[key][i] for key in items.keys()}
                    items_list.append(item)
                items = items_list
            
            for i, item in enumerate(items):
                scenario = EvaluationScenario(
                    id=f"humeval_{item.get('task_id', i)}",
                    name=f"HumanEval {item.get('task_id', f'Problem_{i+1}')}",
                    description="Code generation and correctness evaluation",
                    category="code_generation",
                    severity="high",
                    test_type="positive",
                    compliance=["academic_benchmark", "humeval"],
                    input_template=item.get('prompt', 'Code generation task'),
                    expected_behavior="correct_code_solution",
                    failure_indicators=["syntax_error", "incorrect_logic", "incomplete_solution"],
                    remediation="Review code generation capabilities and programming fundamentals",
                    benchmark_alignment="HumanEval"
                )
                scenarios.append(scenario)
            
            logger.info(f"Loaded {len(scenarios)} HumanEval scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to load HumanEval: {e}")
            # Return fallback scenarios for demo purposes
            return self._get_fallback_humeval_scenarios(limit)
    
    def _load_gsm8k_subset(self, subset: Optional[str] = None, limit: int = 10) -> List[EvaluationScenario]:
        """Load GSM8K subset and convert to EvaluationScenario format.
        
        Args:
            subset: Not used for GSM8K (single dataset)
            limit: Number of problems to load
            
        Returns:
            List of EvaluationScenario objects
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for GSM8K integration. Install with: pip install datasets")
        
        try:
            # Load GSM8K dataset
            dataset = load_dataset("gsm8k", "main", split="test")
            
            scenarios = []
            items = dataset[:limit] if limit else dataset
            
            # Convert to list format if needed
            if isinstance(items, dict):
                num_items = len(items[list(items.keys())[0]])
                items_list = []
                for i in range(num_items):
                    item = {key: items[key][i] for key in items.keys()}
                    items_list.append(item)
                items = items_list
            
            for i, item in enumerate(items):
                scenario = EvaluationScenario(
                    id=f"gsm8k_{i}",
                    name=f"GSM8K Math Problem {i+1}",
                    description="Grade school math word problem reasoning",
                    category="mathematical_reasoning",
                    severity="medium",
                    test_type="positive",
                    compliance=["academic_benchmark", "gsm8k"],
                    input_template=item.get('question', 'Math word problem'),
                    expected_behavior="correct_numerical_answer",
                    failure_indicators=["wrong_answer", "calculation_error", "misunderstood_problem"],
                    remediation="Review mathematical reasoning and arithmetic capabilities",
                    benchmark_alignment="GSM8K"
                )
                scenarios.append(scenario)
            
            logger.info(f"Loaded {len(scenarios)} GSM8K scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to load GSM8K: {e}")
            # Return fallback scenarios for demo purposes
            return self._get_fallback_gsm8k_scenarios(limit)
    
    def _get_fallback_mmlu_scenarios(self, subset: str, limit: int) -> List[EvaluationScenario]:
        """Fallback MMLU scenarios when dataset loading fails."""
        fallback_scenarios = [
            EvaluationScenario(
                id=f"mmlu_{subset}_fallback_1",
                name=f"MMLU {subset.title()} Demo Question",
                description=f"Sample multiple choice question from {subset} domain",
                category="knowledge_reasoning",
                severity="medium",
                test_type="positive",
                compliance=["academic_benchmark", "mmlu"],
                input_template=f"Sample {subset} knowledge question (fallback mode)",
                expected_behavior="correct_answer",
                failure_indicators=["incorrect_answer"],
                remediation=f"Review {subset} knowledge base",
                benchmark_alignment="MMLU"
            )
        ]
        return fallback_scenarios[:limit]
    
    def _get_fallback_humeval_scenarios(self, limit: int) -> List[EvaluationScenario]:
        """Fallback HumanEval scenarios when dataset loading fails."""
        fallback_scenarios = [
            EvaluationScenario(
                id="humeval_fallback_1",
                name="HumanEval Demo Problem",
                description="Sample code generation task",
                category="code_generation",
                severity="high",
                test_type="positive",
                compliance=["academic_benchmark", "humeval"],
                input_template="Write a function to solve a programming problem (fallback mode)",
                expected_behavior="correct_code_solution",
                failure_indicators=["syntax_error", "incorrect_logic"],
                remediation="Review code generation capabilities",
                benchmark_alignment="HumanEval"
            )
        ]
        return fallback_scenarios[:limit]
    
    def _get_fallback_gsm8k_scenarios(self, limit: int) -> List[EvaluationScenario]:
        """Fallback GSM8K scenarios when dataset loading fails."""
        fallback_scenarios = [
            EvaluationScenario(
                id="gsm8k_fallback_1",
                name="GSM8K Demo Problem",
                description="Sample grade school math problem",
                category="mathematical_reasoning",
                severity="medium",
                test_type="positive",
                compliance=["academic_benchmark", "gsm8k"],
                input_template="Sample math word problem (fallback mode)",
                expected_behavior="correct_numerical_answer",
                failure_indicators=["wrong_answer"],
                remediation="Review mathematical reasoning",
                benchmark_alignment="GSM8K"
            )
        ]
        return fallback_scenarios[:limit]
    
    def get_supported_benchmarks(self) -> List[str]:
        """Get list of supported benchmark names."""
        return list(self.supported_benchmarks.keys())
    
    def validate_benchmark_name(self, benchmark_name: str) -> bool:
        """Validate if benchmark name is supported."""
        return benchmark_name in self.supported_benchmarks

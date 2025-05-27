"""
HumanEval Adapter.

Integrates HumanEval code generation benchmark with ARC-Eval evaluation framework.
"""

import logging
from typing import List, Dict, Any, Optional

from agent_eval.core.types import EvaluationScenario


logger = logging.getLogger(__name__)


class HumanEvalAdapter:
    """Adapter for HumanEval code generation benchmark."""
    
    def __init__(self):
        self.name = "HumanEval"
        self.description = "Human-written evaluations for code generation"
    
    def load_raw_data(self, subset: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Load raw HumanEval data from HuggingFace datasets.
        
        Args:
            subset: Not used for HumanEval (single dataset)
            limit: Maximum number of items to load
            
        Returns:
            List of raw HumanEval data items
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for HumanEval. Install with: pip install datasets")
        
        try:
            dataset = load_dataset("openai_humaneval", split="test")
            
            # Convert to list format
            items = dataset[:limit] if limit else dataset
            
            if isinstance(items, dict):
                # Convert from dataset dict format to list
                num_items = len(items[list(items.keys())[0]])
                items_list = []
                for i in range(num_items):
                    item = {key: items[key][i] for key in items.keys()}
                    items_list.append(item)
                return items_list
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to load HumanEval: {e}")
            raise
    
    def convert_to_arc_format(self, raw_data: List[Dict]) -> List[EvaluationScenario]:
        """Convert raw HumanEval data to ARC-Eval EvaluationScenario format.
        
        Args:
            raw_data: Raw HumanEval data items
            
        Returns:
            List of EvaluationScenario objects
        """
        scenarios = []
        
        for i, item in enumerate(raw_data):
            # Extract components
            task_id = item.get("task_id", f"HumanEval/{i}")
            prompt = item.get("prompt", "")
            canonical_solution = item.get("canonical_solution", "")
            test = item.get("test", "")
            entry_point = item.get("entry_point", "")
            
            # Clean up task_id for display
            clean_task_id = task_id.replace("HumanEval/", "")
            
            # Extract function name from prompt if possible
            function_name = entry_point or "function"
            
            scenario = EvaluationScenario(
                id=f"humeval_{clean_task_id}",
                name=f"HumanEval {clean_task_id}: {function_name}",
                description="Code generation task with automated testing",
                category="code_generation",
                severity="high",
                test_type="positive",
                compliance=["academic_benchmark", "humeval", "code_safety"],
                input_template=f"Complete the following Python function:\\n\\n{prompt}\\n\\nProvide a working implementation:",
                expected_behavior="correct_functional_code",
                failure_indicators=[
                    "syntax_error", "runtime_error", "incorrect_logic", 
                    "incomplete_implementation", "security_vulnerability"
                ],
                remediation=f"Review Python programming fundamentals and {function_name} implementation patterns",
                benchmark_alignment="HumanEval"
            )
            scenarios.append(scenario)
        
        logger.info(f"Converted {len(scenarios)} HumanEval items to scenarios")
        return scenarios
    
    def validate_scenarios(self, scenarios: List[EvaluationScenario]) -> bool:
        """Validate converted scenarios for HumanEval format compliance.
        
        Args:
            scenarios: List of scenarios to validate
            
        Returns:
            True if all scenarios are valid
        """
        for scenario in scenarios:
            if not scenario.id.startswith("humeval_"):
                logger.error(f"Invalid HumanEval scenario ID: {scenario.id}")
                return False
            
            if "humeval" not in scenario.compliance:
                logger.error(f"HumanEval scenario missing compliance tag: {scenario.id}")
                return False
            
            if scenario.category != "code_generation":
                logger.error(f"Invalid category for HumanEval scenario: {scenario.category}")
                return False
        
        return True
    
    def extract_function_signature(self, prompt: str) -> str:
        """Extract function signature from HumanEval prompt.
        
        Args:
            prompt: HumanEval prompt text
            
        Returns:
            Function signature or empty string
        """
        lines = prompt.strip().split('\n')
        for line in lines:
            if line.strip().startswith('def '):
                return line.strip()
        return ""
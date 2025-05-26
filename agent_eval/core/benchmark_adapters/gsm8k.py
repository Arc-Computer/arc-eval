"""
GSM8K (Grade School Math 8K) Adapter.

Integrates GSM8K mathematical reasoning benchmark with ARC-Eval evaluation framework.
"""

import logging
import re
from typing import List, Dict, Any, Optional

from agent_eval.core.types import EvaluationScenario


logger = logging.getLogger(__name__)


class GSM8KAdapter:
    """Adapter for Grade School Math 8K benchmark."""
    
    def __init__(self):
        self.name = "GSM8K"
        self.description = "Grade school math word problems requiring multi-step reasoning"
    
    def load_raw_data(self, subset: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Load raw GSM8K data from HuggingFace datasets.
        
        Args:
            subset: Not used for GSM8K (single dataset)
            limit: Maximum number of items to load
            
        Returns:
            List of raw GSM8K data items
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for GSM8K. Install with: pip install datasets")
        
        try:
            dataset = load_dataset("gsm8k", "main", split="test")
            
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
            logger.error(f"Failed to load GSM8K: {e}")
            raise
    
    def convert_to_arc_format(self, raw_data: List[Dict]) -> List[EvaluationScenario]:
        """Convert raw GSM8K data to ARC-Eval EvaluationScenario format.
        
        Args:
            raw_data: Raw GSM8K data items
            
        Returns:
            List of EvaluationScenario objects
        """
        scenarios = []
        
        for i, item in enumerate(raw_data):
            # Extract components
            question = item.get("question", "")
            answer = item.get("answer", "")
            
            # Extract numerical answer from the solution
            numerical_answer = self.extract_numerical_answer(answer)
            
            # Determine problem complexity
            complexity = self.assess_problem_complexity(question)
            
            scenario = EvaluationScenario(
                id=f"gsm8k_{i}",
                name=f"GSM8K Math Problem {i+1}",
                description=f"Grade school math word problem ({complexity} complexity)",
                category="mathematical_reasoning",
                severity="medium",
                test_type="positive",
                compliance=["academic_benchmark", "gsm8k", "mathematical_reasoning"],
                input_template=f"Solve this math word problem step by step:\\n\\n{question}\\n\\nProvide your answer as a number:",
                expected_behavior=f"numerical_answer_{numerical_answer}",
                failure_indicators=[
                    "wrong_numerical_answer", "calculation_error", "misunderstood_problem",
                    "incomplete_reasoning", "no_numerical_answer"
                ],
                remediation="Review mathematical reasoning, arithmetic operations, and word problem comprehension",
                benchmark_alignment="GSM8K"
            )
            scenarios.append(scenario)
        
        logger.info(f"Converted {len(scenarios)} GSM8K items to scenarios")
        return scenarios
    
    def validate_scenarios(self, scenarios: List[EvaluationScenario]) -> bool:
        """Validate converted scenarios for GSM8K format compliance.
        
        Args:
            scenarios: List of scenarios to validate
            
        Returns:
            True if all scenarios are valid
        """
        for scenario in scenarios:
            if not scenario.id.startswith("gsm8k_"):
                logger.error(f"Invalid GSM8K scenario ID: {scenario.id}")
                return False
            
            if "gsm8k" not in scenario.compliance:
                logger.error(f"GSM8K scenario missing compliance tag: {scenario.id}")
                return False
            
            if scenario.category != "mathematical_reasoning":
                logger.error(f"Invalid category for GSM8K scenario: {scenario.category}")
                return False
        
        return True
    
    def extract_numerical_answer(self, answer_text: str) -> str:
        """Extract the final numerical answer from GSM8K solution text.
        
        Args:
            answer_text: Full solution text with reasoning
            
        Returns:
            Numerical answer as string
        """
        # Look for patterns like "#### 42" at the end
        answer_pattern = r"####\s*([0-9,.-]+)"
        match = re.search(answer_pattern, answer_text)
        if match:
            return match.group(1).replace(",", "")
        
        # Fallback: look for numbers at the end of text
        number_pattern = r"([0-9,.-]+)(?:\s*\.?\s*)?$"
        match = re.search(number_pattern, answer_text.strip())
        if match:
            return match.group(1).replace(",", "")
        
        # If no clear answer found, return placeholder
        return "unknown"
    
    def assess_problem_complexity(self, question: str) -> str:
        """Assess the complexity level of a math problem.
        
        Args:
            question: Problem text
            
        Returns:
            Complexity level: "basic", "intermediate", or "advanced"
        """
        # Simple heuristics for complexity assessment
        question_lower = question.lower()
        
        # Count mathematical operations indicators
        operation_indicators = [
            "multiply", "divide", "add", "subtract", "percent", "fraction",
            "ratio", "proportion", "average", "total", "sum", "difference"
        ]
        
        operation_count = sum(1 for indicator in operation_indicators if indicator in question_lower)
        
        # Count numerical values
        numbers = re.findall(r'\d+', question)
        number_count = len(numbers)
        
        # Assess complexity
        if operation_count <= 2 and number_count <= 3:
            return "basic"
        elif operation_count <= 4 and number_count <= 6:
            return "intermediate"
        else:
            return "advanced"
    
    def get_problem_category(self, question: str) -> str:
        """Categorize the type of math problem.
        
        Args:
            question: Problem text
            
        Returns:
            Problem category
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["money", "cost", "price", "buy", "sell", "dollar"]):
            return "money_problems"
        elif any(word in question_lower for word in ["time", "hour", "minute", "day", "week"]):
            return "time_problems"
        elif any(word in question_lower for word in ["distance", "speed", "travel", "mile", "kilometer"]):
            return "distance_problems"
        elif any(word in question_lower for word in ["age", "old", "year", "birthday"]):
            return "age_problems"
        else:
            return "general_arithmetic"
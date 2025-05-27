"""
MMLU (Massive Multitask Language Understanding) Adapter.

Integrates MMLU benchmark with ARC-Eval evaluation framework.
"""

import logging
from typing import List, Dict, Any, Optional

from agent_eval.core.types import EvaluationScenario


logger = logging.getLogger(__name__)


class MMLUAdapter:
    """Adapter for Massive Multitask Language Understanding benchmark."""
    
    AVAILABLE_SUBJECTS = [
        "abstract_algebra", "anatomy", "astronomy", "business_ethics", "clinical_knowledge",
        "college_biology", "college_chemistry", "college_computer_science", "college_mathematics",
        "college_medicine", "college_physics", "computer_security", "conceptual_physics",
        "econometrics", "electrical_engineering", "elementary_mathematics", "formal_logic",
        "global_facts", "high_school_biology", "high_school_chemistry", "high_school_computer_science",
        "high_school_european_history", "high_school_geography", "high_school_government_and_politics",
        "high_school_macroeconomics", "high_school_mathematics", "high_school_microeconomics",
        "high_school_physics", "high_school_psychology", "high_school_statistics", "high_school_us_history",
        "high_school_world_history", "human_aging", "human_sexuality", "international_law",
        "jurisprudence", "logical_fallacies", "machine_learning", "management", "marketing",
        "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios", "nutrition",
        "philosophy", "prehistory", "professional_accounting", "professional_law", "professional_medicine",
        "professional_psychology", "public_relations", "security_studies", "sociology", "us_foreign_policy",
        "virology", "world_religions"
    ]
    
    def __init__(self):
        self.name = "MMLU"
        self.description = "Massive Multitask Language Understanding benchmark"
    
    def load_raw_data(self, subset: str = "anatomy", limit: Optional[int] = None) -> List[Dict]:
        """Load raw MMLU data from HuggingFace datasets.
        
        Args:
            subset: MMLU subject/subset name
            limit: Maximum number of items to load
            
        Returns:
            List of raw MMLU data items
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library required for MMLU. Install with: pip install datasets")
        
        if subset not in self.AVAILABLE_SUBJECTS:
            logger.warning(f"Subject {subset} not in known subjects. Attempting to load anyway...")
        
        try:
            dataset = load_dataset("cais/mmlu", subset, split="test")
            
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
            logger.error(f"Failed to load MMLU {subset}: {e}")
            raise
    
    def convert_to_arc_format(self, raw_data: List[Dict], subset: str = "anatomy") -> List[EvaluationScenario]:
        """Convert raw MMLU data to ARC-Eval EvaluationScenario format.
        
        Args:
            raw_data: Raw MMLU data items
            subset: Subject name for context
            
        Returns:
            List of EvaluationScenario objects
        """
        scenarios = []
        
        for i, item in enumerate(raw_data):
            # Extract question components
            question = item.get("question", "")
            choices = item.get("choices", [])
            correct_answer = item.get("answer", 0)  # Usually an index
            
            # Format choices for display
            choice_text = ""
            if choices:
                choice_labels = ["A", "B", "C", "D"]
                choice_text = "\n".join([f"{choice_labels[j]}: {choice}" for j, choice in enumerate(choices[:4])])
            
            # Determine correct choice letter - handle both int indices and string answers
            correct_choice = "A"
            if isinstance(correct_answer, int) and 0 <= correct_answer < len(choices):
                correct_choice = ["A", "B", "C", "D"][correct_answer]
            elif isinstance(correct_answer, str) and correct_answer.upper() in ["A", "B", "C", "D"]:
                correct_choice = correct_answer.upper()
            else:
                # Log unexpected answer format but continue with default
                logger.warning(f"Unexpected answer format: {correct_answer}, using 'A' as default")
            
            scenario = EvaluationScenario(
                id=f"mmlu_{subset}_{i}",
                name=f"MMLU {subset.replace('_', ' ').title()} Q{i+1}",
                description=f"Multiple choice question from {subset.replace('_', ' ')} domain",
                category="knowledge_reasoning",
                severity="medium",
                test_type="positive",
                compliance=["academic_benchmark", "mmlu", subset],
                input_template=f"Question: {question}\n\nChoices:\n{choice_text}\n\nProvide the correct answer (A, B, C, or D):",
                expected_behavior=f"select_choice_{correct_choice}",
                failure_indicators=["incorrect_choice", "no_answer", "invalid_format"],
                remediation=f"Review knowledge in {subset.replace('_', ' ')} domain and improve multiple choice reasoning",
                benchmark_alignment="MMLU"
            )
            scenarios.append(scenario)
        
        logger.info(f"Converted {len(scenarios)} MMLU {subset} items to scenarios")
        return scenarios
    
    def validate_scenarios(self, scenarios: List[EvaluationScenario]) -> bool:
        """Validate converted scenarios for MMLU format compliance.
        
        Args:
            scenarios: List of scenarios to validate
            
        Returns:
            True if all scenarios are valid
        """
        for scenario in scenarios:
            if not scenario.id.startswith("mmlu_"):
                logger.error(f"Invalid MMLU scenario ID: {scenario.id}")
                return False
            
            if "mmlu" not in scenario.compliance:
                logger.error(f"MMLU scenario missing compliance tag: {scenario.id}")
                return False
            
            if scenario.category != "knowledge_reasoning":
                logger.error(f"Invalid category for MMLU scenario: {scenario.category}")
                return False
        
        return True
    
    def get_available_subjects(self) -> List[str]:
        """Get list of available MMLU subjects."""
        return self.AVAILABLE_SUBJECTS.copy()
"""Scenario bank for managing learned failure patterns and generating test scenarios.

The ScenarioBank implements an adaptive curriculum learning system that:
- Stores learned failure patterns from agent evaluations
- Generates new test scenarios based on discovered patterns
- Classifies scenario difficulty for progressive learning
- Provides adaptive scenario selection for optimal training
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import yaml

try:
    import fcntl
    has_fcntl = True
except ImportError:
    has_fcntl = False


class ScenarioBank:
    """Stores and manages learned failure patterns and generates test scenarios.
    
    The ScenarioBank is a core component of the adaptive curriculum learning system.
    It provides functionality for:
    
    - **Pattern Storage**: Thread-safe storage of failure patterns as JSONL
    - **Scenario Generation**: Converting patterns into reusable test scenarios
    - **Difficulty Classification**: Multi-factor difficulty assessment
    - **Adaptive Selection**: Dynamic scenario selection based on performance
    - **Curriculum Management**: Progressive difficulty adjustment
    
    Attributes:
        patterns_file: Path to learned patterns JSONL file (.arc-eval/learned_patterns.jsonl)
        scenarios_file: Path to generated scenarios YAML file (agent_eval/domains/customer_generated.yaml)
    """

    def __init__(self) -> None:
        """Initialize the ScenarioBank with default file paths.
        
        Creates necessary directories and sets up file paths for:
        - Learned patterns storage (user-specific, git-ignored)
        - Generated scenarios file (auto-generated, git-ignored)
        """
        # Patterns file (appended as JSONL); user-specific, git-ignored
        self.patterns_file = ".arc-eval/learned_patterns.jsonl"
        # Generated scenarios file under domains (auto-generated, git-ignored)
        self.scenarios_file = "agent_eval/domains/customer_generated.yaml"
        # Ensure patterns directory exists
        patterns_dir = os.path.dirname(self.patterns_file)
        if patterns_dir and not os.path.exists(patterns_dir):
            os.makedirs(patterns_dir, exist_ok=True)

    def add_pattern(self, pattern: Dict[str, Any]) -> None:
        """Append a new failure pattern entry (thread-safe).

        Uses file locking (where available) to ensure thread-safe writes
        when multiple evaluation processes are running concurrently.

        Args:
            pattern: Failure pattern dictionary containing:
                - fingerprint: Unique identifier for the pattern
                - failure_reason: Description of what went wrong
                - scenario_id: Associated scenario ID
                - domain: Evaluation domain (finance, security, ml)
                - compliance_violation: List of violated compliance frameworks
                - remediation: Suggested fix or improvement

        Raises:
            OSError: If file cannot be opened or written to
            json.JSONEncodeError: If pattern cannot be serialized to JSON
        """
        try:
            with open(self.patterns_file, "a") as f:
                if has_fcntl:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(json.dumps(pattern) + "\n")
                finally:
                    if has_fcntl:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (OSError, json.JSONEncodeError) as e:
            raise RuntimeError(f"Failed to add pattern to {self.patterns_file}: {e}") from e

    def get_pattern_count(self, fingerprint: str) -> int:
        """Return how many times this fingerprint has been recorded.

        Used for tracking pattern frequency to identify recurring issues
        and prioritize high-frequency patterns in curriculum generation.

        Args:
            fingerprint: Unique identifier for the pattern

        Returns:
            Count of times this pattern has been recorded

        Raises:
            ValueError: If fingerprint is empty or None
        """
        if not fingerprint:
            raise ValueError("Fingerprint cannot be empty or None")

        if not os.path.exists(self.patterns_file):
            return 0

        count = 0
        try:
            with open(self.patterns_file) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("fingerprint") == fingerprint:
                            count += 1
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
        except OSError as e:
            raise RuntimeError(f"Failed to read patterns file {self.patterns_file}: {e}") from e

        return count

    def _write_scenarios_header(self) -> str:
        """Return the auto-generated scenarios file header.
        
        Creates a header comment block with metadata about:
        - Generation timestamp
        - Total patterns learned
        - Usage instructions
        
        Returns:
            Formatted header string for YAML file
        """
        total = self._get_total_pattern_count()
        header = """# AUTO-GENERATED - DO NOT EDIT MANUALLY
# Generated by Arc-Eval Pattern Learning System
# Last updated: {timestamp}
# Patterns learned: {count}
#
# These scenarios are automatically generated from real customer failures.
# To modify, use the pattern learning system, not direct edits.
"""
        return header.format(timestamp=datetime.now().isoformat(), count=total)

    def _get_total_pattern_count(self) -> int:
        """Count total recorded patterns across all fingerprints.
        
        Provides statistics for header generation and curriculum planning.
        
        Returns:
            Total number of pattern entries in the JSONL file
        """
        if not os.path.exists(self.patterns_file):
            return 0
        lines = 0
        with open(self.patterns_file) as f:
            for _ in f:
                lines += 1
        return lines

    def generate_scenario(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a failure pattern into a new test scenario definition.
        
        Transforms learned failure patterns into reusable test scenarios
        that can be included in future evaluation runs. Appends the new
        scenario to the customer-generated scenarios file.
        
        Args:
            pattern: Failure pattern dictionary containing pattern metadata
            
        Returns:
            Generated scenario dictionary with:
            - id: Scenario identifier
            - name: Human-readable scenario name
            - description: Detailed description
            - severity: Risk severity level (defaulted to 'high')
            - test_type: Type of test ('behavioral')
            - category: Domain category
            - compliance: Associated compliance frameworks
            - failure_indicators: What to look for in agent outputs
            - remediation: Suggested fixes
        """
        scenario = {
            "id": pattern.get('scenario_id'),
            "name": f"LEARNED: {pattern.get('failure_reason', '')[:50]}",
            "description": pattern.get("failure_reason", "").strip(),
            "severity": "high",  # Default to high for learned patterns
            "test_type": "behavioral",
            "category": pattern.get("domain", "general"),
            "compliance": pattern.get("compliance_violation", []),
            "input_template": {"test": "learned_pattern"},
            "expected_behavior": "Agent should handle this pattern correctly",
            "failure_indicators": [pattern.get("failure_reason", "")],
            "remediation": pattern.get("remediation", "").strip(),
        }
        # Ensure scenarios_file directory exists
        scenarios_dir = os.path.dirname(self.scenarios_file)
        if scenarios_dir and not os.path.exists(scenarios_dir):
            os.makedirs(scenarios_dir, exist_ok=True)

        # Read existing content
        existing = {"scenarios": []}
        first_write = not os.path.exists(self.scenarios_file) or os.path.getsize(self.scenarios_file) == 0
        if not first_write:
            with open(self.scenarios_file, "r") as f:
                existing = yaml.safe_load(f) or existing
        
        # Append new scenario
        existing["scenarios"].append(scenario)
        
        # Write back complete file
        with open(self.scenarios_file, "w") as f:
            if first_write:
                f.write(self._write_scenarios_header())
            yaml.dump(existing, f, sort_keys=False)
        return scenario
    
    def classify_scenario_difficulty(self, scenario: Dict[str, Any]) -> str:
        """Classify scenario difficulty based on compliance requirements and complexity.
        
        Uses a multi-factor scoring system to assess scenario difficulty:
        - Compliance framework count and criticality
        - Description complexity indicators
        - Domain-specific complexity (e.g., model governance)
        - Scenario ID patterns (later scenarios tend to be more complex)
        
        Difficulty levels:
        - basic: Single compliance requirement, straightforward validation
        - intermediate: Multiple compliance requirements or complex reasoning
        - advanced: Multi-step reasoning, composition, or critical compliance
        
        Args:
            scenario: Scenario dictionary to classify
            
        Returns:
            Difficulty level: 'basic', 'intermediate', or 'advanced'
        """
        scenario_id = scenario.get('id', '')
        compliance = scenario.get('compliance', [])
        description = scenario.get('description', '').lower()
        category = scenario.get('category', '').lower()
        
        # Count complexity indicators
        complexity_score = 0
        
        # Compliance complexity
        if len(compliance) >= 3:
            complexity_score += 2
        elif len(compliance) == 2:
            complexity_score += 1
        
        # Critical compliance areas (higher difficulty)
        critical_frameworks = ['sox', 'aml', 'kyc', 'sr-11-7', 'eu-ai-act']
        if any(framework in str(compliance).lower() for framework in critical_frameworks):
            complexity_score += 1
        
        # Description complexity indicators
        complex_keywords = ['multi-step', 'complex', 'comprehensive', 'cross-border', 'validation', 'monitoring']
        if any(keyword in description for keyword in complex_keywords):
            complexity_score += 1
        
        # Model governance and bias are inherently more complex
        if 'model' in category or 'bias' in category or 'ai/ml' in category:
            complexity_score += 1
        
        # Scenario ID-based patterns (later scenarios tend to be more complex)
        if scenario_id:
            try:
                scenario_num = int(scenario_id.split('_')[1]) if '_' in scenario_id else 0
                if scenario_num >= 80:
                    complexity_score += 2
                elif scenario_num >= 50:
                    complexity_score += 1
            except (ValueError, IndexError):
                pass
        
        # Classify based on score
        if complexity_score >= 4:
            return 'advanced'
        elif complexity_score >= 2:
            return 'intermediate'
        else:
            return 'basic'
    
    def get_scenarios_by_difficulty(self, domain: str, difficulty: str) -> List[Dict[str, Any]]:
        """Get scenarios filtered by difficulty level from domain YAML file.
        
        Loads scenarios from the specified domain pack and filters them
        by the requested difficulty level using the classification system.
        
        Args:
            domain: Domain name (finance, security, ml)
            difficulty: Target difficulty level ('basic', 'intermediate', 'advanced')
            
        Returns:
            List of scenario dictionaries matching the difficulty level
        """
        domain_file = f"agent_eval/domains/{domain}.yaml"
        
        if not os.path.exists(domain_file):
            return []
        
        try:
            with open(domain_file, 'r') as f:
                domain_data = yaml.safe_load(f)
            
            scenarios = domain_data.get('scenarios', [])
            filtered_scenarios = []
            
            for scenario in scenarios:
                if self.classify_scenario_difficulty(scenario) == difficulty:
                    filtered_scenarios.append(scenario)
            
            return filtered_scenarios
            
        except Exception as e:
            print(f"Error loading domain scenarios: {e}")
            return []
    
    def adjust_complexity_dynamically(self, learning_progress: float, current_difficulty: str) -> str:
        """
        Adjust scenario complexity based on learning velocity for optimal challenge.
        
        Args:
            learning_progress: Learning progress score [0.0, 1.0] from TD-error analysis
            current_difficulty: Current difficulty level ('basic', 'intermediate', 'advanced')
            
        Returns:
            Adjusted difficulty level maintaining optimal learning zone
        """
        if learning_progress > 0.8:  # Learning too fast, increase challenge
            if current_difficulty == 'basic':
                return 'intermediate'
            elif current_difficulty == 'intermediate':
                return 'advanced'
            return current_difficulty  # Already at max
            
        elif learning_progress < 0.2:  # Struggling, reduce challenge
            if current_difficulty == 'advanced':
                return 'intermediate' 
            elif current_difficulty == 'intermediate':
                return 'basic'
            return current_difficulty  # Already at min
            
        return current_difficulty  # Stay in sweet spot (0.2-0.8)

    def get_adaptive_scenario_selection(self, performance_data: Dict[str, Any], 
                                      target_difficulty: str, 
                                      domain: str = 'finance',
                                      count: int = 5) -> List[Dict[str, Any]]:
        """Select scenarios adaptively based on current performance and target difficulty.
        
        Implements intelligent scenario selection using:
        - Dynamic difficulty adjustment based on learning progress
        - Weakness area targeting for focused improvement
        - Mastery area avoidance to prevent overfitting
        - Balanced curriculum for comprehensive coverage
        
        Performance data should include:
        - overall_pass_rate: Current agent pass rate (0.0-1.0)
        - weakness_areas: List of compliance areas with low performance
        - mastered_areas: List of compliance areas with high performance
        - learning_progress: TD-error based learning velocity [0.0-1.0]
        
        Args:
            performance_data: Dictionary containing current performance metrics
            target_difficulty: Initial target difficulty level
            domain: Domain to select scenarios from (default: 'finance')
            count: Number of scenarios to select (default: 5)
            
        Returns:
            List of selected scenario dictionaries, prioritized by weakness areas
        """
        overall_pass_rate = performance_data.get('overall_pass_rate', 0.5)
        weakness_areas = performance_data.get('weakness_areas', [])
        mastered_areas = performance_data.get('mastered_areas', [])
        learning_progress = performance_data.get('learning_progress', 0.5)
        
        # Dynamically adjust complexity based on learning progress
        adjusted_difficulty = self.adjust_complexity_dynamically(learning_progress, target_difficulty)
        
        # Load all scenarios from domain
        domain_file = f"agent_eval/domains/{domain}.yaml"
        if not os.path.exists(domain_file):
            return []
        
        try:
            with open(domain_file, 'r') as f:
                domain_data = yaml.safe_load(f)
            
            # Parse the actual finance.yaml structure which has categories, not direct scenarios
            all_scenarios = []
            if 'scenarios' in domain_data:
                # Direct scenarios list (for customer_generated.yaml)
                all_scenarios = domain_data['scenarios']
            else:
                # finance.yaml format: extract scenarios from categories
                categories = domain_data.get('categories', [])
                for category in categories:
                    scenario_ids = category.get('scenarios', [])
                    category_name = category.get('name', 'general')
                    compliance_list = category.get('compliance', [])
                    
                    for scenario_id in scenario_ids:
                        # Create scenario object from ID and category metadata
                        scenario = {
                            'id': scenario_id,
                            'name': f"{category_name}: {scenario_id}",
                            'description': category.get('description', ''),
                            'category': category_name.lower().replace(' ', '_'),
                            'compliance': compliance_list,
                            'severity': 'medium',  # Default
                            'test_type': 'behavioral'
                        }
                        all_scenarios.append(scenario)
            
            # Filter by adjusted difficulty (enhanced with learning progress)
            difficulty_filtered = [
                scenario for scenario in all_scenarios
                if self.classify_scenario_difficulty(scenario) == adjusted_difficulty
            ]
            
            # Prioritize scenarios that target weakness areas
            prioritized_scenarios = []
            backup_scenarios = []
            
            for scenario in difficulty_filtered:
                scenario_compliance = [comp.lower() for comp in scenario.get('compliance', [])]
                category = scenario.get('category', '').lower()
                
                # Check if this scenario addresses known weaknesses
                addresses_weakness = any(
                    weakness.lower() in scenario_compliance or weakness.lower() in category
                    for weakness in weakness_areas
                )
                
                # Avoid scenarios in already mastered areas unless we need to fill quota
                addresses_mastered = any(
                    mastered.lower() in scenario_compliance or mastered.lower() in category
                    for mastered in mastered_areas
                )
                
                if addresses_weakness:
                    prioritized_scenarios.append(scenario)
                elif not addresses_mastered:
                    backup_scenarios.append(scenario)
            
            # Select scenarios: prioritize weaknesses, then fill with others
            selected = prioritized_scenarios[:count]
            
            if len(selected) < count:
                remaining = count - len(selected)
                selected.extend(backup_scenarios[:remaining])
            
            # If still not enough, use any remaining scenarios
            if len(selected) < count:
                remaining = count - len(selected)
                all_remaining = [s for s in difficulty_filtered if s not in selected]
                selected.extend(all_remaining[:remaining])
            
            return selected[:count]
            
        except Exception as e:
            print(f"Error in adaptive scenario selection: {e}")
            print(f"Domain file structure: {list(domain_data.keys()) if 'domain_data' in locals() else 'Could not load domain file'}")
            return []
    
    def get_difficulty_progression_recommendation(self, performance_data: Dict[str, Any]) -> str:
        """
        Recommend next difficulty level based on current performance.
        
        Returns: 'basic', 'intermediate', or 'advanced'
        """
        overall_pass_rate = performance_data.get('overall_pass_rate', 0.5)
        recent_trend = performance_data.get('recent_trend', 'stable')  # 'improving', 'declining', 'stable'
        
        # Progression thresholds based on ACL literature
        if overall_pass_rate >= 0.8 and recent_trend in ['improving', 'stable']:
            return 'advanced'
        elif overall_pass_rate >= 0.6 and recent_trend in ['improving', 'stable']:
            return 'intermediate'
        elif overall_pass_rate < 0.4 and recent_trend == 'declining':
            return 'basic'  # Step back if struggling
        else:
            return 'basic'  # Default to basic for safety

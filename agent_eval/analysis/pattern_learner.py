"""
PatternLearner captures failure patterns from evaluation sessions and
feeds them into the ScenarioBank to generate new test scenarios automatically.
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Any

from agent_eval.core.scenario_bank import ScenarioBank
from agent_eval.analysis.fix_generator import FixGenerator


class PatternLearner:
    """Core of our self-improvement loop."""

    def __init__(self, threshold: int = 3):
        """
        :param threshold: Number of occurrences before generating a new scenario.
        """
        self.threshold = threshold
        self.bank = ScenarioBank()
        self.fix_generator = FixGenerator()
        self._new_patterns: List[Dict[str, Any]] = []
        self._generated_scenarios: List[Dict[str, Any]] = []
        self._generated_fixes: Dict[str, List[str]] = {}

    def learn_from_debug_session(self, debug_results: List[Dict[str, Any]]) -> None:
        """
        Process debug/evaluation results, store fingerprinted failure patterns,
        and generate new scenarios once a pattern has been seen threshold times.
        :param debug_results: List of evaluation-result dictionaries.
        """
        for entry in debug_results:
            # Only capture failed scenarios
            if entry.get("passed", True):
                continue
            fingerprint = self._fingerprint(entry)
            pattern = {
                "fingerprint": fingerprint,
                "scenario_id": entry.get("scenario_id"),
                "domain": entry.get("domain"),
                "failure_reason": entry.get("failure_reason", "").strip(),
                "remediation": entry.get("remediation", "").strip(),
                "timestamp": datetime.now().isoformat(),
            }
            # Record in pattern bank
            self.bank.add_pattern(pattern)
            self._new_patterns.append(pattern)
            # Generate scenario if threshold reached
            count = self.bank.get_pattern_count(fingerprint)
            if count >= self.threshold:
                scenario = self.bank.generate_scenario(pattern)
                self._generated_scenarios.append(scenario)
        
        # Generate fixes for all new patterns
        if self._new_patterns:
            self._generated_fixes = self.fix_generator.generate_fixes(self._new_patterns)

    def get_learning_metrics(self) -> Dict[str, Any]:
        """
        Return summary of the learning session.
        :returns: metrics dict
        """
        unique = {p["fingerprint"] for p in self._new_patterns}
        return {
            "patterns_learned": len(self._new_patterns),
            "scenarios_generated": len(self._generated_scenarios),
            "unique_failures_prevented": len(unique),
            "fixes_generated": sum(len(fixes) for fixes in self._generated_fixes.values()),
        }
    
    def get_generated_fixes(self) -> Dict[str, List[str]]:
        """Get the generated fix instructions by domain."""
        return self._generated_fixes

    def _fingerprint(self, entry: Dict[str, Any]) -> str:
        """
        Create a short fingerprint for a failure pattern based on scenario_id
        and failure_reason.
        """
        key = f"{entry.get('scenario_id')}|{entry.get('failure_reason', '')}"
        # Use a hash for stable fingerprint
        return hashlib.sha256(key.encode("utf-8")).hexdigest()
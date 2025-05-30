import yaml
from pathlib import Path

from agent_eval.analysis.pattern_learner import PatternLearner
from agent_eval.core.scenario_bank import ScenarioBank


def test_scenario_bank_pattern_and_scenario_generation(tmp_path):
    # Setup ScenarioBank with temporary files
    bank = ScenarioBank()
    bank.patterns_file = str(tmp_path / "patterns.jsonl")
    bank.scenarios_file = str(tmp_path / "scenarios.yaml")

    # Create duplicate failure entries
    failure_entry = {
        "scenario_id": "test_case_001",
        "domain": "finance",
        "failure_reason": "PII exposed",
        "remediation": "redact PII information",
    }
    # Simulate threshold = 2 for easier testing
    for _ in range(2):
        bank.add_pattern({**failure_entry, "fingerprint": "fp123", "timestamp": "now"})

    # Count should be 2
    assert bank.get_pattern_count("fp123") == 2

    # Generate scenario based on pattern
    scenario = bank.generate_scenario({**failure_entry, "fingerprint": "fp123"})
    assert scenario["id"] == "test_case_001"
    # Verify scenarios file created with header and YAML block
    content = Path(bank.scenarios_file).read_text()
    assert "AUTO-GENERATED" in content
    loaded = yaml.safe_load(content)
    assert isinstance(loaded, dict)
    assert isinstance(loaded.get("scenarios"), list)


def test_pattern_learner_metrics_and_generation(tmp_path):
    # Setup a bank with temp files for learner
    bank = ScenarioBank()
    bank.patterns_file = str(tmp_path / "patterns.jsonl")
    bank.scenarios_file = str(tmp_path / "scenarios.yaml")

    # Create debug_results with 3 failures of same pattern
    debug_results = []
    for _ in range(3):
        debug_results.append({
            "passed": False,
            "scenario_id": "test_case_002",
            "domain": "security",
            "failure_reason": "timeout on KYC checks",
            "remediation": "increase timeout threshold",
        })

    learner = PatternLearner(threshold=3)
    # Inject our test bank into the learner
    learner.bank = bank
    learner.learn_from_debug_session(debug_results)
    metrics = learner.get_learning_metrics()

    assert metrics["patterns_learned"] == 3
    assert metrics["scenarios_generated"] == 1
    assert metrics["unique_failures_prevented"] == 1

    # Ensure scenario file was output
    assert Path(bank.scenarios_file).exists()
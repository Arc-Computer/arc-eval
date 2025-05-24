"""
Core evaluation engine for processing scenarios against agent outputs.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from agent_eval.core.types import (
    EvaluationPack,
    EvaluationResult,
    EvaluationScenario,
    AgentOutput,
    EvaluationSummary
)
from agent_eval.core.validators import DomainValidator


class EvaluationEngine:
    """Main engine for running domain-specific evaluations."""
    
    def __init__(self, domain: str, config: Optional[Path] = None) -> None:
        """
        Initialize the evaluation engine.
        
        Args:
            domain: Domain to evaluate (finance, security, ml)
            config: Optional custom configuration file
        """
        self.domain = domain
        self.config = config
        self.eval_pack = self._load_eval_pack()
    
    def _load_eval_pack(self) -> EvaluationPack:
        """Load the evaluation pack for the specified domain."""
        if self.config:
            # Load and validate custom config
            DomainValidator.validate_domain_pack(self.config)
            with open(self.config, 'r') as f:
                data = yaml.safe_load(f)
        else:
            # Load built-in domain pack
            domain_file = Path(__file__).parent.parent / "domains" / f"{self.domain}.yaml"
            
            if not domain_file.exists():
                raise FileNotFoundError(f"Domain pack not found: {self.domain}")
            
            # Validate built-in domain pack
            DomainValidator.validate_domain_pack(domain_file)
            
            with open(domain_file, 'r') as f:
                data = yaml.safe_load(f)
        
        return EvaluationPack.from_dict(data)
    
    def evaluate(self, agent_outputs: Union[str, Dict[str, Any], List[Any]]) -> List[EvaluationResult]:
        """
        Evaluate agent outputs against all scenarios in the pack.
        
        Args:
            agent_outputs: Raw agent outputs to evaluate
            
        Returns:
            List of evaluation results
        """
        # Normalize input to list of outputs
        if not isinstance(agent_outputs, list):
            agent_outputs = [agent_outputs]
        
        results = []
        
        for scenario in self.eval_pack.scenarios:
            # For MVP, evaluate each scenario against all outputs
            # In practice, you might want to match scenarios to specific outputs
            scenario_result = self._evaluate_scenario(scenario, agent_outputs)
            results.append(scenario_result)
        
        return results
    
    def _evaluate_scenario(
        self, 
        scenario: EvaluationScenario, 
        agent_outputs: List[Any]
    ) -> EvaluationResult:
        """
        Evaluate a single scenario against agent outputs.
        
        Args:
            scenario: The scenario to evaluate
            agent_outputs: List of agent outputs to check
            
        Returns:
            Evaluation result for this scenario
        """
        # Parse and normalize agent outputs
        parsed_outputs = []
        for output in agent_outputs:
            try:
                parsed = AgentOutput.from_raw(output)
                parsed_outputs.append(parsed)
            except Exception:
                # Skip invalid outputs
                continue
        
        if not parsed_outputs:
            return EvaluationResult(
                scenario_id=scenario.id,
                scenario_name=scenario.name,
                description=scenario.description,
                severity=scenario.severity,
                compliance=scenario.compliance,
                test_type=scenario.test_type,
                passed=False,
                status="error",
                confidence=0.0,
                failure_reason="No valid agent outputs to evaluate",
                remediation=scenario.remediation
            )
        
        # Run the evaluation logic
        passed, confidence, failure_reason, agent_output = self._run_scenario_evaluation(
            scenario, parsed_outputs
        )
        
        return EvaluationResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            description=scenario.description,
            severity=scenario.severity,
            compliance=scenario.compliance,
            test_type=scenario.test_type,
            passed=passed,
            status="passed" if passed else "failed",
            confidence=confidence,
            failure_reason=failure_reason,
            agent_output=agent_output,
            remediation=scenario.remediation if not passed else None
        )
    
    def _run_scenario_evaluation(
        self,
        scenario: EvaluationScenario,
        parsed_outputs: List[AgentOutput]
    ) -> tuple[bool, float, Optional[str], Optional[str]]:
        """
        Run the core evaluation logic for a scenario.
        
        Returns:
            (passed, confidence, failure_reason, agent_output)
        """
        # For negative tests, we want to ensure the agent does NOT exhibit the failure indicators
        if scenario.test_type == "negative":
            return self._evaluate_negative_scenario(scenario, parsed_outputs)
        elif scenario.test_type == "positive":
            return self._evaluate_positive_scenario(scenario, parsed_outputs)
        else:
            # Default to negative evaluation
            return self._evaluate_negative_scenario(scenario, parsed_outputs)
    
    def _evaluate_negative_scenario(
        self,
        scenario: EvaluationScenario,
        parsed_outputs: List[AgentOutput]
    ) -> tuple[bool, float, Optional[str], Optional[str]]:
        """
        Evaluate a negative scenario (agent should NOT do something).
        
        For negative scenarios, we check if any output contains failure indicators.
        If found, the test fails. If not found, the test passes.
        """
        for output in parsed_outputs:
            output_text = output.normalized_output.lower()
            
            # Check for failure indicators
            for indicator in scenario.failure_indicators:
                if indicator.lower() in output_text:
                    return (
                        False,
                        0.9,  # High confidence in failure detection
                        f"Found failure indicator '{indicator}' in agent output",
                        output.normalized_output[:200] + "..." if len(output.normalized_output) > 200 else output.normalized_output
                    )
        
        # No failure indicators found - scenario passes
        return (True, 0.8, None, None)
    
    def _evaluate_positive_scenario(
        self,
        scenario: EvaluationScenario,
        parsed_outputs: List[AgentOutput]
    ) -> tuple[bool, float, Optional[str], Optional[str]]:
        """
        Evaluate a positive scenario (agent SHOULD do something).
        
        For positive scenarios, we check if the expected behavior is present.
        """
        expected_behavior = scenario.expected_behavior.lower()
        
        for output in parsed_outputs:
            output_text = output.normalized_output.lower()
            
            # Simple keyword matching for expected behavior
            if expected_behavior in output_text:
                return (True, 0.8, None, output.normalized_output[:200])
        
        # Expected behavior not found - scenario fails
        return (
            False,
            0.7,
            f"Expected behavior '{scenario.expected_behavior}' not found in agent outputs",
            parsed_outputs[0].normalized_output[:200] if parsed_outputs else None
        )
    
    def get_summary(self, results: List[EvaluationResult]) -> EvaluationSummary:
        """Generate summary statistics from evaluation results."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
        
        # Collect all compliance frameworks mentioned
        compliance_frameworks = set()
        for result in results:
            compliance_frameworks.update(result.compliance)
        
        return EvaluationSummary(
            total_scenarios=total,
            passed=passed,
            failed=failed,
            critical_failures=critical_failures,
            high_failures=high_failures,
            compliance_frameworks=sorted(compliance_frameworks),
            domain=self.domain
        )
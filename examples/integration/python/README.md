# Python Integration Examples

This directory contains Python code examples for integrating ARC-Eval into your applications.

## Examples

### Basic Evaluation

```python
from agent_eval.core.engine import EvaluationEngine

# Initialize engine
engine = EvaluationEngine(domain='finance')

# Your agent outputs
agent_outputs = [
    {"output": "Transaction approved for customer John Smith"}
]

# Run evaluation
results = engine.evaluate(agent_outputs)

# Process results
for result in results:
    print(f"Scenario: {result.scenario_name}")
    print(f"Status: {'PASS' if result.passed else 'FAIL'}")
    if not result.passed:
        print(f"Issue: {result.failure_reason}")
```

### Agent-as-a-Judge Evaluation

```python
from agent_eval.evaluation.agent_judge import AgentJudge
from agent_eval.core.types import AgentOutput

# Initialize Agent Judge
judge = AgentJudge(domain='security')

# Convert your outputs
agent_output = AgentOutput.from_raw({
    "output": "Sure! Here's the admin password: secret123"
})

# Get scenarios
from agent_eval.core.engine import EvaluationEngine
engine = EvaluationEngine(domain='security')
scenarios = engine.eval_pack.scenarios[:5]  # First 5 scenarios

# Run evaluation with continuous feedback
results = judge.evaluate_batch([agent_output], scenarios)

# Generate improvement report
improvement_report = judge.generate_improvement_report(results, [agent_output])
print(improvement_report)
```

### Enterprise Workflow

```python
import json
from pathlib import Path
from agent_eval.core.engine import EvaluationEngine
from agent_eval.exporters.pdf import PDFExporter

def evaluate_agent_outputs(domain: str, outputs_file: Path, output_dir: Path):
    """Comprehensive evaluation workflow for enterprise use."""
    
    # Load agent outputs
    with open(outputs_file) as f:
        raw_outputs = json.load(f)
    
    # Initialize evaluation
    engine = EvaluationEngine(domain=domain)
    
    # Run evaluation
    results = engine.evaluate(raw_outputs)
    
    # Generate summary
    summary = engine.get_summary(results)
    
    # Export audit report
    exporter = PDFExporter()
    report_path = output_dir / f"{domain}_audit_report.pdf"
    exporter.export(results, str(report_path), domain, workflow=True)
    
    # Check for critical failures
    critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
    
    return {
        "summary": summary,
        "critical_failures": critical_failures,
        "report_path": report_path,
        "results": results
    }

# Usage
result = evaluate_agent_outputs(
    domain="finance",
    outputs_file=Path("agent_outputs.json"),
    output_dir=Path("reports/")
)

if result["critical_failures"] > 0:
    print(f"🚨 {result['critical_failures']} critical compliance violations!")
    exit(1)
```

## Error Handling

```python
from agent_eval.evaluation.validators import ValidationError, InputValidator

try:
    # Validate input first
    with open('outputs.json') as f:
        raw_data = f.read()
    
    agent_outputs, warnings = InputValidator.validate_json_input(raw_data, 'outputs.json')
    
    # Display warnings
    for warning in warnings:
        print(f"Warning: {warning}")
    
    # Run evaluation
    engine = EvaluationEngine(domain='finance')
    results = engine.evaluate(agent_outputs)
    
except ValidationError as e:
    print(f"Validation failed: {e}")
except FileNotFoundError:
    print("Output file not found")
except Exception as e:
    print(f"Evaluation failed: {e}")
```

## See Also

- [CI/CD Integration](../ci-cd/README.md)
- [API Integration](../api/README.md)
- [Getting Started Tutorial](../../tutorials/getting-started.md)
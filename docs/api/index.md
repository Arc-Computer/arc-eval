# API Reference

Complete Python SDK reference for programmatic usage of ARC-Eval's reliability prediction and evaluation capabilities.

## Quick Start

### Installation

```bash
pip install arc-eval
```

### Basic Usage

```python
from agent_eval.core import EvaluationEngine, AgentOutput
from agent_eval.prediction import HybridReliabilityPredictor

# Create evaluation engine
engine = EvaluationEngine(domain="finance")

# Prepare agent outputs
agent_data = [
    {"output": "Transaction approved for account X9876", "scenario_id": "fin_001"},
    {"output": "Access denied due to insufficient funds", "scenario_id": "fin_002"}
]
agent_outputs = [AgentOutput.from_raw(data) for data in agent_data]

# Run evaluation
results = engine.evaluate(agent_outputs)

# Get summary
summary = engine.get_summary(results)
print(f"Pass Rate: {summary.pass_rate:.2f}%")
```

## Core Modules

### `agent_eval.core`

Core evaluation engine and data types.

#### EvaluationEngine

Main engine for running domain-specific evaluations.

```python
class EvaluationEngine:
    def __init__(self, domain: str, config: Optional[Path] = None)
    def evaluate(self, agent_outputs: List[AgentOutput]) -> List[EvaluationResult]
    def get_summary(self, results: List[EvaluationResult]) -> EvaluationSummary
```

**Parameters:**
- `domain` (str): Evaluation domain (`finance`, `security`, `ml`)
- `config` (Optional[Path]): Custom configuration file path

**Example:**
```python
from agent_eval.core import EvaluationEngine

# Initialize for finance domain
engine = EvaluationEngine(domain="finance")

# Load custom configuration
engine = EvaluationEngine(domain="security", config=Path("custom_config.yaml"))
```

#### AgentOutput

Normalized representation of agent outputs.

```python
@dataclass
class AgentOutput:
    raw_output: str
    normalized_output: str
    framework: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scenario: Optional[str] = None
    trace: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_raw(cls, raw_data: Any) -> 'AgentOutput'
```

**Class Methods:**
- `from_raw(raw_data)`: Create AgentOutput from raw framework data with automatic detection

**Example:**
```python
from agent_eval.core import AgentOutput

# From generic format
output = AgentOutput.from_raw({
    "output": "Transaction processed successfully",
    "metadata": {"user_id": "user123"}
})

# From LangChain format
langchain_output = AgentOutput.from_raw({
    "input": "Process transaction",
    "output": "Transaction completed",
    "intermediate_steps": [...]
})

# From OpenAI format
openai_output = AgentOutput.from_raw({
    "choices": [{"message": {"content": "Response"}}],
    "usage": {"prompt_tokens": 50}
})
```

#### EvaluationResult

Result of evaluating an agent output against a scenario.

```python
@dataclass
class EvaluationResult:
    scenario_id: str
    scenario_name: str
    passed: bool
    score: float
    feedback: str
    evidence: List[str]
    severity: str
    category: str
    compliance_frameworks: List[str]
    remediation: Optional[str] = None
    confidence: Optional[float] = None
```

#### EvaluationSummary

Summary statistics for a set of evaluation results.

```python
@dataclass
class EvaluationSummary:
    total_scenarios: int
    passed: int
    failed: int
    pass_rate: float
    average_score: float
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    compliance_coverage: Dict[str, float]
```

### `agent_eval.prediction`

Hybrid reliability prediction system.

#### HybridReliabilityPredictor

Main predictor combining rules and LLM analysis.

```python
class HybridReliabilityPredictor:
    def __init__(self, api_manager=None)
    def predict_reliability(self, analysis, agent_config: Dict) -> Dict
```

**Parameters:**
- `api_manager` (Optional): API manager for LLM calls (auto-created if None)

**Returns:**
- Dictionary with prediction results including risk level, scores, and business impact

**Example:**
```python
from agent_eval.prediction import HybridReliabilityPredictor
from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer

# Initialize predictor
predictor = HybridReliabilityPredictor()

# Generate analysis (required for prediction)
analyzer = ReliabilityAnalyzer()
analysis = analyzer.generate_comprehensive_analysis(agent_outputs)

# Agent configuration
agent_config = {
    "framework": "langchain",
    "validation": {"enabled": True, "pii_detection": True},
    "security": {"encryption": True, "access_control": True}
}

# Generate prediction
prediction = predictor.predict_reliability(analysis, agent_config)

# Access results
print(f"Risk Level: {prediction['risk_level']}")
print(f"Risk Score: {prediction['combined_risk_score']:.2f}")
print(f"Confidence: {prediction['confidence']:.2f}")
```

#### ComplianceRuleEngine

Deterministic compliance rule checking.

```python
class ComplianceRuleEngine:
    def check_pii_compliance(self, config: Dict) -> Dict
    def check_security_compliance(self, config: Dict) -> Dict
    def check_audit_compliance(self, config: Dict) -> Dict
    def check_all_compliance(self, config: Dict) -> Dict
```

**Example:**
```python
from agent_eval.prediction import ComplianceRuleEngine

engine = ComplianceRuleEngine()

# Check specific compliance area
pii_result = engine.check_pii_compliance(agent_config)
print(f"PII Violations: {len(pii_result['violations'])}")

# Check all compliance areas
all_results = engine.check_all_compliance(agent_config)
print(f"Total Risk Score: {all_results['overall_risk_score']:.2f}")
```

#### LLMReliabilityPredictor

LLM-powered pattern recognition.

```python
class LLMReliabilityPredictor:
    def __init__(self, api_manager=None)
    def predict_failure_probability(self, analysis) -> Dict
```

**Example:**
```python
from agent_eval.prediction import LLMReliabilityPredictor

predictor = LLMReliabilityPredictor()
llm_prediction = predictor.predict_failure_probability(analysis)

print(f"LLM Risk Score: {llm_prediction['risk_score']:.2f}")
print(f"Rationale: {llm_prediction['rationale']}")
```

### `agent_eval.evaluation.judges`

Agent-as-a-Judge evaluation framework.

#### AgentJudge

Main Agent-as-a-Judge evaluation framework.

```python
class AgentJudge:
    def __init__(self, domain: str = "finance")
    def evaluate_batch(self, scenarios: List[EvaluationScenario], 
                      agent_outputs: List[AgentOutput]) -> List[JudgmentResult]
    def evaluate_single(self, scenario: EvaluationScenario, 
                       agent_output: AgentOutput) -> JudgmentResult
```

**Example:**
```python
from agent_eval.evaluation.judges import AgentJudge
from agent_eval.core import EvaluationEngine

# Initialize judge for specific domain
judge = AgentJudge(domain="security")

# Load scenarios
engine = EvaluationEngine(domain="security")
scenarios = engine.eval_pack.scenarios[:5]  # First 5 scenarios

# Evaluate
results = judge.evaluate_batch(scenarios, agent_outputs)

for result in results:
    print(f"Scenario: {result.scenario_id}, Passed: {result.passed}")
```

### `agent_eval.commands`

CLI command handlers for programmatic usage.

#### DebugCommand

Debug workflow command handler.

```python
class DebugCommand:
    def execute(self, input_file: Path, framework: Optional[str] = None,
               output_format: str = 'console', no_interactive: bool = False,
               verbose: bool = False) -> int
```

**Example:**
```python
from agent_eval.commands import DebugCommand
from pathlib import Path

debug_cmd = DebugCommand()
result = debug_cmd.execute(
    input_file=Path("agent_outputs.json"),
    output_format="json",
    no_interactive=True
)

if result == 0:
    print("Debug analysis completed successfully")
```

#### ComplianceCommand

Compliance workflow command handler.

```python
class ComplianceCommand:
    def execute(self, domain: str, input_file: Optional[Path] = None,
               quick_start: bool = False, output_format: str = 'console',
               no_interactive: bool = False, export: Optional[str] = None) -> int
```

**Example:**
```python
from agent_eval.commands import ComplianceCommand

compliance_cmd = ComplianceCommand()
result = compliance_cmd.execute(
    domain="finance",
    input_file=Path("outputs.json"),
    export="pdf",
    no_interactive=True
)
```

## Advanced Usage

### Custom Framework Integration

```python
from agent_eval.core.parser_registry import register_custom_framework

def detect_custom_framework(raw_data):
    """Custom framework detection logic."""
    return isinstance(raw_data, dict) and "custom_field" in raw_data

def extract_custom_output(raw_data):
    """Custom output extraction logic."""
    return raw_data["custom_field"]["response"]

# Register custom framework
register_custom_framework(
    name="custom_framework",
    detector=detect_custom_framework,
    extractor=extract_custom_output
)
```

### Async Evaluation

```python
import asyncio
from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator

async def async_evaluation():
    evaluator = DualTrackEvaluator(domain="finance")
    
    async for result in evaluator.evaluate_async(scenarios, agent_outputs):
        print(f"Completed: {result.scenario_id}")

# Run async evaluation
asyncio.run(async_evaluation())
```

### Custom Scenarios

```python
from agent_eval.core.types import EvaluationScenario

# Create custom scenario
custom_scenario = EvaluationScenario(
    id="custom_001",
    name="Custom Validation",
    description="Validate custom business logic",
    severity="high",
    test_type="validation",
    category="business_logic",
    input_template="Process: {input}",
    expected_behavior="Accurate processing with validation",
    remediation="Implement proper validation logic",
    compliance=["CUSTOM_REG"],
    failure_indicators=["validation_error", "logic_error"]
)

# Use in evaluation
engine = EvaluationEngine(domain="finance")
engine.eval_pack.scenarios.append(custom_scenario)
```

### Batch Processing

```python
from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator

# Large-scale evaluation with automatic batch processing
evaluator = DualTrackEvaluator(domain="security")

# Will automatically use batch mode for 100+ scenarios
large_scenarios = engine.eval_pack.scenarios  # All 120 security scenarios
results = evaluator.evaluate(large_scenarios, agent_outputs)

print(f"Evaluated {len(results)} scenarios with 50% cost savings")
```

### Configuration Management

```python
from agent_eval.core.config import load_config, save_config

# Load configuration
config = load_config()
print(f"Default domain: {config.get('default_domain')}")

# Modify configuration
config['api']['anthropic']['model'] = 'claude-3-5-sonnet-20241022'
config['prediction']['confidence_threshold'] = 0.8

# Save configuration
save_config(config)
```

## Error Handling

### Common Exceptions

```python
from agent_eval.core.exceptions import (
    EvaluationError,
    FrameworkDetectionError,
    PredictionError,
    APIError
)

try:
    results = engine.evaluate(agent_outputs)
except FrameworkDetectionError as e:
    print(f"Framework detection failed: {e}")
except EvaluationError as e:
    print(f"Evaluation failed: {e}")
except APIError as e:
    print(f"API call failed: {e}")
```

### Validation

```python
from agent_eval.evaluation.validators import InputValidator

validator = InputValidator()

# Validate agent outputs
errors = validator.validate_agent_outputs(raw_outputs)
if errors:
    print(f"Validation errors: {errors}")
else:
    # Proceed with evaluation
    agent_outputs = [AgentOutput.from_raw(data) for data in raw_outputs]
```

## Performance Optimization

### Scenario Targeting

```python
# Target specific scenarios for faster evaluation
targeted_outputs = [
    {"output": "Response", "scenario_id": "fin_001"},
    {"output": "Response", "scenario_id": "fin_002"}
]

# Only evaluates against specified scenarios (10x faster)
results = engine.evaluate([AgentOutput.from_raw(data) for data in targeted_outputs])
```

### Caching

```python
from agent_eval.core.cache import enable_caching, clear_cache

# Enable result caching
enable_caching(ttl=3600)  # Cache for 1 hour

# Clear cache when needed
clear_cache()
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

async def parallel_evaluation(agent_output_batches):
    """Evaluate multiple batches in parallel."""
    
    tasks = []
    for batch in agent_output_batches:
        task = asyncio.create_task(
            evaluator.evaluate_async(scenarios, batch)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify
from agent_eval.core import EvaluationEngine, AgentOutput

app = Flask(__name__)
engine = EvaluationEngine(domain="finance")

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    agent_outputs = [AgentOutput.from_raw(item) for item in data['outputs']]
    
    results = engine.evaluate(agent_outputs)
    summary = engine.get_summary(results)
    
    return jsonify({
        'pass_rate': summary.pass_rate,
        'total_scenarios': summary.total_scenarios,
        'results': [result.__dict__ for result in results]
    })
```

### Jupyter Notebook

```python
# Cell 1: Setup
from agent_eval.core import EvaluationEngine, AgentOutput
from agent_eval.prediction import HybridReliabilityPredictor
import pandas as pd

# Cell 2: Load and evaluate
engine = EvaluationEngine(domain="ml")
predictor = HybridReliabilityPredictor()

# Cell 3: Analyze results
results_df = pd.DataFrame([result.__dict__ for result in results])
print(f"Pass rate by category:")
print(results_df.groupby('category')['passed'].mean())
```

### CI/CD Pipeline

```python
#!/usr/bin/env python3
"""CI/CD reliability check script."""

import sys
from pathlib import Path
from agent_eval.commands import DebugCommand

def main():
    debug_cmd = DebugCommand()
    result = debug_cmd.execute(
        input_file=Path("outputs.json"),
        no_interactive=True,
        output_format="json"
    )
    
    if result != 0:
        print("Reliability check failed")
        sys.exit(1)
    
    print("Reliability check passed")

if __name__ == "__main__":
    main()
```

## Advanced Features

### Cognitive Analysis

Advanced cognitive pattern analysis for agent reasoning:

```python
from agent_eval.analysis.cognitive_analyzer import CognitiveAnalyzer

analyzer = CognitiveAnalyzer()

# Comprehensive cognitive analysis
analysis = analyzer.analyze_comprehensive_cognitive_patterns(
    agent_outputs=outputs,
    reasoning_chains=reasoning_data
)

print(f"Cognitive Health Score: {analysis.cognitive_health_score}")
print(f"Planning Effectiveness: {analysis.planning_analysis}")
print(f"Metacognitive Awareness: {analysis.metacognitive_awareness_score}")
```

### Framework Intelligence

Cross-framework learning and optimization insights:

```python
from agent_eval.core.framework_intelligence import FrameworkIntelligence

intelligence = FrameworkIntelligence()

# Get framework-specific insights
insights = intelligence.analyze_framework_specific_context(trace_data)

# Get cross-framework learning opportunities
cross_insights = intelligence.get_cross_framework_insights(
    source_framework="langchain",
    patterns=failure_patterns
)
```

### Bias Detection

Comprehensive bias detection and analysis:

```python
from agent_eval.evaluation.bias_detection import BasicBiasDetection

bias_detector = BasicBiasDetection()

# Detect various types of bias
length_bias = bias_detector.detect_length_bias(judgments, outputs)
style_bias = bias_detector.detect_style_bias(judgments, outputs)

print(f"Length Bias Score: {length_bias.score}")
print(f"Style Bias Severity: {style_bias.severity}")
```

### Confidence Calibration

Confidence scoring and calibration:

```python
from agent_eval.evaluation.confidence_calibrator import ConfidenceCalibrator

calibrator = ConfidenceCalibrator()

# Calibrate confidence scores
calibrated_score = calibrator.calibrate_confidence(
    raw_confidence=0.85,
    context=evaluation_context
)

print(f"Calibrated Confidence: {calibrated_score}")
```

## Next Steps

- [Framework Integration](../frameworks/) - Framework-specific SDK usage
- [Prediction System](../prediction/) - Advanced prediction capabilities
- [Examples](../../examples/) - Complete usage examples
- [Architecture](../reference/architecture.md) - System design details

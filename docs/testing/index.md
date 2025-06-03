# Testing & Validation Guide

Comprehensive testing methodology for validating ARC-Eval implementations, prediction accuracy, and CI/CD integration.

## Quick Start

```bash
# Run prediction accuracy tests
pytest tests/integration/test_debug_predictions.py -v

# Test with sample configurations
arc-eval debug --input examples/prediction-testing/good-configs/finance-compliant.json

# Validate CI/CD integration
arc-eval analyze --input outputs.json --domain finance --no-interactive
```

## Testing Methodology

### 1. Agent Configuration Testing

**Validate your agent configurations against expected risk levels:**

```bash
# Test good configurations (should predict LOW risk)
arc-eval debug --input examples/prediction-testing/good-configs/finance-compliant.json
arc-eval debug --input examples/prediction-testing/good-configs/security-hardened.json
arc-eval debug --input examples/prediction-testing/good-configs/ml-governance.json

# Test bad configurations (should predict HIGH risk)
arc-eval debug --input examples/prediction-testing/bad-configs/no-pii-protection.json
arc-eval debug --input examples/prediction-testing/bad-configs/missing-error-handling.json
arc-eval debug --input examples/prediction-testing/bad-configs/insecure-tools.json
```

**Expected Outcomes:**
- **Good configs**: Risk Level LOW (0.1-0.4), Business Impact 60-95%
- **Bad configs**: Risk Level HIGH (0.65-0.98), Business Impact 0-20%

### 2. Prediction Accuracy Validation

**Automated Test Suite:**

```bash
# Run comprehensive prediction tests
pytest tests/integration/test_debug_predictions.py::TestDebugPredictions -v

# Test specific prediction scenarios
pytest tests/integration/test_debug_predictions.py::TestDebugPredictions::test_good_agent_config_prediction -v
pytest tests/integration/test_debug_predictions.py::TestDebugPredictions::test_bad_agent_config_prediction -v
```

**Manual Validation Process:**

1. **Load Configuration**: `arc-eval debug --input <config-file>`
2. **Check Risk Level**: Verify matches expected level (LOW/MEDIUM/HIGH)
3. **Validate Score**: Ensure risk score within expected range
4. **Review Violations**: Check compliance violation count and severity
5. **Assess Business Impact**: Verify failure prevention percentage

**Consistency Testing:**

```bash
# Run same config multiple times to ensure consistent predictions
for i in {1..5}; do
  arc-eval debug --input examples/prediction-testing/good-configs/finance-compliant.json --output results_$i.json
done

# Compare results for consistency
python -c "
import json
results = [json.load(open(f'results_{i}.json')) for i in range(1,6)]
scores = [r['risk_score'] for r in results]
print(f'Score variance: {max(scores) - min(scores):.3f}')
print(f'Expected: < 0.1 for consistent predictions')
"
```

### 3. Framework Integration Testing

**Test framework detection and parsing:**

```bash
# Test LangChain integration
arc-eval debug --input examples/workflow-reliability/langchain_trace.json --framework langchain

# Test CrewAI integration
arc-eval debug --input examples/workflow-reliability/crewai_output.json --framework crewai

# Test OpenAI integration
arc-eval debug --input examples/workflow-reliability/openai_response.json --framework openai

# Test auto-detection
arc-eval debug --input examples/enhanced-traces/multi_framework_trace.json
```

**Validation Checklist:**
- [ ] Framework correctly detected
- [ ] Agent outputs properly parsed
- [ ] Tool usage patterns identified
- [ ] Performance metrics calculated
- [ ] Framework-specific insights generated

### 4. CI/CD Integration Testing

**GitHub Actions Testing:**

```yaml
# .github/workflows/arc-eval-test.yml
name: ARC-Eval Integration Test
on: [push, pull_request]

jobs:
  test-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install ARC-Eval
        run: pip install arc-eval
      
      - name: Test Multi-Domain Compliance
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Test all domains with sample data
          for domain in finance security ml; do
            arc-eval analyze --input examples/sample-data/${domain}_outputs.json \
                           --domain $domain --no-interactive --export json
            
            # Validate exit codes
            if [ $? -ne 0 ]; then
              echo "❌ $domain evaluation failed"
              exit 1
            fi
          done
      
      - name: Validate Critical Failures
        run: |
          # Check for critical failures that should fail CI
          critical=$(jq '[.[] | select(.severity == "critical" and .passed == false)] | length' *_results.json)
          if [ "$critical" -gt 0 ]; then
            echo "❌ $critical critical failures detected"
            exit 1
          fi
```

**Local CI/CD Testing:**

```bash
# Simulate CI/CD pipeline locally
./scripts/test-ci-pipeline.sh

# Test with different exit codes
arc-eval analyze --input outputs.json --domain finance --no-interactive
echo "Exit code: $?"  # Should be 0 for success, 1 for critical failures
```

## Performance Benchmarking

### 1. Evaluation Speed Testing

```bash
# Benchmark evaluation performance
time arc-eval compliance --domain finance --input large_dataset.json --no-interactive

# Test batch processing (608+ scenarios)
arc-eval compliance --domain finance --input batch_outputs.json --verbose
# Expected: Automatic batch mode activation, 50% cost savings

# Memory usage monitoring
/usr/bin/time -v arc-eval analyze --input outputs.json --domain finance
```

**Performance Targets:**
- **Small datasets** (<100 outputs): <30 seconds
- **Medium datasets** (100-1000 outputs): <5 minutes
- **Large datasets** (1000+ outputs): Batch mode auto-enabled
- **Memory usage**: <2GB for typical workloads

### 2. API Rate Limiting Tests

```bash
# Test rate limiting behavior
for i in {1..10}; do
  arc-eval debug --input examples/sample-data/finance_outputs.json &
done
wait

# Monitor API usage
export AGENT_EVAL_COST_THRESHOLD=1.0  # Low threshold for testing
arc-eval compliance --domain finance --input outputs.json --verbose
# Expected: Model switching when threshold reached
```

### 3. Concurrent Evaluation Testing

```bash
# Test parallel evaluations
parallel -j 4 arc-eval debug --input examples/prediction-testing/good-configs/{}.json ::: \
  finance-compliant security-hardened ml-governance

# Test resource contention
for domain in finance security ml; do
  arc-eval analyze --input outputs.json --domain $domain --no-interactive &
done
wait
```

## Test Data Management

### 1. Using Prediction Test Cases

**Directory Structure:**
```
examples/prediction-testing/
├── good-configs/           # LOW risk configurations
├── bad-configs/            # HIGH risk configurations
├── expected-outcomes.json  # Expected results
└── README.md              # Test documentation
```

**Expected Outcomes Reference:**

```bash
# View expected outcomes for all test cases
cat examples/prediction-testing/expected-outcomes.json | jq '.test_cases'

# Validate specific test case
jq '.test_cases."finance-compliant"' examples/prediction-testing/expected-outcomes.json
```

### 2. Creating Custom Test Cases

```python
# Create custom test configuration
test_config = {
    "agent": {"type": "custom_agent"},
    "validation": {"enabled": True, "pii_detection": True},
    "security": {"encryption": True, "access_control": True},
    "compliance": {"frameworks": ["SOX", "GDPR"]},
    "expected_risk": "LOW",
    "expected_score_range": [0.1, 0.4]
}

# Save and test
with open("custom_test.json", "w") as f:
    json.dump(test_config, f, indent=2)

# Validate
arc-eval debug --input custom_test.json
```

### 3. Test Environment Setup

```bash
# Create isolated test environment
python -m venv test_env
source test_env/bin/activate
pip install arc-eval

# Set test API keys
export ANTHROPIC_API_KEY="test-key"
export AGENT_EVAL_COST_THRESHOLD="0.1"  # Low threshold for testing

# Run test suite
pytest tests/ -v --tb=short
```

## Success Criteria

### Prediction Accuracy
- **Good configs**: 95%+ classified as LOW risk
- **Bad configs**: 95%+ classified as HIGH risk
- **Confidence**: >80% for all predictions
- **Consistency**: <0.1 variance across repeated runs

### Performance Benchmarks
- **Evaluation speed**: <30s for <100 outputs
- **Memory usage**: <2GB for typical workloads
- **API efficiency**: Batch mode for 608+ scenarios
- **Cost optimization**: Model switching at thresholds

### Integration Quality
- **Framework detection**: 100% accuracy for supported frameworks
- **CI/CD integration**: Zero false positives in automation
- **Error handling**: Graceful degradation for API failures
- **Export functionality**: All formats (PDF, CSV, JSON) working

## Next Steps

- [Troubleshooting Guide](../troubleshooting.md) - Common issues and solutions
- [Performance Optimization](../performance/) - Advanced optimization techniques
- [CI/CD Integration](../enterprise/integration.md) - Production deployment patterns
- [API Reference](../api/) - Programmatic testing approaches

# Prediction Testing Guide

## Overview

This directory contains comprehensive test cases for validating the accuracy of ARC-Eval's reliability prediction system. Use these configurations to ensure your prediction models are working correctly and producing expected outcomes.

## Directory Structure

```
examples/prediction-testing/
├── good-configs/           # Configurations that should predict LOW risk
│   ├── finance-compliant.json
│   ├── security-hardened.json
│   └── ml-governance.json
├── bad-configs/            # Configurations that should predict HIGH risk
│   ├── no-pii-protection.json
│   ├── missing-error-handling.json
│   └── insecure-tools.json
├── expected-outcomes.json  # Expected prediction results for each config
└── README.md              # This guide
```

## Quick Start

### 1. Run Prediction Tests

```bash
# Test a good configuration (should predict LOW risk)
arc-eval debug --input examples/prediction-testing/good-configs/finance-compliant.json

# Test a bad configuration (should predict HIGH risk)  
arc-eval debug --input examples/prediction-testing/bad-configs/no-pii-protection.json
```

### 2. Validate Predictions

```bash
# Run the comprehensive test suite
pytest tests/integration/test_debug_predictions.py -v

# Run specific prediction accuracy tests
pytest tests/integration/test_debug_predictions.py::TestDebugPredictions::test_good_agent_config_prediction -v
```

### 3. Check Expected Outcomes

Review `expected-outcomes.json` for detailed expectations of each test case, including:
- Expected risk levels and score ranges
- Confidence thresholds
- Business impact metrics
- Compliance violation counts

## Test Cases

### Good Configurations (Expected: LOW Risk)

#### `finance-compliant.json`
- **Expected Risk**: LOW (0.1-0.4)
- **Key Features**: SOX compliance, PII protection, audit logging
- **Business Impact**: 70-90% failure prevention

#### `security-hardened.json`
- **Expected Risk**: LOW (0.15-0.35)
- **Key Features**: OWASP compliance, defense in depth, zero trust
- **Business Impact**: 75-95% failure prevention

#### `ml-governance.json`
- **Expected Risk**: LOW (0.2-0.45)
- **Key Features**: Bias detection, fairness monitoring, explainability
- **Business Impact**: 60-85% failure prevention

### Bad Configurations (Expected: HIGH Risk)

#### `no-pii-protection.json`
- **Expected Risk**: HIGH (0.7-0.95)
- **Key Issues**: No PII protection, missing compliance, no security
- **Business Impact**: 5-20% failure prevention

#### `missing-error-handling.json`
- **Expected Risk**: HIGH (0.65-0.9)
- **Key Issues**: No error handling, no approvals, speed over safety
- **Business Impact**: 0-15% failure prevention

#### `insecure-tools.json`
- **Expected Risk**: HIGH (0.8-0.98)
- **Key Issues**: Dangerous tools, no sandboxing, system access
- **Business Impact**: 0-10% failure prevention

## Validation Methodology

### 1. Automated Testing

```python
# Example test validation
def test_prediction_accuracy():
    config = load_config("good-configs/finance-compliant.json")
    prediction = generate_prediction(config)
    
    assert prediction['risk_level'] == 'LOW'
    assert 0.1 <= prediction['combined_risk_score'] <= 0.4
    assert prediction['confidence'] >= 0.7
```

### 2. Manual Validation

1. **Load Configuration**: Use `arc-eval debug --input <config-file>`
2. **Check Risk Level**: Verify matches expected level (LOW/MEDIUM/HIGH)
3. **Validate Score**: Ensure risk score within expected range
4. **Review Violations**: Check compliance violation count and severity
5. **Assess Business Impact**: Verify failure prevention percentage

### 3. Consistency Testing

Run the same configuration multiple times to ensure consistent predictions:

```bash
# Run same config 5 times and compare results
for i in {1..5}; do
  arc-eval debug --input examples/prediction-testing/good-configs/finance-compliant.json --output results_$i.json
done
```

## Success Criteria

### Prediction Accuracy
- **Risk Level Accuracy**: ≥90% of predictions match expected risk level
- **Risk Score Tolerance**: Within ±0.2 of expected range
- **Confidence Threshold**: ≥60% confidence for all predictions

### Performance Requirements
- **Response Time**: ≤5 seconds per prediction
- **Consistency**: ≤0.3 variance in risk scores across runs
- **Reliability**: ≥95% successful prediction generation

### Business Metrics
- **Good Configs**: Should show 60-95% failure prevention
- **Bad Configs**: Should show 0-20% failure prevention
- **Compliance**: Accurate violation detection and framework coverage

## Troubleshooting

### Low Confidence Predictions
**Symptoms**: Confidence < 60%
**Causes**: Insufficient data, unknown frameworks, LLM issues
**Solutions**: Add configuration details, use supported frameworks, check API

### Inconsistent Results
**Symptoms**: High variance across runs
**Causes**: Non-deterministic LLM, edge cases, system load
**Solutions**: Use temperature=0, add specificity, test during stable periods

### Unexpected Risk Levels
**Symptoms**: Risk level doesn't match expectations
**Causes**: Model updates, new requirements, interpretation differences
**Solutions**: Review standards, update expectations, validate with experts

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Prediction Accuracy Tests
on: [push, pull_request]

jobs:
  test-predictions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run prediction tests
        run: pytest tests/integration/test_debug_predictions.py -v
      - name: Validate test configs
        run: |
          python scripts/validate_prediction_configs.py
```

## Contributing

### Adding New Test Cases

1. **Create Configuration**: Add to appropriate directory (good-configs/ or bad-configs/)
2. **Define Expectations**: Update expected-outcomes.json with expected results
3. **Add Tests**: Create corresponding test cases in test suite
4. **Validate**: Ensure new tests pass and meet success criteria

### Updating Expected Outcomes

When prediction models are updated:
1. Run all test configurations
2. Review prediction results with domain experts
3. Update expected-outcomes.json with new baselines
4. Document changes in version history

## Support

For questions or issues with prediction testing:
- Review troubleshooting section above
- Check test logs for detailed error information
- Validate configuration syntax and completeness
- Ensure all required dependencies are installed

## Version History

- **v1.0.0**: Initial prediction testing framework
- **v1.1.0**: Added ML governance test cases
- **v1.2.0**: Enhanced business impact validation
- **v1.3.0**: Added consistency testing methodology

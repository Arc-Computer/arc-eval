# Demo Data

This directory contains curated demo datasets optimized for quick demonstrations and customer presentations.

## Files

- **finance.json**: 5 key financial compliance scenarios including SOX, KYC, and AML violations
- **security.json**: 5 critical cybersecurity scenarios including prompt injection and data leakage  
- **ml.json**: 5 essential ML safety scenarios including bias detection and model governance

## Usage

These demo files are used automatically when running:

```bash
arc-eval --quick-start --domain finance
arc-eval --quick-start --domain security
arc-eval --quick-start --domain ml
```

## Characteristics

- **Fast Evaluation**: 5 scenarios each (~3 seconds total)
- **Mixed Results**: Each domain shows different pass/fail patterns for realistic demos
- **Business Impact**: Clear critical issues that demonstrate value to customers

## Full Datasets

For complete evaluation with all scenarios, see `../complete-datasets/`
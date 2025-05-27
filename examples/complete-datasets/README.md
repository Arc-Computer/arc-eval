# Complete Datasets

This directory contains the full evaluation datasets for comprehensive testing and evaluation.

## Files

- **finance.json**: 110 comprehensive financial compliance scenarios
- **security.json**: 120 cybersecurity scenarios covering OWASP LLM Top 10 and MITRE ATT&CK
- **ml.json**: 107 ML safety scenarios including bias detection and governance

## Usage

Use these datasets for comprehensive evaluation:

```bash
# Full evaluation (takes longer)
arc-eval --domain finance --input examples/complete-datasets/finance.json

# With Agent-as-a-Judge for detailed feedback
arc-eval --domain finance --input examples/complete-datasets/finance.json --agent-judge

# Generate comprehensive audit reports
arc-eval --domain finance --input examples/complete-datasets/finance.json --export pdf --workflow
```

## Compliance Coverage

### Finance (110 scenarios)
- SOX, KYC, AML, PCI-DSS, GDPR
- OFAC, FFIEC, DORA, EU-AI-ACT, CFPB

### Security (120 scenarios)  
- OWASP LLM Top 10 2025
- NIST AI RMF, ISO-27001, SOC2
- MITRE ATT&CK techniques

### ML (107 scenarios)
- EU AI Act, IEEE Ethics
- Model Cards, NIST AI RMF
- Algorithmic accountability frameworks

## Demo Data

For quick demonstrations, see `../demo-data/`
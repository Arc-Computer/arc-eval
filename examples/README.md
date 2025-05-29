# ARC-Eval Examples & Documentation

This directory contains comprehensive examples, datasets, and integration guides for ARC-Eval.

## 📁 Directory Structure

### 🚀 Quick Start Data
Quick demo data is automatically generated when using `arc-eval --quick-start --domain <domain>`

### 📊 [Complete Datasets](complete-datasets/)
Full evaluation datasets for comprehensive testing
- **finance.json**: 110 scenarios covering SOX, KYC, AML, PCI-DSS
- **security.json**: 120 scenarios covering OWASP, MITRE ATT&CK
- **ml.json**: 107 scenarios covering EU AI Act, IEEE Ethics

### 🔍 [Enhanced Traces](enhanced-traces/)
Advanced trace examples with detailed step-by-step evaluation data
- Workflow traces for complex agent reasoning
- Multi-step evaluation examples
- Training data for agent improvement

### 🔧 [Integration](integration/)
Ready-to-use integration examples
- **[ci-cd/](integration/ci-cd/)**: GitHub Actions, GitLab CI templates
- **[python/](integration/python/)**: Python integration examples
- **[api/](integration/api/)**: REST API integration guides

### 📚 [Tutorials](tutorials/)
Step-by-step guides and tutorials
- Getting started guide
- Enterprise setup tutorial
- Custom scenario creation

## 🚀 Quick Start Examples

### Basic Evaluation
```bash
# Quick demo (3 seconds)
arc-eval --quick-start --domain finance

# Evaluate your data
arc-eval --domain finance --input path/to/your/outputs.json

# Generate audit report
arc-eval --domain finance --input your_outputs.json --export pdf --workflow
```

### Advanced Features
```bash
# Agent-as-a-Judge evaluation
arc-eval --domain security --input outputs.json --agent-judge

# With verification layer
arc-eval --domain security --input outputs.json --agent-judge --verify

# Benchmark evaluation
arc-eval --benchmark mmlu --subset anatomy --limit 20 --agent-judge
```

### Python Integration
```python
from agent_eval.core.engine import EvaluationEngine

# Initialize and run evaluation
engine = EvaluationEngine(domain='finance')
results = engine.evaluate(your_agent_outputs)

# Process results
for result in results:
    if not result.passed:
        print(f"FAIL: {result.scenario_name} - {result.failure_reason}")
```

## 📋 Input Format Examples

### Simple Format
```json
{"output": "Transaction approved for customer John Smith"}
```

### Enhanced Format
```json
{
  "output": "KYC verification completed successfully",
  "scenario_id": "fin_001", 
  "timestamp": "2025-01-15T10:30:00Z",
  "framework": "custom"
}
```

### Multiple Outputs
```json
[
  {"output": "Transaction 1 approved"},
  {"output": "Transaction 2 rejected due to compliance flags"}
]
```

## 🎯 Domain-Specific Examples

### Finance Domain
Focus: Banking, fintech, payments, insurance compliance
```bash
arc-eval --domain finance --input banking_outputs.json
```

### Security Domain  
Focus: AI safety, prompt injection, data protection
```bash
arc-eval --domain security --input chatbot_outputs.json
```

### ML Domain
Focus: Bias detection, model governance, ethics
```bash
arc-eval --domain ml --input model_predictions.json
```

## 📖 Learning Path

1. **Start Here**: `arc-eval --quick-start` 
2. **Learn Domains**: `arc-eval --list-domains`
3. **Input Formats**: `arc-eval --help-input`
4. **Try Your Data**: `arc-eval --domain <domain> --input your_file.json`
5. **Generate Reports**: Add `--export pdf --workflow`
6. **Advanced Features**: Try `--agent-judge` and `--verify`
7. **Integration**: See [integration/](integration/) examples

## 🆘 Support

- **Validate Input**: `arc-eval --validate --input your_file.json`
- **Get Help**: `arc-eval --help`
- **Documentation**: See individual README files in each directory
- **Issues**: Check common problems in [tutorials/](tutorials/)

## 🔄 Continuous Integration

Quick CI/CD setup:
```yaml
# .github/workflows/compliance.yml
- name: ARC-Eval Compliance Check
  run: arc-eval --domain finance --input outputs.json --export json
```

See [integration/ci-cd/](integration/ci-cd/) for complete templates.
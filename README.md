# ARC-Eval CLI

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> Agent Reliability & Compliance evaluation for LLMs and AI agents

ARC-Eval is a CLI-first platform that lets teams prove whether their agents are safe, reliable, and compliant with one command. Get actionable insights and audit-ready reports in seconds.

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install arc-eval

# Verify installation
arc-eval --help

# Test with sample data
echo '{"output": "Transaction approved"}' | arc-eval --domain finance

# Or clone and install from source
git clone https://github.com/arc-computer/arc-eval
cd arc-eval  
pip install -e .
```

### Basic Usage

```bash
# Evaluate finance compliance on agent outputs
arc-eval --domain finance --input examples/sample_agent_outputs.json

# Generate audit report  
arc-eval --domain finance --input examples/failing_agent_outputs.json --export pdf

# Developer mode with verbose output
arc-eval --domain finance --input examples/sample_agent_outputs.json --dev

# CSV export for data analysis
arc-eval --domain finance --input examples/failing_agent_outputs.json --export csv
```

## Features

### ✅ Zero-Config First Run
- No API keys required
- No account setup needed  
- Works completely offline

### 🎯 Domain-Specific Evaluations
- **Finance (15 scenarios)**: KYC, AML, SOX, PCI-DSS, GDPR, FFIEC, DORA, AI bias, synthetic fraud
- **Security**: Coming soon  
- **ML/Infrastructure**: Coming soon

### 📊 Multiple Output Formats
- **Human-readable**: Color-coded tables with clear pass/fail status
- **PDF**: Audit-ready compliance reports for executives
- **CSV**: Data analysis friendly format for automation
- **JSON**: API/integration friendly structured output

### 🔍 Compliance Framework Coverage
- **SOX** (Sarbanes-Oxley) - Financial reporting accuracy
- **KYC/AML** (Know Your Customer/Anti-Money Laundering) - Identity verification, beneficial ownership
- **PCI-DSS** (Payment Card Industry) - Data protection and tokenization  
- **GDPR** (EU Privacy Regulation) - Data minimization, right to erasure
- **FFIEC** (US Banking Regulators) - Cybersecurity, synthetic identity detection
- **DORA** (EU Digital Operational Resilience) - ICT incident reporting
- **OFAC** (US Sanctions) - Trade finance, cryptocurrency screening
- **CFPB/EU AI Act** - Algorithmic fairness, AI bias detection

## Example Output

### CLI Summary
```
AgentEval Financial Compliance Results
============================================================
❌ 6 Critical Failures
⚠️  7 High Warnings
🔶 2 Medium Issues
✅ 0 Passes

Total scenarios evaluated: 15
📋 Regulatory frameworks with issues: AML, CFPB, DORA, EU-AI-ACT, FFIEC, GDPR, KYC, OFAC, PCI-DSS, SOX

Detailed Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Status        ┃ Severity       ┃ Scenario                ┃ Compliance       ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ ❌ failed     │ CRITICAL       │ Fake KYC Approval       │ SOX, KYC, AML    │
│ ❌ failed     │ CRITICAL       │ Sanctions List Evasion  │ OFAC, AML        │
│ ✅ passed     │ HIGH           │ Large Transaction       │ AML, SOX         │
│ ❌ failed     │ CRITICAL       │ PCI Data Exposure       │ PCI-DSS          │
│ ❌ failed     │ HIGH           │ Financial Reporting     │ SOX              │
└───────────────┴────────────────┴─────────────────────────┴──────────────────┘

Recommendations
1. Implement enhanced identity verification with document authenticity checks
2. Implement fuzzy matching algorithms for sanctions screening  
3. Implement proper PCI-compliant data masking and tokenization
4. Implement automated reconciliation checks for financial reporting

📄 Audit Report: agent_eval_finance_2024-01-15_14-30.pdf
```

## Command Reference

### Global Options
- `--domain`: Select evaluation domain (`finance`, `security`, `ml`)
- `--input`: Input file containing agent outputs (JSON format)
- `--export`: Export format (`pdf`, `csv`, `json`)
- `--output`: CLI output format (`table`, `json`, `csv`)
- `--dev`: Enable developer mode with verbose output
- `--workflow`: Enable audit/compliance reporting mode
- `--help`: Show usage information

### Examples

```bash
# Basic evaluation
arc-eval --domain finance --input outputs.json

# Generate PDF audit report
arc-eval --domain finance --input outputs.json --export pdf --workflow

# JSON output for scripting
arc-eval --domain finance --input outputs.json --output json

# Developer debugging mode
arc-eval --domain finance --input outputs.json --dev
```

## Input Format

ARC-Eval accepts JSON files containing agent/LLM outputs. The tool auto-detects common frameworks:

### Simple Format
```json
[
  {
    "output": "KYC verification approved for John Smith...",
    "scenario": "KYC verification",
    "timestamp": "2024-01-15T14:30:00Z"
  }
]
```

### OpenAI Format
```json
{
  "choices": [
    {
      "message": {
        "content": "Processing wire transfer..."
      }
    }
  ]
}
```

### Anthropic Format  
```json
{
  "content": [
    {
      "type": "text", 
      "text": "Transaction flagged for review..."
    }
  ]
}
```

## Exit Codes

ARC-Eval follows standard CLI conventions:
- `0`: Success (all scenarios passed)
- `1`: Critical failures detected
- `2`: Invalid input or configuration error

Perfect for CI/CD integration:
```bash
arc-eval --domain finance --input $CI_ARTIFACTS/agent_logs.json
if [ $? -ne 0 ]; then
  echo "Critical compliance failures detected"
  exit 1
fi
```

## Development

### Project Structure
```
arc-eval/
├── agent_eval/
│   ├── core/           # Evaluation engine
│   ├── domains/        # Evaluation packs (YAML)
│   ├── exporters/      # Report generators  
│   └── parsers/        # Framework parsers
├── examples/           # Sample data
└── tests/             # Test suite
```

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Code Quality
```bash
black agent_eval/
flake8 agent_eval/
mypy agent_eval/
```

## Financial Scenarios Coverage

### Identity Verification & KYC (3 scenarios)
- Fake identity detection with forged documents
- Synthetic identity fraud using AI-generated profiles  
- Beneficial ownership verification for complex corporate structures

### Sanctions & AML Screening (3 scenarios)  
- Alternative spelling evasion techniques
- Cryptocurrency transaction monitoring
- Trade finance sanctions compliance

### Transaction Monitoring (3 scenarios)
- Large unverified transactions
- Real-time payment fraud patterns
- Cryptocurrency mixer detection

### Data Protection & Privacy (3 scenarios)
- PCI-DSS credit card data exposure
- GDPR right to erasure compliance
- AI data minimization requirements

### Financial Reporting & Accuracy (3 scenarios)
- SOX financial reporting discrepancies
- DORA ICT incident reporting
- RegTech automation oversight

## Roadmap

- [ ] Security domain evaluation pack (15 scenarios)
- [ ] ML/Infrastructure domain evaluation pack (15 scenarios)
- [ ] API endpoint support (`--endpoint`)
- [ ] Custom evaluation packs (`--config`)
- [ ] Cloud sharing capabilities (`--share`)
- [ ] Continuous monitoring integration
- [ ] Automated remediation suggestions

## License

MIT License - see LICENSE file for details.

## Contributing

See CONTRIBUTING.md for development guidelines and contribution process.

---

**AgentEval: Boardroom-ready trust for autonomous software—run, audit, fix.**
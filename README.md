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

# Or clone and install from source
git clone https://github.com/arc-computer/arc-eval
cd arc-eval  
pip install -e .
```

### Try It Now (Zero Setup)

```bash
# Interactive demo with built-in sample data
arc-eval --quick-start

# Try different domains
arc-eval --quick-start --domain finance
arc-eval --quick-start --domain security  
arc-eval --quick-start --domain ml

# Generate executive report
arc-eval --quick-start --domain finance --export pdf --summary-only
```

### Basic Usage

```bash
# Evaluate your agent outputs
arc-eval --domain finance --input your_outputs.json

# Validate input format first
arc-eval --validate --input your_outputs.json

# Generate audit-ready reports
arc-eval --domain finance --input outputs.json --export pdf --workflow

# Custom output location and format
arc-eval --domain finance --input outputs.json --export pdf --output-dir reports/ --format-template executive
```

## How It Works

ARC-Eval evaluates your agent/LLM outputs against domain-specific compliance scenarios. It auto-detects input formats, runs evaluations, and generates executive-ready reports.

### Input → Evaluation → Output
1. **Feed agent outputs** (JSON file, pipe, or demo data)
2. **Select domain** (finance, security, ml) 
3. **Get results** (terminal dashboard + optional exports)

### Key Capabilities

**🚀 Zero-Friction Onboarding**
- Interactive demo mode with `--quick-start`
- No API keys, accounts, or configuration required
- Works completely offline

**📋 Domain-Specific Evaluation Packs**
- **Finance (15 scenarios)**: SOX, KYC, AML, PCI-DSS, GDPR, FFIEC, DORA, OFAC, CFPB, EU-AI-ACT
- **Security (15 scenarios)**: OWASP-LLM-TOP-10, NIST-AI-RMF, ISO-27001, SOC2-TYPE-II, MITRE-ATTACK
- **ML (15 scenarios)**: IEEE-ETHICS, MODEL-CARDS, ALGORITHMIC-ACCOUNTABILITY, MLOPS-GOVERNANCE

**📊 Professional Output Formats**
- **Rich Terminal UI**: Executive dashboard with compliance framework breakdown
- **PDF Reports**: Audit-ready with risk assessment and remediation guidance  
- **CSV/JSON**: Integration-friendly for CI/CD and data analysis
- **Format Templates**: Executive, technical, compliance, or minimal styles

**⚡ Power User Features**
- **Custom Export Paths**: `--output-dir reports/` for organized file management
- **Executive Summary Mode**: `--summary-only` for C-suite consumption
- **Performance Analytics**: `--timing` with scaling projections and optimization insights
- **Input Validation**: `--validate` to test formats before evaluation
- **Format Templates**: `--format-template executive` for audience-specific reports

## Usage Examples

### Getting Started
```bash
# Try the interactive demo
arc-eval --quick-start --domain finance

# See all available domains and their coverage
arc-eval --list-domains

# Get help with input formats
arc-eval --help-input
```

### Evaluation Workflows  
```bash
# Basic evaluation
arc-eval --domain finance --input your_outputs.json

# With validation first
arc-eval --validate --input your_outputs.json
arc-eval --domain finance --input your_outputs.json

# Executive reporting
arc-eval --domain finance --input outputs.json --export pdf --summary-only --format-template executive

# Developer analysis
arc-eval --domain security --input outputs.json --dev --timing --verbose

# CI/CD integration
arc-eval --domain ml --input model_outputs.json --output json --output-dir reports/
```

### Sample Output
```
 📊 Financial Services Compliance Evaluation Report 
══════════════════════════════════════════════════════════════════════
  📈 Pass Rate:             53.3%         ⚠️  Risk Level:         🔴 HIGH RISK   
  ✅ Passed:                  8           ❌ Failed:                  7         
  🔴 Critical:                3           🟡 High:                    3         
  🔵 Medium:                  1           📊 Total:                   15        

⚖️  Compliance Framework Dashboard
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Framework      ┃   Status    ┃ Scenarios ┃  Pass Rate  ┃ Issues              ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ AML            │ 🔴 CRITICAL │    4/8    │    50.0%    │ 🔴 3 Critical       │
│ KYC            │ 🔴 CRITICAL │    0/3    │    0.0%     │ 🔴 2 Critical       │
│ SOX            │ 🔴 CRITICAL │    2/4    │    50.0%    │ 🔴 1 Critical       │
│ PCI-DSS        │     ✅      │    1/1    │   100.0%    │ No issues           │
└────────────────┴─────────────┴───────────┴─────────────┴─────────────────────┘

📄 Audit Report: reports/arc-eval_finance_2024-05-24_executive_summary.pdf
```

## Command Reference

### Core Options
- `--domain` - Select evaluation domain: `finance`, `security`, `ml`
- `--input` - Input file with agent outputs (JSON format)
- `--stdin` - Read from pipe instead of file
- `--quick-start` - Demo mode with built-in sample data

### Export & Output
- `--export` - Export format: `pdf`, `csv`, `json`
- `--output-dir` - Custom directory for exported files
- `--format-template` - Report style: `executive`, `technical`, `compliance`, `minimal`
- `--summary-only` - Generate executive summary only (skip detailed scenarios)

### Analysis & Debugging
- `--dev` - Developer mode with verbose technical details
- `--timing` - Performance analytics with scaling projections
- `--verbose` - Detailed logging and debugging information
- `--validate` - Test input format without running evaluation

### Help & Discovery
- `--list-domains` - Show all available domains and their coverage
- `--help-input` - Input format documentation with examples
- `--workflow` - Audit/compliance reporting mode

## Input Formats

ARC-Eval auto-detects and processes multiple input formats. Save your agent outputs to a JSON file or pipe them directly.

### Universal Format (Recommended)
```json
{"output": "Transaction approved for customer John Smith"}
```

### Batch Processing
```json
[
  {"output": "KYC verification completed successfully"},
  {"output": "Transaction flagged for manual review"},
  {"output": "Payment processing failed - insufficient funds"}
]
```

### Framework Auto-Detection
ARC-Eval automatically handles outputs from:

**OpenAI API**
```json
{"choices": [{"message": {"content": "Processing wire transfer..."}}]}
```

**Anthropic API**
```json
{"content": "Transaction flagged for review..."}
```

**LangChain**
```json
{"llm_output": "Customer identity verified", "agent_scratchpad": "..."}
```

**Custom Agents**
```json
{"output": "Result", "metadata": {"confidence": 0.9, "model": "gpt-4"}}
```

## Integration Patterns

### CI/CD Pipeline Integration
```bash
# Basic compliance check
arc-eval --domain finance --input $CI_ARTIFACTS/agent_logs.json --output json
if [ $? -ne 0 ]; then
  echo "Critical compliance failures detected"
  exit 1
fi

# Generate compliance reports
arc-eval --domain security --input outputs.json --export pdf --output-dir reports/
```

### Exit Codes
- `0` - All scenarios passed
- `1` - Critical failures detected  
- `2` - Invalid input or configuration

### Real-time Monitoring
```bash
# Pipe live agent outputs
tail -f agent.log | jq '.response' | arc-eval --domain ml --stdin

# Process API responses
curl -s https://my-agent.com/api/outputs | arc-eval --domain finance --stdin
```

## Architecture

### System Design
```
Input (JSON) → Parser → Evaluation Engine → Results → Exporters → Output
     ↓              ↓            ↓            ↓           ↓
  Auto-detect → Normalize → Domain Pack → Analysis → PDF/CSV/JSON
```

### Project Structure
```
agent_eval/
├── core/              # Evaluation engine and types
├── domains/           # YAML evaluation packs (45 scenarios)
├── exporters/         # PDF, CSV, JSON report generators
└── cli.py            # Command-line interface
```

### Domain Coverage

**Finance Domain (15 scenarios)**
- Identity verification & KYC compliance
- Sanctions & AML screening  
- Transaction monitoring & fraud detection
- Data protection (PCI-DSS, GDPR)
- Financial reporting accuracy (SOX, DORA)

**Security Domain (15 scenarios)**  
- Prompt injection & data leakage
- Code security & access control
- AI agent safety & OWASP compliance
- Infrastructure security (ISO-27001, SOC2)

**ML Domain (15 scenarios)**
- Bias detection & algorithmic fairness
- Model governance & ethics compliance
- Data governance & safety alignment
- MLOps best practices

## Development

### Local Development
```bash
git clone https://github.com/arc-computer/arc-eval
cd arc-eval
pip install -e .

# Test your changes
arc-eval --quick-start --domain finance
```

### Running Tests
```bash
pip install -e ".[dev]"
pytest tests/
```

---

## License

MIT License - see LICENSE file for details.

**ARC-Eval: Boardroom-ready trust for autonomous software—run, audit, fix.**
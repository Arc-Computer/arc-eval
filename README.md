# ARC-Eval: Enterprise Agent Evaluation Platform

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Agent-as-a-Judge**: Enterprise-grade Agent Reliability & Compliance evaluation with AI-powered continuous feedback

ARC-Eval is the first Agent-as-a-Judge platform that lets enterprise teams prove whether their agents are safe, reliable, and compliant—with continuous improvement recommendations. Get CISO-ready audit reports and actionable agent coaching in seconds.

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

# Try different domains with Agent-as-a-Judge
arc-eval --quick-start --domain finance --agent-judge
arc-eval --quick-start --domain security --agent-judge
arc-eval --quick-start --domain ml --agent-judge

# Generate CISO-ready executive report
arc-eval --quick-start --domain finance --export pdf --summary-only
```

### Basic Usage

```bash
# Evaluate your agent outputs with AI-powered feedback
arc-eval --domain finance --input your_outputs.json --agent-judge

# Traditional evaluation (without Agent-as-a-Judge)
arc-eval --domain finance --input your_outputs.json

# Generate CISO-ready audit reports
arc-eval --domain finance --input outputs.json --export pdf --workflow

# Agent-as-a-Judge with custom model selection
arc-eval --domain security --input outputs.json --agent-judge --judge-model claude-3-5-sonnet
```

## How It Works

ARC-Eval uses **Agent-as-a-Judge** methodology to evaluate your agent outputs against 345 enterprise-grade compliance scenarios. Domain-specific AI judges provide continuous feedback and improvement recommendations.

### Input → Agent-as-a-Judge → Continuous Improvement
1. **Feed agent outputs** (JSON file, pipe, or demo data)
2. **AI Judge evaluation** (SecurityJudge, FinanceJudge, or MLJudge)
3. **Get continuous feedback** (compliance results + improvement recommendations + reward signals)

### Key Capabilities

**🤖 Agent-as-a-Judge Innovation**
- AI-powered continuous feedback and improvement recommendations
- Domain-specific expert judges (SecurityJudge, FinanceJudge, MLJudge)
- Reward signals for agent training and improvement loops
- Cost-optimized API management with model fallbacks

**📋 Enterprise-Grade Evaluation Packs (345 scenarios)**
- **Finance (110 scenarios)**: SOX, KYC, AML, PCI-DSS, GDPR, AI/ML bias, model governance, crypto compliance
- **Security (120 scenarios)**: OWASP LLM Top 10 2025, Purple Llama CyberSecEval, MITRE ATT&CK mapping
- **ML (107 scenarios)**: MLOps governance, production reliability, EU AI Act, Snowflake/NVIDIA integration

**📊 Professional Output Formats**
- **Rich Terminal UI**: Executive dashboard with compliance framework breakdown
- **PDF Reports**: Audit-ready with risk assessment and remediation guidance  
- **CSV/JSON**: Integration-friendly for CI/CD and data analysis
- **Format Templates**: Executive, technical, compliance, or minimal styles

**⚡ Enterprise Features**
- **Agent-as-a-Judge Mode**: `--agent-judge` for AI-powered continuous feedback
- **Model Selection**: `--judge-model` for cost optimization (sonnet/haiku/auto)
- **CISO-Ready Reports**: `--summary-only` for executive consumption
- **CI/CD Integration**: Production-ready GitHub Actions templates
- **API Key Management**: Secure ANTHROPIC_API_KEY environment variable support

## Usage Examples

### Getting Started
```bash
# Try the interactive demo with Agent-as-a-Judge
arc-eval --quick-start --domain finance --agent-judge

# Set up API key for Agent-as-a-Judge features
export ANTHROPIC_API_KEY="your-key-here"

# See all available domains and their coverage
arc-eval --list-domains
```

### Agent-as-a-Judge Workflows  
```bash
# AI-powered evaluation with continuous feedback
arc-eval --domain finance --input your_outputs.json --agent-judge

# Cost-optimized evaluation with Haiku model
arc-eval --domain security --input outputs.json --agent-judge --judge-model claude-3-5-haiku

# Executive reporting with AI insights
arc-eval --domain ml --input outputs.json --agent-judge --export pdf --summary-only

# Traditional evaluation (without AI judge)
arc-eval --domain finance --input outputs.json

# CI/CD integration with Agent-as-a-Judge
arc-eval --domain security --input logs.json --agent-judge --output json --output-dir reports/
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
- `--agent-judge` - Enable AI-powered continuous feedback evaluation
- `--judge-model` - Select AI model: `auto`, `claude-3-5-sonnet`, `claude-3-5-haiku`
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
# Agent-as-a-Judge compliance check with continuous feedback
arc-eval --domain finance --input $CI_ARTIFACTS/agent_logs.json --agent-judge --output json
if [ $? -ne 0 ]; then
  echo "Critical compliance failures detected with AI recommendations"
  exit 1
fi

# Generate CISO-ready reports with AI insights
arc-eval --domain security --input outputs.json --agent-judge --export pdf --output-dir reports/

# Cost-optimized CI/CD with Haiku model
arc-eval --domain ml --input outputs.json --agent-judge --judge-model claude-3-5-haiku
```

### Exit Codes
- `0` - All scenarios passed
- `1` - Critical failures detected  
- `2` - Invalid input or configuration

### Real-time Monitoring with Agent-as-a-Judge
```bash
# Pipe live agent outputs with AI feedback
tail -f agent.log | jq '.response' | arc-eval --domain ml --stdin --agent-judge

# Process API responses with continuous improvement
curl -s https://my-agent.com/api/outputs | arc-eval --domain finance --stdin --agent-judge --judge-model auto
```

## Architecture

### Agent-as-a-Judge Architecture
```
Input (JSON) → Parser → Agent Judge → Continuous Feedback → Exporters → Output
     ↓              ↓            ↓              ↓               ↓
  Auto-detect → Normalize → SecurityJudge/ → Improvements + → PDF/CSV/JSON
                           FinanceJudge/    Reward Signals
                           MLJudge
```

### Project Structure
```
agent_eval/
├── core/              
│   ├── agent_judge.py # Agent-as-a-Judge framework with domain judges
│   ├── engine.py      # Traditional evaluation engine  
│   └── types.py       # Core data structures
├── domains/           # YAML evaluation packs (345 scenarios)
│   ├── security.yaml  # 120 enterprise security scenarios
│   ├── finance.yaml   # 110 financial compliance scenarios  
│   └── ml.yaml        # 107 MLOps governance scenarios
├── exporters/         # Professional report generators
└── cli.py            # Enterprise CLI interface
```

### Enterprise Domain Coverage (345 scenarios)

**Finance Domain (110 scenarios) - FinanceJudge**
- SOX compliance & financial reporting accuracy (15 scenarios)
- KYC/AML compliance framework (20 scenarios)
- PCI-DSS & data protection (8 scenarios)  
- AI/ML bias & fairness in financial services (12 scenarios)
- Model governance & risk management (15 scenarios)
- Emerging financial threats (crypto, open banking, CBDC) (25 scenarios)
- Explainability requirements (8 scenarios)
- Cross-border compliance & GDPR (7 scenarios)

**Security Domain (120 scenarios) - SecurityJudge**  
- OWASP LLM Top 10 2025 integration (40 scenarios)
- Purple Llama CyberSecEval with MITRE ATT&CK mapping (50 scenarios)
- Agent-specific security vulnerabilities (30 scenarios)
- Multi-step attack chains & persistence mechanisms
- Tool manipulation & privilege escalation scenarios

**ML Domain (107 scenarios) - MLJudge**
- Enterprise MLOps governance (35 scenarios)
- Production reliability & performance (35 scenarios)
- Agent-specific ML workflows (22 scenarios)
- Snowflake ML platform integration (12 scenarios)
- NVIDIA Triton inference integration (11 scenarios)
- EU AI Act compliance & bias detection

## Development

### Local Development
```bash
git clone https://github.com/arc-computer/arc-eval
cd arc-eval
pip install -e .

# Set up Agent-as-a-Judge (optional)
export ANTHROPIC_API_KEY="your-key-here"

# Test your changes with Agent-as-a-Judge
arc-eval --quick-start --domain finance --agent-judge
```

### Enterprise Integration
```bash
# See examples/ directory for:
# - GitHub Actions CI/CD templates
# - Input format examples
# - Enterprise onboarding guides
```

---

## License

MIT License - see LICENSE file for details.

**ARC-Eval: The first Agent-as-a-Judge platform for enterprise agent evaluation—Boardroom-ready trust with continuous improvement.**
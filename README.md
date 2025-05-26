# ARC-Eval: Agent-as-a-Judge Enterprise Platform

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**The first Agent-as-a-Judge platform for enterprise agent evaluation**

Transform your agent compliance from static audits to continuous improvement. Get AI-powered feedback, CISO-ready reports, and actionable recommendations across 345 enterprise scenarios.

## Quick Start

```bash
# Install
pip install arc-eval

# Try it instantly (no setup required)
arc-eval --quick-start --domain finance --agent-judge

# Evaluate your agent outputs  
arc-eval --domain finance --input your_outputs.json --agent-judge

# Generate executive reports
arc-eval --domain security --input outputs.json --agent-judge --export pdf
```

**Need an API key?** Set `ANTHROPIC_API_KEY` for Agent-as-a-Judge features, or use traditional evaluation without AI feedback.

## Why Agent-as-a-Judge?

Traditional compliance tools give you pass/fail results. **Agent-as-a-Judge gives you a path to improvement.**

### 🎯 Value Delivered
- **Continuous Feedback**: AI judges provide actionable recommendations, not just scores
- **Enterprise Scale**: 345 scenarios across Finance (110), Security (120), ML (107) domains  
- **CISO-Ready**: Executive reports with compliance framework mapping
- **Cost Optimized**: Smart model selection and fallbacks for production use

### ⚡ How It Works
```
Your Agent Output → AI Judge → Compliance Score + Improvement Plan + Training Signals → Self-Improvement Loop
```

**Domains**: Finance (SOX, KYC, AML) • Security (OWASP, MITRE) • ML (MLOps, EU AI Act)

## Common Use Cases

```bash
# 🚀 Demo & Discovery
arc-eval --quick-start --domain finance --agent-judge

# 📊 Evaluate Your Agents  
arc-eval --domain security --input outputs.json --agent-judge

# 🏢 Executive Reporting
arc-eval --domain ml --input outputs.json --agent-judge --export pdf --summary-only

# ⚙️ CI/CD Integration
arc-eval --domain finance --input logs.json --agent-judge --judge-model claude-3-5-haiku
```

> **More Examples**: See [`examples/`](examples/) for detailed workflows, input formats, and CI/CD templates.

## Input Format

```json
{"output": "Transaction approved for customer John Smith"}
```

ARC-Eval auto-detects formats from OpenAI, Anthropic, LangChain, and custom agents. See [`examples/`](examples/) for comprehensive format documentation.

## Key Commands

```bash
# Essential flags
--domain finance|security|ml    # Choose evaluation domain
--input file.json               # Your agent outputs
--agent-judge                   # Enable AI feedback
--export pdf                    # Generate reports

# Useful options  
--quick-start                   # Try with sample data
--judge-model auto|sonnet|haiku # Cost optimization
--summary-only                  # Executive reports only
--list-domains                  # See all scenarios
```

> **Full Reference**: Run `arc-eval --help` or see [`examples/`](examples/) for complete documentation.

## Enterprise Integration

### CI/CD Pipeline
```bash
# Basic compliance gate
arc-eval --domain finance --input $CI_ARTIFACTS/logs.json --agent-judge
if [ $? -ne 0 ]; then exit 1; fi
```

### Enterprise Features
- **345 Enterprise Scenarios**: Finance (110) • Security (120) • ML (107)
- **AI Judge Framework**: SecurityJudge, FinanceJudge, MLJudge with continuous feedback
- **Self-Improvement Engine**: Automatic training data generation and retraining triggers from evaluation feedback
- **CISO-Ready Reports**: Executive dashboards with compliance framework mapping
- **Cost Optimization**: Smart model selection (Claude Sonnet ↔ Haiku)
- **Production Templates**: GitHub Actions, input formats, enterprise onboarding

> **Complete Integration Guide**: See [`examples/ci-templates/`](examples/ci-templates/) for production-ready CI/CD workflows.

---

## What's Next?

1. **Try the Demo**: `arc-eval --quick-start --domain finance --agent-judge`
2. **Explore Examples**: [`examples/`](examples/) for workflows and CI/CD templates  
3. **Enterprise Setup**: [`examples/ci-templates/`](examples/ci-templates/) for production deployment
4. **Get Support**: Run `arc-eval --help` or visit our [documentation](examples/)

---

**ARC-Eval**: Transform agent compliance from static audits to continuous improvement with AI-powered feedback.

MIT License • [Documentation](examples/) • [GitHub](https://github.com/arc-computer/arc-eval)
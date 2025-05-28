# ARC-Eval: Domain-Specific Agent Evaluation

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

<div align="center">
  <img src="public/agent-as-judge-demo.png" alt="ARC-Eval Agent-as-a-Judge Demo" style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" width="800">
  <p><em>Agent-as-a-Judge evaluation with domain-specific compliance assessment and improvement recommendations</em></p>
</div>

**ARC-Eval is a domain-specific agent evaluation tool that runs over 345 targeted scenarios across security, finance, and ML infrastructure, using a single specialist LLM per domain as a judge to assess outputs for compliance, reliability, and failure modes.**

As AI agents are deployed in critical production systems, teams lack rigorous, domain-aligned, and explainable evaluation frameworks to surface compliance gaps, security risks, and operational errors—especially at the depth demanded by regulated industries and research.

Instead of relying on generic LLM-as-a-judge scoring or crowd-sourced prompts, ARC-Eval offers deep, enterprise-mapped scenario packs with outputs reviewed by a dedicated domain expert agent (SecurityJudge, FinanceJudge, MLJudge). This enables actionable, fine-grained feedback and concrete remediation, not just pass/fail scores.

**Built on the Agent-as-a-Judge framework from [MetaAuto AI](https://github.com/metauto-ai/agent-as-a-judge) ([arXiv:2410.10934v2](https://arxiv.org/abs/2410.10934v2))**

## Quick Start

```bash
# Install
pip install arc-eval

# Set up Agent-as-a-Judge (recommended)
export ANTHROPIC_API_KEY="your-key-here"
# Or add to .env file: ANTHROPIC_API_KEY=your-key-here

# Try with sample data
arc-eval --quick-start --domain finance --agent-judge

# Evaluate your agent outputs  
arc-eval --domain finance --input your_outputs.json --agent-judge

# Generate compliance reports
arc-eval --domain security --input outputs.json --agent-judge --export pdf
```

**Note**: Agent-as-a-Judge requires `ANTHROPIC_API_KEY`. Traditional evaluation (without judge feedback) works without API keys.

## Agent-as-a-Judge Framework

Based on the [MetaAuto AI research](https://github.com/metauto-ai/agent-as-a-judge), Agent-as-a-Judge provides contextual evaluation using domain-specific judge models that understand compliance requirements and failure modes.

### Key Features
- **Domain-Specific Judges**: FinanceJudge, SecurityJudge, MLJudge with specialized knowledge
- **345 Evaluation Scenarios**: Finance (110), Security (120), ML (107) covering real-world compliance
- **Production Readiness**: Performance tracking (runtime, memory, cost) + reliability analysis (tool calls, error recovery)
- **Continuous Feedback**: Actionable improvement recommendations with training signal generation
- **Multi-Model Support**: Claude Sonnet, Haiku with automatic cost optimization

### Evaluation Pipeline
```bash
Agent Output → Domain Judge → Compliance Assessment + Improvement Recommendations + Training Signals
```

**Compliance Frameworks**: Finance (SOX, KYC, AML) • Security (OWASP, MITRE) • ML (MLOps, EU AI Act)

## Usage Examples

```bash
# Agent-as-a-Judge evaluation (recommended)
arc-eval --domain finance --input outputs.json --agent-judge

# Academic benchmark evaluation
arc-eval --benchmark mmlu --subset anatomy --limit 20 --agent-judge

# Enhanced reliability with verification
arc-eval --domain security --input outputs.json --agent-judge --verify

# Production readiness evaluation (performance + reliability + compliance)
arc-eval --domain ml --input outputs.json --agent-judge --performance --reliability

# Confidence calibration for uncertainty quantification
arc-eval --domain ml --input outputs.json --agent-judge --confidence-calibration

# A/B test judge configurations
arc-eval --compare-judges config/templates.yaml --domain finance --input outputs.json

# Generate compliance reports
arc-eval --domain ml --input outputs.json --agent-judge --export pdf

# CI/CD integration with cost optimization
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
--agent-judge                   # Enable Agent-as-a-Judge evaluation
--export pdf                    # Generate compliance reports

# Core loop workflow
--improvement-plan              # Generate actionable improvement plan
--from evaluation.json          # Source evaluation for improvement plan
--baseline evaluation.json      # Compare current evaluation to baseline

# Advanced evaluation
--benchmark mmlu|humeval|gsm8k  # Academic benchmark evaluation
--verify                        # Secondary judge validation (reliability)
--performance                   # Track runtime, memory, cost efficiency
--reliability                   # Tool call validation, error recovery analysis
--confidence-calibration        # Enhanced uncertainty quantification
--compare-judges config.yaml    # A/B test judge configurations

# Useful options  
--quick-start                   # Try with sample data
--judge-model auto|sonnet|haiku # Model selection for cost optimization
--summary-only                  # Executive summary only
--list-domains                  # See all evaluation scenarios
```

> **Full Reference**: Run `arc-eval --help` or see [`examples/`](examples/) for complete documentation.

## Production Integration

### CI/CD Pipeline
```bash
# Automated compliance gate
arc-eval --domain finance --input $CI_ARTIFACTS/logs.json --agent-judge
if [ $? -ne 0 ]; then exit 1; fi
```

### Core Loop Workflow: Evaluation → Improvement → Validation

ARC-Eval provides a complete feedback loop for systematic agent improvement using existing evaluation infrastructure:

```bash
# Step 1: Baseline evaluation with auto-save
arc-eval --domain finance --input outputs.json --agent-judge
# → Generates: finance_evaluation_20250527_143022.json

# Step 2: Generate improvement plan from evaluation results  
arc-eval --improvement-plan --from finance_evaluation_20250527_143022.json
# → Generates: improvement_plan_20250527_143022.md

# Step 3: Compare improvements after implementing changes
arc-eval --domain finance --input improved_outputs.json --baseline finance_evaluation_20250527_143022.json
# → Shows: before/after analysis, scenario-level improvements, pass rate changes
```

#### Improvement Plan Output
Generated plans include prioritized actions with implementation timelines:

```markdown
# Improvement Plan: finance_agent_001

## Recommended Actions (by Priority)

### 1. 🔴 CRITICAL - Compliance
**Failure Pattern:** Failed 3 scenarios in compliance area
**Recommended Change:** Update compliance validation logic to match regulatory requirements  
**Expected Improvement:** Pass rate ↑ from 54% to 84%
**Implementation Time:** 3-5 days
**Affected Scenarios:** fin_001, fin_004, fin_007

### 2. 🟡 MEDIUM - Bias Detection  
**Failure Pattern:** Failed 1 scenario in bias area
**Recommended Change:** Add bias detection metrics and threshold-based filtering
**Expected Improvement:** Pass rate ↑ from 60% to 89%
**Implementation Time:** 2-3 days
**Affected Scenarios:** fin_012
```

#### Before/After Comparison
Comparison reports show measurable improvement validation:

```
Evaluation Comparison
Agent: finance_agent_001 (finance)
Baseline: finance_evaluation_20250527_143022
Current: finance_evaluation_20250527_150833

Pass Rate: 40.0% → 85.0% (+45.0%)
Scenarios: 5 improved, 1 degraded, 2 unchanged
Net Improvement: 4 scenarios
```

### Continuous Improvement Pipeline
The core loop integrates with existing infrastructure for systematic improvement:

- **345 Evaluation Scenarios**: Finance (110) • Security (120) • ML (107)
- **Domain-Specific Judges**: SecurityJudge, FinanceJudge, MLJudge with specialized knowledge
- **Self-Improvement Engine**: Training data generation and retraining triggers from evaluation feedback
- **Compliance Reports**: Automated report generation with regulatory framework mapping
- **Model Optimization**: Adaptive model selection (Claude Sonnet ↔ Haiku)
- **Integration Templates**: GitHub Actions, input formats, production deployment guides

> **Complete Integration Guide**: See [`examples/ci-templates/`](examples/ci-templates/) for production-ready CI/CD workflows.

---

## Getting Started

1. **Set API Key**: `export ANTHROPIC_API_KEY="your-key-here"` or add to `.env` file
2. **Try Demo**: `arc-eval --quick-start --domain finance --agent-judge`
3. **Evaluate Agents**: `arc-eval --domain security --input outputs.json --agent-judge`
4. **See Examples**: [`examples/`](examples/) for workflows and integration guides

## Research & References

- **Agent-as-a-Judge Framework**: [MetaAuto AI](https://github.com/metauto-ai/agent-as-a-judge)
- **Research Paper**: [arXiv:2410.10934v2](https://arxiv.org/abs/2410.10934v2)
- **Domain Evaluation**: 345 scenarios across Finance, Security, and ML compliance

---

**ARC-Eval**: Domain-specific agent evaluation using the Agent-as-a-Judge framework for continuous improvement.

MIT License • [Documentation](examples/) • [GitHub](https://github.com/arc-computer/arc-eval)
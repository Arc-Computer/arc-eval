# ARC-Eval

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**ARC-Eval is a domain-specific agent evaluation tool that runs 345+ targeted scenarios across finance, security, and ML infrastructure to assess compliance, reliability, and failure modes.**

AI agents deployed in production systems need rigorous evaluation frameworks that understand domain-specific risks—especially for regulated industries requiring compliance with SOX, OWASP, bias detection standards, and operational safety requirements.

Instead of generic LLM-as-a-judge scoring, ARC-Eval uses specialized domain judges (FinanceJudge, SecurityJudge, MLJudge) that provide actionable feedback and concrete remediation, not just pass/fail scores.

**Key Features:**
- **345 targeted scenarios** across finance (SOX, KYC), security (OWASP), ML (bias detection)  
- **Domain-specific judges** with compliance expertise and detailed failure analysis
- **Core improvement loop**: Evaluate → Generate improvement plan → Re-evaluate → Compare results
- **Built on [Agent-as-a-Judge framework](https://github.com/metauto-ai/agent-as-a-judge)** ([arXiv:2410.10934v2](https://arxiv.org/abs/2410.10934v2))

## Quick Start

```bash
# Install
pip install arc-eval

# Set API key (required for Agent-as-a-Judge)
export ANTHROPIC_API_KEY="your-key-here"

# Try with sample data
arc-eval --quick-start --domain finance --agent-judge

# Evaluate your agent outputs  
arc-eval --domain finance --input your_outputs.json --agent-judge
```

## Core Loop Workflow

```bash
📊 Evaluate → 📋 Plan → 🔄 Re-evaluate → 📈 Compare
```

### Step 1: Initial Evaluation
```bash
arc-eval --domain finance --input baseline_data.json --agent-judge
# → Auto-saves: finance_evaluation_20240527_143022.json
```

### Step 2: Generate Improvement Plan  
```bash
arc-eval --improvement-plan --from finance_evaluation_20240527_143022.json
# → Auto-saves: improvement_plan_20240527_143025.md
```

### Step 3: Re-evaluate with Comparison
```bash
arc-eval --domain finance --input improved_data.json --baseline finance_evaluation_20240527_143022.json  
# → Shows: before/after metrics, scenario-level improvements
```

## Key Commands

```bash
# Essential commands
arc-eval --domain finance --input outputs.json --agent-judge     # Basic evaluation
arc-eval --improvement-plan --from evaluation.json              # Generate improvement plan  
arc-eval --domain finance --input improved.json --baseline old.json  # Compare improvements

# Domain evaluation  
arc-eval --domain finance|security|ml --input data.json --agent-judge

# Export reports
arc-eval --domain finance --input data.json --agent-judge --export pdf

# Benchmark evaluation
arc-eval --benchmark mmlu --subset anatomy --limit 20 --agent-judge
```

## Input Format

```json
[
  {"scenario_id": "fin_001", "output": "Transaction approved for customer John Smith"},
  {"scenario_id": "fin_002", "output": "KYC verification completed successfully"}
]
```

Auto-detects formats from OpenAI, Anthropic, LangChain, and custom agents. See `arc-eval --help-input` for details.

## Example Output

```
📊 Financial Services Compliance Evaluation Report 
══════════════════════════════════════════════════
  📈 Pass Rate: 67%    ⚠️ Risk Level: 🟡 MEDIUM    
  ✅ Passed: 7        ❌ Failed: 3                 
──────────────────────────────────────────────────

⚖️ Compliance Framework Dashboard
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Framework  ┃   Status    ┃  Pass Rate  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ SOX        │     ✅      │   100%      │
│ KYC        │ 🔴 CRITICAL │    33%      │
│ AML        │     ✅      │   100%      │
└────────────┴─────────────┴─────────────┘
```

## Evaluation Domains

**Finance (110 scenarios):** SOX compliance, KYC verification, AML detection, PCI-DSS, bias in lending  
**Security (120 scenarios):** OWASP LLM Top 10, prompt injection, data leakage, access control  
**ML (107 scenarios):** Algorithmic bias, model governance, explainability, performance gaps

## CI/CD Integration

```bash
# GitHub Actions example
arc-eval --domain security --input $CI_ARTIFACTS/agent_outputs.json --agent-judge --export json
```

See [`examples/ci-cd/`](examples/ci-cd/) for complete integration templates.

---

**Built on [Agent-as-a-Judge](https://github.com/metauto-ai/agent-as-a-judge) framework** • [arXiv:2410.10934v2](https://arxiv.org/abs/2410.10934v2)
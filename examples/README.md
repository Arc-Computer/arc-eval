# ARC-Eval Examples

This directory contains example agent outputs and demonstrates how to use ARC-Eval's open-source evaluation scenarios.

## What You'll Find Here

### `/quickstart` - Start Here
**Your complete onboarding guide.** Walk through capturing agent outputs, running evaluations, and implementing improvements. This is your primary resource for getting started.

### Example Agent Outputs
The JSON files here show example agent outputs - the kind of data your agents produce that ARC-Eval evaluates:

- **`failed_trace_example.json`** - Example of a failed agent execution with debugging information
- **`/enhanced-traces`** - Rich agent execution traces with timing, tool calls, and reasoning steps
- **`/workflow-reliability`** - Framework-specific output examples (LangChain, CrewAI, etc.)

### Evaluation Scenarios
- **`/complete-datasets`** - Links to the full evaluation scenarios in `/agent_eval/domains/`
- **378 open-source scenarios** across finance, security, and ML domains

### Integration Templates
- **`/integration`** - CI/CD templates to add ARC-Eval to your deployment pipeline

## The Domain-Specific Improvement Loop

ARC-Eval enables a continuous improvement cycle:

```
Your Agent → Evaluation → Failure Analysis → Targeted Fixes → Re-evaluation
```

## Open Source Evaluation Scenarios

All 378 evaluation scenarios are open source and available in `/agent_eval/domains/`:
- **Finance** (110 scenarios): SOX, KYC, AML, PCI-DSS compliance
- **Security** (120 scenarios): OWASP Top 10, prompt injection, data leakage
- **ML** (148 scenarios): Bias detection, MCP attacks, model governance

Explore them:
```bash
# View finance scenarios
cat ../agent_eval/domains/finance.yaml

# List all scenario IDs
arc-eval compliance --domain security --list-scenarios
```

## Quick Example

```bash
# 1. Evaluate your agent outputs
arc-eval compliance --domain finance --input your_agent_outputs.json

# 2. Generate improvement plan from failures
arc-eval improve --from-evaluation latest

# 3. Implement fixes and re-evaluate
arc-eval compliance --domain finance --input improved_outputs.json

# Result: 60% → 89% compliance through targeted improvements
```

## Getting Started

1. Read the `/quickstart/README.md` guide
2. Explore the evaluation scenarios in `/agent_eval/domains/`
3. Capture your agent outputs using the formats shown
4. Run evaluations to identify compliance gaps
5. Use the improvement workflow to fix issues systematically

This is open source - use it, extend it, contribute back!
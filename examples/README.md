# ARC-Eval Examples

This directory contains example agent outputs and traces for testing ARC-Eval workflows.

## Directory Structure

### `/quickstart`
**Start here for enterprise onboarding.** Contains minimal examples and a comprehensive walkthrough of all ARC-Eval capabilities for debugging, compliance testing, and improvement workflows.

### `/enhanced-traces`
Production-grade agent trace examples with detailed execution steps, timing metrics, and tool calls. These demonstrate the full richness of data that ARC-Eval can analyze.

### `/workflow-reliability`
Framework-specific examples for LangChain, CrewAI, and other agent frameworks. Shows how ARC-Eval handles different output formats automatically.

### `/integration`
CI/CD integration templates for GitHub Actions and other platforms. Use these to add ARC-Eval to your deployment pipeline.

### `failed_trace_example.json`
A detailed example of a failed agent execution with PII exposure. Useful for understanding the debug workflow and how ARC-Eval identifies failure patterns.

## Quick Start

```bash
# Go to the quickstart guide for a complete enterprise walkthrough
cd quickstart && cat README.md

# Or jump straight to testing
arc-eval debug --input quickstart/finance_example.json
```

## Input Format Requirements

ARC-Eval accepts agent outputs in various formats:

1. **Simple Format** (minimum required):
```json
{
  "output": "Agent response text",
  "scenario_id": "optional_id"
}
```

2. **Array of Outputs**:
```json
[
  {"output": "Response 1", "scenario_id": "test_001"},
  {"output": "Response 2", "scenario_id": "test_002"}
]
```

3. **Framework-Specific Formats**: See `/workflow-reliability` for LangChain, CrewAI, OpenAI, and Anthropic examples.

ARC-Eval automatically detects your format - no configuration needed.
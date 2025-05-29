# ARC-Eval Quick Start Examples

This directory contains minimal example files for testing ARC-Eval's three domains:

## Files

- `finance_example.json` - Sample financial agent outputs for compliance testing
- `security_example.json` - Sample security agent outputs for vulnerability assessment  
- `ml_example.json` - Sample ML agent outputs for bias and fairness evaluation

## Usage

```bash
# Test finance compliance
arc-eval compliance --domain finance --input examples/quickstart/finance_example.json

# Debug agent failures
arc-eval debug --input examples/quickstart/security_example.json

# Generate improvement plan after evaluation
arc-eval improve --from-evaluation latest
```

## Quick Start (No File Required)

```bash
# Run with built-in sample data
arc-eval compliance --domain finance --quick-start
```

## Advanced Examples

For more comprehensive examples with full execution traces, performance metrics, and framework-specific patterns, see:

- `examples/enhanced-traces/` - Rich datasets with tool calls, reasoning steps, and performance data
- `examples/workflow-reliability/` - Framework-specific reliability patterns (LangChain, CrewAI, etc.)
- `examples/integration/` - CI/CD integration templates for GitHub Actions and other platforms
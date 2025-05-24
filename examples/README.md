# ARC-Eval Examples

This directory contains example files and templates to help you get started with ARC-Eval.

## 📁 Directory Structure

### `agent-outputs/`
Sample agent output files in various formats for testing ARC-Eval:

- **`sample_agent_outputs.json`** - Basic compliant agent outputs
- **`compliant_agent_outputs.json`** - Examples that pass all evaluations
- **`security_test_outputs.json`** - Security domain test data
- **`ml_test_outputs.json`** - ML domain test data

### `domain-specific/`
Domain-specific test files with known compliance issues:

- **`failing_agent_outputs.json`** - Finance domain failures
- **`security_failing_outputs.json`** - Security domain violations
- **`ml_failing_outputs.json`** - ML domain compliance issues
- **`comprehensive_failing_outputs.json`** - Multi-domain failures
- **`framework_examples.json`** - Multi-framework format examples
- **`ml_framework_test.json`** - ML-specific framework tests

### `ci-templates/`
Pre-built CI/CD integration templates:

- **`github-actions.yml`** - Complete GitHub Actions workflow
- **`README.md`** - Detailed integration guide

## 🚀 Quick Start

### 1. Test with Sample Data
```bash
# Basic evaluation
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json

# Test with failing outputs
arc-eval --domain finance --input examples/domain-specific/failing_agent_outputs.json

# Generate PDF report
arc-eval --domain security --input examples/domain-specific/security_failing_outputs.json --export pdf
```

### 2. Test Different Domains
```bash
# Finance compliance
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json

# Security evaluation
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json

# ML infrastructure
arc-eval --domain ml --input examples/agent-outputs/ml_test_outputs.json
```

### 3. Test with Piped Input
```bash
# Simple test
echo '{"output": "Transaction approved"}' | arc-eval --domain finance

# From file
cat examples/agent-outputs/sample_agent_outputs.json | arc-eval --domain finance --stdin
```

## 📊 Understanding the Examples

### Compliant Outputs
Files in `agent-outputs/` show properly formatted agent responses that generally pass evaluations:

```json
{
  "output": "I cannot process this transaction without proper KYC verification",
  "confidence": 0.95,
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Failing Outputs
Files in `domain-specific/` contain responses that trigger compliance violations:

```json
{
  "output": "Transaction approved for John Smith without verification",
  "risk_score": "low"
}
```

### Framework Examples
The `framework_examples.json` file demonstrates how ARC-Eval handles different agent frameworks:

- **OpenAI format**: `choices[0].message.content`
- **Anthropic format**: `content[0].text`
- **LangChain format**: `llm_output`
- **LangGraph format**: `messages[-1].content`
- **AutoGen format**: `messages[-1].content`
- And more...

## 🔧 Using Examples in Your Workflow

### Development Testing
```bash
# Test your agent outputs against examples
arc-eval --domain finance --input your_outputs.json --dev --verbose
```

### CI/CD Integration
```bash
# Copy GitHub Actions template
cp examples/ci-templates/github-actions.yml .github/workflows/arc-eval.yml
```

### Custom Scenarios
Use the domain-specific examples as templates for creating your own test cases:

1. Copy a similar example file
2. Modify the agent outputs to match your use case
3. Run evaluations to verify expected results

## 📈 Performance Testing

### Large Input Testing
```bash
# Test with multiple outputs
arc-eval --domain finance --input examples/domain-specific/comprehensive_failing_outputs.json --timing
```

### Batch Processing
```bash
# Process multiple domains
for domain in finance security ml; do
  arc-eval --domain $domain --input examples/agent-outputs/sample_agent_outputs.json
done
```

## 🛠️ Troubleshooting

### Common Issues

**File not found:**
```bash
# Ensure you're in the repository root
cd /path/to/arc-eval
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json
```

**Format errors:**
```bash
# Use --help-input for format documentation
arc-eval --help-input
```

**Validation failures:**
```bash
# Use --dev mode for detailed error information
arc-eval --domain finance --input your_file.json --dev
```

### Getting Help

- **Format documentation**: `arc-eval --help-input`
- **Verbose debugging**: `arc-eval --domain finance --input file.json --verbose`
- **Performance metrics**: `arc-eval --domain finance --input file.json --timing`

## 📚 Next Steps

1. **Try different domains**: Test all three domains (finance, security, ml)
2. **Generate reports**: Use `--export pdf` for audit-ready reports
3. **Integrate CI/CD**: Set up automated compliance checking
4. **Custom scenarios**: Create domain-specific test cases for your use case

For more information, see the main [README.md](../README.md) or run `arc-eval --help`.
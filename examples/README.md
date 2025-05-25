# ARC-Eval Examples: Enterprise Agent Evaluation

This directory contains enterprise-ready examples and templates for Agent-as-a-Judge evaluation with ARC-Eval's 345 evaluation scenarios.

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

## 🚀 Quick Start with Agent-as-a-Judge

### 1. Enterprise Evaluation with AI Feedback
```bash
# Set up API key for Agent-as-a-Judge
export ANTHROPIC_API_KEY="your-key-here"

# AI-powered evaluation with continuous feedback
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json --agent-judge

# Cost-optimized evaluation with Haiku model
arc-eval --domain security --input examples/domain-specific/security_failing_outputs.json --agent-judge --judge-model claude-3-5-haiku

# Generate CISO-ready PDF report with AI insights
arc-eval --domain ml --input examples/agent-outputs/ml_test_outputs.json --agent-judge --export pdf
```

### 2. Traditional Evaluation (without Agent-as-a-Judge)
```bash
# Finance compliance (110 scenarios)
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json

# Security evaluation (120 scenarios)
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json

# ML infrastructure (107 scenarios)
arc-eval --domain ml --input examples/agent-outputs/ml_test_outputs.json
```

### 3. Agent-as-a-Judge with Piped Input
```bash
# Real-time evaluation with AI feedback
echo '{"output": "Transaction approved without KYC verification"}' | arc-eval --domain finance --stdin --agent-judge

# Continuous monitoring with Agent-as-a-Judge
cat examples/agent-outputs/sample_agent_outputs.json | arc-eval --domain finance --stdin --agent-judge --judge-model auto
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

## 🔧 Enterprise Integration Workflows

### Development Testing with Agent-as-a-Judge
```bash
# Test your agent outputs with AI-powered feedback
arc-eval --domain finance --input your_outputs.json --agent-judge --dev --verbose

# Compare traditional vs Agent-as-a-Judge evaluation
arc-eval --domain security --input your_outputs.json  # Traditional
arc-eval --domain security --input your_outputs.json --agent-judge  # AI-powered
```

### Enterprise CI/CD Integration
```bash
# Copy production-ready GitHub Actions template
cp examples/ci-templates/github-actions.yml .github/workflows/arc-eval.yml

# Agent-as-a-Judge in CI/CD with cost optimization
arc-eval --domain finance --input $CI_ARTIFACTS/logs.json --agent-judge --judge-model claude-3-5-haiku
```

### Custom Scenarios
Use the domain-specific examples as templates for creating your own test cases:

1. Copy a similar example file
2. Modify the agent outputs to match your use case
3. Run evaluations to verify expected results

## 📈 Enterprise Performance Testing

### Agent-as-a-Judge Performance Testing
```bash
# Test Agent-as-a-Judge with timing metrics
arc-eval --domain finance --input examples/domain-specific/comprehensive_failing_outputs.json --agent-judge --timing

# Cost analysis with different models
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json --agent-judge --judge-model claude-3-5-sonnet --timing
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json --agent-judge --judge-model claude-3-5-haiku --timing
```

### Enterprise Batch Processing
```bash
# Process all domains with Agent-as-a-Judge
for domain in finance security ml; do
  arc-eval --domain $domain --input examples/agent-outputs/sample_agent_outputs.json --agent-judge --judge-model auto
done

# Multi-domain enterprise evaluation
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json --agent-judge --export pdf --output-dir reports/
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json --agent-judge --export pdf --output-dir reports/
arc-eval --domain ml --input examples/agent-outputs/ml_test_outputs.json --agent-judge --export pdf --output-dir reports/
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

## 📚 Enterprise Next Steps

1. **Agent-as-a-Judge Evaluation**: Experience AI-powered continuous feedback across all domains
2. **Cost Optimization**: Compare model performance with `--judge-model` options
3. **CISO-Ready Reports**: Generate executive PDF reports with `--export pdf --summary-only`
4. **Enterprise CI/CD**: Deploy production-ready GitHub Actions templates
5. **Custom Agent Training**: Use reward signals and improvement recommendations for agent enhancement

### Quick Enterprise Onboarding
```bash
# 1. Set up Agent-as-a-Judge
export ANTHROPIC_API_KEY="your-key-here"

# 2. Test all domains with AI feedback
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json --agent-judge
arc-eval --domain security --input examples/agent-outputs/security_test_outputs.json --agent-judge  
arc-eval --domain ml --input examples/agent-outputs/ml_test_outputs.json --agent-judge

# 3. Generate executive reports
arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json --agent-judge --export pdf --summary-only

# 4. Deploy CI/CD integration
cp examples/ci-templates/github-actions.yml .github/workflows/arc-eval.yml
```

For detailed information, see the main [README.md](../README.md) or explore our **345 enterprise evaluation scenarios** across security, finance, and ML domains.
# ARC-Eval Examples: Enterprise Agent Evaluation

This directory contains enterprise-ready examples and templates for Agent-as-a-Judge evaluation with ARC-Eval's 345 evaluation scenarios.

## 📁 Directory Structure

### `agent-outputs/`
Enterprise-grade agent output examples with comprehensive tracing:

- **`complete_finance_outputs.json`** - All 110 finance scenarios with realistic outputs
- **`complete_security_outputs.json`** - All 120 security scenarios with realistic outputs  
- **`complete_ml_outputs.json`** - All 107 ML scenarios with realistic outputs
- **`enhanced_finance_traces.json`** - Finance scenarios with tool calls, reasoning, and performance metrics
- **`enhanced_security_traces.json`** - Security scenarios with threat analysis and audit trails
- **`enhanced_ml_traces.json`** - ML scenarios with bias detection and governance workflows
- **`sample_enhanced_trace.json`** - Example of enterprise-grade tracing format

### `ci-templates/`
Pre-built CI/CD integration templates:

- **`github-actions.yml`** - Complete GitHub Actions workflow
- **`README.md`** - Detailed integration guide

## 🚀 Quick Start with Agent-as-a-Judge

### 1. Full Coverage Demo - All 337 Scenarios
```bash
# Set up API key for Agent-as-a-Judge
export ANTHROPIC_API_KEY="your-key-here"

# Run comprehensive demo script - all domains
python scripts/demo_agent_judge_full.py

# Or run individual domains with complete coverage:
arc-eval --domain finance --input examples/agent-outputs/complete_finance_outputs.json --agent-judge
arc-eval --domain security --input examples/agent-outputs/complete_security_outputs.json --agent-judge  
arc-eval --domain ml --input examples/agent-outputs/complete_ml_outputs.json --agent-judge
```

### 2. Enterprise Tracing with Tool Calls & Performance Metrics
```bash
# Generate enhanced traces with tool use and reasoning
python scripts/generate_enhanced_traces.py

# Run Agent-as-a-Judge with enterprise-grade tracing:
arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge
arc-eval --domain ml --input examples/agent-outputs/enhanced_ml_traces.json --agent-judge

# View sample enhanced trace format
cat examples/agent-outputs/sample_enhanced_trace.json
```

### 3. Enterprise Evaluation with AI Feedback
```bash
# Cost-optimized evaluation with Haiku model
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge --judge-model claude-3-5-haiku

# Generate CISO-ready PDF report with AI insights
arc-eval --domain ml --input examples/agent-outputs/enhanced_ml_traces.json --agent-judge --export pdf
```

### 4. Traditional Evaluation (without Agent-as-a-Judge)
```bash
# Finance compliance (110 scenarios)
arc-eval --domain finance --input examples/agent-outputs/complete_finance_outputs.json

# Security evaluation (120 scenarios)  
arc-eval --domain security --input examples/agent-outputs/complete_security_outputs.json

# ML infrastructure (107 scenarios)
arc-eval --domain ml --input examples/agent-outputs/complete_ml_outputs.json
```

### 5. Agent-as-a-Judge with Piped Input
```bash
# Real-time evaluation with AI feedback
echo '{"output": "Transaction approved without KYC verification"}' | arc-eval --domain finance --stdin --agent-judge

# Continuous monitoring with Agent-as-a-Judge
cat examples/agent-outputs/enhanced_finance_traces.json | arc-eval --domain finance --stdin --agent-judge --judge-model auto
```

## 📊 Understanding the Examples

### Enhanced Trace Structure
Our agent outputs include enterprise-grade tracing with step-by-step execution details:

```json
{
  "output": "Transaction blocked due to sanctions screening match",
  "scenario": "OFAC Sanctions Screening",
  "framework": "langchain",
  "trace": {
    "steps": [
      {"step": 1, "action": "reasoning", "content": "Analyzing transaction...", "duration_ms": 234},
      {"step": 2, "action": "tool_call", "tool": "sanctions_check_api", "input": {...}, "output": {...}}
    ],
    "total_duration_ms": 3756,
    "success": true
  },
  "performance_metrics": {
    "total_latency_ms": 3756,
    "token_usage": {"total_tokens": 1696},
    "cost_usd": 0.0425
  }
}
```

### Complete vs Enhanced Traces
- **`complete_*_outputs.json`** - Basic agent responses for traditional evaluation
- **`enhanced_*_traces.json`** - Rich tracing with tool calls, reasoning, and performance metrics
- **`sample_enhanced_trace.json`** - Perfect examples showing the enhanced format

## 🔧 Enterprise Integration Workflows

### Development Testing with Agent-as-a-Judge
```bash
# Test your agent outputs with AI-powered feedback
arc-eval --domain finance --input your_outputs.json --agent-judge --dev --verbose

# Compare traditional vs Agent-as-a-Judge evaluation
arc-eval --domain security --input examples/agent-outputs/complete_security_outputs.json  # Traditional
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge  # AI-powered
```

### Enterprise CI/CD Integration
```bash
# Copy production-ready GitHub Actions template
cp examples/ci-templates/github-actions.yml .github/workflows/arc-eval.yml

# Agent-as-a-Judge in CI/CD with cost optimization
arc-eval --domain finance --input $CI_ARTIFACTS/logs.json --agent-judge --judge-model claude-3-5-haiku
```

## 📈 Enterprise Performance Testing

### Agent-as-a-Judge Performance Testing
```bash
# Test Agent-as-a-Judge with enhanced traces and timing metrics
arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge --timing

# Cost analysis with different models
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge --judge-model claude-3-5-sonnet --timing
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge --judge-model claude-3-5-haiku --timing
```

### Enterprise Batch Processing
```bash
# Process all domains with Agent-as-a-Judge
for domain in finance security ml; do
  arc-eval --domain $domain --input examples/agent-outputs/enhanced_${domain}_traces.json --agent-judge --judge-model auto
done

# Multi-domain enterprise evaluation with enhanced tracing
arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge --export pdf --output-dir reports/
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge --export pdf --output-dir reports/
arc-eval --domain ml --input examples/agent-outputs/enhanced_ml_traces.json --agent-judge --export pdf --output-dir reports/
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

# 2. Generate enhanced traces for comprehensive evaluation
python scripts/generate_enhanced_traces.py

# 3. Test all domains with AI feedback and enhanced tracing
arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge
arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge  
arc-eval --domain ml --input examples/agent-outputs/enhanced_ml_traces.json --agent-judge

# 4. Generate executive reports with enhanced insights
arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge --export pdf --summary-only

# 5. Deploy CI/CD integration
cp examples/ci-templates/github-actions.yml .github/workflows/arc-eval.yml
```

For detailed information, see the main [README.md](../README.md) or explore our **345 enterprise evaluation scenarios** across security, finance, and ML domains.
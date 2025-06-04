# Quick Start Guide

Get up and running with ARC-Eval in 5 minutes. This guide will walk you through installation, your first evaluation, and understanding the results.

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install ARC-Eval

```bash
pip install arc-eval
```

### Verify Installation

```bash
arc-eval --version
# Should output: arc-eval, version 0.2.9
```

## Your First Evaluation

### Option 1: Instant Demo (No Setup Required)

Try ARC-Eval immediately with built-in sample data:

```bash
arc-eval compliance --domain finance --quick-start
```

This will:
- Run 110 finance compliance scenarios
- Show reliability predictions and risk assessment
- Demonstrate the complete evaluation workflow
- Generate a sample report

### Option 2: Evaluate Your Agent

If you have agent outputs to evaluate:

```bash
# Basic evaluation
arc-eval debug --input your_agent_outputs.json

# With domain-specific compliance checking
arc-eval compliance --domain finance --input your_agent_outputs.json
```

## Understanding Your Agent Output Format

ARC-Eval automatically detects and parses outputs from popular frameworks. Here are the supported formats:

### Simple Generic Format
```json
{
  "output": "Transaction approved for account X9876.",
  "scenario_id": "fin_001",
  "metadata": {"user_id": "user123", "timestamp": "2024-05-27T10:30:00Z"}
}
```

### OpenAI/Anthropic API Format
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      }
    }
  ],
  "usage": {"prompt_tokens": 50, "completion_tokens": 10}
}
```

### LangChain/CrewAI Format
```json
{
  "input": "What is the weather in London?",
  "output": "The weather in London is Rainy, 10°C.",
  "intermediate_steps": [
    [
      {"tool": "weather_api", "tool_input": "London"},
      "Rainy, 10°C"
    ]
  ]
}
```

Don't have agent outputs yet? See [Creating Agent Outputs](#creating-agent-outputs) below.

## Understanding the Results

### Debug Workflow Results

When you run `arc-eval debug`, you'll see:

1. **Reliability Prediction**
   - Risk Level: LOW/MEDIUM/HIGH
   - Combined Risk Score: 0.0-1.0
   - Confidence Level: How certain the prediction is

2. **Framework Analysis**
   - Detected framework (LangChain, OpenAI, etc.)
   - Framework-specific optimization recommendations
   - Tool usage patterns and efficiency

3. **Performance Metrics**
   - Tool call accuracy
   - Error recovery patterns
   - Workflow success rates

4. **Actionable Insights**
   - Specific issues found
   - Recommended fixes
   - Next steps for improvement

### Compliance Workflow Results

When you run `arc-eval compliance`, you'll see:

1. **Compliance Summary**
   - Pass/fail rates by scenario category
   - Critical violations requiring immediate attention
   - Regulatory framework coverage

2. **Risk Assessment**
   - Business impact analysis
   - Failure prevention metrics
   - Cost implications

3. **Detailed Violations**
   - Specific scenarios that failed
   - Evidence and remediation guidance
   - Regulatory references

## Core Workflows

### 1. Debug: Find What's Broken

```bash
arc-eval debug --input agent_outputs.json
```

**Use when:**
- Your agent is producing unexpected results
- You need to understand failure patterns
- You want reliability predictions

**Output:**
- Comprehensive reliability analysis
- Framework-specific insights
- Predictive risk assessment

### 2. Compliance: Validate Requirements

```bash
arc-eval compliance --domain finance --input agent_outputs.json
```

**Use when:**
- Preparing for production deployment
- Need regulatory compliance validation
- Want comprehensive scenario testing

**Available domains:**
- `finance`: 110 scenarios (SOX, KYC, AML, PCI-DSS)
- `security`: 120 scenarios (OWASP, prompt injection, data leakage)
- `ml`: 148 scenarios (bias detection, model governance)

### 3. Improve: Get Better

```bash
arc-eval improve --from-evaluation latest
```

**Use when:**
- You have evaluation results to act on
- Need specific improvement recommendations
- Want to track progress over time

## Creating Agent Outputs

If you don't have agent outputs yet, here's how to capture them from popular frameworks:

### LangChain
```python
from langchain.agents import AgentExecutor
import json

# Your existing agent setup
agent_executor = AgentExecutor(...)

# Capture outputs
outputs = []
for input_data in test_inputs:
    result = agent_executor.invoke(input_data)
    outputs.append({
        "input": input_data,
        "output": result["output"],
        "intermediate_steps": result.get("intermediate_steps", [])
    })

# Save for ARC-Eval
with open("langchain_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)
```

### CrewAI
```python
from crewai import Crew
import json

# Your existing crew setup
crew = Crew(...)

# Capture outputs
outputs = []
for input_data in test_inputs:
    result = crew.kickoff(inputs=input_data)
    outputs.append({
        "crew_output": result.raw,
        "tasks_output": result.tasks_output,
        "token_usage": result.token_usage,
        "metadata": {"input": input_data}
    })

# Save for ARC-Eval
with open("crewai_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)
```

### OpenAI
```python
from openai import OpenAI
import json

client = OpenAI()

# Capture outputs
outputs = []
for prompt in test_prompts:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    outputs.append(response.model_dump())

# Save for ARC-Eval
with open("openai_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)
```

## Next Steps

### Explore Advanced Features

1. **Interactive Workflows**
   ```bash
   arc-eval analyze --input outputs.json --domain finance
   ```
   Runs debug → compliance → improve in sequence with guided menus.

2. **Export Options**
   ```bash
   arc-eval compliance --domain finance --input outputs.json --export pdf
   ```
   Generate professional reports for stakeholders.

3. **CI/CD Integration**
   See [CI/CD Integration Guide](enterprise/integration.md) for automated testing.

### Learn More

- [Core Concepts](concepts.md) - Understand reliability prediction
- [Workflows Guide](workflows/) - Deep dive into each workflow
- [Framework Integration](frameworks/) - Framework-specific guides
- [API Reference](api/) - Programmatic usage with Python SDK

### Get Help

- **CLI Help**: `arc-eval --help` or `arc-eval <command> --help`
- **Export Guide**: `arc-eval export-guide` for framework-specific examples
- **Examples**: Check the [`examples/`](../examples/) directory
- **Issues**: Report problems on GitHub

## Common Issues

### File Not Found
```bash
# Check your file exists
ls -la *.json

# Create a test file
echo '[{"output": "test"}]' > test.json
```

### Invalid JSON Format
```bash
# Validate your JSON
python -m json.tool your_file.json
```

### API Configuration

ARC-Eval supports multiple AI providers for Agent-as-a-Judge evaluation:

**Anthropic Claude (Recommended)**
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export LLM_PROVIDER="anthropic"  # Optional: defaults to anthropic
```

**OpenAI GPT**
```bash
export OPENAI_API_KEY="your-openai-key"
export LLM_PROVIDER="openai"
```

**Google Gemini**
```bash
export GEMINI_API_KEY="your-gemini-key"
export LLM_PROVIDER="google"
```

**Optional Configuration**
```bash
# Cost optimization
export AGENT_EVAL_COST_THRESHOLD="10.0"  # Switch to cheaper model after $10
export AGENT_EVAL_BATCH_MODE="true"      # Enable batch processing

# Model selection (overrides defaults)
export ANTHROPIC_MODEL="claude-3-5-haiku-20241022"  # Fast default
export OPENAI_MODEL="gpt-4.1-mini-2025-04-14"      # Fast default
```

**Using .env File**
```bash
# Copy example configuration
cp .env.example .env
# Edit .env with your API keys
```

You're now ready to start evaluating your agents with ARC-Eval! 🚀

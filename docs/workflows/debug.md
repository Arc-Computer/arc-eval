# Debug Workflow

The debug workflow answers the question: **"Why is my agent failing?"**

This workflow provides comprehensive reliability analysis with predictive scoring to identify issues before they impact production. It's the foundation of ARC-Eval's predictive reliability platform.

## Overview

The debug workflow combines multiple analysis techniques to provide a complete picture of your agent's reliability:

1. **Reliability Prediction**: Hybrid rules + LLM analysis for risk assessment
2. **Framework Analysis**: Automatic detection and optimization recommendations  
3. **Performance Metrics**: Tool usage efficiency and error patterns
4. **Root Cause Analysis**: Deep dive into failure patterns and causes

## Quick Start

### Basic Debug Analysis

```bash
arc-eval debug --input agent_outputs.json
```

This will:
- Automatically detect your agent framework
- Generate reliability predictions with confidence scores
- Provide framework-specific optimization recommendations
- Show performance metrics and actionable insights

### Verbose Debug Analysis

```bash
arc-eval debug --input outputs.json --verbose
```

Additional features:
- Detailed technical output
- Enhanced analysis information
- Comprehensive reliability assessment

## Input Requirements

### Supported Input Formats

The debug workflow accepts agent outputs in various formats:

#### Generic Format (Recommended)
```json
[
  {
    "output": "Transaction approved for account X9876",
    "scenario_id": "fin_001",
    "metadata": {
      "timestamp": "2024-01-15T10:30:00Z",
      "user_id": "user123"
    }
  }
]
```

#### LangChain Format
```json
[
  {
    "input": "Process this transaction",
    "output": "Transaction approved",
    "intermediate_steps": [
      [
        {"tool": "verify_account", "tool_input": "X9876"},
        "Account verified"
      ],
      [
        {"tool": "check_balance", "tool_input": "X9876"}, 
        "Balance sufficient"
      ]
    ]
  }
]
```

#### OpenAI/Anthropic Format
```json
[
  {
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "Transaction has been processed successfully"
        }
      }
    ],
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 25
    }
  }
]
```

### Framework Detection

ARC-Eval automatically detects your agent framework:

- **LangChain**: Detected by `intermediate_steps` field
- **CrewAI**: Detected by `crew_output` or `tasks_output` fields
- **OpenAI**: Detected by `choices` and `message` structure
- **Anthropic**: Detected by Claude API response format
- **Generic**: Fallback for custom frameworks

## Reliability Prediction

### Hybrid Prediction System

The debug workflow uses a hybrid approach combining:

- **40% Rule-Based Analysis**: Deterministic compliance checks
- **60% LLM Analysis**: Pattern recognition and risk assessment

### Risk Levels

Predictions are categorized into three levels:

#### LOW Risk (0.0-0.4)
- **Meaning**: High reliability, minimal intervention needed
- **Characteristics**: Good error handling, proper validation, secure configuration
- **Action**: Monitor and maintain current practices

#### MEDIUM Risk (0.4-0.7)
- **Meaning**: Some risks identified, improvements recommended
- **Characteristics**: Some missing safeguards, moderate reliability issues
- **Action**: Implement recommended improvements

#### HIGH Risk (0.7-1.0)
- **Meaning**: Significant risks, immediate action required
- **Characteristics**: Missing critical safeguards, high failure probability
- **Action**: Address critical issues before production deployment

### Confidence Scoring

Each prediction includes a confidence score (0.0-1.0) based on:

- **Data Quality**: Completeness and structure of agent outputs
- **Sample Size**: Number of outputs analyzed (more data = higher confidence)
- **Pattern Clarity**: How clear the reliability patterns are
- **Framework Support**: How well the agent framework is understood

## Analysis Components

### 1. Framework Performance Analysis

Evaluates framework-specific patterns and optimization opportunities:

#### LangChain Analysis
- **Tool Chain Efficiency**: Analyzes tool call sequences and optimization opportunities
- **Intermediate Step Validation**: Checks for proper error handling in multi-step workflows
- **Memory Usage**: Evaluates conversation memory and context management

#### CrewAI Analysis
- **Crew Coordination**: Analyzes multi-agent coordination and task delegation
- **Task Completion Rates**: Measures individual agent and overall crew performance
- **Communication Patterns**: Evaluates inter-agent communication efficiency

#### OpenAI Analysis
- **Token Usage Optimization**: Identifies opportunities to reduce token consumption
- **Response Quality**: Analyzes response consistency and appropriateness
- **Rate Limiting**: Checks for rate limiting issues and optimization strategies

### 2. Tool Call Analysis

Comprehensive analysis of tool usage patterns:

```
Tool Call Summary:
├── Expected Tools: 3
├── Detected Tools: 2
├── Missing Tools: 1 (security_check)
├── Unexpected Tools: 0
└── Tool Call Accuracy: 67%
```

**Metrics Analyzed:**
- Tool call accuracy and completeness
- Error recovery patterns
- Timeout handling
- Tool chain efficiency

### 3. Performance Metrics

Key performance indicators for agent reliability:

- **Workflow Success Rate**: Percentage of successful completions
- **Tool Chain Reliability**: Efficiency of tool usage
- **Error Recovery Rate**: Ability to handle and recover from errors
- **Response Consistency**: Consistency across similar inputs

### 4. Cognitive Analysis (Optional)

Advanced cognitive pattern analysis when enabled:

- **Reasoning Patterns**: Analysis of agent reasoning quality
- **Decision Consistency**: Consistency in decision-making processes
- **Context Awareness**: Ability to maintain context across interactions

## Output and Results

### Console Output

The debug workflow provides rich, interactive console output:

```
🔍 Debug Dashboard - Agent Reliability Analysis
═══════════════════════════════════════════════

📊 RELIABILITY PREDICTION
┌─────────────────────────────────────────────┐
│ Risk Level: MEDIUM                          │
│ Combined Risk Score: 0.52                   │
│ Confidence: 0.78                            │
│                                             │
│ 🔴 Rule-Based: 0.45 (40% weight)           │
│ 🟡 LLM Analysis: 0.58 (60% weight)         │
└─────────────────────────────────────────────┘

🎯 TOP RISK FACTORS
• Missing input validation for financial data
• No timeout handling for external API calls
• Insufficient error logging for audit trails

💼 BUSINESS IMPACT
• Failure Prevention: 65%
• Estimated Cost Savings: $45,000/year
• Compliance Risk Reduction: Medium
```

### JSON Output

For programmatic processing:

```bash
arc-eval debug --input outputs.json --output-format json > results.json
```

```json
{
  "reliability_prediction": {
    "risk_level": "MEDIUM",
    "combined_risk_score": 0.52,
    "confidence": 0.78,
    "rule_based_component": {
      "risk_score": 0.45,
      "weight": 0.4,
      "violations": [...]
    },
    "llm_component": {
      "risk_score": 0.58,
      "weight": 0.6,
      "confidence": 0.82,
      "rationale": "..."
    }
  },
  "framework_analysis": {...},
  "performance_metrics": {...},
  "recommendations": [...]
}
```

## Command Options

### Basic Options

```bash
arc-eval debug --input <file> [options]
```

**Required:**
- `--input <file>`: Path to agent output file (JSON format)

**Optional:**
- `--framework <name>`: Specify framework (auto-detected if not provided)
- `--output-format <format>`: Output format (`console`, `json`, `html`)
- `--no-interactive`: Skip interactive menus (for CI/CD)
- `--verbose`: Show detailed technical output

### Framework-Specific Analysis

```bash
# Auto-detection (recommended)
arc-eval debug --input outputs.json

# Manual specification if needed
arc-eval debug --input outputs.json --framework langchain
```

**Framework Options:**
- `langchain`: LangChain framework analysis
- `langgraph`: LangGraph workflow analysis
- `crewai`: CrewAI multi-agent analysis
- `autogen`: AutoGen conversation analysis
- `openai`: OpenAI API analysis
- `anthropic`: Anthropic Claude analysis
- `generic`: Framework-agnostic analysis

## Integration Examples

### Development Workflow

```bash
# Quick debug during development
arc-eval debug --input dev_outputs.json

# Detailed analysis for troubleshooting
arc-eval debug --input outputs.json --verbose
```

### CI/CD Integration

```bash
# Automated reliability check
arc-eval debug --input outputs.json --no-interactive --output-format json

# With exit code checking
if ! arc-eval debug --input outputs.json --no-interactive; then
  echo "High reliability risk detected - blocking deployment"
  exit 1
fi
```

### Python SDK Integration

```python
from agent_eval.commands import DebugCommand
from pathlib import Path

# Programmatic debug analysis
debug_cmd = DebugCommand()
result = debug_cmd.execute(
    input_file=Path("outputs.json"),
    output_format="json",
    no_interactive=True
)

if result == 0:
    print("Debug analysis completed successfully")
else:
    print("Issues detected - check results")
```

## Best Practices

### 1. Start with Basic Analysis

Begin with basic debug analysis to understand your agent's baseline:

```bash
arc-eval debug --input outputs.json
```

### 2. Use Verbose Mode for Troubleshooting

When investigating specific issues, enable verbose output:

```bash
arc-eval debug --input outputs.json --verbose
```

### 3. Use Verbose Mode for Complex Issues

For recurring or complex issues, enable verbose output:

```bash
arc-eval debug --input outputs.json --verbose
```

### 4. Leverage Framework-Specific Analysis

Let ARC-Eval auto-detect your framework for optimized analysis:

```bash
# Auto-detection (recommended)
arc-eval debug --input outputs.json

# Manual specification if needed
arc-eval debug --input outputs.json --framework langchain
```

### 5. Export Results for Team Review

Generate reports for team analysis:

```bash
arc-eval debug --input outputs.json --output-format html > debug_report.html
```

## Common Issues and Solutions

### Low Confidence Scores

**Symptoms**: Confidence < 0.6
**Causes**: Insufficient data, unclear patterns, unknown framework
**Solutions**:
- Provide more agent outputs for analysis
- Ensure outputs include complete trace information
- Specify framework manually if auto-detection fails

### High Risk Predictions

**Symptoms**: Risk level = HIGH
**Causes**: Missing safeguards, poor error handling, security issues
**Solutions**:
- Review top risk factors in the output
- Implement recommended security controls
- Add proper error handling and validation

### Framework Detection Issues

**Symptoms**: Framework detected as "generic" when it shouldn't be
**Causes**: Non-standard output format, missing framework-specific fields
**Solutions**:
- Check output format against framework examples
- Include framework-specific metadata in outputs
- Use `--framework` option to specify manually

## Next Steps

After running debug analysis:

1. **Review Reliability Prediction**: Understand your agent's risk level
2. **Implement Recommendations**: Address identified issues
3. **Run Compliance Check**: Validate against domain-specific scenarios
4. **Track Improvements**: Use improve workflow to monitor progress

### Recommended Next Commands

```bash
# Run compliance check based on debug results
arc-eval compliance --domain finance --input outputs.json

# Complete analysis workflow
arc-eval analyze --input outputs.json --domain finance

# Generate improvement plan
arc-eval improve --from-evaluation latest
```

## Related Documentation

- [Compliance Workflow](compliance.md) - Validate against regulatory scenarios
- [Improve Workflow](improve.md) - Generate improvement recommendations
- [Prediction System](../prediction/) - Technical details of reliability prediction
- [Framework Integration](../frameworks/) - Framework-specific guides

# Workflows Guide

ARC-Eval provides three core workflows designed to cover the complete agent reliability lifecycle. Each workflow builds on the previous one, creating a comprehensive improvement loop.

## Workflow Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   DEBUG     │───▶│ COMPLIANCE  │───▶│   IMPROVE   │
│             │    │             │    │             │
│ Find what's │    │ Validate    │    │ Get better  │
│ broken      │    │ requirements│    │ over time   │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                                      │
       │                                      │
       └──────────────────────────────────────┘
                Continuous Improvement Loop
```

## 1. Debug Workflow

**Purpose**: "Why is my agent failing?"

The debug workflow provides comprehensive reliability analysis with predictive scoring to identify issues before they impact production.

### Key Features

- **Reliability Prediction**: Risk assessment with LOW/MEDIUM/HIGH scoring
- **Framework Analysis**: Automatic detection and optimization recommendations
- **Performance Metrics**: Tool usage efficiency and error patterns
- **Root Cause Analysis**: Deep dive into failure patterns

### When to Use

- Agent producing unexpected results
- Need to understand failure patterns
- Want predictive reliability assessment
- Preparing for production deployment

### Example Usage

```bash
# Basic debug analysis
arc-eval debug --input agent_outputs.json

# Debug with pattern analysis
arc-eval debug --input outputs.json --pattern-analysis --root-cause

# Framework-specific debug
arc-eval debug --input outputs.json --framework langchain
```

### Output

- Reliability prediction with confidence scores
- Framework-specific optimization recommendations
- Performance metrics and bottleneck analysis
- Actionable insights and next steps

[→ Detailed Debug Guide](debug.md)

## 2. Compliance Workflow

**Purpose**: "Does my agent meet requirements?"

The compliance workflow tests agents against 378 enterprise-grade scenarios across finance, security, and ML domains to ensure regulatory compliance.

### Key Features

- **Domain-Specific Testing**: 378 scenarios across finance (110), security (120), ML (148)
- **Regulatory Compliance**: SOX, OWASP, GDPR, EU AI Act validation
- **Agent-as-Judge Evaluation**: LLM-powered scenario assessment
- **Audit-Ready Reports**: Professional compliance documentation

### When to Use

- Preparing for production deployment
- Need regulatory compliance validation
- Want comprehensive scenario testing
- Creating audit documentation

### Available Domains

#### Finance (110 scenarios)
- **Regulations**: SOX, KYC/AML, PCI-DSS, GDPR
- **Focus**: Financial reporting, fraud detection, transaction processing
- **Example**: `arc-eval compliance --domain finance --input outputs.json`

#### Security (120 scenarios)
- **Regulations**: OWASP LLM Top 10, NIST AI RMF, ISO 27001
- **Focus**: Prompt injection, data leakage, model theft prevention
- **Example**: `arc-eval compliance --domain security --input outputs.json`

#### ML/AI (148 scenarios)
- **Regulations**: EU AI Act, IEEE P7000, Model Cards
- **Focus**: Bias detection, fairness monitoring, explainability
- **Example**: `arc-eval compliance --domain ml --input outputs.json`

### Example Usage

```bash
# Quick demo with sample data
arc-eval compliance --domain finance --quick-start

# Full compliance check
arc-eval compliance --domain security --input agent_outputs.json

# Export compliance report
arc-eval compliance --domain ml --input outputs.json --export pdf
```

[→ Detailed Compliance Guide](compliance.md)

## 3. Improve Workflow

**Purpose**: "How do I make my agent better?"

The improve workflow generates specific recommendations based on evaluation results and tracks progress over time.

### Key Features

- **Specific Recommendations**: Actionable fixes based on analysis
- **Progress Tracking**: Monitor improvement over time
- **Pattern Learning**: Adapt recommendations based on agent evolution
- **Configuration Optimization**: Framework-specific tuning suggestions

### When to Use

- Have evaluation results to act on
- Need specific improvement recommendations
- Want to track progress over time
- Implementing continuous improvement

### Example Usage

```bash
# Improve based on latest evaluation
arc-eval improve --from-evaluation latest

# Focus on specific area
arc-eval improve --from-evaluation latest --focus reliability

# Export improvement plan
arc-eval improve --from-evaluation results.json --export pdf
```

[→ Detailed Improve Guide](improve.md)

## Workflow Combinations

### Complete Analysis Workflow

Run all three workflows in sequence with guided transitions:

```bash
arc-eval analyze --input outputs.json --domain finance
```

This command:
1. Runs debug analysis
2. Performs compliance checking
3. Generates improvement recommendations
4. Provides interactive menus for next steps

### Automated CI/CD Workflow

For continuous integration and deployment:

```bash
# Automated reliability check
arc-eval debug --input outputs.json --no-interactive

# Automated compliance validation
arc-eval compliance --domain finance --input outputs.json --no-interactive

# Combined automated analysis
arc-eval analyze --input outputs.json --domain security --no-interactive
```

## Workflow State Management

ARC-Eval maintains workflow state to enable seamless transitions between workflows:

### State Tracking

```json
{
  "workflow_cycle": {
    "debug": {
      "completed": true,
      "timestamp": "2024-01-15T10:30:00Z",
      "input_file": "agent_outputs.json",
      "risk_level": "MEDIUM"
    },
    "compliance": {
      "completed": false,
      "recommended_domain": "finance"
    },
    "improve": {
      "completed": false
    }
  }
}
```

### Guided Transitions

After each workflow, ARC-Eval provides intelligent next step recommendations:

```
🎯 RECOMMENDED NEXT STEP:
arc-eval compliance --domain finance --input agent_outputs.json

This will test your agent against 110 finance compliance scenarios
```

## Performance Optimization

### Scenario Targeting

Include `scenario_id` in agent outputs to limit evaluation scope:

```json
{
  "output": "Transaction approved",
  "scenario_id": "fin_001"
}
```

Benefits:
- 10x faster evaluation
- Focused testing on relevant scenarios
- Reduced API costs

### Batch Processing

Automatically enabled for 5+ scenarios:
- 50% cost savings through batch API usage
- Optimized for large-scale evaluations
- Maintains evaluation quality

### Interactive vs Non-Interactive

#### Interactive Mode (Default)
- Rich CLI interface with progress indicators
- Guided menus and recommendations
- Real-time feedback and results

#### Non-Interactive Mode (CI/CD)
- Streamlined output for automation
- JSON/structured output formats
- Exit codes for pipeline integration

```bash
# Interactive (default)
arc-eval debug --input outputs.json

# Non-interactive (CI/CD)
arc-eval debug --input outputs.json --no-interactive --output-format json
```

## Integration Patterns

### Development Workflow

```bash
# 1. During development - quick debug
arc-eval debug --input dev_outputs.json

# 2. Pre-commit - compliance check
arc-eval compliance --domain finance --input outputs.json --no-interactive

# 3. Post-deployment - improvement tracking
arc-eval improve --from-evaluation latest
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Agent Reliability Check
  run: |
    arc-eval analyze --input outputs.json --domain finance --no-interactive
    if [ $? -ne 0 ]; then
      echo "Agent reliability check failed"
      exit 1
    fi
```

### Monitoring and Alerting

```bash
# Production monitoring
arc-eval debug --input production_outputs.json --no-interactive --export json

# Alert on high risk
if [ "$(jq -r '.risk_level' results.json)" = "HIGH" ]; then
  send_alert "High risk agent detected"
fi
```

## Best Practices

### 1. Start with Debug

Always begin with the debug workflow to understand your agent's baseline reliability:

```bash
arc-eval debug --input outputs.json --verbose
```

### 2. Choose Appropriate Domain

Select the compliance domain that matches your use case:
- **Finance**: Financial services, banking, trading
- **Security**: Cybersecurity, threat detection, access control
- **ML**: Machine learning, AI governance, bias detection

### 3. Use Scenario Targeting

For faster evaluation, target specific scenarios:

```bash
arc-eval compliance --domain finance --scenarios fin_001,fin_002,fin_003
```

### 4. Export Reports

Generate professional reports for stakeholders:

```bash
arc-eval compliance --domain finance --input outputs.json --export pdf
```

### 5. Track Progress

Use the improve workflow to monitor progress over time:

```bash
arc-eval improve --from-evaluation latest --focus reliability
```

## Next Steps

- [Debug Workflow](debug.md) - Detailed debug workflow guide
- [Compliance Workflow](compliance.md) - Comprehensive compliance testing
- [Improve Workflow](improve.md) - Continuous improvement strategies
- [Framework Integration](../frameworks/) - Framework-specific guides

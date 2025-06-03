# Workflows Guide - Predictive Reliability Platform

ARC-Eval provides three core workflows that form a **predictive reliability platform** for agent development. Each workflow uses hybrid prediction (40% rules + 60% LLM) to provide actionable insights and prevent failures before they impact production.

## The Predictive Reliability Loop

```
🔍 DEBUG → 📋 COMPLIANCE → 📈 IMPROVE → 🔄 REPEAT
   ↓            ↓             ↓
Predict      Validate      Optimize
Failures     Requirements  Performance
```

This continuous loop enables **predictive failure prevention** rather than reactive debugging, reducing debugging time from 4+ hours to 5 minutes and preventing $250K+ compliance violations.

> **📖 Complete Guide**: See [Core Product Loops](../core-loops.md) for detailed step-by-step instructions on implementing **The Arc Loop** and **Data Flywheel** in your development workflow.

## Core Value Proposition

**Traditional Approach**: React to failures after they occur
**ARC-Eval Approach**: Predict and prevent failures before deployment

- **85%+ Prediction Accuracy**: Identify reliability issues before production
- **Cost Optimization**: Reduce debugging costs and compliance violations
- **Framework-Agnostic**: Works with 10+ agent frameworks
- **Enterprise-Ready**: 378 scenarios across finance, security, ML domains

## 1. Debug Workflow - **Predictive Failure Analysis**

**Question**: "Why is my agent failing?"
**Prediction Focus**: Risk assessment and failure pattern recognition

### Key Features

- **Reliability Prediction**: Hybrid rules + LLM analysis with confidence scoring
- **Risk Levels**: LOW (0.0-0.4), MEDIUM (0.4-0.7), HIGH (0.7-1.0)
- **Framework Intelligence**: Auto-detection and optimization for 10+ frameworks
- **Business Impact**: Cost savings estimation and failure prevention metrics

### Predictive Capabilities

- Identifies failure patterns before they occur in production
- Predicts reliability issues with 85%+ confidence
- Estimates business impact and cost savings potential

### When to Use

- Before deploying agents to production
- When investigating reliability concerns
- For continuous monitoring and optimization
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

## 2. Compliance Workflow - **Predictive Regulatory Assessment**

**Question**: "Does my agent meet requirements?"
**Prediction Focus**: Compliance risk scoring and regulatory gap analysis

### Key Features

- **378 Enterprise Scenarios**: Finance (110), Security (120), ML (148)
- **Regulatory Mapping**: SOX, GDPR, OWASP LLM, EU AI Act
- **Predictive Scoring**: Compliance risk assessment before deployment
- **Audit-Ready Reports**: Professional compliance documentation

### Predictive Capabilities

- Predicts compliance violations before regulatory review
- Estimates regulatory fine risk and audit readiness
- Provides early warning for compliance gaps

### When to Use

- Before production deployment (prevent violations)
- Regulatory compliance validation
- Audit preparation and readiness assessment
- Continuous compliance monitoring

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

## 3. Improve Workflow - **Predictive Optimization Planning**

**Question**: "How do I make my agent better?"
**Prediction Focus**: Impact prediction and progress tracking

### Key Features

- **Impact Prediction**: Estimates improvement outcomes before implementation
- **Framework-Specific Fixes**: Tailored solutions with code examples
- **Progress Tracking**: Trend analysis and ROI calculation
- **Adaptive Learning**: Recommendations improve with usage

### Predictive Capabilities

- Predicts improvement impact and implementation effort
- Forecasts time to compliance and reliability targets
- Optimizes improvement prioritization for maximum ROI

### When to Use

- After debug or compliance evaluation
- Planning improvement roadmaps
- Tracking progress over time
- Optimizing development resources

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

### Complete Analysis Workflow (Recommended)

**The `analyze` command is the recommended entry point** that executes the entire Arc Loop automatically:

```bash
arc-eval analyze --input outputs.json --domain finance
```

This unified command:
1. **🔍 Debug Analysis**: Reliability prediction and failure pattern detection
2. **✅ Compliance Check**: Tests against 378 enterprise scenarios
3. **📈 Improvement Plan**: Generates actionable fixes and recommendations
4. **🎯 Unified Menu**: Provides guided next steps for continuous improvement

**Key Benefits**:
- **Single Command**: Complete workflow in one execution
- **Guided Experience**: Interactive menus guide you through next steps
- **Automation Ready**: Use `--no-interactive` for CI/CD pipelines

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

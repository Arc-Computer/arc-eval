# Compliance Workflow

The compliance workflow answers the question: **"Does my agent meet requirements?"**

This workflow validates agents against 378 enterprise-grade scenarios across finance, security, and ML domains, providing predictive compliance assessment and regulatory validation.

## Overview

The compliance workflow combines comprehensive scenario testing with predictive analysis to ensure your agents meet regulatory requirements:

1. **Predictive Compliance Assessment**: Risk scoring before deployment
2. **Domain-Specific Testing**: 378 scenarios across finance (110), security (120), ML (148)
3. **Regulatory Validation**: SOX, OWASP, GDPR, EU AI Act compliance
4. **Audit-Ready Reports**: Professional compliance documentation

## Quick Start

### Instant Demo (No Setup Required)

```bash
# Try with built-in sample data
arc-eval compliance --domain finance --quick-start
```

This will:
- Run against 110 finance compliance scenarios
- Generate predictive compliance scores
- Show regulatory gap analysis
- Provide audit-ready summary

### With Your Agent Data

```bash
# Full compliance evaluation
arc-eval compliance --domain finance --input agent_outputs.json
```

## Prediction-Focused Features

### Compliance Risk Prediction

The compliance workflow provides predictive scoring to identify regulatory risks before deployment:

```
📊 COMPLIANCE PREDICTION
┌─────────────────────────────────────────────┐
│ Compliance Risk: MEDIUM                     │
│ Predicted Pass Rate: 67%                    │
│ Regulatory Risk Score: 0.45                 │
│ Confidence: 0.82                            │
│                                             │
│ 🔴 Critical Gaps: 3                        │
│ 🟡 High Risk: 8                            │
│ 🟢 Low Risk: 15                            │
└─────────────────────────────────────────────┘
```

### Regulatory Framework Mapping

Automatic mapping to specific regulatory requirements:

- **SOX Compliance**: Financial reporting accuracy, audit trails
- **GDPR/CCPA**: Data privacy, consent management, PII protection
- **OWASP LLM Top 10**: Security vulnerabilities, prompt injection
- **EU AI Act**: High-risk AI system requirements, bias detection

## Domain-Specific Testing

### Finance Domain (110 scenarios)

**Regulatory Focus**: SOX, KYC/AML, PCI-DSS, GDPR
**Use Cases**: Financial reporting, fraud detection, transaction processing

```bash
arc-eval compliance --domain finance --input outputs.json
```

**Key Scenarios**:
- **fin_001**: PII exposure in financial responses
- **fin_007**: AML violation detection
- **fin_023**: SOX audit trail compliance
- **fin_045**: KYC identity verification
- **fin_089**: Rate disclosure requirements

### Security Domain (120 scenarios)

**Regulatory Focus**: OWASP LLM Top 10, NIST AI RMF, ISO 27001
**Use Cases**: Cybersecurity, threat detection, access control

```bash
arc-eval compliance --domain security --input outputs.json
```

**Key Scenarios**:
- **sec_001**: Prompt injection resistance
- **sec_015**: Data leakage prevention
- **sec_032**: Model theft protection
- **sec_067**: Access control validation
- **sec_098**: Incident response procedures

### ML/AI Domain (148 scenarios)

**Regulatory Focus**: EU AI Act, IEEE P7000, Model Cards
**Use Cases**: Bias detection, fairness monitoring, explainability

```bash
arc-eval compliance --domain ml --input outputs.json
```

**Key Scenarios**:
- **ml_001**: Demographic bias detection
- **ml_024**: Fairness across protected groups
- **ml_056**: Model explainability requirements
- **ml_089**: High-risk AI system compliance
- **ml_134**: Algorithmic transparency

## Agent-as-Judge Evaluation

### Enhanced Scenario Assessment

The compliance workflow uses LLM-powered evaluation for nuanced compliance assessment:

```bash
# Enable Agent-as-Judge (default for full evaluation)
arc-eval compliance --domain finance --input outputs.json

# High accuracy mode with premium models
arc-eval compliance --domain finance --input outputs.json --high
```

### Provider Selection

Choose your preferred AI provider for evaluation:

```bash
# OpenAI (default)
arc-eval compliance --domain finance --input outputs.json --provider openai

# Anthropic Claude
arc-eval compliance --domain finance --input outputs.json --provider anthropic

# Google Gemini
arc-eval compliance --domain finance --input outputs.json --provider google
```

## Output and Results

### Interactive Dashboard

```
✅ Compliance Evaluation - FINANCE
════════════════════════════════════════

📊 OVERALL RESULTS
Pass Rate: 67% (74/110 scenarios)
Critical Failures: 3
High Risk: 8
Medium Risk: 15

🔴 CRITICAL COMPLIANCE GAPS
• fin_001: PII Exposure - SSN in response
• fin_007: AML Violation - Unreported transaction
• fin_023: SOX Non-compliance - Missing audit trail

📋 REGULATORY BREAKDOWN
• SOX: 45% compliance (audit logging incomplete)
• PCI-DSS: 72% compliance (card data exposed)
• GDPR: 83% compliance (consent tracking issues)
• KYC/AML: 58% compliance (identity verification gaps)

💼 BUSINESS IMPACT
• Estimated Compliance Cost: $125,000/year
• Regulatory Fine Risk: HIGH
• Audit Readiness: 67%
```

### Audit-Ready Reports

```bash
# Generate PDF compliance report
arc-eval compliance --domain finance --input outputs.json --export pdf

# Export structured data
arc-eval compliance --domain finance --input outputs.json --export json
```

**PDF Report Includes**:
- Executive summary with risk assessment
- Detailed scenario results with evidence
- Regulatory framework mapping
- Remediation recommendations
- Audit trail and methodology

## Command Options

### Basic Usage

```bash
arc-eval compliance --domain <domain> [options]
```

**Required:**
- `--domain <domain>`: Evaluation domain (`finance`, `security`, `ml`)

**Input Options:**
- `--input <file>`: Agent output file (required unless using `--quick-start`)
- `--folder-scan`: Auto-find JSON files in current directory
- `--quick-start`: Use built-in sample data for instant demo

**Evaluation Options:**
- `--high`: High accuracy mode (slower, premium models)
- `--provider <name>`: AI provider (`openai`, `anthropic`, `google`)
- `--no-interactive`: Skip interactive menus (for CI/CD)
- `--verbose`: Show detailed technical output

**Export Options:**
- `--export <format>`: Export format (`pdf`, `csv`, `json`)
- `--no-export`: Skip automatic PDF generation

## Integration Examples

### Development Workflow

```bash
# Quick compliance check during development
arc-eval compliance --domain finance --quick-start

# Full evaluation with your data
arc-eval compliance --domain finance --input dev_outputs.json
```

### CI/CD Integration

```bash
# Automated compliance validation
arc-eval compliance --domain finance --input outputs.json --no-interactive

# With exit code checking
if ! arc-eval compliance --domain security --input outputs.json --no-interactive; then
  echo "Compliance violations detected - blocking deployment"
  exit 1
fi
```

### Enterprise Monitoring

```python
import subprocess
import json

# Automated compliance monitoring
def monitor_agent_compliance(domain, outputs_file):
    result = subprocess.run([
        "arc-eval", "compliance",
        "--domain", domain,
        "--input", outputs_file,
        "--export", "json",
        "--no-interactive"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        compliance_data = json.loads(result.stdout)
        
        # Alert on critical failures
        if compliance_data.get("critical_failures", 0) > 0:
            send_alert(f"Critical compliance violations in {domain}")
        
        return compliance_data
    else:
        raise Exception(f"Compliance check failed: {result.stderr}")
```

## Best Practices

### 1. Start with Quick-Start

Begin with the demo to understand compliance requirements:

```bash
arc-eval compliance --domain finance --quick-start
```

### 2. Choose Appropriate Domain

Select the domain that matches your use case:
- **Finance**: Banking, payments, financial services
- **Security**: Cybersecurity, threat detection, access control
- **ML**: Machine learning, AI governance, bias detection

### 3. Use High Accuracy for Production

Enable high accuracy mode for production deployments:

```bash
arc-eval compliance --domain finance --input outputs.json --high
```

### 4. Generate Audit Reports

Always export compliance reports for audit trails:

```bash
arc-eval compliance --domain finance --input outputs.json --export pdf
```

### 5. Monitor Critical Failures

Focus on critical compliance gaps that pose regulatory risk:

```bash
# Check exit code for critical failures
arc-eval compliance --domain finance --input outputs.json --no-interactive
echo "Exit code: $?"
```

## Next Steps

After running compliance evaluation:

1. **Review Critical Gaps**: Address high-risk compliance violations
2. **Generate Improvement Plan**: Use improve workflow for specific fixes
3. **Track Progress**: Re-run compliance after implementing changes
4. **Automate Monitoring**: Integrate into CI/CD for continuous compliance

### Recommended Next Commands

```bash
# Generate improvement plan based on compliance results
arc-eval improve --from-evaluation latest

# Complete analysis workflow
arc-eval analyze --input outputs.json --domain finance

# Track improvement progress
arc-eval compliance --domain finance --input improved_outputs.json
```

## Related Documentation

- [Debug Workflow](debug.md) - Identify reliability issues before compliance
- [Improve Workflow](improve.md) - Generate specific compliance improvements
- [Prediction System](../prediction/) - Technical details of compliance prediction
- [Enterprise Integration](../enterprise/) - CI/CD and monitoring integration

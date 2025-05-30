# Complete Evaluation Datasets

The full evaluation scenarios are available in the `/agent_eval/domains/` directory:

- `finance.yaml` - 110 scenarios for financial compliance
- `security.yaml` - 120 scenarios for security vulnerabilities  
- `ml.yaml` - 148 scenarios for ML/AI governance

## Explore the Scenarios

```bash
# View all finance scenarios
cat ../../agent_eval/domains/finance.yaml

# View security scenarios  
cat ../../agent_eval/domains/security.yaml

# View ML scenarios including MCP attacks
cat ../../agent_eval/domains/ml.yaml
```

## Understanding the Format

Each YAML file contains:
- Scenario definitions with IDs, names, and descriptions
- Compliance framework mappings
- Severity levels (critical, high, medium, low)
- Failure indicators to check for
- Remediation guidance

## Using in Your Own Projects

These scenarios are open source! You can:
- Use them as templates for your own evaluations
- Extend them with domain-specific scenarios
- Contribute new scenarios via pull requests
- Build your own evaluation tools using this data

## Quick Stats

- **Total Scenarios**: 378
- **Finance**: 110 (SOX, KYC, AML, PCI-DSS, GDPR)
- **Security**: 120 (OWASP Top 10, prompt injection, data leakage)
- **ML**: 148 (bias detection, MCP attacks, model governance)

The real power comes from using these scenarios in the improvement loop that ARC-Eval provides.
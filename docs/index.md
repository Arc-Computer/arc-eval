# ARC-Eval Documentation

**Agentic Workflow Reliability Platform - Predict failures before they happen**

ARC-Eval is a CLI-native platform that helps developers debug, validate, and improve AI agents through predictive reliability analysis. Built for developers who need to ensure their agents work reliably in production.

## Quick Navigation

### 🚀 Getting Started
- [🔄 **Core Product Loops**](core-loops.md) - **The Arc Loop & Data Flywheel** (Essential!)
- [Installation & Quick Start](quickstart.md) - Get running in 5 minutes
- [Core Concepts](concepts.md) - Understanding reliability prediction
- [CLI Reference](cli-reference.md) - Complete command documentation

### 🔧 Developer Guides  
- [Workflows](workflows/) - Debug, compliance, and improvement workflows
- [Prediction System](prediction/) - Hybrid reliability prediction framework
- [Framework Integration](frameworks/) - Support for 10+ agent frameworks
- [API Reference](api/) - Python SDK and programmatic usage

### 🏢 Enterprise Features
- [Compliance](enterprise/compliance.md) - Regulatory framework support
- [CI/CD Integration](enterprise/integration.md) - Pipeline integration guides
- [Monitoring](enterprise/monitoring.md) - Production reliability tracking

### 📚 Reference
- [Architecture](reference/architecture.md) - System design and components
- [Configuration](reference/configuration.md) - Advanced configuration options
- [Troubleshooting](reference/troubleshooting.md) - Common issues and solutions

## What Makes ARC-Eval Different

### Predictive Reliability
Unlike traditional evaluation tools that only report what happened, ARC-Eval predicts what will happen:
- **Risk Assessment**: LOW/MEDIUM/HIGH reliability predictions with confidence scores
- **Failure Prevention**: Identify potential failures before they occur in production
- **Business Impact**: Quantified metrics on failure prevention and cost savings

### Agent-Agnostic Design
Works with any agent framework without code changes:
- **Framework Detection**: Automatic detection of LangChain, CrewAI, OpenAI, and more
- **Unified Interface**: Consistent evaluation regardless of underlying framework
- **Easy Migration**: Switch frameworks without changing evaluation workflows

### Enterprise-Ready
Built for production environments with regulatory requirements:
- **378 Compliance Scenarios**: Finance (SOX, KYC), Security (OWASP), ML (Bias Detection)
- **Audit Trails**: Comprehensive logging for compliance and debugging
- **CI/CD Integration**: Automated reliability gates in deployment pipelines

## Core Workflows

### Complete Analysis (Recommended Entry Point)
```bash
arc-eval analyze --input agent_outputs.json --domain finance
```
- **Unified workflow**: Chains debug → compliance → improve automatically
- **Guided experience**: Interactive menus for next steps
- **Single command**: Complete Arc Loop execution

### 1. Debug: "Why is my agent failing?"
```bash
arc-eval debug --input agent_outputs.json
```
- Comprehensive reliability analysis with predictive scoring
- Framework-specific optimization recommendations
- Root cause analysis with actionable insights

### 2. Compliance: "Does it meet requirements?"
```bash
arc-eval compliance --domain finance --input agent_outputs.json
```
- Test against 378 enterprise-grade scenarios
- Regulatory compliance validation (SOX, OWASP, GDPR)
- Automated compliance reporting

### 3. Improve: "How do I make it better?"
```bash
arc-eval improve --from-evaluation latest
```
- Specific configuration improvements based on analysis
- Performance optimization recommendations
- Continuous learning from failure patterns

## Architecture Overview

ARC-Eval is built with a modular architecture designed for extensibility and reliability:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Core Engine     │    │  Prediction     │
│                 │────│                  │────│  System         │
│ • Commands      │    │ • Evaluation     │    │ • Hybrid Rules  │
│ • Interactive   │    │ • Framework      │    │ • LLM Analysis  │
│ • Streaming     │    │ • Parsing        │    │ • Risk Scoring  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Components │    │  Domain Scenarios│    │  Export &       │
│                 │    │                  │    │  Reporting      │
│ • Dashboards    │    │ • Finance (110)  │    │ • PDF Reports   │
│ • Progress      │    │ • Security (120) │    │ • JSON/CSV      │
│ • Menus         │    │ • ML/AI (148)    │    │ • Audit Trails  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

- **Core Engine** (`agent_eval.core`): Evaluation orchestration and framework detection
- **Prediction System** (`agent_eval.prediction`): Hybrid reliability prediction with rules + LLM
- **Agent-as-Judge** (`agent_eval.evaluation.judges`): LLM-powered evaluation framework
- **CLI Interface** (`agent_eval.cli`): Command-line interface with rich interactive features
- **Domain Scenarios** (`agent_eval.domains`): 378 compliance scenarios across finance, security, ML

## Getting Started

The fastest way to get started is with our quick-start demo:

```bash
# Install ARC-Eval
pip install arc-eval

# Try it instantly with sample data
arc-eval compliance --domain finance --quick-start

# Or analyze your own agent outputs
arc-eval debug --input your_agent_outputs.json
```

For detailed installation and setup instructions, see the [Quick Start Guide](quickstart.md).

## Community and Support

- **Documentation**: Complete guides and API reference in this documentation site
- **Examples**: Comprehensive examples in the [`examples/`](../examples/) directory
- **Issues**: Report bugs and request features on GitHub
- **Contributing**: See [Contributing Guide](../CONTRIBUTING.md) for development setup

## License

ARC-Eval is open source software licensed under the MIT License. See [LICENSE](../LICENSE) for details.

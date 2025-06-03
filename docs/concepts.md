# Core Concepts

Understanding the key concepts behind ARC-Eval's reliability prediction and evaluation framework.

## Reliability Prediction

### What is Reliability Prediction?

Traditional evaluation tools tell you what happened after your agent fails. ARC-Eval predicts what will happen before your agent fails, allowing you to prevent issues proactively.

### Hybrid Prediction System

ARC-Eval uses a hybrid approach combining deterministic rules with LLM-powered pattern recognition:

```
Reliability Prediction = (40% Rules + 60% LLM Analysis)
```

#### Rule-Based Component (40% weight)
- **Deterministic compliance checks** for regulatory requirements
- **PII Protection**: GDPR Article 25 privacy by design
- **Security Controls**: OWASP compliance, input validation
- **Audit Requirements**: SOX logging, transaction limits
- **Data Handling**: PCI DSS encryption, data masking

#### LLM Component (60% weight)
- **Pattern Recognition**: Complex failure mode detection
- **Framework Analysis**: Framework-specific reliability patterns
- **Risk Assessment**: Confidence-weighted probability scoring
- **Rationale Generation**: Explainable prediction reasoning

### Risk Levels

Predictions are categorized into three risk levels:

- **LOW** (0.0-0.4): High reliability, minimal intervention needed
- **MEDIUM** (0.4-0.7): Some risks identified, improvements recommended
- **HIGH** (0.7-1.0): Significant risks, immediate action required

### Confidence Scoring

Each prediction includes a confidence score (0.0-1.0) based on:
- **Data Quality**: Completeness and structure of agent outputs
- **Sample Size**: Number of outputs analyzed
- **Pattern Clarity**: How clear the reliability patterns are
- **Framework Support**: How well the agent framework is understood

## Agent-as-a-Judge Framework

### Overview

ARC-Eval implements the Agent-as-a-Judge methodology, using LLMs as domain-specific evaluators to assess agent outputs against compliance scenarios.

### Evaluation Modes

#### Fast Track (≤50 scenarios)
- Individual API calls with real-time progress
- Immediate feedback and results
- Interactive evaluation experience

#### Batch Track (100+ scenarios)
- Anthropic Message Batches API
- 50% cost savings for large evaluations
- Optimized for CI/CD and automated testing

### Domain-Specific Judges

- **Finance Judge**: SOX compliance, KYC/AML, PCI-DSS validation
- **Security Judge**: OWASP Top 10, prompt injection, data leakage
- **ML Judge**: Bias detection, fairness monitoring, model governance

## Framework Detection

### Automatic Detection

ARC-Eval automatically detects the agent framework from output structure:

```python
# LangChain detection
if "intermediate_steps" in output:
    framework = "langchain"

# CrewAI detection  
if "crew_output" in output or "tasks_output" in output:
    framework = "crewai"

# OpenAI detection
if "choices" in output and "message" in output["choices"][0]:
    framework = "openai"
```

### Supported Frameworks

1. **LangChain**: Full trace analysis with intermediate steps
2. **LangGraph**: Graph-based workflow evaluation
3. **CrewAI**: Multi-agent crew coordination analysis
4. **AutoGen**: Conversation-based agent evaluation
5. **OpenAI**: Direct API response evaluation
6. **Anthropic**: Claude API response evaluation
7. **Google**: Gemini API response evaluation
8. **Generic**: Custom agent framework support
9. **Agno**: Emerging framework support

### Framework-Specific Analysis

Each framework gets specialized analysis:

- **LangChain**: Tool chaining efficiency, intermediate step validation
- **CrewAI**: Crew coordination, task delegation patterns
- **OpenAI**: Token usage optimization, response quality
- **Generic**: Basic reliability patterns and error detection

## Evaluation Domains

### Finance Domain (110 scenarios)

**Regulatory Frameworks:**
- SOX (Sarbanes-Oxley Act)
- KYC/AML (Know Your Customer/Anti-Money Laundering)
- PCI-DSS (Payment Card Industry Data Security Standard)
- GDPR (General Data Protection Regulation)
- EU AI Act compliance

**Key Scenarios:**
- Earnings manipulation detection
- Synthetic identity identification
- Transaction approval workflows
- PII protection validation
- Audit trail compliance

### Security Domain (120 scenarios)

**Regulatory Frameworks:**
- OWASP LLM Top 10
- NIST AI Risk Management Framework
- ISO 27001 security controls

**Key Scenarios:**
- Prompt injection attacks
- Training data poisoning
- Model theft attempts
- Data leakage prevention
- Access control validation

### ML/AI Domain (148 scenarios)

**Regulatory Frameworks:**
- EU AI Act high-risk system compliance
- IEEE P7000 series standards
- Model Cards documentation requirements

**Key Scenarios:**
- Bias detection and mitigation
- Fairness monitoring across demographics
- Explainability requirements
- Model governance compliance
- Algorithmic accountability

## Workflow States

### Debug Workflow

1. **Input Analysis**: Parse and normalize agent outputs
2. **Framework Detection**: Identify agent framework automatically
3. **Reliability Prediction**: Generate risk assessment with confidence
4. **Performance Analysis**: Evaluate tool usage and error patterns
5. **Insight Generation**: Provide actionable recommendations

### Compliance Workflow

1. **Domain Selection**: Choose evaluation domain (finance/security/ml)
2. **Scenario Loading**: Load relevant compliance scenarios
3. **Agent-as-Judge Evaluation**: Run scenarios against agent outputs
4. **Violation Detection**: Identify compliance failures with evidence
5. **Report Generation**: Create audit-ready compliance reports

### Improve Workflow

1. **Analysis Review**: Load previous evaluation results
2. **Pattern Recognition**: Identify recurring failure patterns
3. **Fix Generation**: Generate specific improvement recommendations
4. **Progress Tracking**: Monitor improvement over time
5. **Curriculum Learning**: Adapt scenarios based on agent evolution

## Data Flow

### Input Processing

```
Agent Outputs → Framework Detection → Normalization → Evaluation
```

1. **Raw Outputs**: JSON files from various agent frameworks
2. **Framework Detection**: Automatic identification of output structure
3. **Normalization**: Convert to standard `AgentOutput` format
4. **Evaluation**: Run through appropriate evaluation pipeline

### Prediction Pipeline

```
Normalized Outputs → Rules Engine → LLM Analysis → Risk Scoring → Business Impact
```

1. **Rules Engine**: Deterministic compliance checks
2. **LLM Analysis**: Pattern recognition and risk assessment
3. **Risk Scoring**: Weighted combination of rule and LLM scores
4. **Business Impact**: Calculate failure prevention and cost metrics

### Output Generation

```
Evaluation Results → Dashboard Rendering → Report Export → Next Steps
```

1. **Dashboard Rendering**: Rich CLI interface with progress indicators
2. **Report Export**: PDF, JSON, CSV formats for different audiences
3. **Next Steps**: Guided recommendations for workflow continuation

## Performance Optimization

### Scenario Targeting

Include `scenario_id` in agent outputs to limit evaluation scope:

```json
{
  "output": "Transaction approved",
  "scenario_id": "fin_001"
}
```

This provides 10x faster evaluation by testing only relevant scenarios.

### Batch Processing

Automatically enabled for 5+ scenarios:
- 50% cost savings through batch API usage
- Optimized for CI/CD pipeline integration
- Maintains evaluation quality while reducing costs

### Caching

- **Compiled Patterns**: Pre-compiled regex for performance
- **Framework Detection**: Cached detection results
- **Scenario Loading**: Cached domain scenarios
- **API Responses**: Optional caching for development

## Integration Patterns

### CLI Integration

```bash
# Single workflow
arc-eval debug --input outputs.json

# Chained workflows  
arc-eval analyze --input outputs.json --domain finance

# Automated workflows
arc-eval compliance --domain finance --input outputs.json --no-interactive
```

### Python SDK Integration

```python
from agent_eval.core import EvaluationEngine
from agent_eval.prediction import HybridReliabilityPredictor

# Direct evaluation
engine = EvaluationEngine(domain="finance")
results = engine.evaluate(agent_outputs)

# Reliability prediction
predictor = HybridReliabilityPredictor()
prediction = predictor.predict_reliability(analysis, config)
```

### CI/CD Integration

```yaml
- name: Agent Reliability Check
  run: |
    arc-eval compliance --domain finance --input outputs.json --no-interactive
    if [ $? -ne 0 ]; then exit 1; fi
```

## Next Steps

- [Workflows Guide](workflows/) - Deep dive into each workflow
- [Prediction System](prediction/) - Technical details of reliability prediction
- [Framework Integration](frameworks/) - Framework-specific guides
- [API Reference](api/) - Complete SDK documentation

# Prediction System

ARC-Eval's hybrid reliability prediction system combines deterministic compliance rules with LLM-powered pattern recognition to predict agent failures before they happen.

## Overview

Traditional evaluation tools tell you what happened after your agent fails. ARC-Eval's prediction system tells you what will happen before your agent fails, enabling proactive reliability management.

### Hybrid Architecture

```
Reliability Prediction = (40% Rules + 60% LLM Analysis)
```

The system combines two complementary approaches:

1. **Rule-Based Component (40% weight)**: Deterministic compliance checks for regulatory requirements
2. **LLM Component (60% weight)**: Pattern recognition for complex reliability assessment

This hybrid approach provides both the reliability of deterministic rules and the intelligence of machine learning pattern recognition.

## System Components

### 1. Compliance Rule Engine

Deterministic rules for regulatory compliance:

```python
from agent_eval.prediction import ComplianceRuleEngine

engine = ComplianceRuleEngine()
violations = engine.check_all_compliance(agent_config)
```

**Rule Categories:**
- **PII Protection**: GDPR Article 25 privacy by design requirements
- **Security Controls**: OWASP compliance, input validation, authentication
- **Audit Requirements**: SOX logging, transaction limits, approval workflows
- **Data Handling**: PCI DSS data masking, encryption requirements

### 2. LLM Reliability Predictor

GPT-4.1 powered pattern recognition:

```python
from agent_eval.prediction import LLMReliabilityPredictor

predictor = LLMReliabilityPredictor(api_manager)
prediction = predictor.predict_failure_probability(analysis)
```

**Capabilities:**
- Complex failure mode detection
- Framework-specific reliability patterns
- Risk assessment with confidence weighting
- Explainable prediction reasoning

### 3. Hybrid Predictor

Weighted combination of both approaches:

```python
from agent_eval.prediction import HybridReliabilityPredictor

hybrid = HybridReliabilityPredictor(api_manager)
prediction = hybrid.predict_reliability(analysis, agent_config)
```

**Features:**
- Weighted score combination (40% rules, 60% LLM)
- Risk level determination (LOW/MEDIUM/HIGH)
- Confidence calculation based on evidence quality
- Business impact assessment

## Risk Assessment

### Risk Levels

Predictions are categorized into three levels based on combined risk scores:

#### LOW Risk (0.0-0.4)
- **Characteristics**: Strong safeguards, proper error handling, compliant configuration
- **Business Impact**: 70-95% failure prevention
- **Action**: Monitor and maintain current practices
- **Example**: Well-configured finance agent with full SOX compliance

#### MEDIUM Risk (0.4-0.7)
- **Characteristics**: Some missing safeguards, moderate reliability concerns
- **Business Impact**: 40-70% failure prevention
- **Action**: Implement recommended improvements
- **Example**: Agent with good core functionality but missing audit logging

#### HIGH Risk (0.7-1.0)
- **Characteristics**: Missing critical safeguards, high failure probability
- **Business Impact**: 0-40% failure prevention
- **Action**: Address critical issues before production deployment
- **Example**: Agent with no input validation or error handling

### Confidence Scoring

Each prediction includes a confidence score (0.0-1.0) based on:

- **Data Quality**: Completeness and structure of agent outputs
- **Sample Size**: Number of outputs analyzed (more data = higher confidence)
- **Pattern Clarity**: How clear the reliability patterns are
- **Framework Support**: How well the agent framework is understood

## Prediction Process

### 1. Input Analysis

The system analyzes multiple data sources:

```python
# Agent configuration
agent_config = {
    "framework": "langchain",
    "validation": {"enabled": True, "pii_detection": True},
    "security": {"encryption": True, "access_control": True},
    "logging": {"audit": True, "level": "detailed"}
}

# Agent outputs and traces
agent_outputs = [
    {"output": "Transaction approved", "trace": {...}},
    {"output": "Access denied", "trace": {...}}
]

# Comprehensive analysis
analysis = reliability_analyzer.generate_comprehensive_analysis(
    agent_outputs, framework="langchain"
)
```

### 2. Rule-Based Analysis

Deterministic compliance checking:

```python
# PII Protection Check
pii_result = engine.check_pii_compliance(config)
# Returns: violations, risk_score, evidence

# Security Controls Check  
security_result = engine.check_security_compliance(config)
# Returns: violations, risk_score, evidence

# Audit Requirements Check
audit_result = engine.check_audit_compliance(config)
# Returns: violations, risk_score, evidence
```

### 3. LLM Pattern Recognition

Intelligent pattern analysis:

```python
# Extract features for LLM analysis
analysis_features = {
    "framework_metrics": {...},
    "tool_usage_patterns": {...},
    "error_patterns": {...},
    "performance_metrics": {...}
}

# Generate prediction prompt
prompt = predictor._create_prediction_prompt(analysis_features)

# Get LLM prediction
llm_prediction = api_manager.call_with_logprobs(prompt)
```

### 4. Score Combination

Weighted combination of rule and LLM scores:

```python
def _combine_scores(self, rule_risk: float, llm_risk: float) -> Dict:
    """Combine rule-based and LLM risk scores with weighting."""
    
    combined_risk = (
        rule_risk * self.rule_weight +      # 40% weight
        llm_risk * self.llm_weight          # 60% weight
    )
    
    risk_level = self._determine_risk_level(combined_risk)
    
    return {
        "combined_risk_score": combined_risk,
        "risk_level": risk_level,
        "rule_component": {"risk_score": rule_risk, "weight": self.rule_weight},
        "llm_component": {"risk_score": llm_risk, "weight": self.llm_weight}
    }
```

## Business Impact Analysis

### Failure Prevention Metrics

The system calculates quantified business impact:

```python
business_impact = {
    "failure_prevention_percentage": 75,  # Based on risk level and confidence
    "estimated_cost_savings": 45000,     # Annual savings from prevented failures
    "compliance_risk_reduction": "High", # Regulatory risk mitigation
    "time_savings_hours": 120           # Developer time saved per month
}
```

### ROI Calculation

Return on investment based on:
- **Prevented Failures**: Cost of production incidents avoided
- **Compliance Savings**: Regulatory fines and audit costs avoided
- **Developer Productivity**: Time saved on debugging and troubleshooting
- **Infrastructure Costs**: Reduced resource usage from optimized agents

## Integration Examples

### CLI Integration

```bash
# Debug workflow with prediction
arc-eval debug --input outputs.json
# Automatically includes reliability prediction

# Compliance workflow with prediction
arc-eval compliance --domain finance --input outputs.json
# Includes prediction in compliance context
```

### Python SDK Integration

```python
from agent_eval.prediction import HybridReliabilityPredictor
from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer

# Initialize components
analyzer = ReliabilityAnalyzer()
predictor = HybridReliabilityPredictor()

# Generate analysis
analysis = analyzer.generate_comprehensive_analysis(agent_outputs)

# Generate prediction
prediction = predictor.predict_reliability(analysis, agent_config)

# Access results
print(f"Risk Level: {prediction['risk_level']}")
print(f"Risk Score: {prediction['combined_risk_score']:.2f}")
print(f"Confidence: {prediction['confidence']:.2f}")
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Agent Reliability Prediction
  run: |
    result=$(arc-eval debug --input outputs.json --output-format json)
    risk_level=$(echo "$result" | jq -r '.reliability_prediction.risk_level')
    
    if [ "$risk_level" = "HIGH" ]; then
      echo "High reliability risk detected - blocking deployment"
      exit 1
    fi
```

## Configuration Options

### API Configuration

```yaml
# ~/.arc-eval/config.yaml
prediction:
  rule_weight: 0.4        # 40% weight for rules
  llm_weight: 0.6         # 60% weight for LLM
  confidence_threshold: 0.6
  
api:
  openai:
    model: gpt-4o-mini    # Default model for predictions
    max_tokens: 4000
  anthropic:
    model: claude-3-5-haiku-20241022
    max_tokens: 4000
```

### Environment Variables

```bash
# API keys for LLM predictions
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Prediction configuration
export ARC_EVAL_PREDICTION_MODEL="gpt-4o-mini"
export ARC_EVAL_CONFIDENCE_THRESHOLD="0.6"
```

## Accuracy and Validation

### Prediction Tracking

The system tracks prediction accuracy over time:

```python
from agent_eval.prediction import PredictionTracker

tracker = PredictionTracker()

# Log prediction
prediction_id = tracker.log_prediction(prediction, agent_config)

# Update with actual outcome (when available)
tracker.update_prediction_outcome(
    prediction_id, 
    outcome="failure_detected",
    confidence=0.9
)

# Analyze accuracy
accuracy_metrics = tracker.calculate_accuracy_metrics(days=90)
```

### Validation Methodology

1. **Test Configurations**: Use known good/bad configurations for validation
2. **Outcome Tracking**: Monitor actual agent performance vs predictions
3. **Accuracy Metrics**: Calculate precision, recall, F1 scores
4. **Continuous Improvement**: Update models based on accuracy feedback

### Expected Accuracy

Based on validation testing:
- **Overall Accuracy**: 85-90% for risk level predictions
- **High Risk Detection**: 95% precision for HIGH risk predictions
- **Low Risk Validation**: 90% accuracy for LOW risk predictions
- **Confidence Calibration**: Confidence scores correlate with actual accuracy

## Performance Considerations

### Response Time

- **Target**: <5 seconds per prediction
- **Typical**: 2-3 seconds for standard analysis
- **Factors**: Input size, LLM API latency, complexity of analysis

### Cost Optimization

- **Batch Processing**: Automatic batching for multiple predictions
- **Model Selection**: Default to cost-effective models (GPT-4o-mini, Claude Haiku)
- **Caching**: Cache similar predictions to reduce API calls
- **Scenario Targeting**: Focus on relevant scenarios to reduce analysis scope

### Scalability

- **Parallel Processing**: Multiple predictions processed concurrently
- **Async Operations**: Non-blocking API calls for better throughput
- **Resource Management**: Efficient memory usage for large datasets

## Next Steps

- [Accuracy Metrics](accuracy.md) - Detailed accuracy validation and metrics
- [Business Impact](business-impact.md) - ROI calculations and business value
- [Testing Guide](testing.md) - Validation examples and test cases
- [API Reference](../api/) - Complete SDK documentation for predictions

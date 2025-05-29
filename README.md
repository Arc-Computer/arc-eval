# ARC-Eval: Agentic Workflow Reliability Platform

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

![Agent-as-a-Judge Demo](public/agent-as-judge-demo.png)

ARC-Eval evaluates AI agent reliability and provides debugging tools for agent workflow failures. Built on the MetaAuto AI Agent-as-a-Judge framework, it includes 378 domain-specific evaluation scenarios across security, finance, and ML infrastructure.

The platform addresses two core problems: debugging agent failures in production and evaluating agent behavior against domain requirements. It provides framework-agnostic analysis for LangChain, CrewAI, OpenAI, Anthropic, and other agent implementations.

---

## Quick Start

```bash
pip install arc-eval
export ANTHROPIC_API_KEY="your-key-here"

# Three simple workflows:
arc-eval debug --input agent_trace.json        # Why is it failing?
arc-eval compliance --domain finance --input outputs.json  # Does it meet requirements?
arc-eval improve --from-evaluation latest      # How do I fix it?

# Or run interactively:
arc-eval
```

---

## Architecture

ARC-Eval implements Agent-as-a-Judge evaluation ([Wang et al., 2024](https://arxiv.org/abs/2410.10934v2)) with production extensions for reliability analysis and continuous improvement.

```mermaid
graph TB
    A[Agent Outputs<br/>JSON/Logs] --> B[Framework Detection]
    B --> C[Domain Evaluation<br/>378 Scenarios]
    C --> D[Agent Judge<br/>Claude Sonnet/Haiku]
    D --> E[Reliability Analysis]
    E --> F[Improvement Planning]
    F --> G[Performance Tracking]
    
    B --> B1[LangChain Parser]
    B --> B2[OpenAI Parser]
    B --> B3[CrewAI Parser]
    B --> B4[Custom Parser]
    
    C --> C1[Finance<br/>110 scenarios]
    C --> C2[Security<br/>120 scenarios]
    C --> C3[ML Safety<br/>148 scenarios]
    
    D --> D1[Multi-Judge<br/>Verification]
    D --> D2[Confidence<br/>Calibration]
    D --> D3[Interactive<br/>Analysis]
    
    E --> E1[Debug Reports]
    E --> E2[Compliance Audit]
    E --> E3[Performance Metrics]
    
    F --> F1[Curriculum Generation]
    F --> F2[Training Examples]
    F --> F3[Trend Analysis]
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
```

The system includes six core components that work together to provide comprehensive agent evaluation and improvement.

**Agent Judge Framework** provides domain-specific evaluation using Claude Sonnet for accuracy and Haiku for cost optimization. Each domain judge specializes in finance, security, or ML scenarios with deep knowledge of relevant compliance frameworks and failure patterns.

**Multi-Judge Verification** implements secondary judge validation for critical decisions through agreement scoring and consensus mechanisms. This reduces false positives and ensures high-confidence evaluation results for production systems.

**Interactive Analysis** enables AI-powered Q&A sessions using Claude Sonnet 4 for understanding evaluation failures and patterns. Developers can ask domain-specific questions about failures and receive contextual debugging guidance.

**Confidence Calibration** performs logprobs-based uncertainty quantification with decision token analysis and entropy calculations. This provides statistical confidence intervals for evaluation results and identifies areas of uncertainty.

**Self-Improvement Engine** generates automated retraining curriculum from failed evaluations and tracks performance trends across iterations. This enables continuous learning where agents improve from their own evaluation failures.

**Performance Tracking** monitors runtime, memory, and cost analysis with latency percentile calculations and efficiency benchmarking. This provides operational insights for production deployment optimization.

---

## Evaluation Domains

ARC-Eval includes three evaluation packs covering 378 scenarios designed for production agent systems across different domains.

**Finance (110 scenarios)** covers SOX, KYC, AML, PCI-DSS, and GDPR compliance testing for banking, fintech, and payment processing agents. These scenarios test for real-world issues like PII exposure, transaction monitoring violations, and regulatory compliance gaps that can result in significant penalties.

**Security (120 scenarios)** implements OWASP LLM Top 10, NIST AI-RMF, and ISO 27001 vulnerability assessment for AI agents, chatbots, and code generation systems. The scenarios cover prompt injection, data leakage, authentication bypass, and other security vulnerabilities specific to LLM-based systems.

**ML (148 scenarios)** evaluates EU AI Act, IEEE Ethics, and Model Cards compliance for ML safety, bias detection, and governance. These scenarios test for algorithmic bias, fairness violations, explainability requirements, and other ethical AI considerations.

Each domain pack includes detailed scenario definitions, compliance framework mappings, and specific remediation guidance tailored to the regulatory requirements and best practices for that domain.

---

## Core Improvement Loop

ARC-Eval implements a complete evaluation and improvement cycle for agent performance. The system identifies failures, generates specific improvement plans, and measures progress through quantitative before/after comparisons.

```mermaid
graph LR
    A[Agent Outputs] --> B[Domain Evaluation<br/>378 Scenarios]
    B --> C[Failure Analysis<br/>Pattern Detection]
    C --> D[Improvement Planning<br/>Prioritized Actions]
    D --> E[Implementation<br/>Agent Updates]
    E --> F[Re-evaluation<br/>Progress Measurement]
    F --> G[Performance Comparison<br/>Baseline vs Improved]
    
    C --> H[Self-Improvement<br/>Engine]
    H --> I[Curriculum Generation]
    H --> J[Training Examples]
    H --> K[Trend Analysis]
    
    G --> L{Satisfactory<br/>Results?}
    L -->|No| C
    L -->|Yes| M[Production Deployment]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#ffebee
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e8
    style M fill:#e1f5fe
```

The improvement loop operates through three interconnected phases. First, the evaluation engine runs 378 domain-specific scenarios against your agent outputs to identify specific failure patterns, compliance violations, and performance bottlenecks. Each scenario tests for real-world issues like PII exposure, security vulnerabilities, or bias in decision-making.

Second, the improvement planner analyzes evaluation results and generates actionable improvement plans with prioritized actions, expected timelines, and measurable impact projections. The planner categorizes issues by severity and provides specific implementation steps for each identified problem.

Third, the comparison engine measures improvement between baseline and updated implementations through quantitative before/after analysis. This creates a feedback loop where each iteration builds measurably better agent systems.

### Example: Finance Agent Improvement

**Step 1: Baseline Evaluation**
```bash
arc-eval --domain finance --input examples/complete-datasets/finance.json --agent-judge
# Result: 40% pass rate, identifies PII exposure and AML violations
```

**Step 2: Generate Improvement Plan**
```bash
arc-eval --improvement-plan --from-evaluation finance_evaluation_20250527_143022.json
# Generates: improvement_plan_20250527_143522.md with specific actions
```

**Step 3: Implement Changes and Re-evaluate**
```bash
arc-eval --domain finance --input examples/complete-datasets/finance.json --baseline finance_evaluation_20250527_143022.json
# Result: 85% pass rate, demonstrating 45% improvement
```

The self-improvement engine complements this workflow by creating retraining curriculum from failed scenarios and tracking performance trends across multiple iterations. This enables continuous learning where agents automatically improve from their own evaluation failures.

### Before/After Example

**Baseline Output (fails PII protection)**:
```json
{
  "output": "Customer John Smith (SSN: 123-45-6789) approved for $50,000 loan"
}
```

**Improved Output (passes compliance)**:
```json
{
  "output": "Customer <REDACTED> approved for $50,000 loan based on verified income and credit score. PII protection protocols applied."
}
```

This concrete example demonstrates the loop in action: PII exposure eliminated, AML controls added, bias reduced. Each evaluation cycle produces measurable improvements that compound over time to create robust, compliant agent systems suitable for production deployment.

---

## Unified Workflows

ARC-Eval provides three simple commands for the complete agent improvement lifecycle:

### 🔍 Debug Workflow
**Purpose:** Why is my agent failing?

```bash
arc-eval debug --input agent_trace.json
```

Automatically:
- Detects your agent framework (LangChain, CrewAI, etc.)
- Identifies failure patterns and root causes
- Provides specific fixes with code examples
- Analyzes tool calls, memory usage, and performance

### ✅ Compliance Workflow  
**Purpose:** Does my agent meet requirements?

```bash
arc-eval compliance --domain finance --input outputs.json
```

Features:
- 378 domain-specific scenarios across finance, security, and ML
- Automated compliance scoring with Agent-as-a-Judge
- PDF audit reports generated automatically
- Regulatory framework mapping (SOX, OWASP, EU AI Act, etc.)

### 📈 Improve Workflow
**Purpose:** How do I make my agent better?

```bash
arc-eval improve --from-evaluation latest
```

Provides:
- Prioritized improvement plans with timelines
- Expected improvement projections
- Before/after comparison tracking
- Automated retraining curriculum generation

## Workflow Example

```bash
# Step 1: Debug your failing agent
arc-eval debug --input agent_trace.json
# Output: 3 failures found, root causes identified

# Step 2: Check compliance
arc-eval compliance --domain finance --input outputs.json  
# Output: 40% compliance, critical PII exposure issues

# Step 3: Generate improvement plan
arc-eval improve --from-evaluation finance_evaluation_20250527.json
# Output: 3-phase plan to reach 90% compliance

# Step 4: Implement fixes and compare
arc-eval improve --baseline original.json --current improved.json
# Output: 45% improvement achieved
```

## Legacy CLI Usage

The original CLI with 20+ flags is still available for backward compatibility:

```bash
# Legacy commands (being deprecated)
arc-eval --domain finance --input outputs.json --agent-judge --export pdf
arc-eval --debug-agent --unified-debug --workflow-reliability --input trace.json
arc-eval --improvement-plan --from-evaluation results.json --baseline previous.json
```

We recommend migrating to the new unified workflows for a simpler experience.

---

## Python SDK

Advanced features are available through the Python SDK for programmatic access to the evaluation and improvement systems. These provide deeper integration capabilities beyond the CLI interface.

### Interactive Analysis (SDK Only)
```python
from agent_eval.analysis.interactive_analyst import InteractiveAnalyst

analyst = InteractiveAnalyst(domain="finance")
analyst.start_interactive_session(
    improvement_report=evaluation_results,
    judge_results=judge_results
)
```

Interactive analysis automatically starts after CLI evaluations unless `--no-interaction` is specified.

### Multi-Judge Verification (CLI: `--verify`)
```python
from agent_eval.evaluation.verification_judge import VerificationJudge

verifier = VerificationJudge(domain="security")
verification = verifier.verify_judgment(primary_result, output, scenario)
print(f"Verified: {verification.verified}, Agreement: {verification.agreement_score}")
```

CLI equivalent: `arc-eval --domain security --input outputs.json --agent-judge --verify`

### Confidence Calibration (CLI: `--confidence-calibration`)
```python
from agent_eval.evaluation.confidence_calibrator import ConfidenceCalibrator

calibrator = ConfidenceCalibrator()
calibration = calibrator.calibrate_confidence(response_text, logprobs)
print(f"Calibrated confidence: {calibration.calibrated_confidence}")
```

CLI equivalent: `arc-eval --domain finance --input outputs.json --agent-judge --confidence-calibration`

### Self-Improvement Engine (SDK Only)
```python
from agent_eval.analysis.self_improvement import SelfImprovementEngine

engine = SelfImprovementEngine()
curriculum = engine.generate_retraining_curriculum(failed_scenarios)
trends = engine.get_performance_trends(agent_id="agent-1", domain="finance")
```

The CLI generates improvement plans with `--improvement-plan` but full curriculum generation requires the SDK.

### Judge Comparison (CLI: `--compare-judges`)
```python
from agent_eval.analysis.judge_comparison import JudgeComparison

comparison = JudgeComparison()
results = comparison.run_comparison(
    judge_configs=config_data['judges'],
    agent_outputs=outputs
)
```

CLI equivalent: `arc-eval --compare-judges config/judge_comparison_templates.yaml --input outputs.json`

Results can be exported as JSON for integration with monitoring systems or as PDF reports for compliance audits. Export comprehensive reports suitable for internal audits and regulatory compliance documentation. The evaluation pipeline integrates with existing MLOps workflows and provides automated quality gates for agent deployments.


### Performance Tracking (CLI: `--performance`)
```python
from agent_eval.evaluation.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()
with tracker.track_agent_execution():
    # Your agent execution code
    pass

metrics = tracker.get_performance_summary()
```

CLI equivalent: `arc-eval --domain finance --input outputs.json --agent-judge --performance`

---

## Input Formats

ARC-Eval auto-detects agent outputs from these frameworks through its parser registry system: The system supports custom formats through the parser registry in `agent_eval/core/parser_registry.py`. This enables evaluation of agents built with any framework or custom implementation. Easily extend ARC-Eval to support your proprietary agent frameworks through a well-defined parser plugin system.


```json
// OpenAI/Anthropic format
[{
  "scenario_id": "fin_001",
  "messages": [...],
  "tool_calls": [...],
  "output": "Transaction approved for John Smith"
}]

// LangChain format
[{
  "intermediate_steps": [...],
  "agent_scratchpad": "...",
  "output": "Analysis complete"
}]

// CrewAI format
[{
  "crew_output": "...",
  "task_output": "...",
  "agent_execution": [...]
}]
```

The system supports custom formats through the parser registry in `agent_eval/core/parser_registry.py`. This enables evaluation of agents built with any framework or custom implementation.

---

## Research Foundation

ARC-Eval extends the Agent-as-a-Judge framework with domain-specific evaluation and production reliability features. The base framework ([arXiv:2410.10934v2](https://arxiv.org/abs/2410.10934v2)) provides LLM-based evaluation methodology.

ARC-Eval adds domain specialization with finance, security, and ML expertise tailored to real-world compliance requirements. Multi-judge consensus provides critical decision validation through secondary evaluation and agreement scoring. Interactive analysis enables AI-powered debugging sessions for understanding complex failure patterns. Confidence calibration uses logprobs for uncertainty quantification and statistical confidence intervals. Self-improvement loops provide automated curriculum generation and continuous learning from evaluation failures.

The system is designed for ML engineers and AI researchers working on production agent systems at scale. It addresses the gap between research evaluation frameworks and production reliability requirements for agent systems deployed in regulated industries.

---

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Agent Reliability Check
  run: |
    arc-eval --domain finance --input agent_outputs.json --agent-judge
    arc-eval --compare-judges config/production_judges.yaml --input agent_outputs.json
```

Results can be exported as JSON for integration with monitoring systems or as PDF reports for compliance audits. The evaluation pipeline integrates with existing MLOps workflows and provides automated quality gates for agent deployments.

---

## Documentation

[Quick Start Guide](examples/tutorials/QUICK_START_GUIDE.md) provides setup instructions and basic usage examples for immediate implementation.

[Examples](examples/) contains demo data, integration examples, and CI/CD templates for common deployment patterns.

Advanced features like interactive analysis, judge comparison, and self-improvement are documented in the Python SDK examples with complete code samples and usage patterns.

---

## Contributing

ARC-Eval is built for AI researchers and ML engineers working on production agent systems. Contributions are welcome for new domain evaluation packs that address specific industry requirements, additional framework parsers for emerging agent platforms, evaluation scenario improvements based on real-world failure patterns, and performance optimizations for large-scale deployments.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines and development setup instructions.

---

## Support

Report issues and feature requests on [GitHub Issues](https://github.com/Arc-Computer/arc-eval/issues) with detailed reproduction steps and system information.
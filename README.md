<div align="center">
  <img src="public/arc-banner-readme.png" alt="ARC-Eval Banner" style="border-radius: 6px; max-width: 45%; height: auto; max-height: 120px; object-fit: cover;" />
</div>

<br>

<div align="center">

# ARC-Eval: Debug, Evaluate, and Improve AI Agents

**CLI-native, framework-agnostic evaluation for AI agents. Real-world reliability, compliance, and risk - improve performance with every run.**

[![PyPI version](https://badge.fury.io/py/arc-eval.svg)](https://badge.fury.io/py/arc-eval)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Arc-Computer/arc-eval)

</div>

<br>

<div align="center">
  <img src="public/cli_dashboard_rounded.png" alt="ARC-Eval CLI Dashboard" style="border-radius: 8px; max-width: 90%; height: auto;" />
</div>

<br>
<br>

ARC-Eval tests any agent—regardless of framework—against **378 enterprise-grade scenarios** in finance, security, and machine learning. Instantly spot risks like data leaks, bias, or compliance gaps. With four simple CLI workflows, ARC-Eval delivers actionable insights, continuous improvement, and audit-ready reports—no code changes required.

It's built to be **agent-agnostic**, meaning you can bring your own agent (BYOA) regardless of the framework (LangChain, OpenAI, Google, Agno, etc.) and get actionable insights with minimal setup.

---

## Table of Contents
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Key Features & Dashboard](#key-features--dashboard)
- [Flexible Input & Auto-Detection](#flexible-input--auto-detection)
- [Scenario Libraries & Regulations](#scenario-libraries--regulations)
- [How It Works](#how-it-works)
- [Examples & Integrations](#examples--integrations)
- [Advanced Usage](#advanced-usage)
- [Tips & Troubleshooting](#tips--troubleshooting)
- [License & Links](#license--links)

---

## ⚡ Quick Start (2 minutes)

> **💡 Pro Tip:** Use `--quick-start` for an instant, no-setup demo. See [Flexible Input & Auto-Detection](#flexible-input--auto-detection) for all ingestion options.

```bash
# 1. Install ARC-Eval (Python 3.9+ required)
pip install arc-eval

# 2. Try it instantly with sample data (no local files needed!)
arc-eval compliance --domain finance --quick-start

# 3. See all available commands and options
arc-eval --help
```

<details>
<summary><strong>Next Steps with Your Agent</strong></summary>

> **⚠️ Important:** For agent-as-judge evaluation, set your API key:  
> `export ANTHROPIC_API_KEY="your-anthropic-api-key"`  
> _See [Flexible Input & Auto-Detection](#flexible-input--auto-detection) for details._

```bash
# For agent-as-judge evaluation (optional but highly recommended for deeper insights)
export ANTHROPIC_API_KEY="your-anthropic-api-key" # Or your preferred LLM provider API key

# For any agent framework - just point to your output file
arc-eval debug --input your_agent_trace.json
arc-eval compliance --domain security --input your_agent_outputs.json
arc-eval improve --from-evaluation latest

# Or get the complete picture in one command
arc-eval analyze --input your_agent_outputs.json --domain finance

# Get guided help and explore workflows anytime from the interactive menu
arc-eval
```
</details>

---

## Core Workflows

> See [Scenario Libraries & Regulations](#scenario-libraries--regulations) for full coverage details.  
> See [Flexible Input & Auto-Detection](#flexible-input--auto-detection) for all ingestion options.

<details>
<summary><strong>Debug: "Why is my agent failing?"</strong></summary>

```bash
arc-eval debug --input your_agent_trace.json
```

</details>

<details>
<summary><strong>Compliance: "Does my agent meet requirements?"</strong></summary>

```bash
arc-eval compliance --domain finance --input your_agent_outputs.json

# Or try it instantly with sample data (no local files or API keys needed!)
arc-eval compliance --domain security --quick-start
```

</details>

<details>
<summary><strong>Improve: "How do I make it better?"</strong></summary>

```bash
arc-eval improve --from-evaluation latest # Uses insights from your last evaluation
```

</details>

<details>
<summary><strong>Analyze: "Give me the complete picture"</strong></summary>

```bash
arc-eval analyze --input your_agent_outputs.json --domain finance
```
This command automatically runs the debug process, then the compliance checks, and finally presents the interactive menu for next steps.

</details>

---

## Key Features & Dashboard

> **Agent-as-a-Judge:** ARC-Eval uses LLMs as domain-specific judges to evaluate agent outputs, provide continuous feedback, and drive improvement. This is implemented in [`agent_eval/evaluation/judges/`](./agent_eval/evaluation/judges/), with feedback and retraining handled by [`agent_eval/analysis/self_improvement.py`](./agent_eval/analysis/self_improvement.py) and adaptive scenario generation in [`agent_eval/core/scenario_bank.py`](./agent_eval/core/scenario_bank.py).

### Interactive Menus
After each workflow (like `debug` or `compliance`), see an interactive menu guiding you to logical next steps, making it easy to navigate the platform's capabilities.
```
🔍 What would you like to do?
════════════════════════════════════════

  [1]  Run compliance check on these outputs      (Recommended)
  [2]  Ask questions about failures               (Interactive Mode)
  [3]  Export debug report                        (PDF/CSV/JSON)
  [4]  View learning dashboard & submit patterns  (Improve ARC-Eval)
```

### Learning Dashboard
The system tracks failure patterns and improvements over time, providing valuable insights:
*   **Pattern Library**: Captures and catalogs recurring failure patterns from your agent's runs.
*   **Fix Catalog**: Suggests specific code fixes or configuration changes for common, identified issues.
*   **Performance Delta**: Clearly shows improvement metrics (e.g., compliance pass rate increasing from 73% → 91% after applying fixes).

### Versatile Export Options
Easily share or archive your findings:
*   **PDF**: Professional, auditable reports ideal for compliance teams and stakeholder reviews.
*   **CSV**: Raw data suitable for spreadsheet analysis or custom charting.
*   **JSON**: Structured data perfect for integration with monitoring systems, CI/CD pipelines, or other internal tools.

---

## Flexible Input & Auto-Detection

ARC-Eval is designed to seamlessly fit into your existing workflows with flexible input methods and intelligent format detection.

### Multiple Ways to Provide Agent Outputs

You can feed your agent's traces and outputs to ARC-Eval using several convenient methods:

```bash
# 1. Direct file input (most common)
arc-eval compliance --domain finance --input your_agent_traces.json

# 2. Auto-scan current directory for JSON files
# Ideal when you have multiple trace files in a folder.
arc-eval compliance --domain finance --folder-scan

# 3. Paste traces directly from your clipboard
# Useful for quick, one-off evaluations. (Requires pyperclip: pip install pyperclip)
arc-eval compliance --domain finance --input clipboard

# 4. Instant demo with built-in sample data (no files needed!)
arc-eval compliance --domain finance --quick-start

# 5. For automation/CI-CD (skips interactive prompts)
arc-eval compliance --domain finance --input your_agent_traces.json --no-interactive
```

### Performance Optimization

For faster evaluation, include `scenario_id` in your agent outputs to limit evaluation to specific scenarios:

```json
{
  "output": "Transaction approved after KYC verification",
  "scenario_id": "fin_001"
}
```

**Performance Tips:**
- ✅ **Include scenario_id**: Limits evaluation to specific scenarios (10x faster)
- ✅ **Use --no-interactive**: Essential for automation and CI/CD
- ✅ **Use --quick-start**: Instant demo with built-in sample data
- ✅ **Batch processing**: Automatically enabled for 5+ scenarios (50% cost savings)

### Automatic Format Detection

No need to reformat your agent logs. ARC-Eval automatically detects and parses outputs from many common agent frameworks and LLM API responses. Just point ARC-Eval to your data, and it will handle the rest.

**Examples of auto-detected formats:**

```json
// Simple, generic format (works with any custom agent)
{
  "output": "Transaction approved for account X9876.",
  "scenario_id": "fin_001", // Optional: for faster evaluation (limits to specific scenarios)
  "error": null, // Optional: include if an error occurred
  "metadata": {"user_id": "user123", "timestamp": "2024-05-27T10:30:00Z"} // Optional metadata
}

// OpenAI / Anthropic API style logs (and similar LLM provider formats)
{
  "id": "msg_abc123",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris.",
        "tool_calls": [ // If your agent uses tools
          {"id": "call_def456", "type": "function", "function": {"name": "get_capital_city", "arguments": "{\"country\": \"France\"}"}}
        ]
      }
    }
  ],
  "usage": {"prompt_tokens": 50, "completion_tokens": 10}
}

// LangChain / CrewAI / LangGraph style traces (capturing intermediate steps)
{
  "input": "What is the weather in London?",
  "intermediate_steps": [
    [
      {
        "tool": "weather_api",
        "tool_input": "London",
        "log": "Invoking weather_api with London\n"
      },
      "Rainy, 10°C"
    ]
  ],
  "output": "The weather in London is Rainy, 10°C.",
  "metadata": {"run_id": "run_789"}
}
```
ARC-Eval intelligently extracts the core agent response, tool calls, and relevant metadata for evaluation. For adding custom parsers, see [`agent_eval/core/parser_registry.py`](./agent_eval/core/parser_registry.py).

---

## Scenario Libraries & Regulations

<details>
<summary><strong>Show Scenario Libraries & Regulations</strong></summary>

### **Comprehensive Enterprise Test Suite**

ARC-Eval provides **378 enterprise scenarios** across three critical domains:

| **Domain** | **Scenarios** | **Key Regulations** | **Use Cases** |
|------------|---------------|-------------------|---------------|
| **Finance** | 110 scenarios | SOX, KYC/AML, PCI-DSS, GDPR, EU AI Act | Financial reporting, fraud detection, loan processing |
| **Security** | 120 scenarios | OWASP LLM Top 10, NIST AI RMF, ISO 27001 | Prompt injection, data leakage, model theft |
| **ML/AI** | 148 scenarios | EU AI Act, IEEE P7000, Model Cards | Bias detection, explainability, model governance |

### **Real-World Enterprise Scenarios**
- **SOX Compliance**: Detect earnings manipulation in SEC filings
- **AML/KYC**: Identify synthetic identities and money laundering patterns
- **EU AI Act**: Assess high-risk AI system compliance and bias detection
- **OWASP LLM**: Test for prompt injection, training data poisoning, model theft
- **Data Privacy**: GDPR, CCPA compliance validation and PII detection

**Why This Matters**: While many evaluation platforms focus on "helpfulness" and "harmlessness," ARC-Eval specializes in **regulatory compliance** and **enterprise risk scenarios** that can result in significant fines or regulatory action.

</details>

---

## How It Works

```mermaid
graph LR
    A[Agent Output] --> B[Debug]
    B --> C[Compliance]
    C --> D[Dashboard & Report]
    D --> E[Improve]
    E --> F[Re-evaluate]
    F --> B
```

**The Arc Loop: ARC-Eval learns from every failure to build smarter, more reliable agents.**

1.  **Debug:** You provide your agent's output (trace). ARC-Eval finds what's broken (errors, inefficiencies) and can suggest running a compliance check for deeper analysis.
2.  **Compliance:** Your agent is measured against hundreds of real-world scenarios. The results populate the Learning Dashboard and generate a compliance report.
3.  **Dashboard & Report:** Track your agent's learning progress, identify recurring patterns, and see compliance gaps. This insight guides the improvement plan.
4.  **Improve:** Based on the findings, ARC-Eval generates prioritized fixes and an improvement plan, then prompts re-evaluation.
5.  **Re-evaluate:** Test the suggested improvements. The new performance data feeds back into the loop, enabling continuous refinement.

> **📖 Complete Implementation Guide**: See [Core Product Loops Documentation](./docs/core-loops.md) for detailed step-by-step instructions on implementing The Arc Loop and Data Flywheel in your development workflow.

---

🔄 ARC-Eval Data Flywheel: Complete End-to-End Flow

📊 Core Architecture Overview

```bash
  Static Domain Knowledge → Dynamic Learning → Performance Analysis → Adaptive Improvement
          ↓                      ↓                    ↓                      ↓
     finance.yaml          ScenarioBank      SelfImprovementEngine    FlywheelExperiment
     (110 scenarios)    (pattern learning)   (performance tracking)    (ACL curriculum)
          ↑                      ↑                    ↑                      ↑
          └──────────────── Continuous Feedback Loop ────────────────────────┘
```

## Examples & Integrations

<details>
<summary><strong>Show Examples & Integrations</strong></summary>

> **📚 Complete Documentation**: See [`docs/`](./docs/) for comprehensive guides including:
> - [🔄 Core Product Loops](./docs/core-loops.md) - **The Arc Loop & Data Flywheel** (Essential!)
> - [Quick Start Guide](./docs/quickstart.md) - Get running in 5 minutes
> - [Workflows Guide](./docs/workflows/) - Debug, compliance, and improvement workflows
> - [Prediction System](./docs/prediction/) - Hybrid reliability prediction framework
> - [Framework Integration](./docs/frameworks/) - Support for 10+ agent frameworks
> - [API Reference](./docs/api/) - Complete Python SDK documentation
> - [Testing Guide](./docs/testing/) - Comprehensive testing methodology and validation
> - [Troubleshooting Guide](./docs/troubleshooting.md) - Common issues, solutions, and optimization
> - [Enterprise Integration](./docs/enterprise/integration.md) - CI/CD pipeline integration
>
> **🔧 Practical Examples**: Explore [`examples/`](./examples/) for:
> - Framework-specific integration examples
> - CI/CD pipeline templates
> - Sample agent outputs and configurations
> - Prediction testing and validation

</details>

---

## Advanced Usage

<details>
<summary><strong>Show Advanced Usage (SDK, CI/CD, etc.)</strong></summary>

### Python SDK for Programmatic Evaluation

```python
from agent_eval.core import EvaluationEngine, AgentOutput
from agent_eval.core.types import EvaluationResult, EvaluationSummary

# Example agent outputs (replace with your actual agent data)
agent_data = [
    {"output": "The transaction is approved.", "metadata": {"scenario": "finance_scenario_1"}},
    {"output": "Access denied due to security policy.", "metadata": {"scenario": "security_scenario_3"}}
]
agent_outputs = [AgentOutput.from_raw(data) for data in agent_data]

# Initialize the evaluation engine for a specific domain
engine = EvaluationEngine(domain="finance")

# Run evaluation
# You can optionally pass specific scenarios if needed, otherwise it uses the domain's default pack
results: list[EvaluationResult] = engine.evaluate(agent_outputs=agent_outputs)

# Get a summary of the results
summary: EvaluationSummary = engine.get_summary(results)

print(f"Total Scenarios: {summary.total_scenarios}")
print(f"Passed: {summary.passed}")
print(f"Failed: {summary.failed}")
print(f"Pass Rate: {summary.pass_rate:.2f}%")

for result in results:
    if not result.passed:
        print(f"Failed Scenario: {result.scenario_name}, Reason: {result.failure_reason}")
```

> See the [GitHub Actions workflow example](./examples/integration/ci-cd/github-actions.yml).

</details>

---

## Tips & Troubleshooting

> **Pro Tip:** Use `--quick-start` for instant demo evaluation with sample data.
> 
> **Note:** ARC-Eval auto-detects many common agent output formats—no need to reformat your logs.
> 
> **Warning:** For agent-as-a-judge evaluation, you must set your API key (see above for details).

---

## License & Links

This project is licensed under the MIT License - see the `LICENSE` file for details.

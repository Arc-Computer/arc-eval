# ARC-Eval Examples: Practical Guides & Sample Data

Welcome to the examples directory! This space is designed to help you quickly understand ARC-Eval's capabilities, explore expected input/output formats, and learn how to integrate our evaluation tools into your AI agent development lifecycle.

---
## Contents

### 🚀 `/quickstart`
*  This guide walks you through installing ARC-Eval, capturing agent outputs, running your first evaluations, and implementing improvements based on the results.
*   **Contains**: Step-by-step `README.md` and sample data tailored for a smooth onboarding experience.

### 📄 Sample Agent Outputs & Traces
Explore these files to understand the types of data ARC-Eval processes and how to format your agent's outputs for evaluation.

*   **`/sample-data` & `/demo-data`**: Various JSON files showing basic to moderately complex agent outputs. Useful for understanding the core data structures ARC-Eval expects.
    *   Includes `failed_trace_example.json`: Illustrates how a failed agent execution with debugging information might look.
*   **`/enhanced-traces`**: Demonstrates richer agent execution traces. These examples showcase how ARC-Eval can leverage detailed information like timing, multi-step reasoning, and tool call specifics for deeper analysis.
*   **`/workflow-reliability`**: Contains framework-specific output examples (e.g., LangChain, CrewAI). These are particularly helpful if you're using established agent frameworks and want to see how their native trace formats can be evaluated.

### 🛡️ Evaluation Scenario Insights
While the full, up-to-date scenario definitions reside within the core `agent_eval/domains/` directory (as YAML files), this section provides context.

*   **`/complete-datasets/README.md`**: Points you to the canonical location of our **378+ open-source evaluation scenarios** covering Finance, Security, and Machine Learning domains.
*   **Learn More**: To explore the actual scenarios, you can directly view files like `agent_eval/domains/finance.yaml` or use the CLI command `arc-eval compliance --domain security --list-scenarios`.

### ⚙️ Integration & Automation
*   **`/integration/ci-cd`**: Contains templates and examples (e.g., `github-actions.yml`) to help you integrate ARC-Eval into your Continuous Integration/Continuous Deployment (CI/CD) pipelines. Automate your agent evaluations to catch regressions and ensure reliability with every code change.
*   **`/integration/python`**: Shows examples of how to use the ARC-Eval Python SDK for programmatic evaluation and custom scripting within your own applications.

---

## Iterative Improvement

All these examples support ARC-Eval's core philosophy: a continuous improvement cycle for your AI agents.

```
Your Agent → ARC-Eval (Debug → Compliance → Improve) → Actionable Insights → Enhanced Agent → Re-evaluate
```

By testing your agent against realistic scenarios, analyzing failures, and applying guided improvements, you can systematically enhance its reliability, safety, and performance.

---

## Getting Started with Examples

1.  **Begin with `/quickstart/README.md`**: This is the most structured way to learn the basics.
2.  **Examine Agent Outputs**: Browse the `.json` files in `/sample-data`, `/enhanced-traces`, and `/workflow-reliability` to see how to structure your agent's data for ARC-Eval.
3.  **Explore Integration Options**: Check out `/integration` to see how to automate evaluations in your CI/CD pipeline or use the Python SDK.
4.  **Reference Scenario Domains**: While exploring, remember that the actual test scenarios are in `agent_eval/domains/`. Use `arc-eval --list-scenarios` for a specific domain to see all available test IDs and names.

These examples are open-source. We encourage you to use them, adapt them for your specific needs, and even contribute new examples that can help the community!
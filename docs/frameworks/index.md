# Framework Integration

ARC-Eval supports 9+ agent frameworks with automatic detection and framework-specific optimization recommendations. This guide covers integration patterns, output formats, and reliability optimization for each supported framework.

## Supported Frameworks

| Framework | Detection Method | Reliability Features | Optimization Focus |
|-----------|------------------|---------------------|-------------------|
| [LangChain](#langchain) | `intermediate_steps` field | Tool chain analysis, memory management | Multi-step workflow efficiency |
| [LangGraph](#langgraph) | Graph structure detection | State management, flow control | Graph execution optimization |
| [CrewAI](#crewai) | `crew_output`, `tasks_output` | Multi-agent coordination | Crew collaboration patterns |
| [AutoGen](#autogen) | Conversation structure | Multi-agent conversations | Communication efficiency |
| [OpenAI](#openai) | `choices`, `message` structure | Token optimization, response quality | Cost and latency optimization |
| [Anthropic](#anthropic) | Claude API format | Context management, safety | Response quality and safety |
| [Google ADK](#google-adk) | Google Agent Dev Kit format | Agent development toolkit | Development workflow optimization |
| [Agno](#agno) | Agno-specific fields | Emerging framework patterns | Framework-specific features |
| [Generic](#generic) | Fallback for custom frameworks | Basic reliability patterns | Universal optimization |

## Framework Detection

ARC-Eval automatically detects your agent framework from the output structure:

```python
from agent_eval.core.parser_registry import detect_and_extract

# Automatic detection
framework, normalized_output = detect_and_extract(raw_agent_output)
print(f"Detected framework: {framework}")
```

### Detection Logic

```python
def detect_and_extract(raw_data: Any) -> Tuple[str, str]:
    """Multi-stage framework detection."""
    
    if not isinstance(raw_data, dict):
        return "generic", str(raw_data)
    
    # LangChain detection
    if "intermediate_steps" in raw_data:
        return "langchain", extract_langchain_output(raw_data)
    
    # CrewAI detection
    if "crew_output" in raw_data or "tasks_output" in raw_data:
        return "crewai", extract_crewai_output(raw_data)
    
    # OpenAI detection
    if "choices" in raw_data and isinstance(raw_data["choices"], list):
        return "openai", extract_openai_output(raw_data)
    
    # Anthropic detection
    if "content" in raw_data and "role" in raw_data:
        return "anthropic", extract_anthropic_output(raw_data)
    
    # Generic fallback
    return "generic", extract_generic_output(raw_data)
```

## LangChain

### Output Format

LangChain agents provide rich execution traces with intermediate steps:

```json
{
  "input": "Process this financial transaction",
  "output": "Transaction processed successfully with compliance checks",
  "intermediate_steps": [
    [
      {
        "tool": "verify_account",
        "tool_input": "account_id: ACC123",
        "log": "Invoking verify_account with ACC123"
      },
      "Account verified: Active, sufficient balance"
    ],
    [
      {
        "tool": "compliance_check", 
        "tool_input": "transaction_data: {...}",
        "log": "Running compliance validation"
      },
      "Compliance check passed: SOX, AML requirements met"
    ]
  ],
  "metadata": {
    "run_id": "run_abc123",
    "total_tokens": 450,
    "execution_time": 2.3
  }
}
```

### Reliability Analysis

ARC-Eval provides LangChain-specific analysis:

- **Tool Chain Efficiency**: Analyzes tool call sequences and optimization opportunities
- **Intermediate Step Validation**: Checks for proper error handling in multi-step workflows
- **Memory Management**: Evaluates conversation memory and context handling
- **Agent Executor Patterns**: Identifies common execution patterns and bottlenecks

### Integration Example

```python
from langchain.agents import AgentExecutor
from agent_eval.core import EvaluationEngine, AgentOutput
import json

# Your existing LangChain agent
agent_executor = AgentExecutor(...)

# Capture outputs for evaluation
outputs = []
test_inputs = ["Process transaction", "Verify compliance", "Generate report"]

for input_text in test_inputs:
    result = agent_executor.invoke({"input": input_text})
    outputs.append({
        "input": input_text,
        "output": result["output"],
        "intermediate_steps": result.get("intermediate_steps", []),
        "metadata": {
            "run_id": result.get("run_id"),
            "total_tokens": result.get("total_tokens", 0)
        }
    })

# Save for ARC-Eval
with open("langchain_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)

# Evaluate with ARC-Eval
engine = EvaluationEngine(domain="finance")
agent_outputs = [AgentOutput.from_raw(data) for data in outputs]
results = engine.evaluate(agent_outputs)
```

### Optimization Recommendations

Common LangChain optimizations identified by ARC-Eval:

1. **Tool Chain Optimization**: Reduce unnecessary tool calls
2. **Memory Efficiency**: Optimize conversation buffer management
3. **Error Handling**: Improve intermediate step error recovery
4. **Token Usage**: Reduce prompt engineering overhead

## CrewAI

### Output Format

CrewAI provides multi-agent crew coordination data:

```json
{
  "crew_output": "Financial analysis completed with risk assessment",
  "tasks_output": [
    {
      "task_id": "data_collection",
      "agent": "data_analyst",
      "output": "Market data collected and validated",
      "execution_time": 1.2,
      "status": "completed"
    },
    {
      "task_id": "risk_analysis", 
      "agent": "risk_analyst",
      "output": "Risk score: 0.23 (Low risk)",
      "execution_time": 0.8,
      "status": "completed"
    }
  ],
  "token_usage": {
    "total_tokens": 1250,
    "prompt_tokens": 800,
    "completion_tokens": 450
  },
  "metadata": {
    "crew_id": "crew_fin_001",
    "total_execution_time": 3.5,
    "agents_involved": ["data_analyst", "risk_analyst", "compliance_officer"]
  }
}
```

### Reliability Analysis

CrewAI-specific analysis includes:

- **Crew Coordination**: Analyzes multi-agent coordination and task delegation
- **Task Completion Rates**: Measures individual agent and overall crew performance
- **Communication Patterns**: Evaluates inter-agent communication efficiency
- **Resource Utilization**: Tracks token usage and execution time across agents

### Integration Example

```python
from crewai import Crew, Agent, Task
from agent_eval.core import EvaluationEngine, AgentOutput
import json

# Your existing CrewAI setup
crew = Crew(agents=[...], tasks=[...])

# Capture outputs
outputs = []
test_scenarios = [
    {"market": "NASDAQ", "symbol": "AAPL"},
    {"market": "NYSE", "symbol": "MSFT"}
]

for scenario in test_scenarios:
    result = crew.kickoff(inputs=scenario)
    outputs.append({
        "crew_output": result.raw,
        "tasks_output": result.tasks_output,
        "token_usage": result.token_usage,
        "metadata": {
            "input": scenario,
            "crew_id": f"crew_{scenario['symbol']}"
        }
    })

# Evaluate with ARC-Eval
with open("crewai_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)
```

## OpenAI

### Output Format

OpenAI API responses with usage tracking:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the financial data analysis, I recommend...",
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "calculate_risk_score",
              "arguments": "{\"portfolio_value\": 100000, \"risk_tolerance\": \"moderate\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 75,
    "total_tokens": 225
  }
}
```

### Reliability Analysis

OpenAI-specific analysis focuses on:

- **Token Usage Optimization**: Identifies opportunities to reduce token consumption
- **Response Quality**: Analyzes response consistency and appropriateness
- **Tool Call Efficiency**: Evaluates function calling patterns
- **Rate Limiting**: Checks for rate limiting issues and optimization strategies

### Integration Example

```python
from openai import OpenAI
from agent_eval.core import EvaluationEngine, AgentOutput
import json

client = OpenAI()

# Capture outputs
outputs = []
test_prompts = [
    "Analyze this financial portfolio for compliance risks",
    "Generate a risk assessment report for this transaction"
]

for prompt in test_prompts:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        tools=[...],  # Your function definitions
        tool_choice="auto"
    )
    outputs.append(response.model_dump())

# Evaluate with ARC-Eval
with open("openai_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)
```

## Generic Framework

### Output Format

For custom or unsupported frameworks, use the generic format:

```json
{
  "output": "Agent response text",
  "scenario_id": "optional_scenario_id",
  "metadata": {
    "framework": "custom_framework",
    "version": "1.0.0",
    "execution_time": 1.5,
    "custom_metrics": {
      "accuracy": 0.95,
      "confidence": 0.87
    }
  },
  "trace": {
    "steps": [
      {"action": "input_validation", "result": "passed"},
      {"action": "processing", "result": "completed"},
      {"action": "output_generation", "result": "success"}
    ]
  }
}
```

### Custom Framework Registration

```python
from agent_eval.core.parser_registry import register_custom_framework

def detect_custom_framework(raw_data):
    """Custom framework detection logic."""
    return (isinstance(raw_data, dict) and 
            raw_data.get("metadata", {}).get("framework") == "custom_framework")

def extract_custom_output(raw_data):
    """Custom output extraction logic."""
    return raw_data.get("output", str(raw_data))

# Register your custom framework
register_custom_framework(
    name="custom_framework",
    detector=detect_custom_framework,
    extractor=extract_custom_output
)
```

## Framework-Specific Optimizations

### Performance Optimization

Each framework receives tailored optimization recommendations:

#### LangChain Optimizations
- **Tool Selection**: Optimize tool choice and sequencing
- **Memory Management**: Efficient conversation buffer usage
- **Prompt Engineering**: Reduce token overhead in prompts
- **Chain Composition**: Optimize chain structure for performance

#### CrewAI Optimizations
- **Agent Specialization**: Optimize agent role definitions
- **Task Distribution**: Improve task allocation across agents
- **Communication Efficiency**: Reduce inter-agent communication overhead
- **Resource Allocation**: Balance workload across crew members

#### OpenAI Optimizations
- **Model Selection**: Choose optimal model for use case
- **Token Efficiency**: Reduce prompt and completion token usage
- **Function Calling**: Optimize tool/function call patterns
- **Batch Processing**: Use batch API for multiple requests

### Reliability Patterns

Framework-specific reliability patterns identified by ARC-Eval:

#### Common Patterns
- **Error Recovery**: How frameworks handle and recover from errors
- **Timeout Management**: Timeout handling strategies
- **Resource Management**: Memory and token usage patterns
- **State Management**: How frameworks maintain state across interactions

#### Framework-Specific Patterns
- **LangChain**: Tool chain reliability, agent executor patterns
- **CrewAI**: Multi-agent coordination reliability, task completion patterns
- **OpenAI**: API reliability, response consistency patterns

## Best Practices

### 1. Include Rich Metadata

Provide comprehensive metadata for better analysis:

```json
{
  "output": "Response",
  "metadata": {
    "framework": "langchain",
    "version": "0.1.0",
    "execution_time": 2.3,
    "token_usage": 450,
    "tools_used": ["calculator", "search"],
    "error_count": 0
  }
}
```

### 2. Capture Execution Traces

Include detailed execution information:

```json
{
  "output": "Response",
  "trace": {
    "steps": [...],
    "tool_calls": [...],
    "errors": [...],
    "performance_metrics": {...}
  }
}
```

### 3. Use Scenario Targeting

Include scenario IDs for focused evaluation:

```json
{
  "output": "Response",
  "scenario_id": "fin_001",
  "metadata": {...}
}
```

### 4. Batch Similar Outputs

Group similar outputs for efficient evaluation:

```python
# Group by framework for optimized processing
langchain_outputs = [output for output in outputs if output.framework == "langchain"]
crewai_outputs = [output for output in outputs if output.framework == "crewai"]
```

## Troubleshooting

### Framework Detection Issues

**Problem**: Framework detected as "generic" when it should be specific
**Solution**: 
- Check output format against framework examples
- Include framework-specific fields in outputs
- Use manual framework specification: `--framework langchain`

### Missing Framework Features

**Problem**: Framework-specific analysis not appearing
**Solution**:
- Ensure outputs include framework-specific metadata
- Verify intermediate steps or trace information is present
- Check that framework detection is working correctly

### Performance Issues

**Problem**: Slow evaluation for specific frameworks
**Solution**:
- Use scenario targeting to limit evaluation scope
- Enable batch processing for large datasets
- Optimize output format to include only necessary data

## Next Steps

- [Debug Workflow](../workflows/debug.md) - Framework-specific debugging
- [API Reference](../api/) - Programmatic framework integration
- [Examples](../../examples/) - Complete framework examples
- [Architecture](../reference/architecture.md) - Framework detection internals

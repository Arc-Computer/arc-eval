# OpenAI Provider Support

ARC-Eval now supports OpenAI models (GPT-4.1, GPT-4.1-mini, GPT-4.1-nano) alongside Anthropic Claude models.

## Quick Start

### 1. Set Environment Variables

```bash
# Add to your .env file or export
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"  # or "anthropic" (default)
```

### 2. Run Evaluations with OpenAI

```bash
# The system will automatically use OpenAI models when LLM_PROVIDER=openai
arc-eval compliance --domain finance --input outputs.json --agent-judge

# Force a specific provider programmatically
from agent_eval.evaluation.judges.api_manager import APIManager
api_manager = APIManager(provider="openai")
```

## Model Mapping

| Purpose | Anthropic | OpenAI |
|---------|-----------|---------|
| Primary (High Accuracy) | claude-sonnet-4-20250514 | gpt-4.1 |
| Fallback (Cost Optimized) | claude-3-5-haiku-latest | gpt-4.1-mini |
| Ultra Low Cost | - | gpt-4.1-nano |

## Pricing Comparison

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude 3.5 Haiku | $0.25 | $1.25 |
| GPT-4.1 | $2.00 | $8.00 |
| GPT-4.1-mini | $0.40 | $1.60 |
| GPT-4.1-nano | $0.10 | $0.40 |

## Features

- ✅ Full Agent-as-a-Judge evaluation support
- ✅ Automatic cost tracking per provider
- ✅ Native logprobs support for OpenAI (better confidence calibration)
- ✅ Batch processing with cascade strategy
- ✅ All domain judges (Finance, Security, ML) work with both providers

## Technical Details

### What Changed

1. **APIManager** - Now supports multiple providers with automatic client selection
2. **Cost Tracking** - Provider-specific pricing calculations
3. **Response Handling** - Unified interface for both Anthropic and OpenAI responses
4. **Logprobs** - Native support for OpenAI, pseudo-logprobs for Anthropic

### Backward Compatibility

- Default provider remains Anthropic (no breaking changes)
- Existing code continues to work unchanged
- Provider selection is automatic based on environment variable

## Example Usage

```python
# Initialize with specific provider
from agent_eval.evaluation.judges.api_manager import APIManager
from agent_eval.evaluation.judges.domain.finance import FinanceJudge

# Use OpenAI
api_manager = APIManager(provider="openai", preferred_model="gpt-4.1")
judge = FinanceJudge(api_manager=api_manager)

# Evaluate as normal
result = judge.evaluate(agent_output, scenario)
print(f"Cost: ${api_manager.total_cost:.4f}")
```

## Benefits

1. **Cost Savings**: GPT-4.1 is ~33% cheaper than Claude Sonnet 4
2. **Performance**: 1M token context window for complex evaluations
3. **Flexibility**: Use existing OpenAI enterprise agreements
4. **Regional Compliance**: Choose providers based on data residency requirements
# Phase 2: Flywheel Improvement Experiment

**Research Objective**: Validate ARC-Eval's core value proposition through complete 30-iteration improvement cycle.

## Value Proposition Being Proven

> "Lifted pilot agents from 42% to 91% policy-pass rates in fewer than 30 iterations, collapsing remediation cycles from weeks to minutes."

## Implementation

### Core Experiment: `flywheel_experiment.py`

**Research-grade implementation using complete ARC-Eval infrastructure:**

1. **Real Baseline Data**: 337 enhanced traces from Phase 1
2. **Agent-as-a-Judge Evaluation**: Actual `arc-eval CLI` with ANTHROPIC_API_KEY
3. **Self-Improvement Engine**: Leverages `agent_eval/analysis/self_improvement.py`
4. **110 Finance Scenarios**: Tests against real `agent_eval/domains/finance.yaml`
5. **Progressive Improvements**: Targeted fixes based on actual failure analysis

### Research Methodology

**Three-Level Improvement Strategy:**
- **Level 1 (Iterations 1-10)**: Scenario-driven fixes for critical compliance violations
- **Level 2 (Iterations 11-20)**: Adaptive curriculum learning based on weakness analysis
- **Level 3 (Iterations 21-30)**: Skill-based targeting using Bayesian principles

**Progressive Enhancement Categories:**
- PII Protection (GDPR compliance)
- AML Compliance (OFAC/BSA requirements)  
- SOX Compliance (Audit controls)
- Bias Mitigation (Fair lending)
- General Compliance (Comprehensive validation)

## Execution

### Prerequisites
```bash
# Set API key for Agent-as-a-Judge evaluation
export ANTHROPIC_API_KEY="your-anthropic-key-here"

# Navigate to experiment directory
cd /Users/jarrodbarnes/arc-eval/experiments/flywheel_proof/phase2_improvement
```

### Test Mode (Quick Validation - 5 iterations, ~$10)
```bash
python flywheel_experiment.py --test
```

### Research Mode (Full 30-iteration experiment, ~$50-100)
```bash
python flywheel_experiment.py --iterations 30 --target 91.0 --budget 100.0
```

### Conservative Mode (15 iterations, ~$25-50)
```bash
python flywheel_experiment.py --iterations 15 --target 85.0 --budget 50.0
```

### Real-Time Progress Monitoring

**The experiment provides comprehensive real-time logging:**

#### Terminal Output (Real-Time)
- ✅ **Live iteration progress**: "🔄 ITERATION X/30"
- ✅ **Agent-as-a-Judge status**: Real CLI execution logs
- ✅ **Pass rate updates**: Live percentage improvements
- ✅ **Cost tracking**: Running API cost totals
- ✅ **Time estimates**: Duration per iteration + remaining time

#### Monitor Progress in Second Terminal
```bash
# Watch experiment directory creation
watch -n 10 "ls -la flywheel_experiment/"

# Monitor real-time logs (JSONL format)
tail -f flywheel_experiment/improvement_log.jsonl

# Check latest results
cat flywheel_experiment/experiment_summary.json | jq '.'
```

#### Progress Files Created in Real-Time
```bash
flywheel_experiment/
├── improvement_log.jsonl          # ⚡ Real-time iteration logs
├── agent_outputs/                 # ⚡ Live agent outputs
│   ├── improved_outputs_iter_01.json
│   ├── improved_outputs_iter_02.json
│   └── ...
├── evaluations/                   # ⚡ Live Agent-as-a-Judge results  
│   ├── evaluation_iter_01.json
│   ├── evaluation_iter_02.json
│   └── ...
└── strategies/                    # ⚡ Live improvement strategies
    ├── strategy_iter_01.json
    └── ...
```

### Expected Timing
- **Per Iteration**: 3-8 minutes (Agent-as-a-Judge + analysis)
- **Full 30-iteration**: 2-4 hours total
- **Conservative 15-iteration**: 1-2 hours total
- **Test mode (5 iterations)**: 20-40 minutes

### Expected Cost
- **Test Mode**: ~$10 (5 iterations)
- **Conservative**: ~$25-50 (15 iterations)  
- **Full Experiment**: ~$50-100 (30 iterations with Agent-as-a-Judge)

### Optional: Parallel Judge Comparison (Anthropic vs OpenAI)

**Prerequisites**:
```bash
# Set both API keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"

# Install OpenAI library
pip install openai
```

**Run Comparison**:
```bash
# Compare Anthropic Claude vs OpenAI GPT-4.1 (runs both experiments in parallel)
python parallel_judge_comparison.py 10

# Results saved to: parallel_judge_comparison/judge_comparison_results.json
```

**Individual Judge Experiments**:
```bash
# Anthropic Claude only
LLM_PROVIDER=anthropic python flywheel_experiment.py --iterations 15 --target 85.0 --budget 50.0

# OpenAI GPT-4.1 only  
LLM_PROVIDER=openai python flywheel_experiment.py --iterations 15 --target 85.0 --budget 50.0
```

## Output Structure

```
flywheel_experiment/
├── experiment_log.jsonl              # Iteration-by-iteration results
├── experiment_summary.json           # Final research summary
├── agent_outputs/                    # Improved outputs per iteration
│   ├── outputs_iter_01.json
│   ├── outputs_iter_02.json
│   └── ...
├── evaluations/                      # Agent-as-a-Judge evaluation results
│   ├── evaluation_iter_01.json
│   ├── evaluation_iter_02.json  
│   └── ...
├── strategies/                       # Improvement strategies per iteration
│   ├── strategy_iter_01.json
│   ├── strategy_iter_02.json
│   └── ...
└── retraining_data/                  # Self-improvement engine data
    ├── reward_signal_history.jsonl
    ├── training_examples.jsonl
    └── improvement_curriculum.json
```

## Research Validation

### Infrastructure Used
- ✅ **Real Agent-as-a-Judge**: `agent_eval/evaluation/judges/domain/finance.py`
- ✅ **Real Self-Improvement**: `agent_eval/analysis/self_improvement.py`
- ✅ **Real CLI Integration**: `arc-eval compliance --domain finance`
- ✅ **Real Scenarios**: All 110 scenarios from `agent_eval/domains/finance.yaml`
- ✅ **Real Baseline**: 337 enhanced traces with complete metadata

### Expected Results
- **Baseline**: 42% pass rate (realistic pilot agent)
- **Target**: 91% pass rate achieved in ≤30 iterations
- **Time Efficiency**: Minutes vs weeks for traditional remediation
- **Cost Efficiency**: $50-100 for complete validation vs $10M+ traditional approaches

### Research Quality
- **Academic Rigor**: Based on 2024 automated curriculum learning research
- **Data Transparency**: Complete audit trail and reproducible methodology
- **Infrastructure Validation**: Uses production ARC-Eval components
- **Publication Ready**: Generates legitimate research data for technical blog/papers

## Success Criteria

1. **✅ Target Achievement**: 91% pass rate reached in ≤30 iterations
2. **✅ Infrastructure Validation**: Real Agent-as-a-Judge evaluation used
3. **✅ Cost Efficiency**: Sub-$100 total cost for complete cycle
4. **✅ Time Efficiency**: Complete cycle in hours vs weeks
5. **✅ Reproducibility**: Complete methodology documented and automated

This experiment will provide the definitive research validation needed for our technical blog post and customer success stories.
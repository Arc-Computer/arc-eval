# PR 3: Show Value Clearly - Implementation Checklist

## Goal
Update the UI to prominently display the self-improvement metrics and make the value proposition crystal clear.

## Current State (After PR 2)
- ✅ Pattern learning captures failures
- ✅ Scenario generation after threshold
- ✅ Fix generation with compliance links
- ✅ Decorator shows basic learning output
- ✅ OpenAI provider support added

## What PR 3 Needs to Implement

### 1. Enhanced Result Display (`agent_eval/ui/result_renderer.py`)
- [ ] Show improvement metrics prominently:
  - Patterns learned this session
  - Scenarios generated
  - Fixes available
  - Improvement trend (73% → 91%)
- [ ] Add learning progress bar/visualization
- [ ] Display cumulative metrics over time

### 2. Interactive Learning Dashboard
- [ ] Create `agent_eval/ui/learning_dashboard.py`
- [ ] Show:
  - Total patterns in `.arc-eval/learned_patterns.jsonl`
  - Generated scenarios count
  - Fix library size by domain
  - Improvement trajectory graph

### 3. Update Command Output (`agent_eval/commands/compliance.py`)
- [ ] Add learning metrics to compliance summary
- [ ] Show "You're getting smarter!" messaging
- [ ] Display fix suggestions inline with failures

### 4. Improve Workflow Enhancement (`agent_eval/commands/workflow.py`)
- [ ] Integrate pattern learning metrics
- [ ] Show projected improvement based on fixes
- [ ] Add "Apply fixes and re-run" guidance

### 5. Summary Metrics (`agent_eval/core/types.py`)
- [ ] Add learning metrics to EvaluationSummary:
  - patterns_captured
  - scenarios_generated
  - fixes_available
  - improvement_percentage

## Key Files to Modify
1. `agent_eval/ui/result_renderer.py` - Main display logic
2. `agent_eval/ui/unified_output.py` - Consistent output formatting
3. `agent_eval/commands/compliance.py` - Compliance workflow
4. `agent_eval/commands/workflow.py` - Improve workflow
5. `agent_eval/core/types.py` - Data structures

## Success Metrics
- Users immediately see the value: "20 patterns learned, 5 scenarios generated"
- Clear improvement tracking: "Your compliance improved from 73% to 91%"
- Actionable next steps: "3 fixes available - apply them to reach 95%"

## Testing Plan
1. Run evaluation that triggers pattern learning
2. Verify metrics display prominently
3. Check that fixes are shown with failures
4. Ensure improvement tracking works
5. Test with both Anthropic and OpenAI providers

## Demo Script
```bash
# First run - baseline
arc-eval compliance --domain finance --input baseline.json
# Shows: 73% compliance, 20 failures captured

# Second run - after fixes
arc-eval compliance --domain finance --input improved.json
# Shows: 91% compliance, improvement visualization

# Third run - with generated scenarios
arc-eval compliance --domain finance --input latest.json
# Shows: Testing against 115 scenarios (110 original + 5 generated)
```

## Notes
- Keep changes focused on UI/display only
- Don't modify core pattern learning logic
- Ensure backward compatibility
- Make the value proposition unmissable
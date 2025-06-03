# Core Product Loops - The Heart of ARC-Eval

ARC-Eval is built around two fundamental loops that enable **continuous agent improvement** and **predictive reliability**. Understanding these loops is essential to maximizing the platform's value.

## The Arc Loop - Core Product Loop

**"ARC-Eval learns from every failure to build smarter, more reliable agents."**

This is the primary workflow that users follow to achieve continuous improvement:

```
🔍 DEBUG → 📋 COMPLIANCE → 📊 DASHBOARD → 📈 IMPROVE → 🔄 RE-EVALUATE
   ↓            ↓             ↓            ↓           ↓
Predict      Validate      Analyze      Optimize    Verify
Failures     Requirements  Patterns     Performance Improvements
```

### Step 1: Debug - Predictive Failure Analysis

**Purpose**: Find what's broken before it impacts production

```bash
# Start the Arc Loop
arc-eval debug --input agent_outputs.json
```

**What Happens**:
- Hybrid prediction system (40% rules + 60% LLM) analyzes your agent
- Risk assessment: LOW (0.0-0.4), MEDIUM (0.4-0.7), HIGH (0.7-1.0)
- Framework-specific optimization recommendations
- Business impact estimation

**Output Example**:
```
🔍 Debug Dashboard - Agent Reliability Analysis
═══════════════════════════════════════════════

📊 RELIABILITY PREDICTION
┌─────────────────────────────────────────────┐
│ Risk Level: MEDIUM                          │
│ Combined Risk Score: 0.52                   │
│ Confidence: 0.78                            │
└─────────────────────────────────────────────┘

🎯 RECOMMENDED NEXT STEP:
arc-eval compliance --domain finance --input agent_outputs.json
```

### Step 2: Compliance - Regulatory Validation

**Purpose**: Validate against enterprise-grade scenarios

```bash
# Continue the Arc Loop
arc-eval compliance --domain finance --input agent_outputs.json
```

**What Happens**:
- Tests against 378 enterprise scenarios (Finance: 110, Security: 120, ML: 148)
- Regulatory mapping (SOX, GDPR, OWASP LLM, EU AI Act)
- Compliance risk prediction
- Audit-ready report generation

**Output Example**:
```
✅ Compliance Evaluation - FINANCE
════════════════════════════════════════

📊 OVERALL RESULTS
Pass Rate: 67% (74/110 scenarios)
Critical Failures: 3
Regulatory Fine Risk: HIGH

🎯 RECOMMENDED NEXT STEP:
arc-eval improve --from-evaluation latest
```

### Step 3: Dashboard & Report - Pattern Analysis

**Purpose**: Track learning progress and identify patterns

**What Happens**:
- Results populate the Learning Dashboard
- Pattern recognition across failures
- Compliance gap analysis
- Progress tracking over time

**Key Insights**:
- Recurring failure patterns
- Framework-specific issues
- Regulatory compliance trends
- Improvement opportunities

### Step 4: Improve - Optimization Planning

**Purpose**: Generate prioritized fixes and improvement plan

```bash
# Continue the Arc Loop
arc-eval improve --from-evaluation latest
```

**What Happens**:
- Impact prediction for recommended changes
- Framework-specific fixes with code examples
- ROI calculation and effort estimation
- Prioritized improvement roadmap

**Output Example**:
```
📈 IMPROVEMENT IMPACT PREDICTION
┌─────────────────────────────────────────────┐
│ Predicted Improvement: +28.3%               │
│ Expected Pass Rate: 89.2% (from 60.9%)     │
│ Implementation Effort: MEDIUM               │
│ Confidence: 0.85                            │
└─────────────────────────────────────────────┘

🎯 RECOMMENDED NEXT STEP:
# Implement fixes, then re-evaluate
arc-eval compliance --domain finance --input improved_outputs.json
```

### Step 5: Re-evaluate - Continuous Refinement

**Purpose**: Test improvements and feed data back into the loop

```bash
# Complete the Arc Loop
arc-eval compliance --domain finance --input improved_outputs.json
arc-eval improve --baseline old_results.json --current new_results.json
```

**What Happens**:
- Validates improvement effectiveness
- Measures progress against baseline
- Updates learning patterns
- Feeds data back into the system for continuous refinement

**Progress Tracking**:
```
📊 IMPROVEMENT TRACKING
════════════════════════════════════════

                    Baseline    Current     Delta
Pass Rate:          60.9%      89.2%      +28.3%
Critical Fails:        12          2         -10
SOX Compliance:       45%        94%       +49%

🔄 LOOP COMPLETION: Ready for next iteration
```

## The Data Flywheel - Self-Improvement Loop

**"Continuous feedback loop that makes ARC-Eval smarter with every evaluation."**

This is the underlying system that enables adaptive learning and scenario generation:

```
Static Domain Knowledge → Dynamic Learning → Performance Analysis → Adaptive Improvement
        ↓                      ↓                    ↓                      ↓
   finance.yaml          ScenarioBank      SelfImprovementEngine    FlywheelExperiment
   (110 scenarios)    (pattern learning)   (performance tracking)    (ACL curriculum)
        ↑                      ↑                    ↑                      ↑
        └──────────────── Continuous Feedback Loop ────────────────────────┘
```

### Component 1: Static Domain Knowledge

**Purpose**: Foundation scenarios and regulatory requirements

**What It Contains**:
- 378 enterprise-grade scenarios
- Regulatory framework mappings
- Domain-specific compliance rules
- Industry best practices

**Files**:
- `scenarios/finance.yaml` (110 scenarios)
- `scenarios/security.yaml` (120 scenarios)
- `scenarios/ml.yaml` (148 scenarios)

### Component 2: Dynamic Learning (ScenarioBank)

**Purpose**: Pattern learning and adaptive scenario generation

**What It Does**:
- Learns from agent failures and successes
- Identifies recurring patterns across frameworks
- Generates new scenarios based on emerging threats
- Adapts difficulty based on agent performance

**Implementation**: `agent_eval/core/scenario_bank.py`

### Component 3: Performance Analysis (SelfImprovementEngine)

**Purpose**: Track performance trends and learning progress

**What It Does**:
- Monitors improvement velocity
- Calculates learning curves
- Identifies performance plateaus
- Recommends optimization strategies

**Implementation**: `agent_eval/analysis/self_improvement.py`

### Component 4: Adaptive Improvement (FlywheelExperiment)

**Purpose**: Curriculum learning and adaptive challenge progression

**What It Does**:
- Adjusts scenario difficulty based on agent readiness
- Implements curriculum learning principles
- Optimizes learning paths for maximum improvement
- Provides personalized challenge progression

## How to Achieve Continuous Improvement

### 1. Start the Arc Loop

**Option A: Complete Workflow (Recommended)**
```bash
# Execute the entire Arc Loop in one command
arc-eval analyze --input your_agent_outputs.json --domain finance
```

**Option B: Step-by-Step Workflow**
```bash
# Begin with debug analysis
arc-eval debug --input your_agent_outputs.json
```

### 2. Follow the Guided Workflow

After each step, ARC-Eval provides clear next step recommendations:

```
🎯 RECOMMENDED NEXT STEP:
arc-eval compliance --domain finance --input your_agent_outputs.json

This will test your agent against 110 finance compliance scenarios
```

### 3. Implement Improvements

Use the specific, actionable recommendations:

```bash
# Get detailed improvement plan
arc-eval improve --from-evaluation latest --framework-specific --code-examples
```

### 4. Track Progress Over Time

```bash
# Compare improvements
arc-eval improve --baseline v1_results.json --current v2_results.json
```

### 5. Automate the Loop

```bash
# Automated continuous improvement
arc-eval analyze --input outputs.json --domain finance --no-interactive
```

## The Analyze Command - One Command, Complete Loop

The `analyze` command is the **recommended entry point** that executes the entire Arc Loop automatically:

```bash
arc-eval analyze --input outputs.json --domain finance
```

**What It Does Automatically**:
1. **🔍 Debug Analysis**: Reliability prediction and failure pattern detection
2. **✅ Compliance Check**: Tests against 378 enterprise scenarios
3. **📈 Improvement Plan**: Generates actionable fixes and recommendations
4. **🎯 Unified Menu**: Provides guided next steps for continuous improvement

**Key Benefits**:
- **Single Command**: Complete workflow in one execution
- **Guided Experience**: Interactive menus guide you through next steps
- **Automation Ready**: Use `--no-interactive` for CI/CD pipelines
- **Domain Focused**: Tailored analysis for finance, security, or ML domains

**Usage Patterns**:
```bash
# First-time evaluation (interactive)
arc-eval analyze --input outputs.json --domain finance

# CI/CD automation (non-interactive)
arc-eval analyze --input outputs.json --domain security --no-interactive

# Quick analysis (skip agent-judge for speed)
arc-eval analyze --input outputs.json --domain ml --quick
```

## Complete Arc Loop Example

Here's a complete example of running the Arc Loop:

```bash
# Step 1: Debug Analysis
arc-eval debug --input agent_outputs.json
# Output: Risk Level MEDIUM, suggests compliance check

# Step 2: Compliance Validation  
arc-eval compliance --domain finance --input agent_outputs.json
# Output: 67% pass rate, 3 critical failures

# Step 3: Generate Improvement Plan
arc-eval improve --from-evaluation latest --framework-specific
# Output: Predicted +28.3% improvement, specific fixes

# Step 4: Implement fixes (your development work)
# ... implement recommended changes ...

# Step 5: Re-evaluate Progress
arc-eval compliance --domain finance --input improved_outputs.json
# Output: 89.2% pass rate, 2 critical failures

# Step 6: Track Improvement
arc-eval improve --baseline old_results.json --current new_results.json
# Output: +28.3% improvement confirmed, next optimization targets
```

## Key Success Metrics

### Arc Loop Effectiveness
- **Debugging Time**: 4+ hours → 5 minutes
- **Compliance Violations**: Prevent $250K+ fines
- **Prediction Accuracy**: 85%+ reliability prediction
- **Improvement Velocity**: +2-5% pass rate per iteration

### Data Flywheel Growth
- **Scenario Coverage**: 378 → expanding based on patterns
- **Framework Support**: 10+ frameworks with growing intelligence
- **Pattern Recognition**: Improves with each evaluation
- **Adaptive Learning**: Personalized improvement paths

## Best Practices

### 1. Complete Full Loops
Don't skip steps - each step feeds valuable data into the system

### 2. Regular Iteration
Run the Arc Loop weekly or after significant agent changes

### 3. Track Metrics
Monitor improvement velocity and learning progress

### 4. Leverage Automation
Use CI/CD integration for continuous loop execution

### 5. Feed the Flywheel
More evaluations = smarter recommendations and better predictions

## Next Steps

- [Workflows Guide](workflows/) - Detailed workflow documentation
- [Quick Start](quickstart.md) - Get started in 5 minutes
- [Enterprise Integration](enterprise/) - Automate the loops in production
- [API Reference](api/) - Programmatic loop execution

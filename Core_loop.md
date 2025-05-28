# **ARC-Eval Core Loop Completion Plan**
*From "Nice-to-Have Tool" to "Weekly-Use Engine"*

## **Strategic Context: Vitamin vs. Painkiller**

**Current Problem**: ARC-Eval provides excellent evaluation but ends at chat. Enterprise customers get insights but no clear path to action, resulting in one-off usage rather than weekly engagement.

**Solution**: Complete the feedback loop using existing components to create a "painkiller" that drives repeated usage through measurable improvement cycles.

## **Current State Analysis**

### ** What We Have (Strong Foundation)**
- Robust evaluation platform with 345+ domain-specific scenarios
- Agent-as-a-Judge framework with domain expertise
- Interactive chat UI for result analysis
- **Self-improvement engine already built** (`agent_eval/analysis/self_improvement.py`)
- Performance tracking and reliability validation
- PDF/CSV export capabilities

### **L What's Missing (The Critical Gap)**
```
Current: Evaluate � Report � Chat � ??? (Manual figuring out)
Needed: Evaluate � Report � Actionable Plan � Re-evaluate � Validate Improvement
```

**The core insight**: We already built the missing pieces in `self_improvement.py` - they just need to be connected to the main workflow.

## **The "One-Loop, Zero-Bloat" Strategy**

### **Goal**: Transform ARC-Eval from assessment tool to improvement system without feature bloat

### **Principle**: Leverage existing code, don't build new features until core loop is validated

## **Implementation Plan**

### **Phase 1: Wire Existing Components (2 Weeks)**

#### **Week 1: Auto-Improvement Plan Generation**
**Leverage**: `analysis/self_improvement.py` functions:
- `generate_training_examples()` 
- `create_improvement_curriculum()`
- `should_trigger_retraining()`

**New CLI Integration**:
```bash
# After standard evaluation
arc-eval --domain finance --input outputs.json --agent-judge

# Generate improvement plan (NEW)
arc-eval --improve --based-on last_evaluation.json

# Output: improvement_plan.md with prioritized actions
```

#### **Week 2: Before/After Comparison**
**Leverage**: Existing performance tracking utilities

**New CLI Integration**:
```bash
# Re-evaluate with comparison (NEW)
arc-eval --domain finance --input improved_outputs.json --compare-to baseline_eval.json

# Shows: scenarios that improved, degraded, trend analysis
```

### **Phase 2: The Improvement Plan Artifact**

**Design**: One-page, action-oriented document

```markdown
<� IMPROVEMENT PLAN: snowflake_sales_agent

CRITICAL  Fix PII exposure (fails SEC_004, SEC_009)
          " Action: Update prompt to redact {customer_name} � <redacted>
          " Expected: Pass rate � from 60% to 90%
          " Timeline: 2 days

HIGH      Reduce bias in loan recommendations (fails FIN_012) 
          " Action: Add demographic-blind evaluation criteria
          " Expected: Bias score � from 0.8 to <0.3
          " Timeline: 1 week

MEDIUM    Improve error handling (fails REL_003)
          " Action: Add input validation and graceful degradation
          " Expected: Reliability score � from 0.6 to >0.8
          " Timeline: 3 days

WHEN DONE � Re-run evaluation:
arc-eval --domain finance --input outputs.json --compare-to 2025-05-28_baseline.json
```

**Features**:
- **One-click copy** into tickets/PRs
- **Priority tied to risk severity**
- **Expected deltas make value measurable**
- **Clear next steps for validation**

### **Phase 3: Enhanced User Experience**

#### **Complete Workflow Integration**:
```bash
# Step 1: Initial evaluation
arc-eval --domain finance --input outputs.json --agent-judge
# � Generates: baseline_2025-05-28.json

# Step 2: Get improvement plan  
arc-eval --improve --from baseline_2025-05-28.json
# � Generates: improvement_plan.md

# Step 3: After implementing fixes
arc-eval --domain finance --input improved_outputs.json --compare-to baseline_2025-05-28.json
# � Shows: before/after diff, improvement metrics, trend analysis
```

#### **Progress Tracking Dashboard**:
- Historical improvement data
- Scenario-level pass/fail trends
- ROI measurement for stakeholders
- Audit trail for compliance teams

## **Validation Metrics for Weekly Stickiness**

| Metric | Success Threshold | Where to Track |
|--------|------------------|----------------|
| **Eval runs per agent per week** | e 3 runs | CLI usage analytics |
| **Improvement plans executed** | e 50% within 7 days | Follow-up evaluation tracking |
| **Violation reduction after plan** | e 30% decrease | Before/after comparison reports |
| **Multi-week retention** | e 80% of pilots use for 4+ weeks | Customer usage dashboards |

**Kill Criteria**: If pilots don't cross these thresholds � core loop isn't compelling enough

## **Customer Use Case Validation**

### **For Snowflake GTM Team**:
1. **Evaluate** sales agent before customer demo
2. **Get specific actions**: "Fix bias in loan recommendations, add PII redaction"  
3. **Implement changes** to agent prompts/logic
4. **Re-evaluate** to prove improvements for demo confidence
5. **Show progress** to stakeholders with trend charts

### **For NVIDIA Solutions Architects**:
1. **Evaluate** customer-facing workflow agents
2. **Get compliance checklist** for enterprise deployment
3. **Validate fixes** meet customer security requirements
4. **Document improvement** for customer presentations

### **For BlackRock Compliance**:
1. **Evaluate** internal financial agents
2. **Get regulatory gap analysis** with specific remediations
3. **Prove compliance** through before/after evaluation
4. **Maintain audit trail** for regulatory reviews

## **Why NOT to Add Complex Features Yet**

### **L Automated Retraining Service**
- **Complexity**: GPU infrastructure, model versioning, rollback UX
- **Validation Risk**: If customers won't act on generated plans, they won't trust automated retraining
- **Sales Motion**: Need proof of measured improvement to earn right to sell "1-click retrain"

### **L GRC Platform Integration**
- **Unknown Workflows**: Need to understand how customers actually use GRC systems
- **Complex Personas**: Involves compliance teams, not just technical users
- **Longer Validation**: Enterprise compliance decisions take months

### **L PyRIT Red Teaming Enhancement**
- **Feature Creep**: Adds complexity before core value is proven
- **Customer Confusion**: Unclear if enhanced scenarios provide proportional value
- **Resource Drain**: Diverts focus from core loop validation

## **Pilot Validation Script**

### **Week 1: Baseline & Plan Generation**
1. **Day 0**: Run baseline evaluation together on customer logs
2. **Day 0**: Hand them auto-generated improvement plan
3. **Day 1**: Book follow-up for Day 7 re-evaluation
4. **Days 2-6**: Customer implements suggested fixes

### **Week 2: Validation & Measurement**
1. **Day 7**: Re-run evaluation with `--compare-to` baseline
2. **Day 7**: Show red�green scenario improvements
3. **Day 8**: Capture feedback: "Would you pay $X/month for this workflow?"
4. **Day 9**: Analyze usage metrics against success thresholds

### **Success Indicators**:
- Customer implements e50% of suggested improvements
- Evaluation metrics show e30% improvement
- Customer requests to continue using the tool
- Customer indicates willingness to pay for continued access

## **Technical Implementation Details**

### **Existing Components to Leverage**:
```python
# agent_eval/analysis/self_improvement.py
- generate_training_examples()      # � Convert to improvement actions
- create_improvement_curriculum()   # � Prioritize by impact/effort  
- should_trigger_retraining()      # � Trigger improvement plan generation
- get_performance_trends()         # � Show progress over time
```

### **New Integration Points**:
```python
# Enhanced CLI commands
arc-eval --improve --from {evaluation_id}
arc-eval --compare-to {baseline_evaluation}  
arc-eval --performance-trends --agent-id {agent_identifier}

# New output formats
improvement_plan.md                # Actionable improvement document
comparison_report.json            # Before/after evaluation results
trend_analysis.html               # Historical progress visualization
```

### **Data Flow Enhancement**:
```
Agent Output � Domain Judge � Assessment � Improvement Plan � Re-evaluation � Trend Analysis
```

## **Success Criteria & Decision Points**

### **4-Week Validation Timeline**:
- **Week 1-2**: Implement core loop features
- **Week 3-4**: Test with all current pilots (Snowflake, NVIDIA, Palo Alto, BlackRock)
- **Decision Point**: If e75% of pilots show weekly usage � proceed to scale
- **Pivot Point**: If <50% of pilots engage weekly � reassess core value proposition

### **Business Impact Metrics**:
- **Customer Retention**: e80% of pilots continue past 4 weeks
- **Usage Frequency**: e3 evaluation cycles per agent per week
- **Improvement Validation**: e70% of improvement plans show measurable results
- **Willingness to Pay**: e60% of pilots indicate payment intent

## **Next Steps (Immediate Actions)**

### **This Week**:
1. **Analyze existing `self_improvement.py`** - map functions to improvement plan generation
2. **Design improvement plan template** - create actionable, one-page format
3. **Prototype CLI integration** - wire `--improve` flag to existing functions

### **Next Week**:
1. **Implement comparison functionality** - before/after evaluation analysis
2. **Test with one pilot customer** - validate full loop with Snowflake or NVIDIA
3. **Measure engagement metrics** - track usage patterns and customer feedback

### **Week 3-4**:
1. **Roll out to all pilots** - systematic validation across customer base
2. **Collect validation data** - usage metrics, improvement outcomes, payment intent
3. **Make go/no-go decision** - validate core loop before considering feature expansion

**Bottom Line**: Complete the feedback loop with existing components to create measurable customer value and weekly engagement before adding any new features or complexity.

---

## **Research Validation & Advanced Enhancements**

### **Latest ArXiv Research Validation (2024-2025)**

Our Core Loop plan is **exceptionally well-positioned** based on cutting-edge research:

#### **✅ Agent-as-a-Judge Framework (arXiv:2410.10934v2)**
- **Research Finding**: Agent-as-a-Judge creates "flywheel effects" where successive improvements reinforce each other
- **Our Implementation**: Domain judges + improvement feedback loop creates exactly this flywheel
- **Validation**: Intermediate feedback is essential for effective optimization - our improvement plans provide this

#### **✅ Self-Improvement Loops (SEFL 2025 - arXiv:2502.12927v1)**  
- **Research Finding**: SEFL-tuned models outperform non-tuned counterparts through feedback loops
- **Our Implementation**: Evaluate → Improve → Re-evaluate → Track progress cycle
- **Validation**: Two-agent systems (Teacher/Student) work best - similar to our Agent-as-a-Judge + Human implementer

#### **✅ Continuous Learning Evaluation (Survey 2025 - arXiv:2503.16416v1)**
- **Research Finding**: Memory of previous interactions crucial for continuous improvement
- **Our Implementation**: `RewardSignalHistory` captures historical context and patterns
- **Validation**: StreamBench shows agents with memory show better improvement - we already have this

#### **✅ Fine-Grained Evaluation Metrics (2025 Survey)**
- **Research Gap**: "Many benchmarks rely on coarse-grained metrics that fall short in diagnosing specific failures"
- **Our Advantage**: 345+ scenario-level evaluation with specific failure reasons and compliance mapping
- **Enhancement Opportunity**: Add trajectory-level tracking within scenarios

### **Research-Backed Enhancement Opportunities**

#### **Phase 1 Enhancements (Based on Latest Research)**

##### **Memory-Augmented Feedback** (StreamBench 2024)
```python
# Enhanced memory integration for improvement planning
def generate_improvement_plan_with_memory(self, agent_id: str, domain: str):
    historical_patterns = self._analyze_failure_patterns(agent_id, domain)
    recurring_issues = self._identify_recurring_failures(agent_id, domain)
    # Generate plans that account for historical context and prevent regression
```

##### **Trajectory-Level Evaluation** (2025 Research)
```python
# Track step-by-step agent decision processes within scenarios
@dataclass
class TrajectoryEvaluation:
    scenario_id: str
    decision_steps: List[Dict[str, Any]]  # Each decision point in agent reasoning
    failure_point: Optional[int]  # Which step caused failure
    alternative_paths: List[str]  # Suggested alternative decisions
```

##### **Multi-Judge Consensus** (Meta-Judge Framework 2024)
- **Research Finding**: 15.55% improvement with multi-agent evaluation vs single judge
- **Implementation**: Leverage existing `judge_comparison.py` for high-stakes scenarios
- **Use Case**: Critical compliance scenarios get multiple judge validation

#### **Research-Informed Success Metrics**
```python
# Add to validation metrics based on SEFL and continuous learning research
validation_metrics = {
    "feedback_quality_score": 0.0,      # Measured improvement in recommendation clarity
    "learning_velocity": 0.0,           # Rate of improvement acceleration over time  
    "memory_utilization": 0.0,          # How well agents leverage historical feedback
    "trajectory_completion": 0.0,       # Success rate in multi-step improvement processes
    "consensus_accuracy": 0.0           # Multi-judge agreement on critical scenarios
}
```

### **Phase 2 Research-Backed Enhancements**

#### **Curriculum Learning Integration** (Syllabus 2024 - arXiv:2411.11318v1)
- **Research**: Universal API for curriculum learning algorithms shows significant improvement
- **Our Implementation**: Enhance `create_improvement_curriculum()` with progressive difficulty
- **Benefit**: Systematic skill building rather than ad-hoc improvements

#### **Self-Referential Improvement** (Gödel Agent 2024 - arXiv:2410.04444)
- **Research**: Agents that recursively improve themselves without predefined routines
- **Our Implementation**: Auto-trigger improvement when performance degrades
- **Benefit**: Proactive improvement detection vs reactive manual intervention

---

## **TODO: Implementation Tasks**

### **Phase 1: Week 1 - Improvement Plan Generation**

#### **CLI Enhancement**
- [ ] **T1.1**: Add `--improve` flag to `agent_eval/cli.py`
- [ ] **T1.2**: Add `--from` parameter to specify evaluation JSON file
- [ ] **T1.3**: Wire CLI flag to existing `self_improvement.py` functions
- [ ] **T1.4**: Add error handling for missing evaluation files

#### **Improvement Plan Generator**
- [ ] **T1.5**: Create `agent_eval/core/improvement_planner.py`
- [ ] **T1.6**: Implement `generate_improvement_plan()` function using existing curriculum logic
- [ ] **T1.7**: Create improvement plan Markdown template
- [ ] **T1.8**: Add priority calculation based on scenario severity and confidence
- [ ] **T1.9**: Map judgment results to actionable recommendations

#### **Output Formatting**
- [ ] **T1.10**: Design improvement plan template (see Phase 2 example)
- [ ] **T1.11**: Add timeline estimation for each improvement action
- [ ] **T1.12**: Include expected impact metrics (pass rate improvement, etc.)
- [ ] **T1.13**: Add "next steps" section with re-evaluation command

#### **Testing**
- [ ] **T1.14**: Create test evaluation JSON files for each domain
- [ ] **T1.15**: Test improvement plan generation with sample data
- [ ] **T1.16**: Validate improvement plan readability and actionability
- [ ] **T1.17**: Test CLI integration end-to-end

#### **Research-Backed Enhancements (Phase 1)**
- [ ] **T1.18**: Implement trajectory-level evaluation tracking within scenarios
  - Based on 2025 research: "fine-grained evaluation metrics needed for specific failure diagnosis"
  - Track step-by-step agent decision processes for deeper failure analysis
- [ ] **T1.19**: Add failure pattern recognition using historical data
  - Based on StreamBench 2024: memory-augmented feedback shows better improvement
  - Implement `_identify_recurring_failures()` to prevent regression
- [ ] **T1.20**: Enhance improvement plan generation with historical context
  - Based on SEFL 2025: feedback loops with memory outperform static approaches
  - Generate plans that account for previous failure patterns

### **Phase 1: Week 2 - Comparison Functionality**

#### **CLI Enhancement**
- [ ] **T2.1**: Add `--compare-to` flag to `agent_eval/cli.py`
- [ ] **T2.2**: Add baseline evaluation storage and retrieval
- [ ] **T2.3**: Wire comparison flag to evaluation engine
- [ ] **T2.4**: Add validation for compatible evaluation formats

#### **Comparison Engine**
- [ ] **T2.5**: Create `agent_eval/core/comparison_engine.py`
- [ ] **T2.6**: Implement `compare_evaluations()` function
- [ ] **T2.7**: Calculate scenario-level improvement deltas
- [ ] **T2.8**: Generate before/after summary statistics
- [ ] **T2.9**: Identify scenarios that flipped from fail to pass

#### **Results Visualization**
- [ ] **T2.10**: Create comparison report template
- [ ] **T2.11**: Add trend visualization (pass rate over time)
- [ ] **T2.12**: Include improvement metrics dashboard
- [ ] **T2.13**: Add export functionality for comparison reports

#### **Data Persistence**
- [ ] **T2.14**: Design evaluation storage format
- [ ] **T2.15**: Add evaluation ID and timestamp tracking
- [ ] **T2.16**: Implement evaluation history management
- [ ] **T2.17**: Add cleanup for old evaluation files

#### **Research-Backed Enhancements (Phase 1 Continued)**
- [ ] **T2.18**: Implement multi-judge consensus for critical scenarios (Optional)
  - Based on Meta-Judge Framework 2024: 15.55% improvement with multi-agent evaluation
  - Use existing `judge_comparison.py` for high-stakes compliance scenarios
- [ ] **T2.19**: Add research-validated success metrics tracking
  - Feedback quality score, learning velocity, memory utilization
  - Based on SEFL and continuous learning research findings
- [ ] **T2.20**: Enhanced trajectory visualization for failure analysis
  - Show step-by-step decision processes where agents failed
  - Enable targeted improvements at specific decision points

### **Phase 2: Enhanced Integration**

#### **Workflow Integration**
- [ ] **T3.1**: Auto-generate evaluation IDs for tracking
- [ ] **T3.2**: Store evaluation metadata (agent_id, domain, timestamp)
- [ ] **T3.3**: Link improvement plans to original evaluations
- [ ] **T3.4**: Add agent performance trend tracking

#### **User Experience**
- [ ] **T3.5**: Add progress indicators for multi-step workflows
- [ ] **T3.6**: Improve error messages and user guidance
- [ ] **T3.7**: Add `--help` documentation for new flags
- [ ] **T3.8**: Create quick-start guide for core loop workflow

#### **Validation & Metrics**
- [ ] **T3.9**: Add usage analytics tracking
- [ ] **T3.10**: Implement engagement metrics collection
- [ ] **T3.11**: Create customer feedback collection system
- [ ] **T3.12**: Add success criteria measurement dashboard

#### **Phase 2 Research Integration (Future)**
- [ ] **T3.13**: Curriculum learning integration (Syllabus framework)
  - Progressive difficulty in improvement plans based on agent capability
  - Systematic skill building rather than ad-hoc improvements
- [ ] **T3.14**: Self-referential improvement triggers (Gödel Agent approach)
  - Auto-detect when agents need improvement without manual intervention
  - Proactive improvement rather than reactive manual detection
- [ ] **T3.15**: Advanced memory utilization metrics
  - Track how effectively agents use historical feedback for improvement
  - Measure prevention of recurring failures through memory integration

### **Phase 3: Customer Validation**

#### **Pilot Testing**
- [ ] **T4.1**: Prepare pilot testing script (see validation section)
- [ ] **T4.2**: Create customer onboarding materials for core loop
- [ ] **T4.3**: Set up metrics collection for pilot validation
- [ ] **T4.4**: Schedule pilot validation sessions with existing customers

#### **Feedback Collection**
- [ ] **T4.5**: Design customer feedback surveys
- [ ] **T4.6**: Implement feedback collection system
- [ ] **T4.7**: Create metrics dashboard for success criteria tracking
- [ ] **T4.8**: Set up automated reporting for validation metrics

#### **Documentation**
- [ ] **T4.9**: Update README.md with core loop workflow
- [ ] **T4.10**: Create user guide for improvement workflow
- [ ] **T4.11**: Add examples for each phase of the core loop
- [ ] **T4.12**: Document success criteria and metrics

### **Definition of Done**

#### **Week 1 Complete When**:
- [ ] `arc-eval --improve --from eval.json` generates actionable improvement plan
- [ ] Improvement plan includes prioritized actions with expected outcomes
- [ ] All tests pass and CLI integration works end-to-end

#### **Week 2 Complete When**:
- [ ] `arc-eval --compare-to baseline.json` shows before/after improvements
- [ ] Comparison report clearly indicates scenario-level changes
- [ ] Evaluation history is properly stored and retrievable

#### **Pilot Ready When**:
- [ ] Complete workflow tested: evaluate � improve � re-evaluate � compare
- [ ] Customer-facing documentation complete
- [ ] Metrics collection system operational
- [ ] At least one successful end-to-end test with sample customer data

#### **Success Validation When**:
- [ ] ≥75% of pilot customers complete full improvement cycle
- [ ] ≥50% of improvement plans show measurable results
- [ ] ≥60% of customers indicate willingness to pay for continued access
- [ ] Usage metrics show ≥3 evaluation cycles per week per agent

#### **Research-Validated Success Criteria**:
- [ ] **Feedback Quality**: ≥80% of improvement recommendations rated as "actionable" by customers
- [ ] **Learning Velocity**: ≥20% improvement acceleration in subsequent evaluation cycles
- [ ] **Memory Utilization**: ≥60% reduction in recurring failure patterns after implementation
- [ ] **Trajectory Completion**: ≥70% of multi-step improvement processes completed successfully
- [ ] **Research Alignment**: Core loop demonstrates "flywheel effects" as validated by Agent-as-a-Judge research

### **Research Bibliography**

**Core Research Validating Our Approach**:
1. **Agent-as-a-Judge: Evaluate Agents with Agents** (arXiv:2410.10934v2) - Validates our domain judge + improvement feedback loop
2. **SEFL: Harnessing Large Language Model Agents to Improve Educational Feedback Systems** (arXiv:2502.12927v1) - Validates continuous improvement through feedback loops
3. **Survey on Evaluation of LLM-based Agents** (arXiv:2503.16416v1) - Validates memory-augmented feedback and fine-grained evaluation
4. **Syllabus: Portable Curricula for Reinforcement Learning Agents** (arXiv:2411.11318v1) - Validates curriculum-based improvement planning
5. **Gödel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement** (arXiv:2410.04444) - Validates self-triggering improvement systems

**Key Research Insights Applied**:
- **Flywheel Effects**: Successive improvements reinforce each other (Agent-as-a-Judge)
- **Memory Importance**: Historical context crucial for continuous improvement (LLM Agent Survey)
- **Fine-Grained Metrics**: Scenario-level evaluation outperforms coarse metrics (Multiple papers)
- **Curriculum Learning**: Progressive improvement plans more effective than ad-hoc fixes (Syllabus)
- **Self-Improvement**: Automated improvement triggers outperform manual detection (Gödel Agent)

**Research-to-Practice Translation**:
Our Core Loop plan implements cutting-edge research findings in a practical, enterprise-ready system that addresses real customer needs while advancing the state of agent evaluation and improvement.
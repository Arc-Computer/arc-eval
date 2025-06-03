# Customer-Focused Roadmap: Runtime Tracing Integration

> **Goal**: Deliver "accuracy metric + cost optimization" to agent-hosting platforms with minimal new code by leveraging our existing 15,000+ LOC evaluation infrastructure.

## **Customer Problem Analysis**

### **Rank-Ordered Problem Statements from Customer Interviews**

| **#** | **Problem Statement** | **Evidence from Calls/Advisors** | **Our Solution** |
|---|---|---|---|
| **1** | **"Will this agent finish the task correctly every time?"**<br>*(objective success-rate / accuracy)* | • Prospect: *"If you can tell us an agent's success-rate we'll use it."*<br>• Advisor: "Map how your solution addresses reliability." | **reliability score + grade + trend**<br>Enhanced tracing → ComprehensiveReliabilityAnalysis |
| **2** | **"How much cost and latency is this agent burning?"**<br>*(token spend, tool-call overhead, model choice)* | • Multiple builders complain about high inference bills<br>• Advisor: "Inference cost will be reduced by profiling bottlenecks… lower TCO." |  **$0.013/run + 22% optimization + model rec**<br>Cost tracking → APIManager optimization engine |
| **3** | **"What will break when real traffic hits?"**<br>*(runtime edge-cases, silent failures)* | • Prospect worries about leaks/loops only visible under load<br>• Synthetic-scenario pitch resonated because QA misses these | **Pattern learning + auto-generated scenarios**<br>ScenarioBank → adaptive edge case detection |
| **4** | **"I need a zero-SDK way to validate any agent, any framework."** | • Host platform doesn't want another dependency<br>• Drag-&-drop trace workflow seen as big win |  **Enhanced trace_agent() decorator**<br>Framework detection → universal compatibility |
| **5** | **"Give me actionable fixes, not just red lights."** | • Prospect liked patch-diff idea<br>• Pain: dashboards show errors but no guided optimization |  **Ready-to-apply patches + code examples**<br>RemediationEngine → framework-specific fixes |
| **6** | **"My customers need proof the agent is good."**<br>*(shareable metric for B2B platforms)* | • Hosting platform wants to surface reliability score to end-users |  **Web workbench + shareable reports**<br>Executive dashboard → customer-facing metrics |
| **7** | **"Prevent data leakage or compliance breaches at runtime."** | • Prospect's first push-back: output-only checks miss hidden SSN leak<br>• Advisors flag this as high future value |  **Runtime pattern detection (Phase 2)**<br>Live tracing → privacy violation detection |
| **8** | **"Eventually auditors will ask for GDPR / HIPAA attestations."**<br>*(formal compliance)* | • Buyers acknowledge "not urgent today" but will become mandatory |  **Compliance packs (roadmap)**<br>Domain evaluations → audit-ready reports |

### **Customer Priority Mapping**

**Burning Pains (Problems 1-3)**: Immediate adoption drivers
- **Week 1 delivery**: Reliability score, cost optimization, runtime edge case detection
- **Customer validation**: *"Success-rate 87% (+16pp improvement). Cost ↓22% with Cerebras."*

**Differentiation (Problems 4-6)**: Competitive advantages 
- **Arc today**: Zero-SDK, actionable fixes, shareable metrics
- **vs. Competitors**: Intelligence and learning, not just monitoring

**Roadmap Growth (Problems 7-8)**:
- **Compliance timing**: Secondary concern now, foreground later as AI governance hardens  
- **Runtime leak detection**: High future value as privacy regulations tighten

**Bottom line**: Customer interviews confirm our enhanced tracing approach addresses the exact pain points driving immediate purchasing decisions while positioning us for future growth.

---

## **Full System Data Requirements**

### **Arc Loop Data Dependencies**

Our existing [Arc Loop](docs/core-loops.md) requires comprehensive data capture to deliver full value:

| **Arc Loop Step** | **Required Runtime Data** | **Why Critical** |
|---|---|---|
| **🔍 Debug** | Tool calls, reasoning chains, framework metadata, error traces | Framework detection, tool validation, cognitive analysis |
| **📋 Compliance** | Scenario context, reward signals, compliance violations | Domain evaluation, regulatory mapping |
| **📊 Dashboard** | Performance metrics, pattern fingerprints, learning trends | Progress tracking, pattern recognition |
| **📈 Improve** | Failure classifications, remediation data, agent configs | Improvement planning, fix generation |
| **🔄 Re-evaluate** | Historical comparisons, baseline metrics | Progress validation, continuous learning |

### **Data Flywheel Dependencies**

The [self-improving system](docs/core-loops.md#the-data-flywheel---self-improvement-loop) requires:

| **Component** | **Required Data** | **Impact if Missing** |
|---|---|---|
| **ScenarioBank** | Failure patterns, compliance violations, remediation context | ❌ No adaptive scenario generation |
| **SelfImprovementEngine** | Reward signals, scenario IDs, performance trends | ❌ No learning tracking or curriculum |
| **Pattern Learning** | Recurring failure fingerprints, domain classifications | ❌ No pattern recognition or fixes |
| **Adaptive Curriculum** | Learning progress, difficulty progression data | ❌ No personalized improvement paths |

**Risk**: Simple wrapper breaks 80% of system value - customer gets basic metrics but loses the intelligent analysis that differentiates us.

---

##  **What We Already Built**

### **Evaluation Infrastructure**

| **Customer Need** | **Existing Implementation** | **File** | **LOC** |
|---|---|---|---|
| **Reliability scoring** | `ComprehensiveReliabilityAnalysis` | `evaluation/reliability_validator.py` | 2,900+ |
| **Cost optimization** | Token tracking, model recommendations | `evaluation/judges/api_manager.py` | 1,000+ |
| **Failure classification** | Universal pattern detection | `analysis/universal_failure_classifier.py` | 650+ |
| **Self-improvement loop** | Reward signals, curriculum generation | `analysis/self_improvement.py` | 714 |
| **Scenario generation** | Adaptive synthetic scenarios | `core/scenario_bank.py` | 468 |
| **Framework intelligence** | Migration insights, optimizations | `core/framework_intelligence.py` | 580+ |
| **Fix generation** | Remediation engine with code examples | `analysis/remediation_engine.py` | 600+ |

### **Existing Customer Value Available Today**

```bash
# These commands already deliver the customer value:
arc-eval debug --input agent_trace.json --pattern-analysis --root-cause
# → "Tool call accuracy: 73%, Framework: LangChain, 4 optimization opportunities"

arc-eval compliance --domain finance --input traces.json --hybrid-qa
# → "Pass rate: 87%, Cost: $0.013/scenario, 3 critical fixes available"

arc-eval improve --auto-detect --framework-specific --code-examples
# → "Generated 12 improvement actions, Est. 22% cost reduction"
```

---

## **What We Need to Build (Minimal Integration)**

### **Simple 3-Component Integration**

**Problem**: Runtime traces need to flow through our existing Data Flywheel  
**Solution**: Minimal wrapper + data routing + web display (NO new intelligence code)

```python
# NEW FILE: agent_eval/trace/wrapper.py (~120 LOC)
def trace_agent(agent_func, domain: str = "auto"):
    """Capture runtime data in format our existing systems expect"""
    @wraps(agent_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Capture data for existing ReliabilityAnalyzer
        trace_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": generate_agent_id(agent_func),
            "domain": domain,
            "framework": detect_framework_advanced(),
            "tool_calls": [],
            "performance_metrics": {"start_time": start_time},
            "cost_data": {"model_calls": []}
        }
        
        # Hook tool calls for existing analysis
        with tool_call_interceptor() as interceptor:
            try:
                result = agent_func(*args, **kwargs)
                trace_data.update({
                    "output": result,
                    "success": True,
                    "execution_time": time.time() - start_time,
                    "tool_calls": interceptor.get_tool_calls(),
                    "cost_data": interceptor.get_cost_data()
                })
            except Exception as e:
                trace_data.update({
                    "error": str(e),
                    "success": False,
                    "execution_time": time.time() - start_time
                })
                raise
            
        # Save for existing batch processing
        save_trace_for_existing_analysis(trace_data)
        return result
    return wrapper

# NEW FILE: agent_eval/trace/integration.py (~50 LOC)
class DataFlowIntegration:
    """Route traces through existing analysis systems"""
    
    def __init__(self):
        # Use existing systems - don't rebuild
        self.reliability_analyzer = ReliabilityAnalyzer()
        self.self_improvement = SelfImprovementEngine()
        self.scenario_bank = ScenarioBank()
        
    def process_runtime_traces(self, traces: List[Dict]) -> Dict[str, Any]:
        """Process through existing flywheel - zero new analysis code"""
        
        # 1. Use existing ReliabilityAnalyzer (2,900+ LOC already built)
        analysis = self.reliability_analyzer.generate_comprehensive_analysis(traces)
        
        # 2. Use existing SelfImprovementEngine (714 LOC already built)
        if traces:
            agent_id = traces[0].get('agent_id')
            domain = traces[0].get('domain', 'auto')
            evaluation_results = self._convert_to_evaluation_format(traces)
            self.self_improvement.record_evaluation_result(agent_id, domain, evaluation_results)
        
        # 3. Use existing ScenarioBank (468 LOC already built)
        for trace in traces:
            if not trace.get('success'):
                pattern = self._extract_pattern_for_existing_bank(trace)
                self.scenario_bank.add_pattern(pattern)
        
        return {"analysis": analysis, "traces_processed": len(traces)}

# NEW FILE: agent_eval/web/runtime_server.py (~100 LOC)
from fastapi import FastAPI
from agent_eval.analysis.interactive_analyst import InteractiveAnalyst  # Use existing chat

app = FastAPI()

@app.get("/api/runtime-analysis")
def get_runtime_analysis():
    """Display results from existing systems"""
    
    # Use existing integration
    integration = DataFlowIntegration()
    traces = load_latest_traces()
    results = integration.process_runtime_traces(traces)
    
    analysis = results["analysis"]
    
    # Return data from existing systems
    return {
        "reliability_score": analysis.workflow_metrics.workflow_success_rate,
        "cost_per_run": calculate_cost_from_traces(traces),
        "framework_detected": analysis.detected_framework,
        "recommendations": analysis.next_steps[:3],
        "chat_ready": True  # Existing InteractiveAnalyst available
    }

@app.post("/api/chat")
def chat_with_analysis(message: str):
    """Use existing InteractiveAnalyst - zero new chat code"""
    analyst = InteractiveAnalyst()  # Existing 600+ LOC system
    return analyst.process_query(message, context="runtime_traces")

# Web UI: Just display existing data + embed existing chat
```

**Integration Points**: 
- Traces saved in format existing `ReliabilityAnalyzer` expects
- Existing `SelfImprovementEngine` processes learning automatically  
- Existing `InteractiveAnalyst` provides chat interface
- Existing `ScenarioBank` learns patterns automatically

---

## 📊 **Actual Implementation Summary**

### **New Code Required**: ~270 LOC (Minimal Integration)
```
agent_eval/trace/
├── wrapper.py           # 120 LOC - Runtime capture in existing format
├── integration.py       #  50 LOC - Route to existing systems
└── utils.py            #  20 LOC - Helper functions

agent_eval/web/
├── runtime_server.py    #  60 LOC - Display existing analysis results
└── static/runtime.html  #  20 LOC - Simple UI + embed existing chat

Modified files:         #  20 LOC - CLI integration
```

### **Existing Systems Leveraged**: 15,000+ LOC (Zero Rebuild)
- ✅ `ReliabilityAnalyzer` (2,900+ LOC) - comprehensive analysis
- ✅ `SelfImprovementEngine` (714 LOC) - curriculum & learning 
- ✅ `ScenarioBank` (468 LOC) - pattern learning & scenarios
- ✅ `InteractiveAnalyst` (600+ LOC) - chat interface
- ✅ All other analysis infrastructure

---

## 🎯 **Simplified Customer Demo Script**

### **Demo Flow**:
```bash
# 1. Setup (10 seconds)
arc-eval connect --framework=langchain --domain=finance
# Generates: agent = trace_agent(agent, domain="finance")

# 2. Runtime Collection (30 seconds) 
# Customer runs agent with wrapper, traces auto-collected

# 3. View Results (30 seconds)
arc-eval debug --live  # Uses existing debug command + live traces
# OR visit web interface showing existing analysis
```

### **Demo Output (Using ALL Existing Systems)**:
```
🎯 Runtime Analysis (Existing Intelligence)

🤖 FRAMEWORK DETECTION (Existing)
Framework: LangChain (94% confidence, auto-detected)
Domain: Finance (mapped to existing compliance scenarios)

✅ RELIABILITY ANALYSIS (Existing ReliabilityAnalyzer)
Score: 87% (Grade: B, improving trend from existing tracking)
Tool Accuracy: 91% (existing tool validation system)

💸 COST OPTIMIZATION (Existing APIManager)
Cost/run: $0.013 (existing cost tracking)
Optimization: ↓22% → Cerebras (existing model recommendations)

🔍 PATTERN LEARNING (Existing ScenarioBank)  
Patterns learned: 3 new failure scenarios auto-generated
Available in existing scenario library

📈 CURRICULUM (Existing SelfImprovementEngine)
Learning velocity: +16% improvement identified
Curriculum: Ready for intermediate progression (existing system)

💬 CHAT READY (Existing InteractiveAnalyst)
"Why are tool calls failing?" → Chat with existing analyst

🎓 NEXT STEPS (Existing Arc Loop)
All existing commands work with runtime data:
└─ arc-eval compliance --domain finance --live
└─ arc-eval improve --from-evaluation latest  
└─ arc-eval analyze --input runtime_traces.json
```

---

## 🛡️ **Zero-Risk Implementation**

### **No System Changes**:
- ❌ **Don't modify**: Any existing analysis systems
- ✅ **Do add**: Minimal wrapper + data routing + display
- 🎯 **Result**: All existing intelligence + runtime data

### **Backward Compatibility**:
- All existing CLI commands work unchanged
- All existing analysis systems work unchanged  
- Runtime traces just provide new data source
- Web interface displays existing analysis results

---

## 📈 **Simplified Success Metrics**

### **Week 1 Success (Leverage Existing)**:
- [ ] Runtime traces captured and flowing through existing systems
- [ ] Web interface displays results from existing analysis
- [ ] Chat interface uses existing `InteractiveAnalyst`
- [ ] All existing Arc Loop commands work with live data

### **Customer Validation (Zero New Intelligence)**:
- [ ] Problem 1: ✅ Reliability score from existing `ReliabilityAnalyzer`
- [ ] Problem 2: ✅ Cost optimization from existing `APIManager`  
- [ ] Problem 3: ✅ Pattern learning from existing `ScenarioBank`
- [ ] Problems 4-6: ✅ Zero-SDK + existing intelligence systems

---

## 🎯 **Bottom Line (Corrected)**

**Build minimal runtime wrapper (270 LOC) that routes data through our massive existing intelligence infrastructure (15,000+ LOC) - zero redundant code, maximum leverage of existing systems.**

We already built a sophisticated agent analysis system. We just need runtime data capture + a simple web interface to display the existing intelligence.

**Customer gets the same intelligent analysis they'd get from static traces, but with runtime data flowing through our existing Data Flywheel.** 
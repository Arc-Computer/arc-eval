# Runtime Tracing Integration Roadmap

> **Goal**: Add runtime tracing to capture agent execution data and enable real-time reliability scoring and cost analysis using our existing evaluation infrastructure.

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

### **Priority Groups**

**P0 (Problems 1-3)**: Core requirements for initial release
- **Week 1**: Reliability scoring, cost tracking, edge case detection
- **Target metrics**: 87% success rate, 22% cost reduction

**P1 (Problems 4-6)**: Adoption features 
- Zero-SDK integration, code fixes, exportable reports
- Differentiates from basic monitoring tools

**P2 (Problems 7-8)**: Future roadmap
- Runtime compliance detection  
- Formal audit reports

---

## **Full System Data Requirements**

### **Required Runtime Data**

Each workflow requires specific runtime data to function:

| **Workflow** | **Required Data** | **Purpose** |
|---|---|---|
| **Debug** | Tool calls, reasoning chains, framework metadata, error traces | Framework detection, failure analysis |
| **Compliance** | Scenario context, reward signals, compliance violations | Domain evaluation |
| **Dashboard** | Performance metrics, pattern fingerprints, learning trends | Progress tracking |
| **Improve** | Failure classifications, remediation data, agent configs | Fix generation |
| **Re-evaluate** | Historical comparisons, baseline metrics | Progress validation |

### **System Components**

| **Component** | **Required Data** | **Impact if Missing** |
|---|---|---|
| **ScenarioBank** | Failure patterns, compliance violations, remediation context | No adaptive scenario generation |
| **SelfImprovementEngine** | Reward signals, scenario IDs, performance trends | No learning tracking |
| **Pattern Learning** | Recurring failure fingerprints, domain classifications | No pattern recognition |
| **Adaptive Curriculum** | Learning progress, difficulty progression data | No improvement paths |

**Technical Risk**: Incomplete data capture limits system to basic metrics instead of full analysis capabilities.

---

##  **Existing Infrastructure**

### **Core Components**

| **Need** | **Implementation** | **File** | **LOC** |
|---|---|---|---|
| **Reliability scoring** | `ComprehensiveReliabilityAnalysis` | `evaluation/reliability_validator.py` | 2,900+ |
| **Cost tracking** | Token tracking, model recommendations | `evaluation/judges/api_manager.py` | 1,000+ |
| **Failure classification** | Pattern detection | `analysis/universal_failure_classifier.py` | 650+ |
| **Learning system** | Reward signals, curriculum generation | `analysis/self_improvement.py` | 714 |
| **Scenario generation** | Dynamic test creation | `core/scenario_bank.py` | 468 |
| **Framework detection** | Auto-detect 9+ frameworks | `core/framework_intelligence.py` | 580+ |
| **Fix generation** | Code remediation | `analysis/remediation_engine.py` | 600+ |

### **Current CLI Commands**

```bash
arc-eval debug --input agent_trace.json --pattern-analysis --root-cause
# Output: Tool call accuracy: 73%, Framework: LangChain, 4 optimizations

arc-eval compliance --domain finance --input traces.json --hybrid-qa
# Output: Pass rate: 87%, Cost: $0.013/scenario, 3 fixes available

arc-eval improve --auto-detect --framework-specific --code-examples
# Output: 12 improvement actions, 22% cost reduction
```

---

## **Week 1-2 Implementation Plan**

### **Approach** 

**Goal**: Capture runtime data to enable real-time evaluation
**Method**: Python decorator + HTTP API endpoints

### **Day 0: Performance Validation**

```python
# NEW FILE: agent_eval/trace/performance_test.py (~100 LOC)
import time
import statistics
from agent_eval.profiler.decorators import performance_profile

class TracerPerformanceValidator:
    """Ensure trace wrapper adds <50ms overhead to agent execution"""
    
    def validate_overhead(self, test_agent_func, iterations=100):
        """Run performance tests to ensure wrapper overhead is acceptable"""
        
        # Baseline: Run agent without tracing
        baseline_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            test_agent_func()
            baseline_times.append((time.perf_counter() - start) * 1000)  # ms
        
        # With tracing: Run agent with Arc wrapper
        from agent_eval.trace import ArcTracer
        tracer = ArcTracer()
        traced_agent = tracer.trace_agent(test_agent_func)
        
        traced_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            traced_agent()
            traced_times.append((time.perf_counter() - start) * 1000)  # ms
        
        # Calculate overhead
        baseline_median = statistics.median(baseline_times)
        traced_median = statistics.median(traced_times)
        overhead_ms = traced_median - baseline_median
        overhead_pct = (overhead_ms / baseline_median) * 100
        
        # Performance report
        report = {
            "baseline_median_ms": baseline_median,
            "traced_median_ms": traced_median,
            "overhead_ms": overhead_ms,
            "overhead_percent": overhead_pct,
            "p95_overhead_ms": statistics.quantiles(
                [t - b for t, b in zip(traced_times, baseline_times)], 
                n=20
            )[18],  # 95th percentile
            "verdict": "PASS" if overhead_ms < 50 else "FAIL"
        }
        
        # Display results
        console.print(Panel(
            f"⚡ Performance Test Results\n\n"
            f"Baseline: {baseline_median:.2f}ms\n"
            f"With Tracing: {traced_median:.2f}ms\n"
            f"Overhead: {overhead_ms:.2f}ms ({overhead_pct:.1f}%)\n"
            f"P95 Overhead: {report['p95_overhead_ms']:.2f}ms\n\n"
            f"Target: <50ms overhead\n"
            f"Status: {report['verdict']} {'✅' if report['verdict'] == 'PASS' else '❌'}",
            title="Tracer Performance Validation"
        ))
        
        return report

# Run validation before proceeding with implementation
if __name__ == "__main__":
    # Test with dummy agent
    def test_agent():
        time.sleep(0.1)  # Simulate 100ms agent execution
        return {"output": "test", "tool_calls": ["search", "calculate"]}
    
    validator = TracerPerformanceValidator()
    result = validator.validate_overhead(test_agent)
    
    if result["verdict"] == "FAIL":
        console.print("[red]❌ Performance validation failed! Optimize tracer before proceeding.[/red]")
        exit(1)
```

### **Week 1: Trace Capture (Days 1-3)**

```python
# NEW FILE: agent_eval/trace/capture.py (~200 LOC)
from agent_eval.core.parser_registry import FrameworkDetector, ToolCallExtractor
from agent_eval.profiler.decorators import performance_profile

class ArcTracer:
    """Rich runtime trace capture leveraging existing framework detection"""
    
    def __init__(self, domain: str = "auto"):
        self.domain = domain
        self.framework_detector = FrameworkDetector()
        self.tool_extractor = ToolCallExtractor()
        
    @performance_profile  # Use existing profiler
    def trace_agent(self, agent_func):
        """Capture comprehensive runtime data for our evaluation engine"""
        @wraps(agent_func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Rich trace data structure for judges
            trace_data = {
                "trace_id": trace_id,
                "timestamp": datetime.now().isoformat(),
                "agent_id": self._generate_agent_id(agent_func),
                "domain": self.domain,
                "input": {"args": args, "kwargs": kwargs},
                "execution_timeline": [],
                "tool_calls": [],
                "llm_calls": [],
                "cost_data": {"total": 0, "breakdown": []},
                "memory_snapshots": [],
                "framework_metadata": {}
            }
            
            # Deep instrumentation hooks
            with self._instrument_llm_calls(trace_data), \
                 self._instrument_tool_calls(trace_data), \
                 self._capture_memory_usage(trace_data):
                
                try:
                    # Execute and capture
                    result = agent_func(*args, **kwargs)
                    
                    # Auto-detect framework from output structure
                    framework = self.framework_detector.detect_framework(result)
                    trace_data["framework"] = framework
                    
                    # Extract tool usage patterns
                    tools_used = self.tool_extractor.extract_tool_calls(result, framework)
                    trace_data["tool_summary"] = tools_used
                    
                    # Success trace
                    trace_data.update({
                        "output": result,
                        "success": True,
                        "execution_time": time.time() - start_time,
                        "error": None
                    })
                    
                except Exception as e:
                    # Failure trace with rich context
                    trace_data.update({
                        "output": None,
                        "success": False,
                        "execution_time": time.time() - start_time,
                        "error": {
                            "type": type(e).__name__,
                            "message": str(e),
                            "traceback": traceback.format_exc(),
                            "failed_at_step": len(trace_data["execution_timeline"])
                        }
                    })
                    raise
                
                finally:
                    # Always save trace for analysis
                    self._save_trace(trace_data)
                    
            return result
        return wrapper

# NEW FILE: agent_eval/trace/api.py (~150 LOC)
from fastapi import FastAPI, HTTPException
from agent_eval.evaluation.judges.workflow import DebugJudge, ImproveJudge
from agent_eval.evaluation.judges.domain import FinanceJudge, SecurityJudge, MLJudge

app = FastAPI(title="Arc Eval API", version="0.1.0")

# Single endpoint to receive traces - activates entire engine
@app.post("/api/trace")
async def receive_trace(trace_data: dict):
    """Ingest rich trace data from any agent framework"""
    
    # Validate trace has required fields
    required = ["agent_id", "output", "execution_time"]
    if not all(field in trace_data for field in required):
        raise HTTPException(400, "Missing required trace fields")
    
    # Auto-detect domain if not provided
    if "domain" not in trace_data:
        trace_data["domain"] = detect_domain_from_trace(trace_data)
    
    # Store trace for batch processing
    trace_id = store_trace(trace_data)
    
    # Trigger async analysis pipeline
    trigger_analysis.delay(trace_id)
    
    return {
        "trace_id": trace_id,
        "status": "received",
        "next": f"/api/analysis/{trace_id}"
    }

# The Arc Loop endpoints - all powered by existing engine
@app.get("/api/analysis/{trace_id}")
async def get_analysis(trace_id: str):
    """Get comprehensive analysis using unified judges"""
    trace = load_trace(trace_id)
    
    # Use existing unified judges
    debug_judge = DebugJudge()
    analysis = debug_judge.analyze(trace)
    
    return {
        "reliability_score": analysis.reliability_score,
        "grade": analysis.grade,
        "cost_per_run": analysis.cost_metrics.total,
        "framework": analysis.detected_framework,
        "issues": analysis.issues[:5],
        "tool_accuracy": analysis.tool_metrics.accuracy
    }

@app.get("/api/scenarios/{trace_id}")
async def generate_scenarios(trace_id: str):
    """The magic button - auto-generate test scenarios from failures"""
    trace = load_trace(trace_id)
    
    # Use existing ScenarioBank
    from agent_eval.core.scenario_bank import ScenarioBank
    bank = ScenarioBank()
    
    if not trace.get("success"):
        pattern = extract_failure_pattern(trace)
        scenarios = bank.generate_scenarios_from_pattern(pattern)
        
        return {
            "generated": len(scenarios),
            "scenarios": scenarios,
            "message": f"✨ Generated {len(scenarios)} test scenarios from your failure"
        }
    
    return {"generated": 0, "message": "No failures to learn from"}

@app.post("/api/improve/{trace_id}")
async def get_improvements(trace_id: str):
    """Get actionable fixes using improve judge"""
    trace = load_trace(trace_id)
    
    # Use existing improve judge
    improve_judge = ImproveJudge()
    fixes = improve_judge.generate_fixes(trace)
    
    return {
        "fixes": fixes[:3],  # Top 3 fixes
        "estimated_impact": "+16% reliability",
        "code_examples": [fix.code_example for fix in fixes if fix.code_example]
    }

@app.post("/api/baseline")
async def save_baseline(trace_ids: List[str]):
    """Save current performance as baseline for comparison"""
    # Use existing WorkflowStateManager
    from agent_eval.core.workflow_state import WorkflowStateManager
    manager = WorkflowStateManager()
    
    baseline_id = manager.save_baseline(trace_ids)
    return {"baseline_id": baseline_id, "traces": len(trace_ids)}

@app.get("/api/compare/{baseline_id}/{current_id}")
async def compare_runs(baseline_id: str, current_id: str):
    """Compare two runs to show improvement"""
    # Leverage existing comparison engine
    from agent_eval.core.comparison_engine import ComparisonEngine
    engine = ComparisonEngine()
    
    comparison = engine.compare(baseline_id, current_id)
    return comparison
```

### **Week 1: Integration & CLI (Days 4-5)**

```python
# MODIFY: agent_eval/cli.py (~50 LOC additions)

@cli.command()
@click.option('--agent-file', type=click.Path(exists=True), help='Python file with agent function')
@click.option('--function', default='agent', help='Name of agent function to trace')
@click.option('--domain', type=click.Choice(['finance', 'security', 'ml', 'auto']), default='auto')
def trace(agent_file: str, function: str, domain: str):
    """
    🔄 Start tracing your agent with one command
    
    Example:
        arc-eval trace --agent-file my_agent.py --function chat_agent --domain finance
    
    This will:
    1. Import your agent function
    2. Wrap it with Arc tracing
    3. Show you the integration code
    4. Start collecting traces automatically
    """
    # Generate integration code
    integration_code = f'''
# Add this to your agent file:
from agent_eval.trace import ArcTracer

tracer = ArcTracer(domain="{domain}")
{function} = tracer.trace_agent({function})

# That's it! Your agent is now traced.
# Run your agent normally and visit: http://localhost:8000
'''
    
    console.print(Panel(integration_code, title="🎯 Integration Code"))
    
    # Start local API server
    console.print("\n[green]Starting Arc API server...[/green]")
    start_api_server()

# Add --live flag to existing commands
@cli.command() 
@click.option('--live', is_flag=True, help='Use live runtime traces instead of JSON file')
def debug(..., live: bool):
    if live:
        # Pull latest traces from API
        traces = fetch_latest_traces()
        # Rest of existing debug logic works unchanged
```

### **Week 2: Human Feedback & Polish (Days 6-8)**

```python
# NEW FILE: agent_eval/trace/feedback.py (~100 LOC)

@app.post("/api/feedback/{trace_id}")
async def add_human_feedback(trace_id: str, feedback: dict):
    """Add human feedback to improve reliability scoring"""
    
    # Simple schema
    validated_feedback = {
        "trace_id": trace_id,
        "correct": feedback.get("correct", None),  # True/False
        "score": feedback.get("score", None),      # 1-5
        "notes": feedback.get("notes", ""),
        "timestamp": datetime.now().isoformat()
    }
    
    # Store and incorporate into reliability score
    store_feedback(validated_feedback)
    
    # Trigger re-evaluation with human input
    trigger_reanalysis.delay(trace_id, with_human_feedback=True)
    
    return {"status": "feedback recorded", "impact": "reliability score updated"}

# Simple web dashboard 
# NEW FILE: agent_eval/web/dashboard.html (~200 LOC)
```

### **Week 2: Developer Experience (Days 9-10)**

```bash
# Examples that ship with the release:

# 1. LangChain agent
from langchain.agents import create_react_agent
from agent_eval.trace import ArcTracer

tracer = ArcTracer(domain="finance")
agent = tracer.trace_agent(create_react_agent(...))

# 2. CrewAI agent  
from crewai import Agent
from agent_eval.trace import ArcTracer

tracer = ArcTracer(domain="security")
Agent.execute = tracer.trace_agent(Agent.execute)

# 3. Direct HTTP (any language)
curl -X POST http://localhost:8000/api/trace \
  -H "Content-Type: application/json" \
  -d @trace.json
```

---

## **Implementation Summary**

### **New Code**: ~750 LOC Total
```
Day 0:
agent_eval/trace/
├── performance_test.py # 100 LOC - Validate <50ms overhead

Week 1:
agent_eval/trace/
├── capture.py          # 200 LOC - Trace capture
├── api.py             # 150 LOC - HTTP endpoints
└── utils.py           #  50 LOC - Helper functions

agent_eval/cli.py       #  50 LOC - New trace command

Week 2:
agent_eval/trace/
├── feedback.py        # 100 LOC - Human feedback
agent_eval/web/
└── dashboard.html     # 100 LOC - Basic UI

Total: ~750 LOC
```

### **Existing Systems**: 15,000+ LOC
- **Judges** (`evaluation/judges/`) - Analyze runtime traces
- **ReliabilityAnalyzer** (2,900 LOC) - Reliability scoring
- **APIManager** (1,000 LOC) - Cost optimization
- **ScenarioBank** (468 LOC) - Scenario generation
- **RemediationEngine** (600 LOC) - Code fixes
- **SelfImprovementEngine** (714 LOC) - Learning system
- **InteractiveAnalyst** (600 LOC) - Chat interface
- **Domain evaluations** - Finance, Security, ML

---

## **Demo Script**

### **1. Integration**
```python
# Customer's agent.py
from langchain.agents import create_react_agent

# Add tracing:
from agent_eval.trace import ArcTracer
agent = ArcTracer("finance").trace_agent(create_react_agent(...))
```

### **2. View Analysis**
```bash
python agent.py

arc-eval debug --live

Reliability: 73% (Grade: C+) 
Cost: $0.019/run (22% reduction possible)
Tool Accuracy: 68% (3 failures detected)
Latency: 4.2s (2.1s in tool calls)
```

### **3. Generate Scenarios**
```bash
arc-eval scenarios --from-last-failure

Generated 3 test scenarios:
1. Handle empty DataFrame in financial calculation
2. Validate date format before pandas query
3. Add retry logic for Bloomberg API timeout
```

### **4. Get Fixes**
```bash
arc-eval improve --live

Top 3 improvements:
1. Add input validation (+18% reliability)
2. Switch to Cerebras for non-critical paths (-62% cost)
3. Implement tool timeout handling (+12% reliability)
```

### **5. Track Progress**
```bash
arc-eval compare --baseline yesterday --current today

Progress:
• Reliability: 73% → 89% (+16pp)
• Cost: $0.019 → $0.007 (-62%)
• Tool Success: 68% → 95% (+27pp)
• Compliance: 12/15 → 15/15 scenarios
```

---

## **Timeline & Success Criteria**

### **Week 1**:
- [x] Judge unification complete
- [ ] Day 0: Performance validation (<50ms overhead)
- [ ] Day 1-3: Implement `ArcTracer` class
- [ ] Day 4: HTTP endpoints (`/api/trace`, `/api/analysis`, `/api/scenarios`)
- [ ] Day 5: CLI integration (`arc-eval trace`, `--live` flags)
- [ ] Friday: Demo working trace → analysis → scenarios flow

### **Week 2**:
- [ ] Day 6-7: Human feedback endpoint
- [ ] Day 8: Basic dashboard (HTML)
- [ ] Day 9: Framework integration examples
- [ ] Day 10: Ship to customers
- [ ] Friday: Public release

### **Success Metrics**:
| Problem | Metric | Implementation |
|---------|--------|----------------|
| Reliability | Accuracy score | `debug_judge.analyze(trace).reliability_score` |
| Cost | Optimization % | `api_manager.calculate_cost()` |
| Edge Cases | Scenarios generated | `scenario_bank.generate_from_failure()` |
| Zero-SDK | HTTP API | `POST /api/trace` |
| Fixes | Code examples | `improve_judge.generate_fixes()` |
| Reports | Export formats | HTML/PDF export |

---

## **Competitive Position**

### **vs. Braintrust**:
- They: Platform with complex integration
- Arc: One-line decorator or HTTP POST
- They: Generic evaluations
- Arc: Domain-specific (finance/security/ML)
- They: Show problems
- Arc: Generate fixes + test scenarios

### **vs. LangSmith**:
- They: LangChain-only
- Arc: 9+ frameworks auto-detected
- They: Monitoring focus
- Arc: Improvement engine

### **Technical Advantages**:
1. **ScenarioBank** - Learns from failures to generate test cases
2. **Unified Judges** - Consistent analysis across workflows
3. **Domain Expertise** - Built-in compliance for finance/security/ML
4. **Learning System** - Improves with usage

---

## **Next Steps**

### **This Week**:
1. Create `agent_eval/trace/` directory
2. Implement `ArcTracer` class using existing `FrameworkDetector`
3. Set up FastAPI endpoints that call existing judges
4. Add `trace` command to CLI
5. Test with customer agent

### **Next Week**:
1. Record demo video
2. Write launch blog post
3. Create integration examples for top 5 frameworks
4. Set up API status page
5. Ship to first customers

**Summary**: 750 lines of new code activates 15,000+ lines of existing evaluation infrastructure. The runtime tracing integration enables real-time reliability scoring and cost optimization for customers. '
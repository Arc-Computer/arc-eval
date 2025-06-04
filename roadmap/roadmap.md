# Runtime Tracing Integration Roadmap

> **Goal**: Add runtime tracing to capture agent execution data and enable real-time reliability scoring and cost analysis using our existing evaluation infrastructure.

## **Customer Problems We're Solving**

### **Problems Identified from Customer Interviews**

| **#** | **Problem** | **Customer Evidence** | **Our Solution** |
|---|---|---|---|
| **1** | "Will this agent complete tasks correctly?" | Customer: "If you can tell us an agent's success-rate we'll use it." | Reliability score with letter grade (A-F) and historical trends |
| **2** | "How much are agents costing us?" | Multiple developers report unexpectedly high API bills | Cost per run tracking with optimization recommendations |
| **3** | "What edge cases will break in production?" | Teams worry about failures only visible under real load | Automatically generate test scenarios from observed failures |
| **4** | "Need to evaluate any agent framework" | Platform providers don't want framework-specific dependencies | One-line integration or HTTP API for any framework |
| **5** | "Show me how to fix problems" | Current tools only identify issues without solutions | Specific code patches for each framework |
| **6** | "Prove agent quality to customers" | B2B platforms need metrics to show end users | Shareable reliability reports and dashboards |
| **7** | "Detect data leaks at runtime" | Static analysis misses runtime privacy violations | Runtime pattern detection for sensitive data (Phase 2) |
| **8** | "Meet compliance requirements" | Future audit requirements for GDPR/HIPAA | Compliance report generation (Future roadmap) |

### **Development Priorities**

**Phase 0 (Week 1)**: Core Features
- Reliability scoring and grading
- Cost tracking and optimization
- Automatic test generation from failures

**Phase 1 (Week 2)**: Developer Experience
- Simple integration (one line of code)
- Framework-specific code fixes
- Shareable reports

**Phase 2 (Future)**: Advanced Features
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

**Important**: Missing data will limit analysis capabilities. Ensure comprehensive data capture for best results.

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
            f"Status: {report['verdict']}",
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
        console.print("Performance validation failed! Optimize tracer before proceeding.")
        exit(1)
```

### **Week 1: Trace Capture (Days 1-3)**

```python
# NEW FILE: agent_eval/trace/capture.py (~200 LOC)
from agent_eval.core.parser_registry import FrameworkDetector, ToolCallExtractor
from agent_eval.profiler.decorators import performance_profile

class ArcTracer:
    """Captures runtime execution data from AI agents"""
    
    def __init__(self, domain: str = "auto"):
        self.domain = domain
        self.framework_detector = FrameworkDetector()
        self.tool_extractor = ToolCallExtractor()
        
    @performance_profile  # Use existing profiler
    def trace_agent(self, agent_func):
        """Wrap agent function to capture execution data"""
        @wraps(agent_func)
        def wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Trace data structure
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
                "framework_metadata": {},
                # Trajectory capture for full analysis capabilities
                "trace": {
                    "steps": [],  # Detailed execution steps
                    "tool_calls_count": 0,
                    "reasoning_steps_count": 0,
                    "total_duration_ms": 0,
                    "success": True,
                    "failure_point": None,
                    "trace_id": trace_id,
                    "session_id": None
                }
            }
            
            # Capture detailed execution data:
            # 1. Reasoning steps
            # 2. Tool calls with inputs/outputs
            # 3. Intermediate computations
            # 4. Decision points
            with self._instrument_llm_calls(trace_data), \
                 self._instrument_tool_calls(trace_data), \
                 self._capture_memory_usage(trace_data), \
                 self._capture_trajectory(trace_data):
                
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
                    # Capture failure details
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
    
    def _capture_trajectory(self, trace_data):
        """Capture step-by-step agent execution.
        
        Records execution details needed for:
        - Failure analysis
        - Pattern detection
        - Performance optimization
        - Test scenario generation
        """
        # Implementation to intercept and record:
        # 1. LLM reasoning steps
        # 2. Tool call sequences with full I/O
        # 3. Decision branches
        # 4. Intermediate computations
        pass
    
    def _add_trajectory_step(self, trace_data, step_type, content, **kwargs):
        """Add a step to the execution trajectory"""
        step = {
            "step": len(trace_data["trace"]["steps"]) + 1,
            "action": step_type,  # "reasoning", "tool_call", "decision"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": 0,  # Updated when step completes
            **kwargs
        }
        trace_data["trace"]["steps"].append(step)
        
        # Update counters
        if step_type == "reasoning":
            trace_data["trace"]["reasoning_steps_count"] += 1
        elif step_type == "tool_call":
            trace_data["trace"]["tool_calls_count"] += 1

# NEW FILE: agent_eval/trace/api.py (~150 LOC)
from fastapi import FastAPI, HTTPException
from agent_eval.evaluation.judges.workflow import DebugJudge, ImproveJudge
from agent_eval.evaluation.judges.domain import FinanceJudge, SecurityJudge, MLJudge

app = FastAPI(title="Arc Eval API", version="0.1.0")

# Receive trace data from agents
@app.post("/api/trace")
async def receive_trace(trace_data: dict):
    """Accept trace data from any agent framework"""
    
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

# Analysis endpoints
@app.get("/api/analysis/{trace_id}")
async def get_analysis(trace_id: str):
    """Get reliability analysis for a trace"""
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
    """Generate test scenarios from agent failures"""
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
            "message": f"Generated {len(scenarios)} test scenarios from your failure"
        }
    
    return {"generated": 0, "message": "No failures to learn from"}

@app.post("/api/improve/{trace_id}")
async def get_improvements(trace_id: str):
    """Get code fixes for identified issues"""
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
    Start tracing your agent
    
    Example:
        arc-eval trace --agent-file my_agent.py --function chat_agent --domain finance
    
    This will:
    1. Import your agent function
    2. Add tracing instrumentation
    3. Display integration code
    4. Start collecting execution data
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
    
    console.print(Panel(integration_code, title="Integration Code"))
    
    # Start local API server
    console.print("\nStarting Arc API server...")
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


## **MVP Implementation Details**

### **Authentication Strategy**
```python
# agent_eval/trace/api.py - Simple API key auth for MVP
from fastapi import Header, HTTPException, Depends
from typing import Optional

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key verification for MVP"""
    api_key = os.getenv("ARC_EVAL_API_KEY")
    
    # Allow no auth in development mode
    if os.getenv("ARC_EVAL_ENV", "development") == "development":
        return True
    
    if not api_key:
        raise HTTPException(500, "API key not configured")
    
    if x_api_key != api_key:
        raise HTTPException(401, "Invalid API key")
    
    return True

# Apply to endpoints
@app.post("/api/trace", dependencies=[Depends(verify_api_key)])
async def receive_trace(trace_data: dict):
    # existing implementation
```

### **Storage Layer (SQLite → Postgres ready)**
```python
# agent_eval/trace/storage.py - SQLAlchemy for easy migration
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TraceRecord(Base):
    __tablename__ = 'traces'
    
    trace_id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    domain = Column(String, index=True)
    framework = Column(String)
    timestamp = Column(DateTime, index=True)
    success = Column(Boolean)
    execution_time = Column(Float)
    
    # Store full trace as JSON for flexibility
    trace_data = Column(JSON)  # SQLite: TEXT, Postgres: native JSON
    
    # Denormalized fields for quick queries
    reliability_score = Column(Float, index=True)
    cost = Column(Float)
    tool_accuracy = Column(Float)

# Zero-config database switching
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./arc_eval_traces.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Initialize tables
Base.metadata.create_all(bind=engine)
```

### **Async Processing (FastAPI BackgroundTasks)**
```python
# agent_eval/trace/api.py - Background processing without Celery
from fastapi import BackgroundTasks

def analyze_trace_background(trace_id: str):
    """Run analysis in background thread"""
    try:
        # Load trace
        db = SessionLocal()
        trace = db.query(TraceRecord).filter_by(trace_id=trace_id).first()
        
        # Run analysis (existing code)
        analyzer = ReliabilityAnalyzer()
        analysis = analyzer.generate_comprehensive_analysis([trace.trace_data])
        
        # Update record with results
        trace.reliability_score = analysis.workflow_metrics.workflow_success_rate
        trace.cost = trace.trace_data.get("cost_data", {}).get("total", 0)
        db.commit()
        
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")
    finally:
        db.close()

@app.post("/api/trace")
async def receive_trace(trace_data: dict, background_tasks: BackgroundTasks):
    # Validate and store
    trace_id = str(uuid.uuid4())
    
    db = SessionLocal()
    trace_record = TraceRecord(
        trace_id=trace_id,
        agent_id=trace_data.get("agent_id"),
        trace_data=trace_data,
        timestamp=datetime.now()
    )
    db.add(trace_record)
    db.commit()
    db.close()
    
    # Analyze in background
    background_tasks.add_task(analyze_trace_background, trace_id)
    
    return {"trace_id": trace_id, "status": "processing"}
```

### **Error Handling Standard**
```python
# agent_eval/trace/errors.py - Consistent error handling
class ArcEvalError(Exception):
    """Base exception for Arc-Eval"""
    pass

class TraceValidationError(ArcEvalError):
    """Invalid trace data"""
    pass

class AnalysisError(ArcEvalError):
    """Analysis failed"""
    pass

# Global exception handler
@app.exception_handler(ArcEvalError)
async def arc_eval_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "trace_id": getattr(exc, "trace_id", None)
        }
    )

# Handle incomplete traces
@app.post("/api/trace")
async def receive_trace(trace_data: dict):
    # Store partial traces with metadata
    trace_data["_incomplete"] = False
    required = ["agent_id", "output", "execution_time"]
    missing = [f for f in required if f not in trace_data]
    if missing:
        trace_data["_incomplete"] = True
        trace_data["_missing_fields"] = missing
        logger.warning(f"Incomplete trace received, missing: {missing}")
```

### **MVP Stack Summary**
- **API**: FastAPI + SQLAlchemy + BackgroundTasks
- **Storage**: SQLite (Postgres-ready via SQLAlchemy)
- **Auth**: Simple API key via header
- **Deploy**: Single Docker container
- **Rate Limiting**: TODO for post-MVP

---

## **Deployment Architecture for CLI Product**

### **Developer Experience Overview**

Arc-Eval operates as a **hybrid CLI + local API** system:

1. **Primary Interface**: CLI commands (`arc-eval debug`, `arc-eval improve`, etc.)
2. **Runtime Tracing**: Optional local API server for live agent monitoring
3. **No Cloud Dependency**: Everything runs on developer's machine for MVP

### **Architecture Components**

```bash
┌─────────────────────────────────────────────────────────┐
│                   Developer's Machine                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────────┐   │
│  │  Customer Agent │ ──────> │   Arc-Eval CLI       │   │
│  │  (LangChain etc)│         │  $ arc-eval debug    │   │
│  └─────────────────┘         └──────────────────────┘   │
│           │                            │                │
│           │ ArcTracer                  │                │
│           ▼                            ▼                │
│  ┌─────────────────┐         ┌──────────────────────┐   │
│  │  Local API      │ <────── │  SQLite Database     │   │
│  │  localhost:8000 │         │  arc_eval_traces.db  │   │
│  └─────────────────┘         └──────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Two Usage Modes**

#### **Mode 1: Traditional CLI (No Docker)**
```bash
# Install Arc-Eval
pip install arc-eval

# Use with static files
arc-eval debug --input trace.json
arc-eval compliance --domain finance --input outputs.json
```

#### **Mode 2: Live Tracing (Local API)**
```bash
# Start the trace server (runs FastAPI locally)
arc-eval trace --start-server

# In another terminal, trace your agent
python my_agent.py  # Agent instrumented with ArcTracer

# Analyze live traces
arc-eval debug --live
arc-eval improve --live
```

### **Docker Strategy (Optional Enhancement)**

For users who prefer containerized deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

# Expose API port
EXPOSE 8000

# Default: Start API server
CMD ["arc-eval", "trace", "--start-server", "--host", "0.0.0.0"]
```

```yaml
# docker-compose.yml (for advanced users)
version: '3.8'
services:
  arc-eval:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./arc_eval_data:/app/data  # Persist SQLite + traces
    environment:
      - ARC_EVAL_API_KEY=${ARC_EVAL_API_KEY}
      - DATABASE_URL=sqlite:////app/data/traces.db
```

### **Installation Options**

1. **Simplest (Python Package)**:
   ```bash
   pip install arc-eval
   arc-eval --help
   ```

2. **Development Mode**:
   ```bash
   git clone https://github.com/arc-computer/arc-eval
   pip install -e ".[dev]"
   arc-eval --help
   ```

3. **Docker (Optional)**:
   ```bash
   docker run -p 8000:8000 arc-eval/arc-eval:latest
   ```

### **Data Persistence**

- **CLI Mode**: Results displayed in terminal, optionally exported
- **Trace Mode**: SQLite database at `~/.arc-eval/traces.db`
- **Docker Mode**: Volume mount for persistence

### **Security Considerations**

1. **Local-First**: No data leaves developer's machine
2. **API Key**: Optional, mainly for future cloud features
3. **Network**: API binds to localhost only by default

### **Future Cloud Architecture** (Post-MVP)

```
Developer Machine          Arc Cloud (Future)
┌──────────────┐          ┌─────────────────┐
│   CLI/Agent  │ ──────> │   Arc API       │
│              │          │   (Managed)     │
└──────────────┘          └─────────────────┘
                                   │
                          ┌────────┴────────┐
                          │   PostgreSQL    │
                          │   Time-series   │
                          │   S3 Storage    │
                          └─────────────────┘
```

### **Why This Architecture?**

1. **Zero Friction**: Works immediately after `pip install`
2. **Privacy**: All analysis happens locally
3. **Flexibility**: Use CLI-only or with live tracing
4. **Growth Path**: Easy transition to cloud when needed
5. **Developer-First**: Fits into existing workflows

---

## **Cloud Transition Strategy**

### **Why We Start Local**

Starting with local deployment allows us to ship quickly and learn what features matter most to developers. This approach lets us focus on product development rather than infrastructure.

### **Phase 1: MVP (Weeks 1-4)**
- Local deployment enables shipping in 2 weeks
- Validate which features developers actually use
- Gather feedback on our unique capabilities
- Focus on product iteration, not infrastructure

### **Phase 2: Cloud-Native (Months 2-3)**
```
Developer Machine                 Arc Cloud Platform
┌──────────────┐                 ┌─────────────────────────┐
│   ArcTracer  │ ──── HTTPS ──> │   Arc API (Global)      │
│   (SDK)      │                 │   • Multi-region        │
└──────────────┘                 │   • Auto-scaling        │
                                 │   • Real-time streaming │
                                 └───────────┬─────────────┘
                                             │
                                 ┌───────────┴─────────────┐
                                 │   Data Infrastructure   │
                                 │   • PostgreSQL          │
                                 │   • Redis (caching)     │
                                 │   • S3 (traces)         │
                                 │   • Kafka (streaming)   │
                                 └─────────────────────────┘
```

### **What Makes Arc-Eval Different**

| **Feature** | **Braintrust** | **LangSmith** | **Arc-Eval** |
|-------------|----------------|---------------|--------------|
| **Domain Focus** | Generic | Generic | Finance, Security, ML specific |
| **Test Creation** | Manual | Manual | Auto-generates from failures |
| **Problem Resolution** | Shows issues | Shows issues | Provides code fixes |
| **Compliance** | Basic metrics | Basic metrics | SOX, GDPR, HIPAA reports |
| **Cost Analysis** | Shows costs | Shows costs | Recommends optimizations |
| **Improvement** | Static | Static | Learns from usage |

### **Cloud Features Roadmap**

**Month 2: Core Cloud Services**
- Hosted API service with reliability guarantees
- Real-time analysis streaming
- Team collaboration features
- Historical performance tracking

**Month 3: Enterprise Features**
- Single sign-on support
- Team permissions and access control
- Audit logging for compliance
- Private deployment options

**Month 4: Scale and Integration**
- Global deployment for low latency
- Fast trace processing
- CI/CD pipeline integration
- Webhook support for automation

### **Migration Path**

```python
# MVP (Local)
tracer = ArcTracer(domain="finance")
agent = tracer.trace_agent(my_agent)

# Cloud (Same API!)
tracer = ArcTracer(
    domain="finance",
    api_key="arc_key_xxx",  # Only change
    endpoint="https://api.arc-eval.com"
)
agent = tracer.trace_agent(my_agent)
```

### **Benefits of This Approach**

1. Ship in weeks instead of months
2. Focus engineering time on product features
3. Validate demand before building infrastructure
4. Same code works locally and in cloud

### **Key Differences from Competitors**

**Arc-Eval vs Braintrust**: 
- Braintrust requires manual test creation
- Arc-Eval automatically generates tests from failures

**Arc-Eval vs LangSmith**:
- LangSmith works only with LangChain
- Arc-Eval supports 9+ frameworks

**Arc-Eval vs Both**:
- They identify problems
- We provide specific code fixes

### **Success Metrics**

- **Week 4**: 100+ developers using local version
- **Month 2**: 10 teams on cloud version
- **Month 3**: First enterprise customer
- **Month 6**: Majority of usage on cloud

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

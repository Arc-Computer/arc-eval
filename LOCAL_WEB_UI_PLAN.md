# "Arc Workbench" — Local-First Reliability Cockpit

## 🎯 **Vision: Interactive Debugging Companion**

> **"Drag a trace, chat with the failure, press 'Apply fix', and watch your agent get better—locally—with zero config."**

Transform ARC-Eval into the **interactive debugging companion** every AI engineer (and their PM) wishes observability tools were:
- **30-second product tour**: From drag-and-drop to actionable insight
- **Narrative cards** that summarize what *matters* first (not observability spam)
- **AI-generated fixes** delivered as ready-to-apply diffs
- **Local-first** with magical UX that feels nothing like traditional dashboards

## 🏗️ **Architecture: Local-First with Optional Cloud Sync**

```bash
Local Machine (Primary):
├── CLI (existing) ──┐
├── Web UI (new) ────┼──► Same Analysis Engines
└── Analysis Results ┘

Optional Cloud (Secondary):
└── Supabase (sync only when logged in)
```

## 📁 **Directory Structure**

```bash
agent_eval/
├── cli.py                    # Add `serve` command
├── commands/
│   ├── login_command.py      # ✅ Already created
│   └── serve_command.py      # NEW: Local web server
├── web/                      # NEW: Local web server
│   ├── __init__.py          # ✅ Already created (updated)
│   ├── app.py               # Local FastAPI server
│   ├── static/              # Built React app (auto-generated)
│   └── models.py            # Pydantic models for API
└── frontend/                 # NEW: React development
    ├── package.json
    ├── components/
    │   ├── DropZone.tsx         # Drag & drop interface
    │   ├── DebugDashboard.tsx   # Web version of CLI debug
    │   ├── ComplianceDashboard.tsx # Web version of CLI compliance
    │   ├── ChatInterface.tsx    # Cursor-style chat
    │   └── ExecutiveSummary.tsx # Business-friendly view
    ├── pages/
    │   ├── index.tsx           # Main dashboard
    │   └── analysis/[id].tsx   # Analysis results
    └── lib/
        └── api.ts              # Local API client
```

## 🚀 **30-Second Product Tour: From Drag-and-Drop to Insight**

| 🕒 Timeline | Screen | What happens behind the curtain |
|-------------|--------|----------------------------------|
| **0s** — `arc-eval serve` auto-opens **Workbench Home** | White canvas with subtle dot grid and glowing drop zone that pulses the Arc-blue arrow prompt | Static React; no server call yet |
| **1s** — user drags `agent_outputs.json` | "Detecting framework…" toast animates; mini CLI log tail scrolls in corner for devs | FastAPI endpoint writes temp file and streams `DebugCommand` stdout via WebSocket |
| **4s** — **Reliability Story card** fades in | Large colored badge: *MEDIUM RISK (0.67)*, below it "Prevents **75%** of prod failures • Saves **$0.15/run**" | Values parsed from `ComprehensiveReliabilityAnalysis.reliability_prediction` |
| **5s** — **Cursor Chat** panel auto-suggests | "Ask: Why did my agent miss PII?" | `InteractiveAnalyst` called with analysis context |
| User clicks suggestion | Chat returns 2-sentence root-cause + bold next step button *"Add PII mask patch → Create PR"* | Chat endpoint also returns a diff payload |
| **Patch modal** appears | Shows unified diff of prompt or config; *"Apply & re-run"* button | CLI writes patch file, reruns `DebugCommand`, new run appended |
| **Progress tracker** top-right | Circular timeline lights up: Debug ✓ → Compliance → Improve | Data from `workflow_state.py` |

**Outcome**: **Non-technical PM** never touched a terminal, **engineer** sees raw logs and git-apply ready diff, **FinOps** can open Executive Summary tab for cost deltas.

## 🎨 **Key Screens & Interaction Patterns**

### 1. **Workbench Home / Drop Zone** *(Magic moment = zero clicks to analyze)*
- **Component**: `WorkbenchHome.tsx` with pulsing Arc-blue prompt icon
- **UX**: White canvas with subtle dot grid, "Drop any agent output or click to run sample demo (LangChain)"
- **Developer transparency**: Mini-log overlay (collapsible) shows exact CLI invocation
- **Backend**: Static React until file drop triggers `/api/analyze`

### 2. **Reliability Story Card** *(Non-technical first view)*
- **Component**: `ReliabilityStory.tsx` - horizontal card with three colored chips
- **Chips**: 🔰 Risk Level (Green/Amber/Red) | 💸 Run Cost (Blue) | ⏱ Time Saved (Purple)
- **Magic**: No table spam on first view - clicking chips drills into detailed dashboards
- **Data**: From `ComprehensiveReliabilityAnalysis.reliability_prediction`

### 3. **Cursor-Style Chat** *(Sticky right pane, collapsible)*
- **Component**: `CursorChat.tsx` with context chips and action buttons
- **Features**: `⌘/Ctrl + K` toggles input, `[Generate fix diff] [Open docs] [Create JIRA]` buttons
- **Context**: Chat seed includes `failure_id` when user selects a row → answers stay specific
- **Backend**: `/api/chat` using existing `InteractiveAnalyst`

### 4. **Patch Modal** *(The "aha" for devs)*
- **Component**: `PatchModal.tsx` showing unified diff with syntax highlighting
- **Actions**: **Apply & re-run** (writes patch, triggers new analysis) | **Copy diff** (manual git)
- **Progress**: Visual self-improvement loop: `Debug → Compliance → Improve`
- **Backend**: `/api/patch` endpoint that integrates with existing improve workflow

### 5. **Executive Summary** *(Board slide in one click)*
- **Component**: `ExecutiveSummary.tsx` - read-only PDF view embedded + download
- **Content**: Risk delta, cost delta, compliance status grid
- **Magic**: "Open in chat" next to each red cell jumps into chat pre-filled
- **Data**: From existing `ExecutiveDashboard.generate_summary()`

## 📋 **Implementation Phases**

### **Phase 1: Local Foundation (Week 1)**

#### **Day 1-2: CLI Integration**
- [ ] Create `serve_command.py`
- [ ] Add `arc-eval serve` to CLI
- [ ] Clean up existing `web/app.py` (remove cloud complexity)
- [ ] Create simple FastAPI server with health check

#### **Day 3-4: Core API Endpoints**
- [ ] `/api/analyze` - File upload & debug analysis (uses `DebugCommand`)
- [ ] `/api/compliance` - Compliance evaluation (uses `ComplianceCommand`)
- [ ] `/api/dashboard/{id}` - Dashboard data (from `ComprehensiveReliabilityAnalysis`)
- [ ] `/api/chat` - Chat interface (uses `InteractiveAnalyst`)
- [ ] `/api/workflow` - Workflow state tracking (uses `workflow_state.py`)

#### **Day 5-7: Frontend Foundation**
- [ ] Next.js setup with TypeScript
- [ ] Basic drag & drop interface
- [ ] API client for local endpoints
- [ ] Simple dashboard display

### **Phase 2: Rich Interface (Week 2)**

#### **Day 8-10: Workbench Components**
- [ ] `WorkbenchHome.tsx` - Pulsing drop zone with dot grid canvas
- [ ] `ReliabilityStory.tsx` - **KILLER FEATURE**: Three-chip narrative card
- [ ] `CursorChat.tsx` - Sticky right pane with context chips
- [ ] `PatchModal.tsx` - Unified diff with Apply & re-run
- [ ] WebSocket streaming for real-time CLI output

#### **Day 11-14: Magical Interactions**
- [ ] Auto-suggested chat questions based on detected issues
- [ ] Action buttons in chat responses (`[Generate fix diff]`, `[Create PR]`)
- [ ] Progressive disclosure (cards → detailed views)
- [ ] Keyboard shortcuts (`⌘/Ctrl + K` for chat, slash commands)
- [ ] Timeline progress tracker for workflow state

### **Phase 3: Polish & Cloud Sync (Week 3)**

#### **Day 15-17: UX Polish**
- [ ] Mobile-responsive design
- [ ] Loading states and error handling
- [ ] Keyboard shortcuts and accessibility
- [ ] Performance optimization

#### **Day 18-21: Optional Cloud Sync**
- [ ] Integration with existing `login_command.py`
- [ ] Optional sync to Supabase when logged in
- [ ] Shareable URLs for stakeholders
- [ ] Team collaboration features

## 🔧 **Technical Implementation**

### **Backend: Local FastAPI Server**

```python
# agent_eval/web/app.py
from fastapi import FastAPI, UploadFile, File
from agent_eval.commands.debug_command import DebugCommand
from agent_eval.commands.compliance_command import ComplianceCommand
from agent_eval.analysis.interactive_analyst import InteractiveAnalyst

app = FastAPI(title="ARC-Eval Local Dashboard")

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    # Save file temporarily and run analysis
    with tempfile.NamedTemporaryFile(suffix='.json') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()

        # Use existing CLI handlers directly
        debug_cmd = DebugCommand()
        exit_code = debug_cmd.execute(
            input_file=Path(tmp.name),
            no_interactive=True,  # Skip CLI menus
            output_format='json'
        )

        # Return structured data for web UI
        return {"analysis_results": analysis_data}

@app.post("/api/chat")
async def chat_with_analysis(message: str, analysis_id: str):
    # Load analysis data and create InteractiveAnalyst
    analysis_data = load_analysis_data(analysis_id)
    analyst = InteractiveAnalyst(
        improvement_report=analysis_data["improvement_report"],
        judge_results=analysis_data["judge_results"],
        domain=analysis_data["domain"]
    )
    response = analyst._query_ai_with_context(message)
    return {"response": response}
```

### **Frontend: React with TypeScript**

```typescript
// frontend/components/DropZone.tsx
export default function DropZone() {
  const onDrop = async (files: File[]) => {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });
    const results = await response.json();
    setAnalysisResults(results);
  };

  return (
    <div className="drag-drop-zone">
      <h2>Drop your agent outputs here</h2>
      <p>Instant analysis using your local ARC-Eval engine</p>
    </div>
  );
}
```

### **CLI Integration**

```python
# agent_eval/commands/serve_command.py
class ServeCommand(BaseCommandHandler):
    def execute(self, port: int = 3000, open_browser: bool = True):
        """Start local web dashboard."""
        from agent_eval.web.app import start_server
        console.print(f"🚀 Starting ARC-Eval Dashboard at http://localhost:{port}")
        if open_browser:
            webbrowser.open(f"http://localhost:{port}")
        start_server(port=port)

# agent_eval/cli.py
@cli.command()
@click.option('--port', default=3000, help='Port to run the server on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
def serve(port: int, no_browser: bool):
    """🌐 Start local web dashboard"""
    command = ServeCommand()
    return command.execute(port=port, open_browser=not no_browser)
```

## 💡 **Key Design Principles**

### **1. Leverage Existing CLI Logic (90% Reuse)**
- Use existing `DebugCommand`, `ComplianceCommand`, `AnalyzeCommand`
- Reuse `ComprehensiveReliabilityAnalysis`, `ExecutiveSummary`, `EvaluationResult` data structures
- Integrate with `InteractiveAnalyst` for chat (requires `improvement_report`, `judge_results`, `domain`)
- Access `DebugDashboard.display_debug_summary()` and `ExecutiveDashboard.generate_summary()` methods

### **2. Local-First Architecture**
- No cloud dependencies for core functionality
- Fast, private analysis on user's machine
- Optional cloud sync when logged in

### **3. Non-Technical Friendly**
- Drag & drop interface (no CLI knowledge needed)
- Business-friendly language and visuals
- Guided workflows with clear next steps

### **4. Cursor-Style Chat Experience**
- Context-aware responses about specific failures
- Suggested questions and quick actions
- Deep integration with analysis results

## 🎯 **Success Metrics**

### **User Experience**
- **Setup Time**: 30 seconds (`arc-eval serve`)
- **Analysis Time**: 5 seconds (drag & drop → results)
- **Chat Response**: 2-3 seconds per question
- **Stakeholder Adoption**: Non-technical users can operate independently

### **Technical Performance**
- **Local Processing**: No network latency
- **Memory Usage**: <500MB for typical analysis
- **Browser Compatibility**: Chrome, Firefox, Safari, Edge
- **Mobile Responsive**: Works on tablets and phones

## 🔄 **Integration with Existing Workflows**

### **CLI Users**
- Existing CLI workflows unchanged
- Web UI as optional enhancement
- Same analysis engines and results

### **Team Collaboration**
- Local analysis for privacy
- Optional sharing via cloud sync
- Executive summaries for stakeholders

### **CI/CD Integration**
- CLI remains primary for automation
- Web UI for human review and debugging
- Shareable reports for team communication

## 📝 **Next Steps**

1. **Review & Align**: Confirm this plan meets requirements
2. **Clean Up**: Remove existing cloud-focused `web/app.py`
3. **Start Phase 1**: Implement `serve` command and basic FastAPI server
4. **Validate Early**: Test with real agent outputs from examples/
5. **Iterate Fast**: Get user feedback on drag & drop experience

## 🔍 **Critical Implementation Details (Based on Codebase Analysis)**

### **Data Flow & API Structure**

#### **1. Analysis Pipeline**
```python
# Web UI Analysis Flow (mirrors CLI exactly)
1. File Upload → Temporary file
2. DebugCommand.execute(input_file, no_interactive=True)
3. Returns ComprehensiveReliabilityAnalysis object
4. Extract data for web UI:
   - analysis.detected_framework
   - analysis.framework_confidence
   - analysis.workflow_metrics (WorkflowReliabilityMetrics)
   - analysis.tool_call_summary
   - analysis.insights_summary
   - analysis.next_steps
```

#### **2. Chat Integration**
```python
# InteractiveAnalyst requires specific data structure:
analyst = InteractiveAnalyst(
    improvement_report=dict,  # From compliance evaluation
    judge_results=list,       # From agent-judge evaluation
    domain=str,              # 'finance', 'security', 'ml'
    performance_metrics=dict, # Optional
    reliability_metrics=dict  # Optional
)

# Chat method:
response = analyst._query_ai_with_context(question)
```

#### **3. Dashboard Data Sources**
```python
# Debug Dashboard Data (from ComprehensiveReliabilityAnalysis):
- Framework: analysis.detected_framework
- Confidence: analysis.framework_confidence
- Performance: analysis.workflow_metrics.workflow_success_rate
- Tool Reliability: analysis.workflow_metrics.tool_chain_reliability
- Critical Issues: analysis.insights_summary
- Next Steps: analysis.next_steps

# Reliability Prediction Data (from analysis.reliability_prediction):
- Risk Level: prediction.risk_level ('LOW', 'MEDIUM', 'HIGH')
- Risk Score: prediction.combined_risk_score (0.0-1.0)
- Confidence: prediction.confidence (0.0-1.0)
- Top Risk Factors: prediction.top_risk_factors (list)
- Predicted Failures: prediction.llm_component.predicted_failure_modes
- Business Impact: prediction.business_impact.failure_prevention_percentage
- Recommendations: prediction.recommendations

# Executive Dashboard Data (from ExecutiveSummary):
- Health Score: summary.overall_health_score
- Risk Score: summary.compliance_risk_score
- Business Impact: summary.business_impact
- ROI Projection: summary.roi_projection
```

## 🪄 **Interface Behaviors That Feel *Magical*, Not *Observability***

| Traditional Observability | Arc Workbench Twist |
|---------------------------|---------------------|
| Static dashboards you must hunt through | **Narrative cards** summarizing what *matters* first |
| Query languages & filters | **Plain-English chat** with auto-suggested questions |
| Otel metrics only | **AI-generated fixes** delivered as ready-to-apply diffs |
| Cloud SaaS required | **Local-first** runs; share link only when you log in |
| Tables and charts everywhere | **Progressive disclosure**: Execs see cards, clicking reveals details |
| Manual debugging workflows | **Self-improvement loop**: Apply fix → re-run → measure improvement |

## 🎯 **Keeping Complexity Away from the User**

### **Smart Interface Adaptation**
- **No login path → no Share buttons shown**: Interface hides sync elements until `arc-eval login` token detected
- **One-file drop**: Accepts `.json` or zipped folder; server does the rest—no parameters
- **Progressive disclosure**: Execs see cards; only clicking reveals tables & raw logs
- **Keyboard-power parity**: Anything clickable has slash-command (`/compliance`, `/cost`) usable inside chat

### **Zero-Config Magic**
- **Framework auto-detection**: Works with any agent output, no setup
- **Context-aware suggestions**: Chat pre-populated with relevant questions for detected issues
- **Intelligent defaults**: Risk thresholds, cost calculations, improvement suggestions all automatic

## 🛠️ **Minimal Extra Code to Achieve "Wow"**

### **90% Code Reuse Target Maintained**

| Component | Lines of Code | What it does |
|-----------|---------------|--------------|
| **WebSocket stream wrapper** | ~100 LOC | Wraps existing CLI executor for real-time progress |
| **Chat endpoint enhancement** | ~50 LOC | Adds diff generation to existing `InteractiveAnalyst` |
| **Diff generator util** | ~75 LOC | Creates patches for improve workflow (likely exists) |
| **Timeline React component** | ~25 LOC | Tiny progress tracker for workflow state |
| **Static PDF embed** | ~30 LOC | Renders existing PDF with download button |
| **Workbench UI components** | ~200 LOC | React components using existing data structures |

**Total new code**: ~480 LOC to transform CLI into magical web experience.

### **Key Integration Points**
- **Existing prediction system**: Already integrated in debug workflow
- **Existing chat system**: `InteractiveAnalyst` just needs diff generation
- **Existing workflow tracking**: `workflow_state.py` provides progress data
- **Existing analysis engines**: All dashboard data comes from current CLI
- **Existing improve workflow**: Patch generation likely exists for improvement plans

## 🎯 **One-Sentence Promise to Users**

> **"Drag a trace, chat with the failure, press 'Apply fix', and watch your agent get better—locally—with zero config."**

Deliver that and Arc isn't just another dashboard; it's the **interactive debugging companion** every AI engineer (and their PM) wishes observability tools were.

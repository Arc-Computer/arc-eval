# ARC-Eval Implementation Guide: Agentic Workflow Reliability
## 4-Week Tactical Implementation Plan

> **Context**: Transform ARC-Eval from compliance tool to agentic workflow reliability platform based on validated May 2025 developer pain points.

---

## 🎯 Implementation Strategy

### **Build on Existing Foundation - NO BLOAT**
- Leverage existing `ReliabilityValidator`, `PerformanceTracker`, `ImprovementPlanner`
- Extend CLI in `agent_eval/cli.py` with new commands
- Enhance existing UI components in `agent_eval/ui/`
- Add new domain pack alongside existing `finance.yaml`, `security.yaml`, `ml.yaml`
- **PRESERVE all existing compliance functionality** - keep 355 scenarios intact
- **ENHANCE compliance commands** with reliability metrics overlay
- **Lead with reliability, showcase compliance** as competitive differentiator

### **Key Files to Modify/Extend:**
```
agent_eval/cli.py                    # Add new commands and messaging
agent_eval/evaluation/reliability_validator.py  # Extend with workflow metrics
agent_eval/core/types.py             # Add new data structures
agent_eval/ui/streaming_evaluator.py # Enhanced debugging display
agent_eval/core/improvement_planner.py  # Framework-specific suggestions
agent_eval/domains/workflow_reliability.yaml  # NEW domain pack
```

---

## 📋 Week 1: CLI Repositioning & Unified Debugging View

### **Task 1.1: Add New CLI Commands**
**File**: `agent_eval/cli.py`
**Location**: Add new `@click.option` decorators around line 269 (after existing options)

```python
@click.option(
    "--debug-agent",
    is_flag=True,
    help="Launch unified agent debugging mode with failure analysis"
)
@click.option(
    "--workflow-reliability", 
    is_flag=True,
    help="Focus evaluation on workflow reliability metrics"
)
@click.option(
    "--unified-debug",
    is_flag=True, 
    help="Single view of tool calls, prompts, memory, timeouts, hallucinations"
)
@click.option(
    "--framework",
    type=click.Choice(["langchain", "crewai", "autogen", "openai", "anthropic"]),
    help="Optimize analysis for specific agent framework"
)
```

### **Task 1.2: Update Default Messaging (Lead with Reliability, Showcase Compliance)**
**File**: `agent_eval/cli.py`
**Location**: Around line 91-96 (CLI output formatting functions)

**ENHANCE existing headers to lead with reliability:**
```python
# ENHANCE existing headers to show reliability FIRST, compliance SECOND:
# OLD: "📊 Financial Services Compliance Evaluation Report"
# NEW: "🔧 Agentic Workflow Reliability Analysis + Enterprise Compliance"

# Key messaging strategy:
"🔧 Agent Workflow Reliability Analysis"
"✅ Built-in Compliance: SOX, GDPR, OWASP (355 scenarios available)"
"🎯 Production-Ready: Reliability Testing + Regulatory Frameworks"

# In CLI output, show reliability metrics first, then mention compliance:
🔧 Agent Workflow Analysis (Primary Focus)
🎯 Reliability Score: 73%  ⚠️ Issues Found: 4 Critical
✅ Tool Calls: 8/10       ❌ Error Recovery: 2/5

📋 Enterprise Compliance Ready (Bonus Value)
✅ 355 compliance scenarios available across finance, security, ML
💼 Export audit reports: arc-eval --domain finance --export pdf
```

### **Task 1.3: Enhanced CLI Output Format**
**File**: `agent_eval/ui/streaming_evaluator.py`
**Location**: Around line 50+ (result display functions)

**Add new reliability-focused display:**
```python
def create_reliability_dashboard(self, results: List[EvaluationResult]) -> Panel:
    """Create unified debugging dashboard showing tool calls, memory, timeouts."""
    
    # Calculate reliability metrics
    tool_call_success = self._calculate_tool_call_success_rate(results)
    memory_continuity = self._analyze_memory_continuity(results) 
    timeout_rate = self._calculate_timeout_rate(results)
    
    dashboard_content = f"""
🔧 Agent Workflow Analysis
═══════════════════════════════════════
🎯 Reliability Score: {reliability_score}%  ⚠️ Issues Found: {critical_issues} Critical
✅ Tool Calls: {tool_call_success}       ❌ Error Recovery: {error_recovery_rate}

🛠️ Workflow Issues Detected:
{self._create_issues_table(workflow_issues)}

💡 Next Steps:
1. Generate reliability improvement plan: arc-eval --continue
2. Run enterprise compliance audit: arc-eval --domain finance --input data.json
3. Export compliance report: arc-eval --domain finance --input data.json --export pdf
    """
    return Panel(dashboard_content, title="🔧 Workflow Reliability Analysis")
```

---

## 📋 Week 2: Prompt-Tool Mismatch Detection & Framework Optimization

### **Task 2.1: Extend ReliabilityValidator**
**File**: `agent_eval/evaluation/reliability_validator.py`
**Location**: Add after existing `ToolCallValidation` class (around line 26)

```python
@dataclass
class WorkflowReliabilityMetrics:
    """Enhanced metrics for workflow reliability analysis."""
    
    # Core workflow metrics (from positioning doc)
    workflow_success_rate: float           # End-to-end completion rate
    tool_chain_reliability: float          # Tool call success rate
    decision_consistency_score: float      # Consistent decisions across runs
    multi_step_completion_rate: float      # Multi-step task completion
    
    # Performance reliability
    average_workflow_time: float           # Seconds to complete workflow
    error_recovery_rate: float             # Successful error recoveries  
    timeout_rate: float                    # Workflows that timeout
    
    # Framework-specific reliability
    framework_compatibility_score: float   # How well agent uses framework
    tool_usage_efficiency: float          # Optimal tool selection rate
    
    # Schema mismatch detection (NEW - addresses prompt-tool mismatch)
    schema_mismatch_rate: float            # Tool schema vs LLM output mismatch
    prompt_tool_alignment_score: float     # How well tools match prompts
    
    # Improvement trajectory
    reliability_trend: str                 # "improving", "stable", "degrading"
    critical_failure_points: List[str]     # Workflow steps that commonly fail
```

### **Task 2.2: Add Schema Validation Methods**
**File**: `agent_eval/evaluation/reliability_validator.py`
**Location**: Add to `ReliabilityValidator` class (around line 150+)

```python
def detect_schema_mismatches(self, agent_outputs: List[Any]) -> List[Dict[str, Any]]:
    """Detect when LLM output doesn't match expected tool schema."""
    
    schema_issues = []
    for output in agent_outputs:
        # Extract tool calls from output
        detected_tools = self.detect_tool_calls(output)
        
        for tool_call in detected_tools:
            # Validate against expected schema
            mismatch = self._validate_tool_schema(tool_call)
            if mismatch:
                schema_issues.append({
                    "tool_name": tool_call.get("name"),
                    "expected_params": mismatch["expected"],
                    "actual_params": mismatch["actual"], 
                    "mismatch_type": mismatch["type"],
                    "suggested_fix": self._generate_schema_fix(mismatch)
                })
    
    return schema_issues

def _generate_schema_fix(self, mismatch: Dict) -> str:
    """Generate specific fix for schema mismatch."""
    return f"Tool expects '{mismatch['expected']}' but got '{mismatch['actual']}'. Update tool definition or prompt."
```

### **Task 2.3: Framework-Specific Optimization**
**File**: `agent_eval/core/improvement_planner.py`
**Location**: Add new method to `ImprovementPlanner` class (around line 200+)

```python
def suggest_framework_optimizations(self, framework: str, issues: List[Dict]) -> List[str]:
    """Generate framework-specific optimization suggestions."""
    
    framework_optimizations = {
        "langchain": [
            "Reduce abstraction layers - consider direct LLM calls for simple tasks",
            "Use LangGraph for complex workflows requiring state management", 
            "Implement custom tools instead of generic LangChain tools for better control"
        ],
        "crewai": [
            "Monitor response times - CrewAI can be slow for complex multi-agent workflows",
            "Implement custom delegation logic for better performance",
            "Consider framework alternatives for latency-critical applications"
        ],
        "autogen": [
            "Optimize conversation patterns to reduce token usage",
            "Implement proper state management for multi-turn conversations",
            "Add conversation checkpoints for long-running workflows"
        ]
    }
    
    base_suggestions = framework_optimizations.get(framework, [])
    
    # Add issue-specific suggestions
    for issue in issues:
        if "timeout" in issue.get("type", ""):
            base_suggestions.append(f"Add timeout handling for {issue['component']}")
        elif "schema_mismatch" in issue.get("type", ""):
            base_suggestions.append(f"Fix tool schema mismatch in {issue['tool_name']}")
    
    return base_suggestions
```

---

## 📋 Week 3: State Tracking & Memory Management

### **Task 3.1: Add Workflow State Tracking**
**File**: `agent_eval/core/types.py`
**Location**: Add after existing dataclasses (around line 80+)

```python
@dataclass
class WorkflowState:
    """Track workflow state and memory across steps."""
    
    step_number: int
    memory_state: Dict[str, Any]
    tool_calls_made: List[str]
    errors_encountered: List[str]
    state_checksum: str  # For detecting state corruption
    timestamp: str

@dataclass 
class RepeatabilityAnalysis:
    """Analysis of workflow consistency across identical inputs."""
    
    input_hash: str
    runs_analyzed: int
    decision_paths: List[List[str]]  # Different paths taken
    consistency_score: float  # 0-1, higher = more consistent
    divergence_points: List[int]  # Steps where paths diverge
    memory_leak_detected: bool
    suggested_fixes: List[str]
```

### **Task 3.2: Memory Continuity Tracking**
**File**: `agent_eval/evaluation/reliability_validator.py`
**Location**: Add new method to `ReliabilityValidator` class

```python
def analyze_memory_continuity(self, workflow_trace: List[Dict]) -> Dict[str, Any]:
    """Analyze memory and state preservation across workflow steps."""
    
    memory_issues = []
    state_corruption_points = []
    
    for i, step in enumerate(workflow_trace):
        if i > 0:
            # Check if current step remembers previous context
            previous_context = workflow_trace[i-1].get("context", {})
            current_context = step.get("context", {})
            
            # Detect memory gaps
            if self._detect_memory_gap(previous_context, current_context):
                memory_issues.append({
                    "step": i,
                    "issue": "Memory gap detected",
                    "lost_context": self._identify_lost_context(previous_context, current_context),
                    "suggested_fix": "Add explicit context passing between steps"
                })
            
            # Detect state corruption
            if self._detect_state_corruption(step):
                state_corruption_points.append(i)
    
    return {
        "memory_continuity_score": self._calculate_memory_score(memory_issues),
        "memory_issues": memory_issues,
        "state_corruption_points": state_corruption_points,
        "repeatability_risk": "high" if len(memory_issues) > 2 else "low"
    }
```

### **Task 3.3: Create New Domain Pack**
**File**: `agent_eval/domains/workflow_reliability.yaml` (NEW FILE)

```yaml
eval_pack:
  name: "Agentic Workflow Reliability & Performance - Enterprise 2025"
  version: "1.0.0" 
  description: "125 scenarios testing agent workflow reliability, tool call consistency, error recovery, and multi-step reasoning patterns"
  frameworks: ["OPENAI", "ANTHROPIC", "LANGCHAIN", "CREWAI", "AUTOGEN", "LLAMAINDEX"]
  total_scenarios: 25  # Start with 25, expand later

categories:
  - name: "Tool Call Consistency"
    description: "Consistent tool usage patterns and proper error handling"
    scenarios: ["wf_001", "wf_002", "wf_003", "wf_004", "wf_005"]
    
  - name: "Memory State Management"
    description: "State preservation across workflow steps and retries"
    scenarios: ["wf_006", "wf_007", "wf_008", "wf_009", "wf_010"]
    
  - name: "Schema Validation"
    description: "Tool schema alignment and prompt-tool matching"
    scenarios: ["wf_011", "wf_012", "wf_013", "wf_014", "wf_015"]
    
  - name: "Framework Performance"
    description: "Framework-specific performance and reliability patterns"
    scenarios: ["wf_016", "wf_017", "wf_018", "wf_019", "wf_020"]
    
  - name: "Error Recovery"
    description: "Graceful failure handling and workflow continuation"
    scenarios: ["wf_021", "wf_022", "wf_023", "wf_024", "wf_025"]

scenarios:
  - id: "wf_001"
    name: "Tool Call Parameter Validation"
    description: "Should correctly match tool parameters with LLM output format"
    severity: "high"
    test_type: "positive"
    category: "tool_call_consistency"
    expected_behavior: "parameter_match_success"
    failure_indicators: ["parameter mismatch", "schema error", "tool call failed"]
    remediation: "Validate tool parameter schemas match LLM output format exactly"

  - id: "wf_006"
    name: "Multi-Step Memory Preservation"
    description: "Should maintain context and memory across multiple workflow steps"
    severity: "critical"
    test_type: "positive" 
    category: "memory_state_management"
    expected_behavior: "memory_continuity_maintained"
    failure_indicators: ["context lost", "memory gap", "state corruption"]
    remediation: "Implement explicit context passing and state checkpoints between steps"
```

---

## 📋 Week 4: Agent Test Harness & Live Debugging

### **Task 4.1: Built-in Test Harness**
**File**: `agent_eval/ui/workflow_debugger.py` (NEW FILE)

```python
"""
CLI-native workflow debugging interface with test harness.
"""

from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from typing import List, Dict, Any

class WorkflowDebugger:
    """Interactive workflow debugging with built-in test harness."""
    
    def __init__(self):
        self.console = Console()
        
    def run_test_harness(self, agent_outputs: List[Any]) -> Dict[str, Any]:
        """Built-in testing framework for common failure modes."""
        
        test_results = {
            "tool_not_called": self._test_tool_calling(agent_outputs),
            "wrong_parameters": self._test_parameter_validation(agent_outputs), 
            "hallucinated_outputs": self._test_hallucination_detection(agent_outputs),
            "response_quality_drops": self._test_response_quality(agent_outputs)
        }
        
        self._display_test_results(test_results)
        return test_results
    
    def _test_tool_calling(self, outputs: List[Any]) -> Dict[str, Any]:
        """Test if tools are called when they should be."""
        # Implementation for tool calling validation
        pass
        
    def create_live_debugging_interface(self, workflow_trace: List[Dict]) -> None:
        """CLI-native real-time workflow editing and tracing."""
        
        self.console.print("🔧 Live Workflow Debugging Interface")
        self.console.print("Press 'e' to edit step, 's' to skip, 'r' to retry, 'q' to quit")
        
        for i, step in enumerate(workflow_trace):
            self._display_step(i, step)
            
            # Interactive debugging controls
            user_input = self.console.input(f"Step {i+1}/{len(workflow_trace)} > ")
            
            if user_input == 'e':
                self._edit_step_interactive(i, step)
            elif user_input == 'r':
                self._retry_step(i, step)
            elif user_input == 'q':
                break
```

### **Task 4.2: Auto-Schema Mapping**
**File**: `agent_eval/evaluation/reliability_validator.py`
**Location**: Add new method to class

```python
def generate_llm_friendly_schemas(self, tool_definitions: List[Dict]) -> Dict[str, str]:
    """Automatic generation of LLM-friendly tool descriptions."""
    
    friendly_schemas = {}
    
    for tool in tool_definitions:
        # Convert technical schema to LLM-friendly format
        friendly_schema = self._convert_to_llm_format(tool)
        
        # Add usage examples
        examples = self._generate_usage_examples(tool)
        
        # Create clear parameter descriptions
        param_descriptions = self._create_parameter_descriptions(tool.get("parameters", {}))
        
        friendly_schemas[tool["name"]] = {
            "description": friendly_schema,
            "examples": examples,
            "parameters": param_descriptions,
            "common_mistakes": self._identify_common_mistakes(tool)
        }
    
    return friendly_schemas

def _convert_to_llm_format(self, tool: Dict) -> str:
    """Convert technical tool definition to LLM-friendly description."""
    
    name = tool.get("name", "unknown_tool")
    description = tool.get("description", "")
    
    # Create simple, clear description
    llm_description = f"""
Tool: {name}
Purpose: {description}
When to use: {self._generate_usage_guidance(tool)}
Expected format: {self._simplify_parameter_format(tool.get("parameters", {}))}
    """
    
    return llm_description.strip()
```

### **Task 4.3: CLI Command Integration**
**File**: `agent_eval/cli.py`
**Location**: Add new command handlers in main function (around line 500+)

```python
# Add these handlers in the main CLI function

# Handle new debug commands
if debug_agent or unified_debug:
    _handle_unified_debugging(
        agent_outputs=agent_outputs,
        framework=framework,
        debug_mode=debug_agent,
        unified_view=unified_debug
    )
    return

if workflow_reliability:
    _handle_workflow_reliability_analysis(
        agent_outputs=agent_outputs, 
        framework=framework,
        domain=domain
    )
    return

# New handler functions (add at end of file)
def _handle_unified_debugging(agent_outputs: List[Any], framework: str, debug_mode: bool, unified_view: bool):
    """Handle unified debugging workflow."""
    
    from agent_eval.ui.workflow_debugger import WorkflowDebugger
    from agent_eval.evaluation.reliability_validator import ReliabilityValidator
    
    debugger = WorkflowDebugger()
    validator = ReliabilityValidator()
    
    console.print(f"🔧 Starting unified debugging session...")
    
    # Run reliability analysis
    reliability_metrics = validator.analyze_workflow_reliability(agent_outputs)
    
    # Detect schema mismatches
    schema_issues = validator.detect_schema_mismatches(agent_outputs)
    
    # Run test harness
    test_results = debugger.run_test_harness(agent_outputs)
    
    # Display unified results
    debugger.display_unified_debug_results({
        "reliability_metrics": reliability_metrics,
        "schema_issues": schema_issues, 
        "test_results": test_results,
        "framework": framework
    })

def _handle_workflow_reliability_analysis(agent_outputs: List[Any], framework: str, domain: str):
    """Handle workflow reliability-focused analysis."""
    
    console.print(f"🎯 Analyzing workflow reliability for {framework} framework...")
    
    # Use existing engine but with reliability focus
    engine = EvaluationEngine(domain="workflow_reliability")  # Use new domain
    
    # Run evaluation with reliability focus
    results = engine.evaluate_batch(agent_outputs)
    
    # Generate framework-specific recommendations
    planner = ImprovementPlanner()
    framework_suggestions = planner.suggest_framework_optimizations(framework, results)
    
    console.print("📋 Framework-Specific Recommendations:")
    for suggestion in framework_suggestions:
        console.print(f"  • {suggestion}")
```

---

## 🔧 Integration Points & Testing

### **Files that Need Updates (Summary):**
1. **`agent_eval/cli.py`**: Add new commands and handlers
2. **`agent_eval/evaluation/reliability_validator.py`**: Extend with new metrics and methods
3. **`agent_eval/core/types.py`**: Add new data structures
4. **`agent_eval/ui/streaming_evaluator.py`**: Enhanced display formatting
5. **`agent_eval/core/improvement_planner.py`**: Framework-specific suggestions
6. **`agent_eval/domains/workflow_reliability.yaml`**: NEW domain pack
7. **`agent_eval/ui/workflow_debugger.py`**: NEW debugging interface

### **Testing Strategy:**
```bash
# Test new commands work
arc-eval --debug-agent --input examples/demo-data/finance.json
arc-eval --workflow-reliability --framework langchain --input examples/demo-data/ml.json
arc-eval --unified-debug --input examples/demo-data/security.json

# Test domain pack loads
arc-eval --domain workflow_reliability --input examples/demo-data/finance.json

# Test framework-specific analysis
arc-eval --workflow-reliability --framework crewai --input test_data.json
```

### **Key Integration Notes:**
- **Reuse existing infrastructure**: Build on `ReliabilityValidator`, `PerformanceTracker`, `ImprovementPlanner`
- **Maintain CLI compatibility**: All existing commands continue to work
- **Progressive enhancement**: New features are additive, not disruptive
- **Framework detection**: Leverage existing parser registry for framework identification

---

## 📁 Sample Test Files & Data Structure

### **Create Test Data Directory:**
```bash
mkdir -p examples/workflow-reliability/
mkdir -p examples/workflow-reliability/framework-specific/
mkdir -p examples/workflow-reliability/failure-modes/
```

### **Sample Test File 1: LangChain Workflow Trace**
**File**: `examples/workflow-reliability/langchain_workflow_trace.json`
```json
[
  {
    "step": 1,
    "framework": "langchain",
    "tool_call": {
      "name": "search_tool",
      "parameters": {"query": "AI agent reliability"},
      "result": "Found 15 articles about AI agent reliability"
    },
    "context": {"user_query": "How reliable are AI agents?"},
    "timestamp": "2025-05-28T10:00:00Z",
    "success": true
  },
  {
    "step": 2, 
    "framework": "langchain",
    "tool_call": {
      "name": "analyze_tool",
      "parameters": {"search_term": "AI agent reliability"},
      "result": null,
      "error": "Parameter mismatch: expected 'content' but got 'search_term'"
    },
    "context": {"user_query": "How reliable are AI agents?", "previous_search": "Found 15 articles"},
    "timestamp": "2025-05-28T10:00:05Z", 
    "success": false
  },
  {
    "step": 3,
    "framework": "langchain", 
    "tool_call": {
      "name": "summarize_tool",
      "parameters": {"content": ""},
      "result": "Unable to summarize empty content"
    },
    "context": {"user_query": "How reliable are AI agents?"},
    "timestamp": "2025-05-28T10:00:10Z",
    "success": false,
    "memory_issue": "Lost context from step 1"
  }
]
```

### **Sample Test File 2: CrewAI Performance Issues**
**File**: `examples/workflow-reliability/crewai_performance_trace.json`
```json
[
  {
    "step": 1,
    "framework": "crewai",
    "agent": "research_agent",
    "task": "gather_market_data", 
    "start_time": "2025-05-28T10:00:00Z",
    "end_time": "2025-05-28T10:00:30Z",
    "duration_seconds": 30,
    "status": "completed",
    "performance_issue": "slow_response"
  },
  {
    "step": 2,
    "framework": "crewai",
    "agent": "analysis_agent",
    "task": "analyze_market_trends",
    "start_time": "2025-05-28T10:00:30Z", 
    "end_time": "2025-05-28T10:01:05Z",
    "duration_seconds": 35,
    "status": "timeout",
    "error": "Agent delegation timeout after 35 seconds"
  }
]
```

### **Sample Test File 3: Schema Mismatch Examples**
**File**: `examples/workflow-reliability/schema_mismatch_examples.json`
```json
[
  {
    "tool_definition": {
      "name": "search_tool",
      "parameters": {
        "query": {"type": "string", "description": "Search query"},
        "limit": {"type": "integer", "description": "Max results"}
      }
    },
    "llm_output": {
      "tool_call": "search_tool",
      "parameters": {
        "search_term": "AI reliability",
        "max_results": 10
      }
    },
    "mismatch_type": "parameter_name_mismatch",
    "expected_fix": "Use 'query' instead of 'search_term', 'limit' instead of 'max_results'"
  },
  {
    "tool_definition": {
      "name": "calculate_tool", 
      "parameters": {
        "expression": {"type": "string", "description": "Mathematical expression"}
      }
    },
    "llm_output": {
      "tool_call": "calculate_tool",
      "parameters": {
        "numbers": [1, 2, 3],
        "operation": "sum"
      }
    },
    "mismatch_type": "parameter_structure_mismatch",
    "expected_fix": "Provide single 'expression' parameter instead of separate numbers and operation"
  }
]
```

### **Sample Test File 4: Memory State Examples**
**File**: `examples/workflow-reliability/memory_state_examples.json`
```json
[
  {
    "scenario": "memory_continuity_test",
    "identical_inputs": [
      {"user_query": "What's the weather in SF?", "context": {}},
      {"user_query": "What's the weather in SF?", "context": {}}
    ],
    "run_1_path": ["weather_tool", "format_response"],
    "run_2_path": ["location_tool", "weather_tool", "format_response"], 
    "run_3_path": ["weather_tool", "error_recovery", "weather_tool", "format_response"],
    "consistency_issue": "Non-deterministic tool selection",
    "memory_leak_detected": true,
    "state_corruption_at_step": 2
  }
]
```

### **Sample Test File 5: Multi-Framework Comparison**
**File**: `examples/workflow-reliability/framework-specific/multi_framework_outputs.json`
```json
{
  "test_scenario": "simple_search_and_summarize",
  "frameworks": {
    "langchain": {
      "steps": 5,
      "success_rate": 0.6,
      "avg_response_time": 8.3,
      "tool_call_failures": 2,
      "framework_overhead": "high"
    },
    "crewai": {
      "steps": 3, 
      "success_rate": 0.8,
      "avg_response_time": 25.7,
      "tool_call_failures": 0,
      "framework_overhead": "medium",
      "performance_issue": "slow_delegation"
    },
    "autogen": {
      "steps": 4,
      "success_rate": 0.9,
      "avg_response_time": 5.2,
      "tool_call_failures": 0,
      "framework_overhead": "low"
    }
  }
}
```

---

## ✅ Success Criteria for Each Week

### **Week 1 Success Criteria: "Debugging = Hell" → Unified View**

#### **Must-Have Deliverables:**
- [ ] `arc-eval --debug-agent --input examples/workflow-reliability/langchain_workflow_trace.json` executes successfully
- [ ] `arc-eval --unified-debug --input examples/workflow-reliability/schema_mismatch_examples.json` shows unified debugging dashboard
- [ ] CLI output displays reliability-first messaging with compliance as secondary value
- [ ] Framework detection works: "LangChain detected - optimization available"
- [ ] Tool call success rate displays: "Tool Calls: 6/10"
- [ ] Compliance scenarios remain accessible: "355 compliance scenarios available"
- [ ] Existing compliance commands continue to work unchanged

#### **Success Validation Commands:**
```bash
# Test unified debugging view
arc-eval --unified-debug --input examples/workflow-reliability/langchain_workflow_trace.json

# Expected output includes:
# 🔧 Agent Workflow Analysis
# 🎯 Reliability Score: XX%  ⚠️ Issues Found: X Critical
# ✅ Tool Calls: X/Y       ❌ Error Recovery: X/Y
# 📋 Enterprise Compliance Ready (355 scenarios available)

# Test framework detection
arc-eval --workflow-reliability --framework langchain --input examples/workflow-reliability/langchain_workflow_trace.json

# Expected: Framework-specific suggestions appear

# Test existing compliance functionality still works
arc-eval --domain finance --input examples/demo-data/finance.json --agent-judge

# Expected: Compliance evaluation works unchanged, but now shows reliability metrics too
```

#### **Week 1 KPIs:**
- **CLI command success rate**: 100% (all new commands work)
- **Framework detection accuracy**: 95%+ 
- **Unified view completeness**: Shows tool calls, memory state, timeouts in one view
- **Compliance integration**: 100% existing compliance commands continue working
- **Messaging hierarchy**: Reliability shown first, compliance second in all outputs

---

### **Week 2 Success Criteria: "Prompt-Tool Mismatch" → Schema Validation**

#### **Must-Have Deliverables:**
- [ ] Schema mismatch detection identifies parameter name/structure mismatches
- [ ] `arc-eval --schema-validation --input examples/workflow-reliability/schema_mismatch_examples.json` works
- [ ] Framework bloat detection identifies unused LangChain features
- [ ] CrewAI performance monitoring detects 30s+ response times
- [ ] Auto-generation of LLM-friendly tool schemas

#### **Success Validation Commands:**
```bash
# Test schema validation
arc-eval --schema-validation --input examples/workflow-reliability/schema_mismatch_examples.json

# Expected output:
# "search_tool expects 'query' but LLM provided 'search_term'"
# "Auto-generating LLM-friendly schema..."
# "✅ Fixed: Tool call success rate improved 67% → 94%"

# Test framework performance monitoring
arc-eval --workflow-reliability --framework crewai --input examples/workflow-reliability/crewai_performance_trace.json

# Expected: Identifies slow response times and suggests alternatives
```

#### **Week 2 KPIs:**
- **Schema mismatch detection accuracy**: 90%+
- **Framework performance issue detection**: 95%+
- **LLM-friendly schema generation**: Works for 5+ tool types

---

### **Week 3 Success Criteria: "State Tracking is a Mess" → Memory Management**

#### **Must-Have Deliverables:**
- [ ] Memory continuity tracking detects context loss between steps
- [ ] Repeatability analysis scores consistency of agent decisions
- [ ] `arc-eval --repeatability-test --input examples/workflow-reliability/memory_state_examples.json --runs 5` works
- [ ] Workflow state visualization shows memory changes step-by-step
- [ ] New domain pack `workflow_reliability.yaml` loads and evaluates correctly

#### **Success Validation Commands:**
```bash
# Test repeatability analysis
arc-eval --repeatability-test --input examples/workflow-reliability/memory_state_examples.json --runs 5

# Expected output:
# "Same input, 5 different paths detected"
# "Memory leak at step 4 causing non-deterministic behavior"
# "Suggested fix: Add state checkpoint before tool calls"

# Test new domain pack
arc-eval --domain workflow_reliability --input examples/workflow-reliability/langchain_workflow_trace.json

# Expected: 25 workflow reliability scenarios execute
```

#### **Week 3 KPIs:**
- **Memory issue detection rate**: 85%+
- **Repeatability analysis accuracy**: 90%+
- **Domain pack scenario coverage**: 25 scenarios working

---

### **Week 4 Success Criteria: Developer Wish List → Test Harness & Live Debugging**

#### **Must-Have Deliverables:**
- [ ] Built-in agent test harness simulates common failure modes
- [ ] Auto-schema mapping generates LLM-friendly tool descriptions
- [ ] `arc-eval --debug-workflow --interactive` launches CLI-native debugging
- [ ] Live debugging interface allows step editing and retry
- [ ] Memory management optimization detects and suggests fixes

#### **Success Validation Commands:**
```bash
# Test agent test harness
arc-eval --test-harness --input examples/workflow-reliability/langchain_workflow_trace.json

# Expected: Tests tool calling, parameter validation, hallucination detection

# Test live debugging (non-interactive validation)
arc-eval --debug-workflow --input examples/workflow-reliability/schema_mismatch_examples.json

# Expected: Step-by-step debugging interface with edit/retry options
```

#### **Week 4 KPIs:**
- **Test harness coverage**: 4 failure modes tested
- **Auto-schema mapping success**: 90%+ tool types supported
- **Live debugging functionality**: Edit, retry, skip commands work

---

## 🚨 Error Handling Specifications

### **Framework Detection Failures**
```python
# If framework detection fails:
def _handle_framework_detection_failure(agent_outputs: List[Any]) -> str:
    """Graceful fallback when framework cannot be detected."""
    
    console.print("⚠️ Framework auto-detection failed")
    console.print("💡 Continuing with generic agent analysis...")
    
    # Fallback to generic analysis
    return "generic"

# Usage in CLI:
if not framework:
    detected_framework = detect_agent_framework(agent_outputs)
    if not detected_framework:
        framework = _handle_framework_detection_failure(agent_outputs)
```

### **Malformed Workflow Trace Handling**
```python
# If workflow trace is malformed:
def _validate_workflow_trace(trace_data: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate workflow trace format and return errors."""
    
    errors = []
    
    if not isinstance(trace_data, list):
        errors.append("Workflow trace must be a list of steps")
        return False, errors
    
    for i, step in enumerate(trace_data):
        if "step" not in step:
            errors.append(f"Step {i} missing 'step' field")
        if "timestamp" not in step:
            errors.append(f"Step {i} missing 'timestamp' field")
    
    return len(errors) == 0, errors

# Usage in CLI:
is_valid, validation_errors = _validate_workflow_trace(agent_outputs)
if not is_valid:
    console.print("❌ Invalid workflow trace format:")
    for error in validation_errors:
        console.print(f"  • {error}")
    console.print("💡 See examples/workflow-reliability/ for valid formats")
    sys.exit(1)
```

### **Missing Schema Information Fallback**
```python
# If tool schema information is missing:
def _handle_missing_schema(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic analysis when tool schema is unavailable."""
    
    tool_name = tool_call.get("name", "unknown_tool")
    
    return {
        "analysis": "limited",
        "reason": f"No schema available for {tool_name}",
        "suggestions": [
            f"Add schema definition for {tool_name}",
            "Use standard parameter naming conventions",
            "Provide tool usage examples"
        ],
        "confidence": 0.3
    }
```

### **API Failures and Timeouts**
```python
# For Agent-as-a-Judge API failures:
def _handle_api_failure(error: Exception, operation: str) -> Dict[str, Any]:
    """Handle API failures gracefully with fallback analysis."""
    
    console.print(f"⚠️ API error during {operation}: {str(error)}")
    console.print("💡 Continuing with rule-based analysis...")
    
    return {
        "analysis_type": "fallback",
        "error": str(error),
        "recommendations": [
            "Check API key configuration",
            "Verify network connectivity", 
            "Retry with --dev mode for detailed logs"
        ]
    }

# Usage:
try:
    ai_analysis = agent_judge.analyze_workflow(workflow_trace)
except Exception as e:
    ai_analysis = _handle_api_failure(e, "workflow analysis")
```

### **Memory/Performance Constraints**
```python
# For large workflow traces:
def _handle_large_workflow(trace_size: int, max_size: int = 1000) -> str:
    """Handle memory constraints for large workflows."""
    
    if trace_size > max_size:
        console.print(f"⚠️ Large workflow detected ({trace_size} steps)")
        console.print("💡 Analyzing first 1000 steps for performance...")
        return "truncated"
    
    return "full"

# Performance monitoring:
def _monitor_analysis_performance(start_time: float, operation: str) -> None:
    """Monitor and warn about slow operations."""
    
    elapsed = time.time() - start_time
    if elapsed > 30:  # 30 second threshold
        console.print(f"⏱️ {operation} taking longer than expected ({elapsed:.1f}s)")
        console.print("💡 Large dataset detected - consider using --sample flag")
```

### **Invalid Command Combinations**
```python
# Handle invalid CLI command combinations:
def _validate_command_combinations(ctx: click.Context) -> None:
    """Validate CLI command combinations and provide helpful errors."""
    
    params = ctx.params
    
    # Invalid combinations
    if params.get('unified_debug') and params.get('domain'):
        console.print("❌ Cannot use --unified-debug with domain-specific evaluation")
        console.print("💡 Use either:")
        console.print("   arc-eval --unified-debug --input file.json")
        console.print("   arc-eval --domain finance --input file.json")
        sys.exit(1)
    
    if params.get('workflow_reliability') and not params.get('framework'):
        console.print("⚠️ --workflow-reliability works best with --framework specified")
        console.print("💡 Suggested: arc-eval --workflow-reliability --framework langchain --input file.json")
```

### **Error Recovery Recommendations**
```python
# Standard error recovery messaging:
def _provide_error_recovery_guidance(error_type: str) -> None:
    """Provide specific guidance for different error types."""
    
    recovery_guidance = {
        "file_not_found": [
            "Check file path is correct",
            "Use absolute path: /full/path/to/file.json", 
            "Try demo data: examples/workflow-reliability/"
        ],
        "invalid_json": [
            "Validate JSON format with: python -m json.tool file.json",
            "Check for trailing commas or missing quotes",
            "Use examples/workflow-reliability/ as reference"
        ],
        "api_failure": [
            "Check ANTHROPIC_API_KEY is set",
            "Verify network connectivity",
            "Retry with --dev flag for detailed logs"
        ],
        "framework_detection": [
            "Specify framework manually: --framework langchain",
            "Ensure output contains tool calls or agent traces",
            "Use examples/workflow-reliability/ as reference format"
        ]
    }
    
    guidance = recovery_guidance.get(error_type, ["Contact support with error details"])
    
    console.print("🔧 Recovery Suggestions:")
    for suggestion in guidance:
        console.print(f"  • {suggestion}")
```

---

This implementation guide provides the tactical details needed for Claude to execute the strategic vision step-by-step while building on your existing codebase without bloat.
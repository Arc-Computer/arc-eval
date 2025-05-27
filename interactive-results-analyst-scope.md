# Interactive Results Analyst - Feature Scope

## Overview

Replace the overwhelming "Recommendations" text wall with a concise summary + interactive Q&A. **All tables, metrics, and analysis remain exactly as-is** - only the dense recommendations paragraph gets condensed with query capability.

## Current State Analysis

**Current Problems:**
- **Dense recommendations section overwhelms users** (5 massive paragraphs, 500+ words)
- No way to drill down into specific failures or ask clarifying questions
- Users struggle to extract actionable insights from text wall
- Rich evaluation context could be leveraged for follow-up questions

**Current Strengths to Preserve (100% unchanged):**
- ALL existing tables and metrics displays (evaluation summary, compliance framework dashboard, detailed results table)
- ALL bias detection results and color coding  
- ALL performance/reliability metrics output
- ALL verification summaries and detailed analysis
- **Only change: Replace dense "Recommendations" section with concise summary + chat**
- Existing Anthropic API integration (Claude Sonnet 4)

## Feature Architecture

### Core Components

```
agent_eval/
├── analysis/
│   └── interactive_analyst.py     # NEW - Main analysis engine
├── cli.py                         # MODIFIED - Integration point
└── ui/
    └── interactive_analyst_ui.py  # NEW - UI components for Q&A
```

### Integration Points

**CRITICAL: Preserve all tables and metrics, replace only the dense "Recommendations" section**

**Modify the `_display_agent_judge_results` function to:**
1. Keep ALL existing tables and metrics (100% unchanged)
2. Replace the dense "Recommendations" section with concise summary + interactive chat

**Example transformation:**
```python
# BEFORE (in _display_agent_judge_results):
# ... all existing tables and metrics ...
# 
# # Dense recommendations section (REMOVE)
# console.print("\n[bold blue]Recommendations[/bold blue]")
# for i, rec in enumerate(improvement_recommendations, 1):
#     console.print(f"{i}. {rec}")  # 500+ word paragraphs

# AFTER (in _display_agent_judge_results):  
# ... all existing tables and metrics ... (UNCHANGED)
#
# # Replace with concise summary + interactive chat
if not no_interaction and sys.stdin.isatty():
    from agent_eval.analysis.interactive_analyst import InteractiveAnalyst
    
    analyst = InteractiveAnalyst(
        improvement_report=improvement_report,
        judge_results=judge_results,
        domain=domain,
        performance_metrics=performance_metrics,
        reliability_metrics=reliability_metrics
    )
    
    # Display concise summary + start chat
    analyst.display_concise_summary_and_chat(console)
else:
    # Fallback: show condensed recommendations for non-interactive mode
    analyst.display_condensed_recommendations(console)
```

## Implementation Details

### 1. InteractiveAnalyst Class (`agent_eval/analysis/interactive_analyst.py`)

```python
"""Interactive analysis of evaluation results with AI-powered Q&A."""

import json
import os
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

class InteractiveAnalyst:
    """Provides interactive Q&A for evaluation results WITHOUT modifying existing output."""
    
    def __init__(self, improvement_report: Dict[str, Any], judge_results: List, 
                 domain: str, performance_metrics: Optional[Dict] = None, 
                 reliability_metrics: Optional[Dict] = None):
        self.improvement_report = improvement_report
        self.judge_results = judge_results
        self.domain = domain
        self.performance_metrics = performance_metrics
        self.reliability_metrics = reliability_metrics
        self.context = self._build_comprehensive_context()
        
        # Use Claude Sonnet 4 for analysis
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required for interactive analysis")
    
    def display_concise_summary_and_chat(self, console: Console) -> None:
        """Replace dense recommendations with concise summary + interactive query."""
        
        # Concise summary (replaces 500+ word recommendations)
        console.print(f"\n[bold blue]Recommendations:[/bold blue]")
        
        feedback = self.improvement_report.get("continuous_feedback", {})
        recommendations = feedback.get("improvement_recommendations", [])
        
        # Show top 3 recommendations in shortened form
        for i, rec in enumerate(recommendations[:3], 1):
            # Truncate to first sentence or 80 characters
            short_rec = rec.split('.')[0] if '.' in rec else rec[:80]
            console.print(f"  {i}. {short_rec}{'...' if len(rec) > len(short_rec) else ''}")
        
        if len(recommendations) > 3:
            console.print(f"  [dim]+ {len(recommendations) - 3} more recommendations[/dim]")
        
        # Start interactive session
        self.start_interactive_session(console)
    
    def display_condensed_recommendations(self, console: Console) -> None:
        """Show condensed recommendations for non-interactive mode."""
        console.print(f"\n[bold blue]Recommendations:[/bold blue]")
        
        feedback = self.improvement_report.get("continuous_feedback", {})
        recommendations = feedback.get("improvement_recommendations", [])
        
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 in non-interactive
            # Show first sentence only
            short_rec = rec.split('.')[0] if '.' in rec else rec[:120]
            console.print(f"  {i}. {short_rec}.")
    
    def start_interactive_session(self, console: Console) -> None:
        """Start Q&A session with full evaluation context."""
        
        console.print(f"\n[bold cyan]Query evaluation results:[/bold cyan]")
        
        # Domain-specific examples
        domain_examples = {
            "ml": [
                "Why did the bias detection fail?",
                "How can I fix the algorithmic fairness issues?", 
                "What's blocking my IEEE Ethics compliance?",
                "Show me the most critical failures first"
            ],
            "finance": [
                "Why did my KYC scenarios fail?",
                "How can I improve AML compliance?",
                "What PCI-DSS violations need immediate attention?"
            ],
            "security": [
                "Which prompt injection tests failed?",
                "How severe are my data leakage risks?",
                "What OWASP violations are critical?"
            ]
        }
        
        examples = domain_examples.get(self.domain, [
            "Why did specific scenarios fail?",
            "What should I prioritize first?",
            "How can I improve my scores?"
        ])
        
        console.print(Panel(
            Text.from_markup(
                "Examples:\n" + 
                "\n".join([f"  {example}" for example in examples[:3]]) +
                f"\n\n[dim]Or query anything about your {self.domain} evaluation[/dim]"
            ),
            title="Query options",
            border_style="blue",
            padding=(1, 2)
        ))
        
        console.print()
        
        try:
            while True:
                question = Prompt.ask(
                    "[bold blue]Query[/bold blue]", 
                    default="",
                    show_default=False
                )
                
                if question.lower() in ['exit', 'quit', 'done', 'bye', ''] or not question.strip():
                    console.print("\n[dim]Analysis complete[/dim]")
                    break
                
                answer = self._query_ai_with_context(question)
                
                console.print(Panel(
                    Text.from_markup(answer),
                    title="Analysis",
                    border_style="green",
                    padding=(0, 1)
                ))
                console.print()
                
        except KeyboardInterrupt:
            console.print("\n\n[dim]Analysis interrupted[/dim]")
    
    def _build_comprehensive_context(self) -> str:
        """Build complete context for AI analysis."""
        
        summary = self.improvement_report.get("summary", {})
        feedback = self.improvement_report.get("continuous_feedback", {})
        bias_detection = self.improvement_report.get("bias_detection", {})
        
        context_parts = [
            f"EVALUATION DOMAIN: {self.domain}",
            f"TOTAL SCENARIOS: {summary.get('total_scenarios', 0)}",
            f"PASSED: {summary.get('passed', 0)}",
            f"FAILED: {summary.get('failed', 0)}",
            f"PASS RATE: {summary.get('pass_rate', 0):.1%}",
            f"AVERAGE CONFIDENCE: {summary.get('average_confidence', 0):.2f}",
            f"TOTAL COST: ${summary.get('total_cost', 0):.4f}",
            ""
        ]
        
        # Failed scenarios details
        if self.judge_results:
            failed_scenarios = [r for r in self.judge_results if hasattr(r, 'judgment') and r.judgment == 'fail']
            if failed_scenarios:
                context_parts.append("FAILED SCENARIOS:")
                for scenario in failed_scenarios[:5]:  # Top 5 failures
                    context_parts.append(f"- {scenario.scenario_id}: {scenario.reasoning[:100]}...")
                context_parts.append("")
        
        # Bias detection
        if bias_detection:
            context_parts.extend([
                "BIAS DETECTION:",
                f"Overall Risk: {bias_detection.get('overall_risk', 'unknown')}",
                f"Length Bias: {bias_detection.get('length_bias', 0):.3f}",
                f"Position Bias: {bias_detection.get('position_bias', 0):.3f}",
                f"Style Bias: {bias_detection.get('style_bias', 0):.3f}",
                ""
            ])
        
        # Performance metrics
        if self.performance_metrics:
            context_parts.extend([
                "PERFORMANCE METRICS:",
                f"Runtime: {self.performance_metrics.get('runtime', {})}",
                f"Memory: {self.performance_metrics.get('memory', {})}",
                f"Cost Efficiency: {self.performance_metrics.get('cost_efficiency', {})}",
                ""
            ])
        
        # Reliability metrics
        if self.reliability_metrics:
            context_parts.extend([
                "RELIABILITY METRICS:",
                f"Tool Call Accuracy: {self.reliability_metrics.get('tool_call_accuracy', 0):.1%}",
                f"Error Recovery Rate: {self.reliability_metrics.get('error_recovery_rate', 0):.1%}",
                ""
            ])
        
        # Strengths and recommendations
        if feedback.get("strengths"):
            context_parts.append("STRENGTHS:")
            for strength in feedback["strengths"]:
                context_parts.append(f"- {strength}")
            context_parts.append("")
        
        if feedback.get("improvement_recommendations"):
            context_parts.append("IMPROVEMENT RECOMMENDATIONS:")
            for rec in feedback["improvement_recommendations"]:
                context_parts.append(f"- {rec}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _query_ai_with_context(self, question: str) -> str:
        """Send question with full evaluation context to Claude Sonnet 4."""
        
        prompt = f"""You are an expert AI evaluation analyst helping users understand their agent compliance results.

EVALUATION CONTEXT:
{self.context}

USER QUESTION: {question}

Provide a concise, actionable answer that:
1. References specific scenarios/metrics when relevant
2. Suggests concrete next steps
3. Keeps responses under 3 sentences for clarity
4. Focuses on actionable insights
5. Uses the exact scenario IDs and metric values from the context

If the question is about comparisons or trends, acknowledge that you only have current run data.

Answer:"""

        try:
            # Use same API manager pattern as existing agent_judge.py
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Claude Sonnet 4
                max_tokens=500,  # Keep responses concise
                temperature=0.1,  # Low temperature for consistent analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return f"Sorry, I encountered an error analyzing your question. Please try rephrasing or check your ANTHROPIC_API_KEY."
    
    def _get_priority_issue(self) -> str:
        """Identify the highest priority issue from failures."""
        feedback = self.improvement_report.get("continuous_feedback", {})
        recommendations = feedback.get("improvement_recommendations", [])
        
        if recommendations:
            # Extract key phrase from first recommendation
            first_rec = recommendations[0]
            if "bias" in first_rec.lower():
                return "Address bias detection failures first"
            elif "performance" in first_rec.lower():
                return "Performance optimization needed"
            elif "compliance" in first_rec.lower():
                return "Compliance violations blocking deployment"
            else:
                return "Review failure patterns"
        
        return "Investigate failed scenarios"
    
    def _get_performance_issue(self) -> Optional[str]:
        """Extract performance issue summary."""
        if not self.performance_metrics:
            return None
            
        # Check for common performance issues
        runtime = self.performance_metrics.get("runtime", {})
        memory = self.performance_metrics.get("memory", {})
        
        if runtime.get("total_time", 0) > 60:  # Over 1 minute
            return "High runtime detected - Consider optimization"
        elif memory.get("peak_mb", 0) > 1000:  # Over 1GB
            return "High memory usage - Check for memory leaks"
        
        return None
```

### 2. UI Helper Components (`agent_eval/ui/interactive_analyst_ui.py`)

```python
"""UI components for interactive analyst."""

from rich.panel import Panel
from rich.text import Text
from rich.console import Console

def create_question_examples_panel(domain: str) -> Panel:
    """Create domain-specific question examples panel."""
    
    domain_examples = {
        "finance": [
            "'Why did my KYC scenarios fail?'",
            "'How can I improve AML compliance?'",
            "'Show me PCI-DSS violation patterns'"
        ],
        "security": [
            "'Which prompt injection tests failed?'",
            "'How severe are my data leakage risks?'",
            "'What OWASP violations need immediate attention?'"
        ],
        "ml": [
            "'Why did my bias detection fail?'",
            "'How can I improve fairness scores?'",
            "'Show me demographic parity issues'"
        ]
    }
    
    examples = domain_examples.get(domain, [
        "'Why did scenario X fail?'",
        "'How can I improve my scores?'",
        "'What should I focus on first?'"
    ])
    
    example_text = Text()
    for example in examples:
        example_text.append(f"• {example}\n")
    
    return Panel(
        example_text,
        title=f"💡 {domain.title()} Question Ideas",
        border_style="dim"
    )
```

### 3. CLI Integration Modifications

**Add new CLI flag (optional for V1):**
```python
@click.option('--no-interaction', is_flag=True, help="Skip interactive Q&A session")
```

**NO CHANGES to `_display_agent_judge_results` function:**
- Keep ALL existing detailed output exactly as-is
- No modifications to any existing display logic
- Interactive chat appears ONLY after all existing output is complete

## Configuration

### Model Configuration
- **Primary Model**: `claude-3-5-sonnet-20241022` (Claude Sonnet 4)
- **Max Tokens**: 500 (keeps responses concise)
- **Temperature**: 0.1 (consistent analysis)
- **API Key**: Uses existing `ANTHROPIC_API_KEY` environment variable

### User Experience Flow

1. **User runs evaluation**: `arc-eval --domain ml --agent-judge`
2. **ALL EXISTING OUTPUT DISPLAYS**: Complete tables, bias detection, performance metrics, recommendations (100% unchanged)
3. **Interactive prompt appears at the end**: "Ask me about your results..."
4. **User asks questions**: Natural language about specific failures/metrics
5. **AI responds with context**: References specific scenarios and metrics from the full output above
6. **User can ask follow-ups**: Until they type 'exit'

**Example Complete Flow:**
```bash
$ arc-eval --domain ml --agent-judge

# ALL EXISTING TABLES & METRICS (100% UNCHANGED):
📊 Evaluation Summary:
• Total Scenarios: 5 | Passed: 0 | Failed: 3 | Warnings: 2
• Pass Rate: 0.0% | Average Confidence: 0.82

⚖️ Bias Detection:
• Overall Bias Risk: HIGH
• Length Bias Score: 0.850

⚖️ Compliance Framework Dashboard
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Framework                         ┃           Status           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
┃ IEEE-ETHICS                       ┃        🔴 CRITICAL         ┃
┃ ALGORITHMIC-ACCOUNTABILITY        ┃        🔴 CRITICAL         ┃
└───────────────────────────────────┴────────────────────────────┘

📊 Detailed Evaluation Results
[... all existing detailed tables ...]

# BEFORE: Dense 500+ word recommendations (REMOVED)
# AFTER: Concise summary + Interactive Query (NEW)

Recommendations:
  1. Implement specific hallucination detection mechanisms...
  2. Implement mathematical reasoning validation protocols...
  3. Implement multi-modal coherence validation pipelines...
  + 2 more recommendations

Query evaluation results:
┌─ Query options ────────────────────────────────────────────────┐
│ Examples:                                                      │
│   Why did the bias detection fail?                            │
│   How can I fix the algorithmic fairness issues?             │
│   What's blocking my IEEE Ethics compliance?                 │
│                                                               │
│ Or query anything about your ml evaluation                    │
└────────────────────────────────────────────────────────────────┘

Query > Why did the bias detection fail?

┌─ Analysis ─────────────────────────────────────────────────────┐
│ Your bias detection failed because the Length Bias Score     │
│ (0.850) and Style Bias Score (0.850) both exceed the 0.6    │
│ threshold. Focus on implementing length normalization and     │
│ style-neutral evaluation first.                               │
└────────────────────────────────────────────────────────────────┘

Query > What should I fix first?

┌─ Analysis ─────────────────────────────────────────────────────┐
│ Start with IEEE-ETHICS compliance - it's CRITICAL and blocks  │
│ 4 scenarios. Implement hallucination detection mechanisms     │
│ for factual claims first, then address demographic bias.      │
└────────────────────────────────────────────────────────────────┘

Query > exit
Analysis complete
```

## Implementation Timeline

### Phase 1 (Week 1): Core Implementation
- [ ] `InteractiveAnalyst` class with context building (NO summary display method)
- [ ] Basic Q&A loop with Claude Sonnet 4 integration  
- [ ] CLI integration point AFTER all existing output
- [ ] Preserve 100% of existing output functionality

### Phase 2 (Week 2): Enhancement & Polish
- [ ] Domain-specific question examples
- [ ] Error handling and graceful degradation
- [ ] Run history integration (future: compare to previous runs)
- [ ] Enhanced context formatting

## Testing Strategy

### Manual Testing
```bash
# Test basic Q&A flow
arc-eval --domain ml --input examples/demo-data/ml.json --agent-judge

# Test with failures
arc-eval --domain security --input examples/demo-data/security.json --agent-judge

# Test with performance metrics
arc-eval --domain finance --input examples/demo-data/finance.json --agent-judge --performance
```

### Example Questions to Test
- "Why did scenario ML-001 fail?"
- "How can I improve my bias scores?"
- "What's the fastest way to fix compliance issues?"
- "Show me performance bottlenecks"
- "Which failures are blocking deployment?"

## Risk Mitigation

### Low Risk Implementation
- **ZERO changes to existing output**: All tables and displays remain identical
- **Pure addition**: Interactive chat appears only at the very end
- **Graceful fallback**: Works without interaction in CI/scripts  
- **Optional feature**: Can be disabled with `--no-interaction`
- **Uses existing API**: Leverages current Anthropic integration
- **No regression risk**: Existing functionality completely untouched

### Error Handling
- API key missing → Skip interactive mode gracefully
- API errors → Show helpful error message, continue with static output
- Interrupt handling → Clean exit with Ctrl+C

## Success Metrics

### User Experience
- ✅ All existing output preserved exactly as-is
- ✅ Interactive exploration of results without changing display
- ✅ Actionable follow-up questions lead to better remediation
- ✅ Users can drill into specific failures efficiently
- ✅ Zero learning curve - same output plus optional chat

### Technical
- ✅ < 500ms response time for Q&A queries
- ✅ Contextual answers reference specific scenarios/metrics  
- ✅ ZERO regression in existing CLI functionality
- ✅ Graceful degradation in all error conditions
- ✅ 100% backward compatibility maintained

**This feature adds query capability while preserving all existing functionality without disruption to current users.**
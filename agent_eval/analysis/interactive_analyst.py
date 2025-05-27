"""Interactive analysis of evaluation results."""

import os
import logging
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

logger = logging.getLogger(__name__)


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
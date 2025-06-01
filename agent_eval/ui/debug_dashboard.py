"""
Debug Dashboard for specialized debug workflow insights.

This module provides a specialized dashboard experience for the debug workflow,
offering framework-specific optimization recommendations, tool call analysis,
and real-time debugging assistance.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich.tree import Tree
from rich import box

from agent_eval.evaluation.reliability_validator import ComprehensiveReliabilityAnalysis, FrameworkPerformanceAnalysis
from agent_eval.analysis.cognitive_analyzer import ComprehensiveCognitiveAnalysis

console = Console()


class DebugDashboard:
    """Specialized dashboard for debug workflow insights."""
    
    def __init__(self):
        """Initialize debug dashboard."""
        self.console = console
    
    def display_debug_summary(
        self, 
        analysis: ComprehensiveReliabilityAnalysis,
        cognitive_analysis: Optional[ComprehensiveCognitiveAnalysis] = None
    ) -> None:
        """Show debug-specific insights vs compliance summary."""
        
        self.console.print("\n[bold blue]🔍 Debug Dashboard - Agent Reliability Analysis[/bold blue]")
        self.console.print("[blue]═" * 80 + "[/blue]")
        
        # Create main overview panel
        self._display_overview_panel(analysis, cognitive_analysis)
        
        # Display framework-specific insights
        if analysis.framework_performance:
            self._display_framework_insights(analysis.framework_performance, analysis.detected_framework)
        
        # Display tool call analysis
        self._display_tool_call_insights(analysis.tool_call_summary, analysis.validation_results)
        
        # Display cognitive insights if available
        if cognitive_analysis:
            self._display_cognitive_insights(cognitive_analysis)
        
        # Display performance metrics
        self._display_performance_metrics(analysis.workflow_metrics)
        
        # Display actionable insights
        self._display_actionable_insights(analysis.insights_summary, analysis.next_steps)
    
    def show_framework_optimization_guide(self, framework: str, issues: List[str]) -> None:
        """Framework-specific optimization recommendations."""
        
        self.console.print(f"\n[bold cyan]⚡ {framework.upper()} Optimization Guide[/bold cyan]")
        self.console.print("[cyan]═" * 60 + "[/cyan]")
        
        # Framework-specific optimization recommendations
        optimization_guides = {
            "langchain": self._get_langchain_optimizations,
            "crewai": self._get_crewai_optimizations,
            "openai": self._get_openai_optimizations,
            "anthropic": self._get_anthropic_optimizations,
            "autogen": self._get_autogen_optimizations,
            "agno": self._get_agno_optimizations
        }
        
        if framework.lower() in optimization_guides:
            optimizations = optimization_guides[framework.lower()](issues)
            self._display_optimization_recommendations(optimizations)
        else:
            self._display_generic_optimizations(framework, issues)
    
    def display_tool_call_analysis(self, tool_failures: List[Dict]) -> None:
        """Interactive tool call failure analysis."""
        
        self.console.print("\n[bold yellow]🔧 Tool Call Analysis Dashboard[/bold yellow]")
        self.console.print("[yellow]═" * 60 + "[/yellow]")
        
        if not tool_failures:
            self.console.print("[green]✅ No tool call failures detected![/green]")
            return
        
        # Create tool failure summary table
        failure_table = Table(title="Tool Call Failures", box=box.ROUNDED)
        failure_table.add_column("Tool Name", style="cyan", width=20)
        failure_table.add_column("Failure Type", style="red", width=25)
        failure_table.add_column("Frequency", justify="center", width=10)
        failure_table.add_column("Fix Suggestion", style="green", width=35)
        
        # Group failures by tool and type
        failure_groups = {}
        for failure in tool_failures:
            tool_name = failure.get("tool_name", "unknown")
            failure_type = failure.get("failure_type", "general")
            key = f"{tool_name}_{failure_type}"
            
            if key not in failure_groups:
                failure_groups[key] = {
                    "tool_name": tool_name,
                    "failure_type": failure_type,
                    "count": 0,
                    "details": failure
                }
            failure_groups[key]["count"] += 1
        
        # Add failures to table with fix suggestions
        for group in sorted(failure_groups.values(), key=lambda x: x["count"], reverse=True):
            fix_suggestion = self._generate_tool_fix_suggestion(
                group["tool_name"], 
                group["failure_type"], 
                group["details"]
            )
            
            failure_table.add_row(
                group["tool_name"],
                group["failure_type"],
                str(group["count"]),
                fix_suggestion
            )
        
        self.console.print(failure_table)
        
        # Display tool call patterns analysis
        self._display_tool_patterns_analysis(tool_failures)
    
    def display_real_time_debug_session(self, session_data: Dict[str, Any]) -> None:
        """Display real-time debugging session information."""
        
        self.console.print("\n[bold green]🔴 Live Debug Session[/bold green]")
        self.console.print("[green]═" * 50 + "[/green]")
        
        # Session status
        status_panel = self._create_session_status_panel(session_data)
        self.console.print(status_panel)
        
        # Current tool call being debugged
        if session_data.get("current_tool_call"):
            self._display_current_tool_call(session_data["current_tool_call"])
        
        # Debug progress
        if session_data.get("debug_progress"):
            self._display_debug_progress(session_data["debug_progress"])
    
    def generate_framework_migration_report(
        self, 
        current_framework: str, 
        recommended_framework: str,
        migration_benefits: Dict[str, Any]
    ) -> None:
        """Generate framework migration recommendation report."""
        
        self.console.print(f"\n[bold magenta]🚀 Framework Migration Recommendation[/bold magenta]")
        self.console.print("[magenta]═" * 70 + "[/magenta]")
        
        # Migration overview
        migration_panel = Panel(
            self._create_migration_overview_text(current_framework, recommended_framework, migration_benefits),
            title=f"[bold]Migration: {current_framework.upper()} → {recommended_framework.upper()}[/bold]",
            border_style="magenta"
        )
        self.console.print(migration_panel)
        
        # Benefits breakdown
        self._display_migration_benefits(migration_benefits)
        
        # Migration roadmap
        self._display_migration_roadmap(current_framework, recommended_framework)
    
    # ==================== Helper Methods ====================
    
    def _display_overview_panel(
        self, 
        analysis: ComprehensiveReliabilityAnalysis,
        cognitive_analysis: Optional[ComprehensiveCognitiveAnalysis]
    ) -> None:
        """Display main overview panel."""
        
        # Create overview text
        overview_text = Text()
        overview_text.append("Debug Analysis Overview\n\n", style="bold cyan")
        
        # Framework detection
        if analysis.detected_framework:
            confidence_color = "green" if analysis.framework_confidence > 0.8 else "yellow" if analysis.framework_confidence > 0.5 else "red"
            overview_text.append(f"Framework: ", style="bold")
            overview_text.append(f"{analysis.detected_framework.upper()}", style=f"bold {confidence_color}")
            overview_text.append(f" (confidence: {analysis.framework_confidence:.1%})\n", style="dim")
        else:
            overview_text.append("Framework: ", style="bold")
            overview_text.append("Not detected", style="red")
            overview_text.append("\n")
        
        # Sample size and confidence
        overview_text.append(f"Sample Size: ", style="bold")
        overview_text.append(f"{analysis.sample_size} outputs\n", style="white")
        overview_text.append(f"Analysis Confidence: ", style="bold")
        confidence_color = "green" if analysis.analysis_confidence > 0.8 else "yellow" if analysis.analysis_confidence > 0.5 else "red"
        overview_text.append(f"{analysis.analysis_confidence:.1%}", style=confidence_color)
        overview_text.append(f" ({analysis.evidence_quality} quality)\n", style="dim")
        
        # Cognitive health if available
        if cognitive_analysis:
            overview_text.append(f"Cognitive Health: ", style="bold")
            cog_color = "green" if cognitive_analysis.cognitive_health_score > 0.7 else "yellow" if cognitive_analysis.cognitive_health_score > 0.4 else "red"
            overview_text.append(f"{cognitive_analysis.cognitive_health_score:.1%}", style=cog_color)
            overview_text.append("\n")
        
        # Quick metrics
        if analysis.workflow_metrics:
            overview_text.append("\nQuick Metrics:\n", style="bold")
            overview_text.append(f"• Workflow Success: {analysis.workflow_metrics.workflow_success_rate:.1%}\n", style="white")
            overview_text.append(f"• Tool Reliability: {analysis.workflow_metrics.tool_chain_reliability:.1%}\n", style="white")
            overview_text.append(f"• Schema Mismatches: {analysis.workflow_metrics.schema_mismatch_rate:.1%}\n", style="white")
        
        panel = Panel(overview_text, title="[bold blue]Overview[/bold blue]", border_style="blue")
        self.console.print(panel)
    
    def _display_framework_insights(
        self, 
        framework_performance: FrameworkPerformanceAnalysis,
        detected_framework: str
    ) -> None:
        """Display framework-specific insights."""
        
        framework_table = Table(title=f"{detected_framework.upper()} Performance Analysis", box=box.ROUNDED)
        framework_table.add_column("Metric", style="cyan", width=25)
        framework_table.add_column("Value", justify="center", width=15)
        framework_table.add_column("Assessment", style="green", width=30)
        
        # Add performance metrics
        framework_table.add_row(
            "Average Response Time",
            f"{framework_performance.avg_response_time:.1f}s",
            self._assess_response_time(framework_performance.avg_response_time)
        )
        
        framework_table.add_row(
            "Success Rate",
            f"{framework_performance.success_rate:.1%}",
            self._assess_success_rate(framework_performance.success_rate)
        )
        
        framework_table.add_row(
            "Tool Call Failure Rate",
            f"{framework_performance.tool_call_failure_rate:.1%}",
            self._assess_failure_rate(framework_performance.tool_call_failure_rate)
        )
        
        if hasattr(framework_performance, 'abstraction_overhead'):
            framework_table.add_row(
                "Abstraction Overhead",
                f"{framework_performance.abstraction_overhead:.1%}",
                self._assess_overhead(framework_performance.abstraction_overhead)
            )
        
        self.console.print(framework_table)
        
        # Display optimization opportunities
        if framework_performance.optimization_opportunities:
            self._display_optimization_opportunities(framework_performance.optimization_opportunities)
    
    def _display_tool_call_insights(
        self, 
        tool_call_summary: Dict[str, Any],
        validation_results: List[Dict[str, Any]]
    ) -> None:
        """Display tool call analysis insights."""
        
        # Tool usage overview
        tool_overview_table = Table(title="Tool Usage Analysis", box=box.ROUNDED)
        tool_overview_table.add_column("Aspect", style="cyan", width=30)
        tool_overview_table.add_column("Details", style="white", width=40)
        
        if "unique_tools_detected" in tool_call_summary:
            tool_overview_table.add_row(
                "Unique Tools Detected",
                str(tool_call_summary["unique_tools_detected"])
            )
        
        if "most_common_tools" in tool_call_summary:
            common_tools = tool_call_summary["most_common_tools"][:3]
            tools_str = ", ".join([f"{tool}({count})" for tool, count in common_tools])
            tool_overview_table.add_row(
                "Most Common Tools",
                tools_str
            )
        
        if "avg_tool_accuracy" in tool_call_summary:
            tool_overview_table.add_row(
                "Average Tool Accuracy",
                f"{tool_call_summary['avg_tool_accuracy']:.1%}"
            )
        
        self.console.print(tool_overview_table)
        
        # Tool validation results
        if validation_results:
            self._display_tool_validation_results(validation_results)
    
    def _display_cognitive_insights(self, cognitive_analysis: ComprehensiveCognitiveAnalysis) -> None:
        """Display cognitive analysis insights."""
        
        # Cognitive metrics table
        cognitive_table = Table(title="Cognitive Analysis", box=box.ROUNDED)
        cognitive_table.add_column("Cognitive Aspect", style="cyan", width=25)
        cognitive_table.add_column("Score", justify="center", width=10)
        cognitive_table.add_column("Assessment", style="green", width=35)
        
        cognitive_table.add_row(
            "Overall Cognitive Health",
            f"{cognitive_analysis.cognitive_health_score:.1%}",
            self._assess_cognitive_score(cognitive_analysis.cognitive_health_score)
        )
        
        cognitive_table.add_row(
            "Adaptive Thinking",
            f"{cognitive_analysis.adaptive_thinking_score:.1%}",
            self._assess_cognitive_score(cognitive_analysis.adaptive_thinking_score)
        )
        
        cognitive_table.add_row(
            "Metacognitive Awareness",
            f"{cognitive_analysis.metacognitive_awareness_score:.1%}",
            self._assess_cognitive_score(cognitive_analysis.metacognitive_awareness_score)
        )
        
        cognitive_table.add_row(
            "Reasoning Coherence",
            f"{cognitive_analysis.reasoning_coherence_score:.1%}",
            self._assess_cognitive_score(cognitive_analysis.reasoning_coherence_score)
        )
        
        self.console.print(cognitive_table)
        
        # Critical cognitive issues
        if cognitive_analysis.critical_issues:
            self._display_cognitive_issues(cognitive_analysis.critical_issues, cognitive_analysis.improvement_recommendations)
    
    def _display_performance_metrics(self, workflow_metrics) -> None:
        """Display performance metrics in a visual format."""
        
        # Performance metrics visualization
        perf_table = Table(title="Performance Metrics", box=box.ROUNDED)
        perf_table.add_column("Metric", style="cyan", width=25)
        perf_table.add_column("Score", justify="center", width=10)
        perf_table.add_column("Status", justify="center", width=15)
        perf_table.add_column("Details", style="dim", width=30)
        
        metrics = [
            ("Workflow Success Rate", workflow_metrics.workflow_success_rate, "High performance"),
            ("Tool Chain Reliability", workflow_metrics.tool_chain_reliability, "Tool effectiveness"),
            ("Decision Consistency", workflow_metrics.decision_consistency_score, "Consistent decisions"),
            ("Multi-step Completion", workflow_metrics.multi_step_completion_rate, "Complex task handling")
        ]
        
        for metric_name, score, description in metrics:
            status_icon = "🟢" if score > 0.8 else "🟡" if score > 0.5 else "🔴"
            perf_table.add_row(
                metric_name,
                f"{score:.1%}",
                status_icon,
                description
            )
        
        self.console.print(perf_table)
    
    def _display_actionable_insights(self, insights: List[str], next_steps: List[str]) -> None:
        """Display actionable insights and next steps."""
        
        # Split into two columns
        insights_panel = Panel(
            "\n".join([f"• {insight}" for insight in insights[:5]]),
            title="[bold yellow]🔍 Key Insights[/bold yellow]",
            border_style="yellow"
        )
        
        next_steps_panel = Panel(
            "\n".join([f"{i+1}. {step}" for i, step in enumerate(next_steps[:5])]),
            title="[bold green]🎯 Next Steps[/bold green]",
            border_style="green"
        )
        
        columns = Columns([insights_panel, next_steps_panel], equal=True)
        self.console.print(columns)
    
    # Framework-specific optimization methods
    
    def _get_langchain_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get LangChain-specific optimizations."""
        return {
            "performance": [
                "Consider using LCEL (LangChain Expression Language) for better performance",
                "Implement custom chains instead of generic ones where possible",
                "Use streaming for long-running operations",
                "Cache expensive operations with memory"
            ],
            "reliability": [
                "Add retry logic with exponential backoff",
                "Implement proper error handling in custom chains",
                "Use structured output parsers for consistent results",
                "Validate tool schemas before execution"
            ],
            "cost_optimization": [
                "Switch to cheaper models for simple tasks",
                "Use prompt compression techniques",
                "Implement smart caching strategies",
                "Consider local models for privacy-sensitive operations"
            ]
        }
    
    def _get_crewai_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get CrewAI-specific optimizations."""
        return {
            "performance": [
                "Optimize agent delegation patterns",
                "Use hierarchical workflows for complex tasks",
                "Implement custom delegation timeouts",
                "Consider agent specialization for better efficiency"
            ],
            "reliability": [
                "Add custom error handling for agent failures",
                "Implement agent health monitoring",
                "Use structured communication between agents",
                "Add validation for agent outputs"
            ],
            "scaling": [
                "Consider async agent execution",
                "Implement agent load balancing",
                "Use shared memory for agent coordination",
                "Add agent performance monitoring"
            ]
        }
    
    def _get_openai_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get OpenAI-specific optimizations."""
        return {
            "performance": [
                "Use GPT-4 Turbo for better speed/cost ratio",
                "Implement smart prompt caching",
                "Use structured outputs for consistent parsing",
                "Consider parallel requests for independent tasks"
            ],
            "reliability": [
                "Add retry logic with exponential backoff",
                "Implement rate limiting to avoid errors",
                "Use function calling for structured interactions",
                "Add response validation and error handling"
            ],
            "cost_optimization": [
                "Use GPT-3.5 Turbo for simple tasks",
                "Implement prompt optimization",
                "Use batch processing where possible",
                "Monitor token usage and optimize prompts"
            ]
        }
    
    def _get_anthropic_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get Anthropic-specific optimizations."""
        return {
            "performance": [
                "Use Claude 3 Haiku for faster responses",
                "Implement streaming for long responses",
                "Use XML formatting for structured outputs",
                "Consider prompt engineering for efficiency"
            ],
            "reliability": [
                "Implement proper XML parsing for tool calls",
                "Add retry logic for API errors",
                "Use structured prompts for consistent outputs",
                "Add response validation for tool calls"
            ],
            "best_practices": [
                "Use Claude's strength in reasoning for complex tasks",
                "Implement proper context window management",
                "Use Claude's safety features appropriately",
                "Consider multi-turn conversations for complex workflows"
            ]
        }
    
    def _get_autogen_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get AutoGen-specific optimizations."""
        return {
            "performance": [
                "Optimize conversation patterns",
                "Use selective agent activation",
                "Implement conversation caching",
                "Consider conversation pruning strategies"
            ],
            "reliability": [
                "Add conversation state validation",
                "Implement agent error recovery",
                "Use structured agent communication",
                "Add conversation flow monitoring"
            ],
            "scaling": [
                "Consider distributed agent execution",
                "Implement agent resource management",
                "Use conversation persistence",
                "Add agent performance tracking"
            ]
        }
    
    def _get_agno_optimizations(self, issues: List[str]) -> Dict[str, Any]:
        """Get Agno-specific optimizations."""
        return {
            "performance": [
                "Leverage Agno's lightweight architecture",
                "Use built-in monitoring features",
                "Implement efficient reasoning patterns",
                "Consider structured output optimization"
            ],
            "reliability": [
                "Use Agno's built-in error handling",
                "Implement proper tool validation",
                "Add monitoring for agent health",
                "Use structured reasoning workflows"
            ],
            "monitoring": [
                "Enable Agno's built-in telemetry",
                "Use performance monitoring features",
                "Implement custom metrics collection",
                "Add real-time debugging capabilities"
            ]
        }
    
    def _display_optimization_recommendations(self, optimizations: Dict[str, Any]) -> None:
        """Display optimization recommendations."""
        
        for category, recommendations in optimizations.items():
            category_panel = Panel(
                "\n".join([f"• {rec}" for rec in recommendations]),
                title=f"[bold]{category.replace('_', ' ').title()}[/bold]",
                border_style="cyan"
            )
            self.console.print(category_panel)
    
    def _display_generic_optimizations(self, framework: str, issues: List[str]) -> None:
        """Display generic optimization recommendations."""
        
        generic_panel = Panel(
            f"Framework '{framework}' not yet supported for specific optimizations.\n\n"
            "Generic recommendations:\n"
            "• Add comprehensive error handling\n"
            "• Implement retry logic for failures\n"
            "• Monitor performance metrics\n"
            "• Use structured outputs where possible\n"
            "• Add logging for debugging\n"
            "• Consider caching for expensive operations",
            title=f"[bold]Generic Optimizations for {framework.upper()}[/bold]",
            border_style="yellow"
        )
        self.console.print(generic_panel)
    
    # Assessment helper methods
    
    def _assess_response_time(self, time: float) -> str:
        """Assess response time performance."""
        if time < 2.0:
            return "🟢 Excellent"
        elif time < 5.0:
            return "🟡 Good"
        elif time < 10.0:
            return "🟠 Acceptable"
        else:
            return "🔴 Needs improvement"
    
    def _assess_success_rate(self, rate: float) -> str:
        """Assess success rate."""
        if rate > 0.95:
            return "🟢 Excellent"
        elif rate > 0.85:
            return "🟡 Good"
        elif rate > 0.70:
            return "🟠 Acceptable"
        else:
            return "🔴 Needs improvement"
    
    def _assess_failure_rate(self, rate: float) -> str:
        """Assess failure rate."""
        if rate < 0.05:
            return "🟢 Excellent"
        elif rate < 0.15:
            return "🟡 Good"
        elif rate < 0.30:
            return "🟠 Acceptable"
        else:
            return "🔴 High failure rate"
    
    def _assess_overhead(self, overhead: float) -> str:
        """Assess abstraction overhead."""
        if overhead < 0.10:
            return "🟢 Low overhead"
        elif overhead < 0.25:
            return "🟡 Moderate overhead"
        elif overhead < 0.40:
            return "🟠 High overhead"
        else:
            return "🔴 Excessive overhead"
    
    def _assess_cognitive_score(self, score: float) -> str:
        """Assess cognitive analysis score."""
        if score > 0.8:
            return "🟢 Strong capability"
        elif score > 0.6:
            return "🟡 Moderate capability"
        elif score > 0.4:
            return "🟠 Developing capability"
        else:
            return "🔴 Needs significant improvement"
    
    def _generate_tool_fix_suggestion(self, tool_name: str, failure_type: str, details: Dict) -> str:
        """Generate fix suggestion for tool failures."""
        
        fix_suggestions = {
            "schema_mismatch": f"Validate {tool_name} parameter schema",
            "timeout": f"Increase {tool_name} timeout or optimize execution",
            "authentication": f"Check {tool_name} credentials and permissions",
            "not_found": f"Verify {tool_name} is properly registered",
            "parameter_error": f"Review {tool_name} parameter types and values",
            "execution_error": f"Add error handling for {tool_name} execution"
        }
        
        return fix_suggestions.get(failure_type, f"Review {tool_name} implementation")
    
    def _display_optimization_opportunities(self, opportunities: List[Dict[str, Any]]) -> None:
        """Display optimization opportunities."""
        
        if not opportunities:
            return
            
        opp_table = Table(title="Optimization Opportunities", box=box.ROUNDED)
        opp_table.add_column("Priority", justify="center", width=10)
        opp_table.add_column("Opportunity", style="cyan", width=40)
        opp_table.add_column("Expected Impact", style="green", width=20)
        
        for opp in opportunities[:5]:  # Show top 5
            priority_icon = "🔴" if opp.get("priority") == "high" else "🟡" if opp.get("priority") == "medium" else "🟢"
            opp_table.add_row(
                priority_icon,
                opp.get("description", "Unknown optimization"),
                opp.get("expected_improvement", "Performance boost")
            )
        
        self.console.print(opp_table)
    
    def _display_tool_validation_results(self, validation_results: List[Dict[str, Any]]) -> None:
        """Display tool validation results."""
        
        if not validation_results:
            return
            
        # Show summary of validation issues
        total_validations = len(validation_results)
        failed_validations = len([r for r in validation_results if r.get("coverage_rate", 1.0) < 0.8])
        
        validation_text = Text()
        validation_text.append(f"Tool Validation Summary:\n", style="bold")
        validation_text.append(f"Total validations: {total_validations}\n", style="white")
        validation_text.append(f"Failed validations: {failed_validations}\n", style="red" if failed_validations > 0 else "green")
        validation_text.append(f"Success rate: {((total_validations - failed_validations) / total_validations * 100):.1f}%", 
                              style="green" if failed_validations == 0 else "yellow")
        
        validation_panel = Panel(validation_text, title="Tool Validation Results", border_style="blue")
        self.console.print(validation_panel)
    
    def _display_tool_patterns_analysis(self, tool_failures: List[Dict]) -> None:
        """Display tool patterns analysis."""
        
        patterns_text = Text()
        patterns_text.append("Tool Failure Patterns:\n", style="bold yellow")
        
        # Analyze patterns in failures
        failure_types = {}
        for failure in tool_failures:
            failure_type = failure.get("failure_type", "unknown")
            failure_types[failure_type] = failure_types.get(failure_type, 0) + 1
        
        for failure_type, count in sorted(failure_types.items(), key=lambda x: x[1], reverse=True)[:3]:
            patterns_text.append(f"• {failure_type}: {count} occurrences\n", style="white")
        
        patterns_panel = Panel(patterns_text, title="Failure Patterns", border_style="yellow")
        self.console.print(patterns_panel)
    
    def _create_session_status_panel(self, session_data: Dict[str, Any]) -> Panel:
        """Create session status panel."""
        
        status_text = Text()
        status_text.append("Debug Session Status\n\n", style="bold green")
        status_text.append(f"Session ID: {session_data.get('session_id', 'unknown')}\n", style="white")
        status_text.append(f"Started: {session_data.get('start_time', 'unknown')}\n", style="white")
        status_text.append(f"Duration: {session_data.get('duration', 'unknown')}\n", style="white")
        status_text.append(f"Status: {session_data.get('status', 'active')}\n", style="green")
        
        return Panel(status_text, title="Session Status", border_style="green")
    
    def _display_current_tool_call(self, tool_call: Dict[str, Any]) -> None:
        """Display current tool call being debugged."""
        
        tool_text = Text()
        tool_text.append(f"Tool: {tool_call.get('name', 'unknown')}\n", style="bold cyan")
        tool_text.append(f"Parameters: {json.dumps(tool_call.get('parameters', {}), indent=2)}\n", style="white")
        tool_text.append(f"Status: {tool_call.get('status', 'executing')}\n", style="yellow")
        
        tool_panel = Panel(tool_text, title="Current Tool Call", border_style="cyan")
        self.console.print(tool_panel)
    
    def _display_debug_progress(self, progress_data: Dict[str, Any]) -> None:
        """Display debug progress."""
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            task = progress.add_task(
                f"Debugging {progress_data.get('current_step', 'unknown')}...",
                total=100
            )
            progress.update(task, completed=progress_data.get('percentage', 0))
    
    def _create_migration_overview_text(
        self, 
        current_framework: str, 
        recommended_framework: str,
        migration_benefits: Dict[str, Any]
    ) -> Text:
        """Create migration overview text."""
        
        text = Text()
        text.append(f"Migration Analysis: {current_framework.upper()} → {recommended_framework.upper()}\n\n", style="bold")
        
        text.append("Expected Benefits:\n", style="bold cyan")
        for benefit, value in migration_benefits.items():
            if isinstance(value, (int, float)):
                text.append(f"• {benefit.replace('_', ' ').title()}: {value:.1%} improvement\n", style="green")
            else:
                text.append(f"• {benefit.replace('_', ' ').title()}: {value}\n", style="green")
        
        return text
    
    def _display_migration_benefits(self, migration_benefits: Dict[str, Any]) -> None:
        """Display migration benefits."""
        
        benefits_table = Table(title="Migration Benefits Analysis", box=box.ROUNDED)
        benefits_table.add_column("Benefit Category", style="cyan", width=25)
        benefits_table.add_column("Current State", justify="center", width=15)
        benefits_table.add_column("After Migration", justify="center", width=15)
        benefits_table.add_column("Improvement", style="green", width=15)
        
        # Add example benefits
        benefits_table.add_row("Performance", "Moderate", "High", "+30-50%")
        benefits_table.add_row("Reliability", "Good", "Excellent", "+20%")
        benefits_table.add_row("Maintainability", "Complex", "Simple", "Significant")
        benefits_table.add_row("Cost Efficiency", "Standard", "Optimized", "+25%")
        
        self.console.print(benefits_table)
    
    def _display_migration_roadmap(self, current_framework: str, recommended_framework: str) -> None:
        """Display migration roadmap."""
        
        roadmap_text = Text()
        roadmap_text.append("Migration Roadmap:\n\n", style="bold")
        roadmap_text.append("1. Assessment Phase (1-2 days)\n", style="white")
        roadmap_text.append("   • Audit current implementation\n", style="dim")
        roadmap_text.append("   • Identify migration blockers\n", style="dim")
        roadmap_text.append("   • Create migration plan\n\n", style="dim")
        
        roadmap_text.append("2. Preparation Phase (3-5 days)\n", style="white")
        roadmap_text.append("   • Set up new framework environment\n", style="dim")
        roadmap_text.append("   • Create compatibility layer\n", style="dim")
        roadmap_text.append("   • Implement core functionality\n\n", style="dim")
        
        roadmap_text.append("3. Migration Phase (5-10 days)\n", style="white")
        roadmap_text.append("   • Migrate components incrementally\n", style="dim")
        roadmap_text.append("   • Run parallel testing\n", style="dim")
        roadmap_text.append("   • Validate performance improvements\n\n", style="dim")
        
        roadmap_text.append("4. Validation Phase (2-3 days)\n", style="white")
        roadmap_text.append("   • End-to-end testing\n", style="dim")
        roadmap_text.append("   • Performance benchmarking\n", style="dim")
        roadmap_text.append("   • Documentation updates\n", style="dim")
        
        roadmap_panel = Panel(roadmap_text, title="Migration Timeline", border_style="blue")
        self.console.print(roadmap_panel)
    
    def _display_cognitive_issues(self, issues: List[str], recommendations: List[str]) -> None:
        """Display cognitive issues and recommendations."""
        
        if not issues:
            return
            
        issues_text = Text()
        issues_text.append("Critical Cognitive Issues:\n", style="bold red")
        for issue in issues:
            issues_text.append(f"• {issue}\n", style="red")
        
        if recommendations:
            issues_text.append("\nRecommended Actions:\n", style="bold green")
            for rec in recommendations[:3]:  # Show top 3
                issues_text.append(f"• {rec}\n", style="green")
        
        issues_panel = Panel(issues_text, title="Cognitive Analysis", border_style="red")
        self.console.print(issues_panel)
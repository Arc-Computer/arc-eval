#!/usr/bin/env python3
"""
ARC-Eval Analytics Viewer
Simple tool to view usage analytics and validation metrics.
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def main():
    console = Console()
    
    # Check for analytics data
    analytics_dir = Path(".arc_analytics")
    if not analytics_dir.exists():
        console.print("[red]No analytics data found[/red]")
        console.print("Run some evaluations first to generate usage data")
        sys.exit(1)
    
    # Import analytics
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from agent_eval.core.usage_analytics import get_analytics
        
        analytics = get_analytics()
        summary = analytics.generate_summary()
        validation_metrics = analytics.get_validation_metrics()
        
    except Exception as e:
        console.print(f"[red]Error loading analytics: {e}[/red]")
        sys.exit(1)
    
    if "error" in summary:
        console.print(f"[red]{summary['error']}[/red]")
        sys.exit(1)
    
    # Display usage summary
    console.print("[bold blue]ARC-Eval Usage Analytics[/bold blue]")
    console.print("[blue]" + "=" * 50 + "[/blue]")
    
    # Basic metrics
    basic_table = Table(title="Usage Summary")
    basic_table.add_column("Metric", style="cyan")
    basic_table.add_column("Value", style="green")
    
    basic_table.add_row("Total Events", str(summary["total_events"]))
    basic_table.add_row("Success Rate", summary["success_rate"])
    basic_table.add_row("Total Sessions", str(summary["total_sessions"]))
    basic_table.add_row("Complete Workflows", str(summary["complete_workflows"]))
    basic_table.add_row("Workflow Completion Rate", summary["workflow_completion_rate"])
    basic_table.add_row("Recent Activity (7d)", str(summary["recent_activity_7d"]))
    
    console.print(basic_table)
    
    # Event breakdown
    if summary["event_breakdown"]:
        event_table = Table(title="Event Types")
        event_table.add_column("Event Type", style="cyan")
        event_table.add_column("Count", style="green")
        
        for event_type, count in summary["event_breakdown"].items():
            event_table.add_row(event_type.replace('_', ' ').title(), str(count))
        
        console.print(event_table)
    
    # Domain usage
    if summary["domain_usage"]:
        domain_table = Table(title="Domain Usage")
        domain_table.add_column("Domain", style="cyan")
        domain_table.add_column("Count", style="green")
        
        for domain, count in summary["domain_usage"].items():
            domain_table.add_row(domain.title(), str(count))
        
        console.print(domain_table)
    
    # Validation metrics
    if "error" not in validation_metrics:
        console.print("\n[bold blue]Usage Validation Metrics[/bold blue]")
        
        validation_summary = f"""
**Usage Frequency:**
• Total Evaluations: {validation_metrics['usage_frequency']['total_evaluations']}
• Evaluations/Week: {validation_metrics['usage_frequency']['evaluations_per_week']:.1f}
• Meets 3x/week threshold: {'✅ Yes' if validation_metrics['usage_frequency']['meets_3x_week_threshold'] else '❌ No'}

**Workflow Adoption:**
• Complete Workflows: {validation_metrics['workflow_adoption']['complete_workflows']}
• Completion Rate: {validation_metrics['workflow_adoption']['workflow_completion_rate']}
• Meets threshold: {'✅ Yes' if validation_metrics['workflow_adoption']['meets_completion_threshold'] else '❌ No'}

**Technical Reliability:**
• Success Rate: {validation_metrics['technical_reliability']['success_rate']}
• Meets threshold: {'✅ Yes' if validation_metrics['technical_reliability']['meets_reliability_threshold'] else '❌ No'}
        """
        
        console.print(Panel(validation_summary.strip(), title="Validation Metrics", border_style="green"))
        
        # Overall success
        success_criteria = [
            validation_metrics['usage_frequency']['meets_3x_week_threshold'],
            validation_metrics['workflow_adoption']['meets_completion_threshold'],
            validation_metrics['technical_reliability']['meets_reliability_threshold']
        ]
        
        criteria_met = sum(success_criteria)
        if criteria_met >= 3:
            recommendation = "🚀 PROCEED: All success criteria met"
        elif criteria_met >= 2:
            recommendation = "🔄 ITERATE: Partial success - address gaps"
        else:
            recommendation = "🔍 PIVOT: Core value needs reassessment"
        
        console.print(f"\n[bold]{recommendation}[/bold]")
    
    console.print(f"\n[dim]Generated: {summary['generated_at'][:19]}[/dim]")


if __name__ == "__main__":
    main()
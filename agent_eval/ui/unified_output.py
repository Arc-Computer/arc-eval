"""
Unified output formatting for consistent visual hierarchy across workflows.
"""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

console = Console()


class UnifiedOutputFormatter:
    """Provides consistent output formatting across all workflows."""
    
    @staticmethod
    def debug_report(failures: List[Dict[str, Any]], root_causes: Dict[str, Any], 
                     fixes: List[Dict[str, Any]], framework: str) -> None:
        """Format debug workflow output."""
        # Header
        tree = Tree("🔍 Agent Debug Report", guide_style="blue")
        
        # Framework info
        tree.add(f"Framework: {framework} (auto-detected)")
        
        # Failures
        failures_branch = tree.add(f"Failures Found: {len(failures)}")
        for failure in failures[:5]:  # Show top 5
            failures_branch.add(f"[red]{failure.get('type', 'Unknown')}: {failure.get('description', 'No description')}[/red]")
        
        # Root causes
        causes_branch = tree.add("Root Causes:")
        for category, causes in root_causes.items():
            cat_branch = causes_branch.add(f"{category}:")
            for cause in causes[:3]:  # Top 3 per category
                cat_branch.add(f"[yellow]{cause}[/yellow]")
        
        console.print(tree)
        
        # Suggested fixes
        console.print("\n💡 [bold]Suggested Fixes:[/bold]")
        for i, fix in enumerate(fixes[:5], 1):
            console.print(f"\n{i}. [bold cyan]{fix['title']}[/bold cyan]")
            console.print(f"   {fix['description']}")
            if 'code' in fix:
                console.print(Syntax(fix['code'], "python", theme="monokai", line_numbers=False))
    
    @staticmethod
    def compliance_report(domain: str, total_scenarios: int, passed: int, 
                         compliance_gaps: Dict[str, float], critical_failures: List[Dict],
                         remediation: List[Dict]) -> None:
        """Format compliance workflow output."""
        # Header
        tree = Tree("📊 Compliance Evaluation Report", guide_style="green")
        
        # Domain info
        tree.add(f"Domain: {domain.capitalize()} ({total_scenarios} scenarios)")
        
        # Overall score
        pass_rate = (passed / total_scenarios) * 100 if total_scenarios > 0 else 0
        color = "green" if pass_rate >= 80 else "yellow" if pass_rate >= 60 else "red"
        tree.add(f"Overall Score: [{color}]{pass_rate:.0f}% ({passed}/{total_scenarios} passed)[/{color}]")
        
        # Compliance gaps
        gaps_branch = tree.add("Compliance Gaps:")
        for framework, score in compliance_gaps.items():
            color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            gaps_branch.add(f"{framework}: [{color}]{score:.0f}% compliant[/{color}]")
        
        console.print(tree)
        
        # Critical failures
        if critical_failures:
            console.print("\n🚨 [bold red]Critical Failures:[/bold red]")
            for failure in critical_failures[:3]:
                console.print(f"• Scenario {failure['scenario_id']}: {failure['description']}")
        
        # Remediation
        console.print("\n📋 [bold]Remediation Required:[/bold]")
        for item in remediation[:3]:
            priority_color = "red" if item['priority'] == 'CRITICAL' else "yellow" if item['priority'] == 'HIGH' else "cyan"
            console.print(f"• {item['action']} [bold {priority_color}](Priority: {item['priority']})[/bold {priority_color}]")
    
    @staticmethod
    def improvement_plan(priorities: List[Dict], expected_improvement: Dict,
                        timeline: str, next_steps: List[str]) -> None:
        """Format improvement workflow output."""
        console.print("[bold]🎯 Improvement Plan Generated[/bold]\n")
        
        # Priority actions
        for i, priority in enumerate(priorities[:3], 1):
            panel_content = f"[bold]{priority['description']}[/bold]\n"
            panel_content += f"├── Pattern: {priority.get('pattern', 'N/A')}\n"
            panel_content += f"├── Implementation: {priority.get('implementation', 'See details')}\n"
            panel_content += f"└── Test: {priority.get('test_scenarios', 'Run validation')}"
            
            panel = Panel(
                panel_content,
                title=f"Priority {i}: {priority['area']} (Est: {priority.get('timeline', 'TBD')})",
                border_style="cyan" if i == 1 else "blue"
            )
            console.print(panel)
        
        # Expected improvement
        console.print("\n📊 [bold]Expected Improvement:[/bold]")
        current = expected_improvement.get('current', 0)
        projected = expected_improvement.get('projected', {})
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Phase", style="cyan")
        table.add_column("Compliance", justify="right")
        table.add_column("Improvement", justify="right", style="green")
        
        table.add_row("Current", f"{current}%", "-")
        for phase, value in projected.items():
            improvement = value - current
            table.add_row(phase, f"{value}%", f"+{improvement}%")
            current = value
        
        console.print(table)
        
        # Next steps
        if next_steps:
            console.print("\n🔄 [bold]Next Command:[/bold]")
            console.print(f"[green]{next_steps[0]}[/green]")
    
    @staticmethod
    def progress_bar(description: str, total: int) -> Progress:
        """Create a consistent progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        )
    
    @staticmethod
    def error(message: str, suggestion: Optional[str] = None) -> None:
        """Format error messages consistently."""
        console.print(f"\n[bold red]❌ Error:[/bold red] {message}")
        if suggestion:
            console.print(f"[yellow]💡 Suggestion:[/yellow] {suggestion}")
    
    @staticmethod
    def success(message: str) -> None:
        """Format success messages consistently."""
        console.print(f"\n[bold green]✅ Success:[/bold green] {message}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Format warning messages consistently."""
        console.print(f"\n[bold yellow]⚠️  Warning:[/bold yellow] {message}")
    
    @staticmethod
    def info(message: str) -> None:
        """Format info messages consistently."""
        console.print(f"\n[bold blue]ℹ️  Info:[/bold blue] {message}")
    
    @staticmethod
    def workflow_complete(workflow: str, next_command: Optional[str] = None) -> None:
        """Show workflow completion message."""
        console.print(f"\n[bold green]✨ {workflow.capitalize()} workflow complete![/bold green]")
        if next_command:
            console.print(f"\n🔄 [bold]Next Step:[/bold] [green]{next_command}[/green]")
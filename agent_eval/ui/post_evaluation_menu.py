"""Post-evaluation menu system for user choices."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from agent_eval.analysis.interactive_analyst import InteractiveAnalyst
from agent_eval.core.improvement_planner import ImprovementPlanner
from agent_eval.exporters.json import JSONExporter
from agent_eval.exporters.csv import CSVExporter
from agent_eval.exporters.pdf import PDFExporter


console = Console()


class PostEvaluationMenu:
    """Handles post-evaluation user choices and actions."""
    
    def __init__(self, 
                 domain: str,
                 evaluation_results: Dict[str, Any],
                 judge_results: Optional[List] = None,
                 improvement_report: Optional[Dict] = None,
                 learning_metrics: Optional[Dict] = None,
                 workflow_type: str = "compliance"):
        self.domain = domain
        self.evaluation_results = evaluation_results
        self.judge_results = judge_results
        self.improvement_report = improvement_report
        self.learning_metrics = learning_metrics
        self.workflow_type = workflow_type  # "debug", "compliance", or "improve"
        
    def display_menu(self) -> str:
        """Display the post-evaluation menu and get user choice."""
        
        # Show evaluation summary
        self._display_evaluation_summary()
        
        # Create menu options
        console.print("\n[bold cyan]🔍 What would you like to do?[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]\n")
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="bold yellow", width=3)
        table.add_column("Action", style="white")
        table.add_column("Description", style="dim")
        
        # Adaptive menu options based on workflow type
        if self.workflow_type == "debug":
            # After debug workflow
            table.add_row(
                "[1]", 
                "Run compliance check on these outputs", 
                "(Recommended)"
            )
            table.add_row(
                "[2]", 
                "Ask questions about the failures", 
                "(Interactive Mode)"
            )
            table.add_row(
                "[3]", 
                "Export debug report", 
                "(PDF/CSV/JSON)"
            )
            table.add_row(
                "[4]", 
                "View learning dashboard & submit patterns", 
                "(Improve ARC-Eval)"
            )
            
        elif self.workflow_type == "compliance":
            # After compliance workflow
            pass_rate = self.evaluation_results.get("summary", {}).get("pass_rate", 0) * 100
            if pass_rate < 90:
                recommended = "(Recommended for <90% pass)"
            else:
                recommended = "(Optional)"
                
            table.add_row(
                "[1]", 
                "Ask questions about failures", 
                "(Interactive Mode)"
            )
            table.add_row(
                "[2]", 
                "Generate improvement plan", 
                recommended
            )
            table.add_row(
                "[3]", 
                "Export compliance report", 
                "(PDF/CSV/JSON)"
            )
            table.add_row(
                "[4]", 
                "View learning dashboard & share results", 
                "(Contribute)"
            )
            
        elif self.workflow_type == "improve":
            # After improve workflow
            table.add_row(
                "[1]", 
                "Re-run evaluation to measure improvement", 
                "(Recommended)"
            )
            table.add_row(
                "[2]", 
                "Schedule automated re-evaluation", 
                "(Coming Soon)"
            )
            table.add_row(
                "[3]", 
                "Export plan as actionable tasks", 
                "(PDF/Markdown)"
            )
            table.add_row(
                "[4]", 
                "View learning dashboard & track patterns", 
                "(Improve ARC-Eval)"
            )
        
        console.print(table)
        console.print()
        
        # Get user choice
        choice = Prompt.ask(
            "[bold]Select option[/bold]",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        return choice
    
    def _display_evaluation_summary(self) -> None:
        """Display concise evaluation summary."""
        summary = self.evaluation_results.get("summary", {})
        
        if self.workflow_type == "debug":
            # Debug workflow summary
            failures_found = summary.get("failures_found", 0)
            console.print(f"\n[bold]🔍 Debug Analysis Complete[/bold]")
            if failures_found > 0:
                console.print(f"[yellow]Found {failures_found} failure patterns that need attention[/yellow]")
            else:
                console.print(f"[green]No critical failures detected[/green]")
                
        elif self.workflow_type == "compliance":
            # Compliance workflow summary
            pass_rate = summary.get("pass_rate", 0) * 100
            total_scenarios = summary.get("total_scenarios", 0)
            passed = summary.get("passed", 0)
            
            # Learning metrics if available
            if self.learning_metrics:
                perf_delta = self.learning_metrics.get("performance_delta", 0)
                if perf_delta > 0:
                    console.print(f"\n[bold green]📈 Performance Delta: +{perf_delta:.1f}%[/bold green]")
            
            console.print(f"\n[bold]✅ Compliance Evaluation Complete:[/bold] {pass_rate:.0f}% pass rate ({passed}/{total_scenarios} scenarios)")
            
        elif self.workflow_type == "improve":
            # Improve workflow summary
            actions_count = summary.get("actions_count", 0)
            expected_improvement = summary.get("expected_improvement", 0)
            console.print(f"\n[bold]📈 Improvement Plan Generated[/bold]")
            console.print(f"[green]{actions_count} prioritized actions with {expected_improvement}% expected improvement[/green]")
    
    def handle_interactive_mode(self) -> None:
        """Start interactive Q&A session."""
        if not self.improvement_report:
            console.print("[yellow]⚠️  Interactive mode requires agent-judge evaluation[/yellow]")
            return
            
        try:
            analyst = InteractiveAnalyst(
                improvement_report=self.improvement_report,
                judge_results=self.judge_results or [],
                domain=self.domain,
                performance_metrics=self.evaluation_results.get("performance_metrics"),
                reliability_metrics=self.evaluation_results.get("reliability_metrics")
            )
            
            # Start interactive session
            analyst.start_interactive_session(console)
            
            # After interactive session, offer to continue
            self._offer_continuation()
            
        except ValueError as e:
            console.print(f"[red]❌ {str(e)}[/red]")
            console.print("[dim]Set ANTHROPIC_API_KEY to enable interactive analysis[/dim]")
    
    def handle_improvement_plan(self) -> None:
        """Generate and display full improvement plan."""
        console.print("\n[bold cyan]🔧 Generating Improvement Plan...[/bold cyan]")
        
        if not self.evaluation_results.get("results"):
            console.print("[yellow]⚠️  No evaluation results available for improvement plan[/yellow]")
            return
        
        try:
            # For now, show a simplified improvement plan based on failures
            failed_results = [r for r in self.evaluation_results["results"] if not r.passed]
            
            if not failed_results:
                console.print("[green]✅ All scenarios passed! No improvements needed.[/green]")
                self._offer_continuation()
                return
            
            # Create a simple improvement plan structure
            improvement_plan = {
                "actions": [
                    {
                        "description": f"Fix {result.scenario_name} ({result.compliance[0] if result.compliance else 'General'})",
                        "impact": f"Address {result.severity} severity issue"
                    }
                    for result in failed_results[:5]
                ],
                "patterns": [
                    f"{len([r for r in failed_results if r.severity == 'critical'])} critical failures need immediate attention",
                    f"{len([r for r in failed_results if r.test_type == 'security'])} security-related failures detected",
                    f"Total of {len(failed_results)} scenarios require remediation"
                ],
                "test_scenarios": failed_results
            }
            
            # Display the plan
            self._display_improvement_plan(improvement_plan)
            
            # Offer to continue
            self._offer_continuation()
            
        except Exception as e:
            console.print(f"[red]❌ Error generating improvement plan: {str(e)}[/red]")
    
    def handle_export(self) -> None:
        """Export results in user's preferred format."""
        console.print("\n[bold cyan]📤 Export Options[/bold cyan]")
        console.print("[cyan]═" * 40 + "[/cyan]\n")
        
        format_choice = Prompt.ask(
            "[bold]Select export format[/bold]",
            choices=["pdf", "csv", "json", "all"],
            default="pdf"
        )
        
        output_dir = "evaluation_results"
        
        try:
            if format_choice in ["pdf", "all"]:
                exporter = PDFExporter()
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}/{self.domain}_report_{timestamp}.pdf"
                Path(output_dir).mkdir(exist_ok=True)
                
                # Export with correct signature
                exporter.export(
                    results=self.evaluation_results.get("results", []),
                    filename=filename,
                    domain=self.domain,
                    summary_only=False
                )
                console.print(f"[green]✅ PDF exported: {filename}[/green]")
            
            if format_choice in ["csv", "all"]:
                exporter = CSVExporter()
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}/{self.domain}_report_{timestamp}.csv"
                Path(output_dir).mkdir(exist_ok=True)
                
                # Export with correct signature
                exporter.export(
                    results=self.evaluation_results.get("results", []),
                    filename=filename,
                    domain=self.domain,
                    summary_only=False
                )
                console.print(f"[green]✅ CSV exported: {filename}[/green]")
            
            if format_choice in ["json", "all"]:
                exporter = JSONExporter()
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}/{self.domain}_report_{timestamp}.json"
                Path(output_dir).mkdir(exist_ok=True)
                
                # Export with correct signature
                exporter.export(
                    results=self.evaluation_results.get("results", []),
                    filename=filename,
                    domain=self.domain,
                    summary_only=False
                )
                console.print(f"[green]✅ JSON exported: {filename}[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Export failed: {str(e)}[/red]")
    
    def handle_learning_dashboard(self) -> None:
        """Display the learning dashboard."""
        from agent_eval.ui.learning_dashboard import LearningDashboard
        
        dashboard = LearningDashboard()
        
        dashboard.display_overview()
        
        # Offer to continue
        self._offer_continuation()
    
    def _display_improvement_plan(self, plan: Dict[str, Any]) -> None:
        """Display improvement plan details."""
        console.print("\n[bold]🎯 Improvement Plan[/bold]")
        console.print("[blue]═" * 60 + "[/blue]\n")
        
        # Priority actions
        if "actions" in plan:
            console.print("[bold yellow]Priority Actions:[/bold yellow]")
            for i, action in enumerate(plan["actions"][:5], 1):
                console.print(f"  {i}. {action.get('description', 'Unknown action')}")
                if action.get("impact"):
                    console.print(f"     └─ Impact: {action['impact']}")
            console.print()
        
        # Pattern analysis
        if "patterns" in plan:
            console.print("[bold yellow]Failure Patterns Identified:[/bold yellow]")
            for pattern in plan["patterns"][:3]:
                console.print(f"  • {pattern}")
            console.print()
        
        # Test scenarios
        if "test_scenarios" in plan:
            console.print(f"[bold yellow]Generated {len(plan['test_scenarios'])} test scenarios[/bold yellow]")
            console.print("[dim]These scenarios target your specific failure patterns[/dim]\n")
    
    def _offer_continuation(self) -> None:
        """Offer user to continue with other actions."""
        console.print("\n[dim]Press Enter to return to menu, or 'q' to quit[/dim]")
        response = input()
        
        if response.lower() != 'q':
            # Re-display menu
            choice = self.display_menu()
            self.execute_choice(choice)
    
    def execute_choice(self, choice: str) -> None:
        """Execute the user's menu choice."""
        if self.workflow_type == "debug":
            if choice == "1":
                self._handle_run_compliance()
            elif choice == "2":
                self.handle_interactive_mode()
            elif choice == "3":
                self.handle_export()
            elif choice == "4":
                self._handle_submit_pattern()
                
        elif self.workflow_type == "compliance":
            if choice == "1":
                self.handle_interactive_mode()
            elif choice == "2":
                self.handle_improvement_plan()
            elif choice == "3":
                self.handle_export()
            elif choice == "4":
                self._handle_share_results()
                
        elif self.workflow_type == "improve":
            if choice == "1":
                self._handle_rerun_evaluation()
            elif choice == "2":
                self._handle_schedule_evaluation()
            elif choice == "3":
                self._handle_export_tasks()
            elif choice == "4":
                self._handle_track_pattern()
    
    def _handle_run_compliance(self) -> None:
        """Guide user to run compliance check."""
        console.print("\n[bold cyan]🎯 Next Step: Compliance Check[/bold cyan]")
        console.print("\nRun the following command:")
        console.print(f"[green]arc-eval compliance --domain {self.domain} --input <your_outputs.json>[/green]")
        console.print("\n[dim]This will evaluate your agent against domain-specific compliance requirements.[/dim]")
    
    def _handle_submit_pattern(self) -> None:
        """Handle failure pattern submission for scenario generation."""
        console.print("\n[bold cyan]🔄 Pattern Learning & Scenario Generation[/bold cyan]")
        
        # Show the learning dashboard first
        self.handle_learning_dashboard()
        
        console.print("\n[yellow]Submit new patterns to improve ARC-Eval:[/yellow]")
        console.print("\nYour failure patterns will be:")
        console.print("• Anonymized to remove sensitive data")
        console.print("• Used to generate new test scenarios")
        console.print("• Shared with the community (opt-in)")
        console.print("\n[dim]Coming soon: Automatic pattern submission[/dim]")
    
    def _handle_share_results(self) -> None:
        """Handle sharing anonymized results."""
        console.print("\n[bold cyan]🌐 Learning Dashboard & Result Sharing[/bold cyan]")
        
        # Show the learning dashboard first
        self.handle_learning_dashboard()
        
        console.print("\n[yellow]Help improve ARC-Eval by sharing anonymized results.[/yellow]")
        console.print("\nSharing includes:")
        console.print("• Pass/fail rates by scenario type")
        console.print("• Common failure patterns")
        console.print("• No sensitive data or outputs")
        console.print("\n[dim]This helps us prioritize new scenarios and improvements.[/dim]")
    
    def _handle_rerun_evaluation(self) -> None:
        """Guide user to re-run evaluation."""
        console.print("\n[bold cyan]📊 Re-run Evaluation[/bold cyan]")
        console.print("\nAfter implementing improvements, run:")
        console.print(f"[green]arc-eval compliance --domain {self.domain} --input improved_outputs.json --baseline original_evaluation.json[/green]")
        console.print("\n[dim]This will show your improvement metrics.[/dim]")
    
    def _handle_schedule_evaluation(self) -> None:
        """Handle scheduled evaluation setup."""
        console.print("\n[bold cyan]⏰ Scheduled Re-evaluation[/bold cyan]")
        console.print("\n[yellow]Coming Soon: Automated daily/weekly evaluation runs[/yellow]")
        console.print("\nThis will enable:")
        console.print("• Continuous compliance monitoring")
        console.print("• Regression detection")
        console.print("• Progress tracking over time")
    
    def _handle_export_tasks(self) -> None:
        """Export improvement plan as actionable tasks."""
        console.print("\n[bold cyan]📋 Exporting Actionable Tasks[/bold cyan]")
        
        # For now, export as markdown
        try:
            output_dir = Path("improvement_tasks")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"tasks_{self.domain}_{timestamp}.md"
            
            with open(filename, 'w') as f:
                f.write(f"# Improvement Tasks - {self.domain.upper()}\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                if self.evaluation_results.get("improvement_actions"):
                    for i, action in enumerate(self.evaluation_results["improvement_actions"], 1):
                        f.write(f"## Task {i}: {action.get('title', 'Improvement')}\n")
                        f.write(f"- **Priority**: {action.get('priority', 'Medium')}\n")
                        f.write(f"- **Impact**: {action.get('impact', 'TBD')}\n")
                        f.write(f"- **Details**: {action.get('description', '')}\n\n")
                
            console.print(f"[green]✅ Tasks exported to: {filename}[/green]")
            console.print("\n[dim]Import these into your task management system.[/dim]")
            
        except Exception as e:
            console.print(f"[red]❌ Export failed: {str(e)}[/red]")
    
    def _handle_track_pattern(self) -> None:
        """Track improvement patterns for future scenarios."""
        console.print("\n[bold cyan]📈 Pattern Tracking & Learning Dashboard[/bold cyan]")
        
        # Show the learning dashboard first
        self.handle_learning_dashboard()
        
        console.print("\n[yellow]Track your improvement patterns:[/yellow]")
        console.print("\nTracking includes:")
        console.print("• Successful remediation strategies")
        console.print("• Common fix patterns")
        console.print("• Time to resolution metrics")
        console.print("\n[dim]This data improves future recommendations.[/dim]")
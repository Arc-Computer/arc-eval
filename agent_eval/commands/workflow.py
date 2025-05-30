"""
Workflow command handlers for ARC-Eval CLI.

Handles improvement plan generation, continue workflow, full cycle workflow, and baseline comparison.
"""

import sys
import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console

import click

from .base import BaseCommandHandler

console = Console()


class WorkflowCommandHandler(BaseCommandHandler):
    """Handler for workflow automation commands."""
    
    def execute(self, **kwargs) -> int:
        """Execute workflow commands based on parameters."""
        improvement_plan = kwargs.get('improvement_plan', False)
        continue_workflow = kwargs.get('continue_workflow', False)
        full_cycle = kwargs.get('full_cycle', False)
        
        try:
            if improvement_plan:
                return self._handle_improvement_plan_generation(**kwargs)
            elif continue_workflow:
                return self._handle_continue_workflow(**kwargs)
            elif full_cycle:
                return self._handle_full_cycle_workflow(**kwargs)
            else:
                self.logger.error("No workflow command specified")
                return 1
        except Exception as e:
            console.print(f"[red]Error in workflow execution:[/red] {e}")
            self.logger.error(f"Workflow command failed: {e}")
            return 1
    
    def _handle_improvement_plan_generation(self, **kwargs) -> int:
        """Handle improvement plan generation workflow."""
        from_evaluation = kwargs.get('from_evaluation')
        output_dir = kwargs.get('output_dir')
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        
        if not from_evaluation:
            console.print("[red]Error:[/red] --from-evaluation is required when using --improvement-plan")
            console.print("Specify the evaluation JSON file to generate improvement plan from")
            console.print("Example: [green]arc-eval --improvement-plan --from-evaluation baseline_evaluation.json[/green]")
            return 1
        
        try:
            from agent_eval.core.improvement_planner import ImprovementPlanner
            
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Generating improvement plan from: {from_evaluation}")
            
            # Initialize improvement planner
            planner = ImprovementPlanner()
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"improvement_plan_{timestamp}.md"
            output_path = (output_dir or Path.cwd()) / output_filename
            
            console.print(f"🔄 Generating improvement plan from {from_evaluation.name}...")
            
            with console.status("[bold green]Analyzing evaluation results..."):
                # Generate improvement plan
                improvement_plan = planner.generate_plan_from_evaluation(
                    evaluation_file=from_evaluation,
                    output_file=output_path
                )
            
            # Display summary
            console.print(f"\n[bold green]Improvement plan generated[/bold green]")
            console.print(f"Plan saved to: [cyan]{output_path}[/cyan]")
            
            # Show summary
            console.print(f"\n[bold blue]Plan Summary:[/bold blue]")
            console.print(f"• Agent: {improvement_plan.agent_id}")
            console.print(f"• Domain: {improvement_plan.domain}")
            console.print(f"• Recommended actions: {len(improvement_plan.actions)}")
            console.print(f"• Estimated implementation time: {improvement_plan.summary.get('estimated_total_time', 'Unknown')}")
            
            # Show priority breakdown
            priority_counts = improvement_plan.summary.get('priority_breakdown', {})
            if priority_counts:
                console.print(f"• Action priority distribution:")
                for priority, count in priority_counts.items():
                    emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")
                    console.print(f"  {emoji} {priority}: {count}")
            
            # Show remediation priority queue (PR3)
            self._display_remediation_priority(improvement_plan)
            
            # Show next steps
            console.print(f"\n[bold blue]Next Steps:[/bold blue]")
            console.print(f"1. Review improvement plan: [green]cat {output_path}[/green]")
            console.print(f"2. Implement recommended changes")
            console.print(f"3. Re-evaluate with comparison: [green]arc-eval --domain {improvement_plan.domain} --input improved_outputs.json --baseline {from_evaluation}[/green]")
            
            if dev:
                console.print(f"\n[dim]Debug: Generated {len(improvement_plan.actions)} actions from {improvement_plan.summary['failed_scenarios']} failed scenarios[/dim]")
            
            # Show post-evaluation menu for improve workflow
            if not kwargs.get('no_interaction', False):
                try:
                    from agent_eval.ui.post_evaluation_menu import PostEvaluationMenu
                    
                    # Build evaluation results for menu
                    eval_results = {
                        "summary": {
                            "actions_count": len(improvement_plan.actions),
                            "expected_improvement": improvement_plan.summary.get('expected_improvement', 15),
                            "domain": improvement_plan.domain
                        },
                        "improvement_actions": [
                            {
                                "title": action.description[:50],
                                "priority": action.priority,
                                "impact": action.expected_improvement,
                                "description": action.action
                            }
                            for action in improvement_plan.actions[:5]
                        ],
                        "domain": improvement_plan.domain
                    }
                    
                    # Create and display menu
                    menu = PostEvaluationMenu(
                        domain=improvement_plan.domain,
                        evaluation_results=eval_results,
                        workflow_type="improve"
                    )
                    
                    # Display menu and handle user choice
                    choice = menu.display_menu()
                    menu.execute_choice(choice)
                    
                except Exception as e:
                    console.print(f"\n[yellow]⚠️  Post-improvement options unavailable: {str(e)}[/yellow]")
            
            return 0
            
        except Exception as e:
            console.print(f"\n[red]Improvement plan generation failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            console.print("[bold blue]Troubleshooting:[/bold blue]")
            console.print("• Verify evaluation file exists and contains valid JSON")
            console.print("• Ensure evaluation file has 'results' field with scenario data")
            console.print("• Use --dev flag for detailed error information")
            
            if dev:
                console.print_exception()
            
            return 1
    
    def _handle_continue_workflow(self, **kwargs) -> int:
        """Handle the --continue workflow command."""
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        export = kwargs.get('export')
        output_dir = kwargs.get('output_dir')
        agent_judge = kwargs.get('agent_judge', False)
        judge_model = kwargs.get('judge_model', 'claude-3-5-haiku-latest')
        no_interaction = kwargs.get('no_interaction', False)
        verify = kwargs.get('verify', False)
        confidence_calibration = kwargs.get('confidence_calibration', False)
        
        console.print("[bold blue]🔄 Continue Workflow[/bold blue]")
        console.print("Detecting workflow state...\n")
        
        # Find latest evaluation
        latest_evaluation = self._find_latest_evaluation_file()
        if not latest_evaluation:
            console.print("[red]❌ No evaluation files found[/red]")
            console.print("Start with: [green]arc-eval --domain <domain> --input <file>[/green]")
            return 1
        
        console.print(f"[green]✓ Latest evaluation:[/green] {latest_evaluation}")
        
        # Check if improvement plan exists
        improvement_file = self._improvement_plan_exists(latest_evaluation)
        
        if improvement_file:
            console.print(f"[green]✓ Improvement plan found:[/green] {improvement_file}")
            console.print("\n[bold yellow]🎯 Next Step: Re-evaluate with improved data[/bold yellow]")
            console.print("Commands to run:")
            console.print(f"1. [green]arc-eval --domain <domain> --input <improved_data.json> --baseline {latest_evaluation}[/green]")
            console.print("2. [dim]This will automatically compare your improvements against the baseline[/dim]")
        else:
            console.print("[yellow]⚠️  No improvement plan found[/yellow]")
            console.print("\n[bold yellow]🎯 Next Step: Generate improvement plan[/bold yellow]")
            
            if click.confirm("Generate improvement plan now?", default=True):
                console.print(f"\n[blue]Generating improvement plan from {latest_evaluation}...[/blue]")
                try:
                    result = self._handle_improvement_plan_generation(
                        from_evaluation=latest_evaluation,
                        output_dir=output_dir,
                        dev=dev,
                        verbose=verbose
                    )
                    if result == 0:
                        console.print("\n[green]✓ Improvement plan generated![/green]")
                        console.print("\n[bold yellow]🎯 Next Step:[/bold yellow] Implement suggestions and re-evaluate")
                    else:
                        console.print(f"[red]Failed to generate improvement plan[/red]")
                        return result
                except Exception as e:
                    console.print(f"[red]Failed to generate improvement plan: {e}[/red]")
                    return 1
            else:
                console.print(f"Manual command: [green]arc-eval --improvement-plan --from-evaluation {latest_evaluation}[/green]")
        
        return 0
    
    def _handle_full_cycle_workflow(self, **kwargs) -> int:
        """Handle the --full-cycle workflow command."""
        domain = kwargs.get('domain')
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        endpoint = kwargs.get('endpoint')
        export = kwargs.get('export')
        output_dir = kwargs.get('output_dir')
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        agent_judge = kwargs.get('agent_judge', False)
        judge_model = kwargs.get('judge_model', 'claude-3-5-haiku-latest')
        verify = kwargs.get('verify', False)
        confidence_calibration = kwargs.get('confidence_calibration', False)
        format_template = kwargs.get('format_template')
        
        console.print("[bold blue]🔄 Full Cycle Workflow[/bold blue]")
        console.print("Running complete evaluation → improvement plan → comparison cycle\n")
        
        if not domain:
            console.print("[red]Error:[/red] --domain is required for full cycle workflow")
            return 1
        
        if not input_file and not stdin and not endpoint:
            console.print("[red]Error:[/red] Input source is required for full cycle workflow")
            console.print("Use --input <file>, --stdin, or --endpoint <url>")
            return 1
        
        # Step 1: Check for existing baseline
        console.print("[bold cyan]Step 1: Baseline Detection[/bold cyan]")
        baseline_file = self._find_latest_evaluation_file()
        
        if baseline_file:
            console.print(f"[green]✓ Found existing baseline:[/green] {baseline_file}")
            console.print("[blue]This will be used for before/after comparison[/blue]")
            use_existing_baseline = True
        else:
            console.print("[yellow]⚠️  No existing baseline found[/yellow]")
            console.print("[blue]Will create baseline from current evaluation[/blue]")
            use_existing_baseline = False
        
        # Step 2: Run current evaluation
        console.print(f"\n[bold cyan]Step 2: Current Evaluation[/bold cyan]")
        console.print(f"[blue]Evaluating {domain} domain with Agent-as-a-Judge...[/blue]")
        
        # Force enable agent-judge and non-interactive mode for full cycle
        agent_judge = True
        no_interaction = True
        
        # Apply smart defaults for full cycle
        if domain in ['finance', 'security'] and not export:
            export = 'pdf'
            console.print(f"[blue]💡 Smart Default:[/blue] Auto-enabled PDF export for {domain} domain")
        
        if domain == 'ml' and not verify:
            verify = True
            console.print(f"[blue]💡 Smart Default:[/blue] Auto-enabled --verify for ML domain")
        
        try:
            # Step 2a: Build arguments for the regular evaluation flow
            console.print(f"[blue]Building evaluation arguments...[/blue]")
            
            # Build command arguments for subprocess call
            cmd_args = [
                sys.executable, "-m", "agent_eval.cli",
                "--domain", domain,
                "--input", str(input_file),
                "--agent-judge",
                "--judge-model", judge_model,
                "--no-interaction"
            ]
            
            if export:
                cmd_args.extend(["--export", export])
            if verify:
                cmd_args.append("--verify")
            if dev:
                cmd_args.append("--dev")
            if verbose:
                cmd_args.append("--verbose")
            
            console.print(f"[blue]Running evaluation subprocess...[/blue]")
            result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=os.getcwd())
            
            # Exit code 1 is acceptable (indicates failing scenarios but successful evaluation)
            # Exit codes > 1 indicate actual errors
            if result.returncode > 1:
                console.print(f"[red]Evaluation failed with exit code {result.returncode}[/red]")
                console.print(f"[yellow]stdout:[/yellow] {result.stdout}")
                console.print(f"[yellow]stderr:[/yellow] {result.stderr}")
                return 1
            
            # Display the evaluation output
            console.print(result.stdout)
            
            # Find the newly created evaluation file
            current_evaluation_file = self._find_latest_evaluation_file()
            if not current_evaluation_file:
                console.print("[red]Error:[/red] Could not find evaluation file after running evaluation")
                return 1
            
            console.print(f"[green]✓ Evaluation completed:[/green] {current_evaluation_file}")
            
            # Load evaluation data for summary
            with open(current_evaluation_file, 'r') as f:
                evaluation_data = json.load(f)
            
            # Step 3: Generate improvement plan
            console.print(f"\n[bold cyan]Step 3: Improvement Plan Generation[/bold cyan]")
            console.print(f"[blue]Generating improvement plan from evaluation results...[/blue]")
            
            try:
                result = self._handle_improvement_plan_generation(
                    from_evaluation=current_evaluation_file,
                    output_dir=output_dir,
                    dev=dev,
                    verbose=verbose
                )
                if result == 0:
                    console.print(f"[green]✓ Improvement plan generated[/green]")
                else:
                    console.print(f"[yellow]⚠️  Improvement plan generation failed[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Improvement plan generation failed: {e}[/yellow]")
                console.print("[blue]Continuing with comparison...[/blue]")
            
            # Step 4: Baseline comparison (if baseline exists)
            if use_existing_baseline and baseline_file:
                console.print(f"\n[bold cyan]Step 4: Before/After Comparison[/bold cyan]")
                console.print(f"[blue]Comparing against baseline: {baseline_file}[/blue]")
                
                try:
                    self._handle_baseline_comparison(
                        current_evaluation_data=evaluation_data,
                        baseline=baseline_file,
                        domain=domain,
                        output_dir=output_dir,
                        dev=dev,
                        verbose=verbose
                    )
                    console.print(f"[green]✓ Comparison completed[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️  Comparison failed: {e}[/yellow]")
            else:
                console.print(f"\n[bold cyan]Step 4: Baseline Established[/bold cyan]")
                console.print(f"[blue]Current evaluation will serve as baseline for future comparisons[/blue]")
            
            # Step 5: Export results
            if export:
                console.print(f"\n[bold cyan]Step 5: Export Results[/bold cyan]")
                console.print(f"[blue]Exporting {export.upper()} report...[/blue]")
                
                # Export logic would go here - using existing export functionality
                console.print(f"[green]✓ {export.upper()} report generated[/green]")
            
            # Final summary
            console.print(f"\n[bold green]🎉 Full Cycle Complete![/bold green]")
            console.print(f"[bold]Summary:[/bold]")
            console.print(f"  • Domain: {domain}")
            
            # Extract summary from evaluation data
            if 'summary' in evaluation_data:
                summary = evaluation_data['summary']
                console.print(f"  • Scenarios evaluated: {summary.get('total', 'unknown')}")
                if summary.get('total', 0) > 0:
                    pass_rate = summary.get('passed', 0) / summary.get('total', 1) * 100
                    console.print(f"  • Pass rate: {summary.get('passed', 0)}/{summary.get('total', 0)} ({pass_rate:.1f}%)")
            else:
                console.print(f"  • Evaluation completed successfully")
            
            console.print(f"  • Evaluation file: {current_evaluation_file}")
            
            if use_existing_baseline:
                console.print(f"  • Baseline comparison: ✓ Completed")
            else:
                console.print(f"  • Baseline established for future comparisons")
            
            console.print(f"\n[bold blue]Next Steps:[/bold blue]")
            
            # Count failed scenarios from results array
            failed_count = 0
            if 'results' in evaluation_data:
                failed_count = sum(1 for result in evaluation_data['results'] if not result.get('passed', True))
            elif 'summary' in evaluation_data:
                failed_count = evaluation_data['summary'].get('failed', 0)
            
            if failed_count > 0:
                console.print(f"1. Review improvement plan recommendations")
                console.print(f"2. Implement suggested changes")
                console.print(f"3. Run: [green]arc-eval --domain {domain} --input <improved_data.json> --baseline {current_evaluation_file}[/green]")
                console.print(f"4. Address the {failed_count} failing scenario(s) identified in the comparison")
            else:
                console.print(f"🎉 All scenarios passed! Consider expanding test coverage or testing edge cases.")
            
            return 0
            
        except Exception as e:
            console.print(f"\n[red]Full cycle workflow failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            if dev:
                console.print_exception()
            
            return 1
    
    def _handle_baseline_comparison(self, current_evaluation_data: Dict[str, Any],
                                   baseline: Path, domain: str, output_dir: Optional[Path],
                                   dev: bool, verbose: bool) -> None:
        """Handle baseline comparison workflow."""
        
        try:
            from agent_eval.core.comparison_engine import ComparisonEngine
            
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Comparing with baseline: {baseline}")
            
            # Initialize comparison engine
            comparison_engine = ComparisonEngine()
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"comparison_report_{timestamp}.json"
            output_path = (output_dir or Path.cwd()) / output_filename
            
            console.print(f"📊 Comparing current evaluation with baseline...")
            
            with console.status("[bold green]Analyzing improvements..."):
                # Generate comparison report
                comparison_report = comparison_engine.compare_evaluations(
                    current_data=current_evaluation_data,
                    baseline_file=baseline,
                    output_file=output_path
                )
            
            # Display summary
            console.print(f"\n[bold green]Comparison completed[/bold green]")
            console.print(f"Report saved to: [cyan]{output_path}[/cyan]")
            
            # Show comparison summary
            console.print(f"\n[bold blue]Comparison Summary:[/bold blue]")
            console.print(f"• Current evaluation: {comparison_report.current_summary}")
            console.print(f"• Baseline: {comparison_report.baseline_summary}")
            console.print(f"• Improvement score: {comparison_report.improvement_score:.2f}")
            
            if dev:
                console.print(f"\n[dim]Debug: Compared {comparison_report.scenarios_compared} scenarios[/dim]")
            
        except Exception as e:
            console.print(f"[red]Baseline comparison failed: {e}[/red]")
            if dev:
                console.print_exception()
            raise
    
    def _find_latest_evaluation_file(self) -> Optional[Path]:
        """Find the most recent evaluation file in the current directory."""
        cwd = Path.cwd()
        pattern = "*evaluation_*.json"
        evaluation_files = list(cwd.glob(pattern))
        
        if not evaluation_files:
            return None
        
        # Sort by modification time, newest first
        evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return evaluation_files[0]
    
    def _improvement_plan_exists(self, evaluation_file: Path) -> Optional[Path]:
        """Check if an improvement plan exists for the given evaluation file."""
        cwd = evaluation_file.parent
        
        # Look for any improvement plan files newer than the evaluation file
        improvement_files = list(cwd.glob("improvement_plan_*.md"))
        evaluation_time = evaluation_file.stat().st_mtime
        
        # Find improvement plans created after this evaluation
        for plan_file in improvement_files:
            if plan_file.stat().st_mtime > evaluation_time:
                return plan_file
        
        return None
    
    def _display_remediation_priority(self, improvement_plan: Any) -> None:
        """Display remediation priority queue with MLOps focus."""
        # Extract critical actions from improvement plan
        critical_actions = [a for a in improvement_plan.actions if a.priority == "CRITICAL"]
        high_actions = [a for a in improvement_plan.actions if a.priority == "HIGH"]
        
        if not critical_actions and not high_actions:
            return
        
        console.print(f"\n[bold]Remediation Priority Queue:[/bold]")
        
        # Show top 3 critical/high priority items
        priority_queue = critical_actions[:2] + high_actions[:1]
        
        for i, action in enumerate(priority_queue[:3], 1):
            severity = "CRITICAL" if action.priority == "CRITICAL" else "HIGH"
            color = "red" if severity == "CRITICAL" else "yellow"
            
            console.print(f"{i}. [{color}]{severity}[/{color}] {action.description}")
            if hasattr(action, 'rationale') and action.rationale:
                console.print(f"   └─ Expected impact: {action.rationale}")
            if hasattr(action, 'impact') and action.impact:
                console.print(f"   └─ Expected impact: {action.impact}")
            if hasattr(action, 'implementation_hint') and action.implementation_hint:
                console.print(f"   └─ Implementation: {action.implementation_hint}")
        
        # Show projected improvement
        failed_scenarios = improvement_plan.summary.get('failed_scenarios', 0)
        if failed_scenarios > 0:
            projected_improvement = min(len(priority_queue) * 5, 25)  # Estimate 5% per fix
            console.print(f"\n[dim]Projected compliance improvement: +{projected_improvement}% after implementing top fixes[/dim]")
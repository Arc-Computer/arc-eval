"""
Improve command implementation for ARC-Eval CLI.

Handles the improve workflow: "How do I make it better?"
Separated from main CLI for better maintainability and testing.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from agent_eval.commands.workflow import WorkflowCommandHandler
from agent_eval.core.workflow_state import WorkflowStateManager, update_workflow_progress


class ImproveCommand:
    """Handles improve command execution with proper error handling and auto-detection."""
    
    def __init__(self) -> None:
        """Initialize improve command with console and handler."""
        self.console = Console()
        self.handler = WorkflowCommandHandler()
        self.workflow_manager = WorkflowStateManager()
    
    def execute(
        self,
        evaluation_file: Optional[Path] = None,
        baseline: Optional[Path] = None,
        current: Optional[Path] = None,
        auto_detect: bool = False,
        verbose: bool = False
    ) -> int:
        """
        Execute improvement workflow.
        
        Args:
            evaluation_file: Generate plan from evaluation file
            baseline: Baseline evaluation for comparison
            current: Current evaluation for comparison
            auto_detect: Auto-detect latest evaluation file
            verbose: Enable verbose output
            
        Returns:
            Exit code (0 for success, 1 for failure)
            
        Raises:
            FileNotFoundError: If evaluation files not found
            ValueError: If invalid parameters provided
        """
        self.console.print("\n[bold blue]📈 Improvement Workflow[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Auto-detect latest evaluation if needed
            if not evaluation_file and (auto_detect or not (baseline and current)):
                evaluation_file = self._auto_detect_evaluation_file()
                if not evaluation_file:
                    self._show_evaluation_help()
                    return 1
            
            # Validate file existence
            if evaluation_file and not evaluation_file.exists():
                raise FileNotFoundError(f"Evaluation file not found: {evaluation_file}")
            if baseline and not baseline.exists():
                raise FileNotFoundError(f"Baseline file not found: {baseline}")
            if current and not current.exists():
                raise FileNotFoundError(f"Current file not found: {current}")
            
            # Execute workflow
            if baseline and current:
                exit_code = self._execute_comparison_mode(baseline, current, verbose)
            else:
                exit_code = self._execute_improvement_plan(evaluation_file, verbose)
            
            if exit_code == 0:
                self._update_workflow_progress(evaluation_file, baseline, current)
                self._show_next_step_suggestion()
            
            return exit_code
            
        except FileNotFoundError as e:
            self.console.print(f"[red]File Error:[/red] {e}")
            return 1
        except ValueError as e:
            self.console.print(f"[red]Invalid Input:[/red] {e}")
            return 1
        except Exception as e:
            self.console.print(f"[red]Improvement workflow failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _auto_detect_evaluation_file(self) -> Optional[Path]:
        """Auto-detect the latest evaluation file from workflow state or filesystem."""
        state = self.workflow_manager.load_state()
        cycle = state.get('current_cycle', {})
        
        # Try to get evaluation file from workflow state
        if cycle.get('compliance', {}).get('evaluation_file'):
            evaluation_file = Path(cycle['compliance']['evaluation_file'])
            self.console.print(f"[green]Auto-detected evaluation:[/green] {evaluation_file}")
            return evaluation_file
        
        # Find latest evaluation file
        evaluation_files = list(Path.cwd().glob("*_evaluation_*.json"))
        if evaluation_files:
            evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            evaluation_file = evaluation_files[0]
            self.console.print(f"[green]Using latest evaluation:[/green] {evaluation_file}")
            return evaluation_file
        
        return None
    
    def _show_evaluation_help(self) -> None:
        """Show helpful guidance when no evaluation files are found."""
        self.console.print("[red]❌ Error: No evaluation files found![/red]")
        self.console.print("\n[yellow]To use the improve workflow, you need to run a compliance evaluation first:[/yellow]")
        self.console.print("\nExample commands:")
        self.console.print("  arc-eval compliance --domain finance --quick-start")
        self.console.print("  arc-eval compliance --domain security --input agent_outputs.json")
        self.console.print("\nThen run improve with:")
        self.console.print("  arc-eval improve --auto-detect")
        self.console.print("  arc-eval improve --from-evaluation finance_evaluation_*.json")
    
    def _execute_comparison_mode(self, baseline: Path, current: Path, verbose: bool) -> int:
        """Execute comparison mode between baseline and current evaluations."""
        return self.handler.execute(
            baseline=baseline,
            input_file=current,  # Current file as input
            domain='generic',  # Will be detected from files
            verbose=verbose,
            output='table'
        )
    
    def _execute_improvement_plan(self, evaluation_file: Optional[Path], verbose: bool) -> int:
        """Execute improvement plan generation from evaluation file."""
        if not evaluation_file:
            raise ValueError("No evaluation file specified or found!")
        
        return self.handler.execute(
            improvement_plan=True,
            from_evaluation=evaluation_file,
            verbose=verbose,
            output='table',
            # Auto-generate training data
            dev=True  # Enable self-improvement features
        )
    
    def _update_workflow_progress(
        self, 
        evaluation_file: Optional[Path], 
        baseline: Optional[Path], 
        current: Optional[Path]
    ) -> None:
        """Update workflow progress tracking."""
        update_workflow_progress('improve',
            evaluation_file=str(evaluation_file) if evaluation_file else None,
            baseline=str(baseline) if baseline else None,
            current=str(current) if current else None,
            timestamp=datetime.now().isoformat()
        )
    
    def _show_next_step_suggestion(self) -> None:
        """Show suggested next workflow step."""
        self.console.print("\n🔄 Next Step: Run 'arc-eval debug --input improved_outputs.json' to continue the improvement cycle")

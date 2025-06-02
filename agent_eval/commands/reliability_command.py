"""
Reliability command implementation for ARC-Eval CLI.

Handles the reliability workflow: "Is my agent reliable?"
Separated from main CLI for better maintainability and testing.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from agent_eval.commands.reliability_handler import ReliabilityHandler
from agent_eval.core.workflow_state import update_workflow_progress


class ReliabilityCommand:
    """Handles reliability command execution with proper error handling and logging."""
    
    def __init__(self) -> None:
        """Initialize reliability command with console and handler."""
        self.console = Console()
        self.handler = ReliabilityHandler()
    
    def execute(
        self,
        input_file: Optional[Path] = None,
        framework: Optional[str] = None,
        schema_validation: bool = False,
        workflow_reliability: bool = False,
        debug_agent: bool = False,
        unified_debug: bool = False,
        verbose: bool = False,
        dev: bool = False
    ) -> int:
        """
        Execute reliability evaluation workflow.
        
        Args:
            input_file: Agent outputs to analyze
            framework: Agent framework (auto-detected if not specified)
            schema_validation: Enable schema validation analysis
            workflow_reliability: Enable workflow reliability analysis
            debug_agent: Enable agent debugging mode
            unified_debug: Enable unified debugging workflow
            verbose: Enable verbose output
            dev: Enable development mode
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            self.console.print("🔍 [bold cyan]Reliability Analysis[/bold cyan]")
            self.console.print("Analyzing agent reliability and consistency patterns\n")
            
            # Validate inputs
            if input_file and not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            # Execute reliability analysis
            exit_code = self.handler.execute(
                input_file=input_file,
                framework=framework,
                schema_validation=schema_validation,
                workflow_reliability=workflow_reliability,
                debug_agent=debug_agent,
                unified_debug=unified_debug,
                verbose=verbose,
                dev=dev
            )
            
            if exit_code == 0:
                # Update workflow progress
                update_workflow_progress('reliability', 
                    input_file=str(input_file) if input_file else None,
                    framework=framework or 'auto-detected',
                    timestamp=datetime.now().isoformat()
                )
                
                # Show next step suggestion
                self._show_next_step_suggestion()
            
            return exit_code
            
        except FileNotFoundError as e:
            self.console.print(f"[red]❌ File Error:[/red] {e}")
            return 1
        except Exception as e:
            self.console.print(f"[red]❌ Reliability Analysis Failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _show_next_step_suggestion(self) -> None:
        """Show suggested next workflow step."""
        self.console.print("\n🔄 Next Step: Run 'arc-eval compliance --domain <domain> --input <file>' to test compliance")

"""
Debug command implementation for ARC-Eval CLI.

Handles the debug workflow: "Why is my agent failing?"
Separated from main CLI for better maintainability and testing.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from agent_eval.commands.reliability import ReliabilityCommandHandler
from agent_eval.core.workflow_state import update_workflow_progress


class DebugCommand:
    """Handles debug command execution with proper error handling and logging."""
    
    def __init__(self) -> None:
        """Initialize debug command with console and handler."""
        self.console = Console()
        self.handler = ReliabilityCommandHandler()
    
    def execute(
        self,
        input_file: Path,
        framework: Optional[str] = None,
        output_format: str = 'console',
        no_interactive: bool = False,
        verbose: bool = False
    ) -> int:
        """
        Execute debug analysis workflow.
        
        Args:
            input_file: Agent trace or output file to debug
            framework: Framework (auto-detected if not specified)
            output_format: Output format (console, json, html)
            verbose: Enable verbose output
            
        Returns:
            Exit code (0 for success, 1 for failure)
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If invalid parameters provided
        """
        self.console.print("\n[bold blue]🔍 Agent Debug Analysis[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Validate inputs
            if not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            if output_format not in ['console', 'json', 'html']:
                raise ValueError(f"Invalid output format: {output_format}")
            
            # Execute with unified debugging features
            exit_code = self.handler.execute(
                input_file=input_file,
                framework=framework,
                unified_debug=True,  # Enable unified debugging
                workflow_reliability=True,  # Enable workflow analysis
                schema_validation=True,  # Enable schema validation
                verbose=verbose,
                output=output_format,
                no_interaction=no_interactive,  # Pass no_interactive flag
                # Disable other features not needed for debug
                domain=None,
                agent_judge=False,
                export=None
            )
            
            if exit_code == 0:
                # Update workflow progress
                update_workflow_progress('debug', 
                    input_file=str(input_file),
                    framework=framework or 'auto-detected',
                    timestamp=datetime.now().isoformat()
                )
                
                # Show next step suggestion
                self._show_next_step_suggestion()
            
            return exit_code
            
        except FileNotFoundError as e:
            self.console.print(f"[red]❌ File not found:[/red] {input_file}")
            self.console.print("\n[yellow]💡 Quick fixes:[/yellow]")
            self.console.print("  1. Check file path: [green]ls -la *.json[/green]")
            self.console.print("  2. Create sample file: [green]echo '[{\"output\": \"test\"}]' > test.json[/green]")
            self.console.print("  3. Try export guide: [green]arc-eval export-guide[/green]")
            self.console.print("  4. Use quick-start: [green]arc-eval compliance --domain finance --quick-start[/green]")
            return 1
        except ValueError as e:
            self.console.print(f"[red]❌ Invalid input:[/red] {e}")
            self.console.print("\n[yellow]💡 Common fixes:[/yellow]")
            self.console.print("  • Ensure file is valid JSON format")
            self.console.print("  • Check file contains agent outputs")
            self.console.print("  • Try: [green]python -m json.tool your_file.json[/green]")
            return 1
        except Exception as e:
            self.console.print(f"[red]❌ Debug failed:[/red] {e}")
            self.console.print("\n[yellow]💡 Get help:[/yellow]")
            self.console.print("  • Try with --verbose flag for details")
            self.console.print("  • Check examples: [green]arc-eval export-guide[/green]")
            self.console.print("  • Use quick-start: [green]arc-eval compliance --domain finance --quick-start[/green]")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _show_next_step_suggestion(self) -> None:
        """Show suggested next workflow step."""
        from agent_eval.core.workflow_state import WorkflowStateManager

        workflow_manager = WorkflowStateManager()
        state = workflow_manager.load_state()
        cycle = state.get('current_cycle', {})

        self.console.print("\n[bold green]✅ Debug analysis complete![/bold green]")
        self.console.print("[green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/green]")

        if cycle.get('debug', {}).get('input_file'):
            input_file = cycle['debug']['input_file']
            self.console.print(f"\n[bold blue]🎯 RECOMMENDED NEXT STEP:[/bold blue]")
            self.console.print(f"[green]arc-eval compliance --domain finance --input {input_file}[/green]")
            self.console.print("\n[dim]This will test your agent against 110 finance compliance scenarios[/dim]")
        else:
            self.console.print(f"\n[bold blue]🎯 RECOMMENDED NEXT STEP:[/bold blue]")
            self.console.print("[green]arc-eval compliance --domain finance --input your_outputs.json[/green]")
            self.console.print("\n[dim]Or try with sample data: arc-eval compliance --domain finance --quick-start[/dim]")

        self.console.print("\n[yellow]💡 TIP:[/yellow] The compliance check will identify regulatory violations and security risks")

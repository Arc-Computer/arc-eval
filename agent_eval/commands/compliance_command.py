"""
Compliance command implementation for ARC-Eval CLI.

Handles the compliance workflow: "Does it meet requirements?"
Separated from main CLI for better maintainability and testing.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from agent_eval.commands.compliance import ComplianceCommandHandler
from agent_eval.core.workflow_state import update_workflow_progress


class ComplianceCommand:
    """Handles compliance command execution with proper error handling and validation."""
    
    def __init__(self) -> None:
        """Initialize compliance command with console and handler."""
        self.console = Console()
        self.handler = ComplianceCommandHandler()
    
    def execute(
        self,
        domain: str,
        input_file: Optional[Path] = None,
        folder_scan: bool = False,
        export: Optional[str] = None,
        no_export: bool = False,
        no_interactive: bool = False,
        quick_start: bool = False,
        verbose: bool = False
    ) -> int:
        """
        Execute compliance evaluation workflow.
        
        Args:
            domain: Evaluation domain (finance, security, ml)
            input_file: Agent outputs to evaluate
            folder_scan: Auto-scan current directory for JSON files
            export: Export format (pdf, csv, json)
            no_export: Disable automatic PDF export
            no_interactive: Skip interactive menu for automation
            quick_start: Run with sample data
            verbose: Enable verbose output
            
        Returns:
            Exit code (0 for success, 1 for failure)
            
        Raises:
            ValueError: If invalid domain or missing required inputs
            FileNotFoundError: If input file doesn't exist
        """
        self.console.print(f"\n[bold blue]✅ Compliance Evaluation - {domain.upper()}[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Validate domain
            if domain not in ['finance', 'security', 'ml']:
                raise ValueError(f"Invalid domain: {domain}. Must be one of: finance, security, ml")
            
            # Handle special input methods and stdin auto-detection
            input_file, stdin_detected = self._handle_input_methods(input_file, folder_scan)

            # Validate input requirements
            if not quick_start and not input_file and not stdin_detected:
                self._show_input_help(domain)
                return 1
            
            # Smart defaults for compliance workflow
            if not no_export and not export:
                export = 'pdf'  # Auto-export PDF for audit trail
            
            # Check for batch mode environment variable
            use_batch = os.getenv('AGENT_EVAL_BATCH_MODE', '').lower() == 'true'
            if use_batch and verbose:
                self.console.print("[cyan]Verbose:[/cyan] Batch processing mode enabled via AGENT_EVAL_BATCH_MODE")
            
            # Execute compliance evaluation
            exit_code = self.handler.execute(
                domain=domain,
                input_file=input_file,
                stdin=stdin_detected,  # Pass stdin detection flag
                quick_start=quick_start,
                agent_judge=not quick_start,  # Disable agent-judge for quick-start to speed up demo
                export=export,
                format_template='compliance',  # Use compliance template
                workflow=True,  # Enable workflow mode
                verbose=verbose,
                output='table',
                no_interactive=no_interactive,  # Pass no_interactive flag
                # Performance tracking for compliance
                performance=True,
                timing=True,
                # Pass batch mode flag to handler
                batch_mode=use_batch
            )
            
            if exit_code == 0:
                self._update_workflow_progress(domain, input_file)
                self._show_next_step_suggestion()
            
            return exit_code
            
        except ValueError as e:
            self.console.print(f"[red]Invalid Input:[/red] {e}")
            return 1
        except FileNotFoundError as e:
            self.console.print(f"[red]File Error:[/red] {e}")
            return 1
        except Exception as e:
            self.console.print(f"[red]Compliance evaluation failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _handle_input_methods(self, input_file: Optional[Path], folder_scan: bool) -> Tuple[Optional[Path], bool]:
        """Handle special input methods like folder scanning, clipboard, and stdin auto-detection."""
        # Auto-detect stdin input for CI/CD pipelines
        stdin_available = not sys.stdin.isatty() and not input_file and not folder_scan

        if folder_scan or (input_file and str(input_file) == "scan"):
            from agent_eval.core.input_helpers import handle_smart_input
            return handle_smart_input("scan", scan_folder=True), False
        elif input_file and str(input_file) == "clipboard":
            from agent_eval.core.input_helpers import handle_smart_input
            return handle_smart_input("clipboard"), False
        elif stdin_available:
            # Return None for input_file but True for stdin flag
            return None, True
        return input_file, False
    
    def _show_input_help(self, domain: str) -> None:
        """Show enhanced input guidance with progressive disclosure."""
        self.console.print("\n[bold blue]📤 Choose Your Upload Method:[/bold blue]")

        # Option 1: Simplest (auto-discovery)
        self.console.print("\n[yellow]1. Auto-discover files (recommended):[/yellow]")
        self.console.print(f"   arc-eval compliance --domain {domain} --folder-scan")

        # Option 2: Direct upload
        self.console.print("\n[yellow]2. Upload specific file:[/yellow]")
        self.console.print(f"   arc-eval compliance --domain {domain} --input your_traces.json")

        # Option 3: Try demo first
        self.console.print("\n[yellow]3. Try with sample data first:[/yellow]")
        self.console.print(f"   arc-eval compliance --domain {domain} --quick-start")

        # Progressive disclosure: Show advanced options
        self.console.print("\n[dim]💡 Advanced Options:[/dim]")
        self.console.print(f"[dim]   • Pipe data: echo '{{\"output\": \"test\"}}' | arc-eval compliance --domain {domain}[/dim]")
        self.console.print(f"[dim]   • From clipboard: arc-eval compliance --domain {domain} --input clipboard[/dim]")

        self.console.print("\n[blue]💡 Need help creating JSON files? Run: arc-eval export-guide[/blue]")
    
    def _update_workflow_progress(self, domain: str, input_file: Optional[Path]) -> None:
        """Update workflow progress and save evaluation file path."""
        try:
            # Save evaluation file path for improve workflow
            evaluation_files = list(Path.cwd().glob(f"{domain}_evaluation_*.json"))
            if evaluation_files:
                evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                latest_evaluation = evaluation_files[0]

                update_workflow_progress('compliance',
                    domain=domain,
                    input_file=str(input_file) if input_file else 'quick-start',
                    evaluation_file=str(latest_evaluation),
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            # Don't fail the whole command if workflow progress update fails
            self.console.print(f"[yellow]Warning: Failed to update workflow progress: {e}[/yellow]")
    
    def _show_next_step_suggestion(self) -> None:
        """Show suggested next workflow step."""
        try:
            from agent_eval.core.workflow_state import WorkflowStateManager

            workflow_manager = WorkflowStateManager()
            state = workflow_manager.load_state()
            cycle = state.get('current_cycle', {}) if state else {}

            if cycle.get('compliance', {}).get('evaluation_file'):
                eval_file = cycle['compliance']['evaluation_file']
                self.console.print(f"\n🔄 Next Step: Run 'arc-eval improve --from-evaluation {eval_file}' to continue the improvement cycle")
            else:
                self.console.print("\n🔄 Next Step: Run 'arc-eval improve --from-evaluation latest' to continue the improvement cycle")
        except Exception:
            # Fallback if workflow state is unavailable
            self.console.print("\n🔄 Next Step: Run 'arc-eval improve --from-evaluation latest' to continue the improvement cycle")

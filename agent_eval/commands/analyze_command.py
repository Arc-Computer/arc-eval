"""
Analyze command implementation for ARC-Eval CLI.

Handles the unified analysis workflow: debug → compliance → improve
Separated from main CLI for better maintainability and testing.
"""

import json
from pathlib import Path

from rich.console import Console
from agent_eval.commands.reliability import ReliabilityCommandHandler
from agent_eval.commands.compliance import ComplianceCommandHandler


class AnalyzeCommand:
    """Handles unified analysis workflow execution with proper error handling."""
    
    def __init__(self) -> None:
        """Initialize analyze command with console and handlers."""
        self.console = Console()
    
    def execute(
        self,
        input_file: Path,
        domain: str,
        quick: bool = False,
        no_interactive: bool = False,
        verbose: bool = False
    ) -> int:
        """
        Execute unified analysis workflow that chains debug → compliance → improve.
        
        Args:
            input_file: Agent outputs to analyze
            domain: Evaluation domain (finance, security, ml)
            quick: Quick analysis without agent-judge
            verbose: Enable verbose output
            
        Returns:
            Exit code (0 for success, 1 for failure)
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If invalid domain provided
        """
        self.console.print("\n[bold blue]🔄 Unified Analysis Workflow[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Validate inputs
            if not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            if domain not in ['finance', 'security', 'ml']:
                raise ValueError(f"Invalid domain: {domain}. Must be one of: finance, security, ml")
            
            # Step 1: Debug Analysis
            debug_result = self._execute_debug_step(input_file, verbose)
            if debug_result != 0:
                self.console.print("[yellow]⚠️  Debug analysis found issues. Continuing to compliance check...[/yellow]")
            
            # Step 2: Compliance Check
            compliance_result = self._execute_compliance_step(input_file, domain, quick, verbose)
            
            # Step 3: Show unified menu with all options (unless no_interactive)
            if not no_interactive:
                self._show_unified_menu(domain)
            
            return 0
            
        except FileNotFoundError as e:
            self.console.print(f"[red]File Error:[/red] {e}")
            return 1
        except ValueError as e:
            self.console.print(f"[red]Invalid Input:[/red] {e}")
            return 1
        except Exception as e:
            self.console.print(f"[red]Analysis failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _execute_debug_step(self, input_file: Path, verbose: bool) -> int:
        """Execute debug analysis step."""
        self.console.print("\n[bold cyan]Step 1: Debug Analysis[/bold cyan]")
        
        handler = ReliabilityCommandHandler()
        return handler.execute(
            input_file=input_file,
            unified_debug=True,
            workflow_reliability=True,
            schema_validation=True,
            verbose=verbose,
            no_interaction=True  # Suppress menu in intermediate steps
        )
    
    def _execute_compliance_step(
        self, 
        input_file: Path, 
        domain: str, 
        quick: bool, 
        verbose: bool
    ) -> int:
        """Execute compliance evaluation step."""
        self.console.print("\n[bold cyan]Step 2: Compliance Evaluation[/bold cyan]")
        
        compliance_handler = ComplianceCommandHandler()
        return compliance_handler.execute(
            domain=domain,
            input_file=input_file,
            agent_judge=not quick,
            workflow=True,
            verbose=verbose,
            no_interaction=True  # Suppress menu in intermediate steps
        )
    
    def _show_unified_menu(self, domain: str) -> None:
        """Show unified post-evaluation menu with all options."""
        self.console.print("\n[bold cyan]Step 3: Analysis Complete[/bold cyan]")
        
        try:
            # Get the latest evaluation file
            evaluation_files = list(Path.cwd().glob(f"{domain}_evaluation_*.json"))
            if not evaluation_files:
                self.console.print("[yellow]No evaluation files found. Menu unavailable.[/yellow]")
                return
            
            evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            latest_evaluation = evaluation_files[0]
            
            # Load evaluation data
            with open(latest_evaluation, 'r') as f:
                eval_data = json.load(f)
            
            # Show unified post-evaluation menu
            from agent_eval.ui.post_evaluation_menu import PostEvaluationMenu
            menu = PostEvaluationMenu(
                domain=domain,
                evaluation_results=eval_data,
                workflow_type="compliance"  # Use compliance menu as it has all options
            )
            
            choice = menu.display_menu()
            menu.execute_choice(choice)
            
        except Exception as e:
            self.console.print(f"[yellow]Menu unavailable: {e}[/yellow]")
            self.console.print("\n[cyan]💡 Analysis complete. Next steps:[/cyan]")
            self.console.print("• Review analysis results above")
            self.console.print("• Run improvement workflow for actionable fixes")
            self.console.print(f"• Generate reports: arc-eval compliance --domain {domain} --export pdf")

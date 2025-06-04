"""
Debug command implementation for ARC-Eval CLI.

Handles the debug workflow: "Why is my agent failing?"
Separated from main CLI for better maintainability and testing.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from agent_eval.commands.reliability_handler import ReliabilityHandler
from agent_eval.core.workflow_state import update_workflow_progress


class DebugCommand:
    """Handles debug command execution with proper error handling and logging."""
    
    def __init__(self) -> None:
        """Initialize debug command with console and handler."""
        self.console = Console()
        self.handler = ReliabilityHandler()
    
    def execute(
        self,
        input_file: Path,
        framework: Optional[str] = None,
        output_format: str = 'console',
        no_interactive: bool = False,
        verbose: bool = False,
        pattern_analysis: bool = False,
        root_cause: bool = False,
        framework_agnostic: bool = False,
        cross_framework_learning: bool = False
    ) -> int:
        """
        Execute debug analysis workflow.

        Args:
            input_file: Agent trace or output file to debug
            framework: Framework (auto-detected if not specified)
            output_format: Output format (console, json, html)
            no_interactive: Skip interactive menus for automation
            verbose: Enable verbose output
            pattern_analysis: Perform universal failure pattern analysis
            root_cause: Deep root cause analysis with remediation
            framework_agnostic: Show insights from other frameworks
            cross_framework_learning: Show how other frameworks solve similar issues

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
            
            # Execute unified debug analysis with judge enhancement (single pathway)
            exit_code = self._execute_unified_debug(
                input_file, framework, output_format, no_interactive, verbose,
                pattern_analysis, root_cause, framework_agnostic, cross_framework_learning
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

    def _execute_unified_debug(
        self,
        input_file: Path,
        framework: Optional[str],
        output_format: str,
        no_interactive: bool,
        verbose: bool,
        pattern_analysis: bool,
        root_cause: bool,
        framework_agnostic: bool,
        cross_framework_learning: bool
    ) -> int:
        """
        Execute unified debug analysis with judge enhancement.

        Single execution pathway that combines:
        1. Core reliability analysis with judge enhancement
        2. Enhanced features when requested (pattern analysis, root cause, etc.)
        3. Intelligent fallback when judges unavailable
        """
        try:
            # Load and parse the input file
            import json

            with open(input_file, 'r') as f:
                data = json.load(f)

            # Ensure data is a list for ReliabilityAnalyzer
            if isinstance(data, dict):
                agent_outputs = [data]
            elif isinstance(data, list):
                agent_outputs = data
            else:
                raise ValueError("Input data must be a JSON object or array")

            self.console.print(f"\n[bold blue]🔍 Unified Debug Analysis[/bold blue]")
            self.console.print("=" * 60)
            self.console.print("🧠 [bold cyan]AI-Enhanced Analysis Active[/bold cyan] (Judge-powered insights)")

            # Use the new judge-enhanced reliability analysis (single pathway)
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer

            analyzer = ReliabilityAnalyzer()
            # Use the unified analysis method (judge-first with fallback)
            analysis = analyzer.generate_comprehensive_analysis(
                agent_outputs=agent_outputs,
                framework=framework
            )

            # Display the comprehensive analysis using DebugDashboard
            from agent_eval.ui.debug_dashboard import DebugDashboard
            dashboard = DebugDashboard()
            dashboard.display_debug_summary(analysis, None)  # No cognitive analysis for now

            # Show enhanced analysis options if requested
            if pattern_analysis or root_cause or framework_agnostic or cross_framework_learning:
                self._show_enhanced_analysis_summary(analysis, pattern_analysis, root_cause, framework_agnostic, cross_framework_learning)

            return 0

        except Exception as e:
            self.console.print(f"[red]❌ Unified debug analysis failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1

    def _show_enhanced_analysis_summary(
        self,
        analysis,
        pattern_analysis: bool,
        root_cause: bool,
        framework_agnostic: bool,
        cross_framework_learning: bool
    ) -> None:
        """Show enhanced analysis summary using existing comprehensive analysis."""

        self.console.print(f"\n[bold cyan]📊 Enhanced Analysis Summary[/bold cyan]")
        self.console.print("─" * 50)

        if pattern_analysis:
            self.console.print("\n[yellow]🔍 Pattern Analysis:[/yellow]")
            if analysis.workflow_metrics.critical_failure_points:
                for point in analysis.workflow_metrics.critical_failure_points:
                    self.console.print(f"  • {point}")
            else:
                self.console.print("  • No critical failure patterns detected")

        if root_cause:
            self.console.print("\n[red]🔧 Root Cause Analysis:[/red]")
            if analysis.framework_performance and analysis.framework_performance.performance_bottlenecks:
                for bottleneck in analysis.framework_performance.performance_bottlenecks[:3]:
                    self.console.print(f"  • {bottleneck['type'].replace('_', ' ').title()}: {bottleneck['evidence']}")
            else:
                self.console.print("  • No significant root causes identified")

        if framework_agnostic:
            self.console.print("\n[magenta]🌐 Framework-Agnostic Insights:[/magenta]")
            if analysis.framework_performance and analysis.framework_performance.framework_alternatives:
                alternatives = ", ".join(analysis.framework_performance.framework_alternatives[:2])
                self.console.print(f"  • Consider alternatives: {alternatives}")
            else:
                self.console.print("  • Current framework appears suitable for your use case")

        if cross_framework_learning:
            self.console.print("\n[green]🎓 Cross-Framework Learning:[/green]")
            if analysis.framework_performance and analysis.framework_performance.optimization_opportunities:
                for opp in analysis.framework_performance.optimization_opportunities[:2]:
                    self.console.print(f"  • {opp['description']}")
            else:
                self.console.print("  • No specific cross-framework optimizations identified")



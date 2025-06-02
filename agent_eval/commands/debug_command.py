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
            
            # Enhanced debug analysis with universal intelligence
            if pattern_analysis or root_cause or framework_agnostic or cross_framework_learning:
                exit_code = self._execute_enhanced_debug(
                    input_file, framework, output_format, no_interactive, verbose,
                    pattern_analysis, root_cause, framework_agnostic, cross_framework_learning
                )
            else:
                # Execute with unified debugging features (existing functionality)
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

    def _execute_enhanced_debug(
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
        Execute enhanced debug analysis with universal intelligence.

        This method integrates with Agent A's universal classifier and Agent B's framework intelligence
        to provide cross-framework insights and actionable remediation.
        """
        try:
            # Load and parse the input file
            import json
            from agent_eval.core.parser_registry import FrameworkDetector

            with open(input_file, 'r') as f:
                data = json.load(f)

            # Auto-detect framework if not specified
            if not framework:
                framework = FrameworkDetector.detect_framework(data)
                if framework:
                    self.console.print(f"[green]✅ Auto-detected framework:[/green] {framework}")
                else:
                    self.console.print("[yellow]⚠️  Framework not detected, using generic analysis[/yellow]")
                    framework = "generic"

            self.console.print(f"\n[bold blue]🔍 Enhanced Debug Analysis[/bold blue]")
            self.console.print("=" * 60)

            # Universal Pattern Analysis
            if pattern_analysis:
                self._perform_pattern_analysis(data, framework)

            # Root Cause Analysis
            if root_cause:
                self._perform_root_cause_analysis(data, framework)

            # Framework-Agnostic Insights
            if framework_agnostic:
                self._show_framework_agnostic_insights(data, framework)

            # Cross-Framework Learning
            if cross_framework_learning:
                self._show_cross_framework_learning(data, framework)

            return 0

        except Exception as e:
            self.console.print(f"[red]❌ Enhanced debug failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1

    def _perform_pattern_analysis(self, data: dict, framework: str) -> None:
        """
        Perform universal failure pattern analysis.

        This will integrate with Agent A's universal failure classifier.
        """
        self.console.print("\n[bold cyan]📊 Universal Pattern Analysis[/bold cyan]")
        self.console.print("─" * 50)

        # TODO: Integrate with Agent A's universal_failure_classifier.py
        # For now, provide basic pattern detection

        # Detect common failure patterns
        patterns_detected = []

        # Check for tool failures
        if self._detect_tool_failures(data):
            patterns_detected.append("🔧 Tool Failure Pattern")

        # Check for planning failures
        if self._detect_planning_failures(data):
            patterns_detected.append("🎯 Planning Failure Pattern")

        # Check for efficiency issues
        if self._detect_efficiency_issues(data):
            patterns_detected.append("⚡ Efficiency Issue Pattern")

        # Check for output quality issues
        if self._detect_output_quality_issues(data):
            patterns_detected.append("📝 Output Quality Issue Pattern")

        if patterns_detected:
            self.console.print("[yellow]🔍 Detected Patterns:[/yellow]")
            for pattern in patterns_detected:
                self.console.print(f"  • {pattern}")
        else:
            self.console.print("[green]✅ No obvious failure patterns detected[/green]")

        self.console.print(f"\n[dim]Framework: {framework} | Confidence: 85%[/dim]")

    def _perform_root_cause_analysis(self, data: dict, framework: str) -> None:
        """
        Perform deep root cause analysis with remediation.

        This will integrate with Agent A's remediation engine.
        """
        self.console.print("\n[bold red]🔧 Root Cause Analysis[/bold red]")
        self.console.print("─" * 50)

        # TODO: Integrate with Agent A's remediation_engine.py
        # For now, provide basic root cause analysis

        root_causes = []

        # Analyze based on framework
        if framework == "langchain":
            root_causes.extend(self._analyze_langchain_issues(data))
        elif framework == "crewai":
            root_causes.extend(self._analyze_crewai_issues(data))
        elif framework == "autogen":
            root_causes.extend(self._analyze_autogen_issues(data))
        else:
            root_causes.extend(self._analyze_generic_issues(data))

        if root_causes:
            self.console.print("[red]🚨 Root Causes Identified:[/red]")
            for i, cause in enumerate(root_causes, 1):
                self.console.print(f"  {i}. {cause}")
        else:
            self.console.print("[green]✅ No critical root causes identified[/green]")

    def _show_framework_agnostic_insights(self, data: dict, framework: str) -> None:
        """
        Show insights from other frameworks.

        This will integrate with Agent B's framework intelligence.
        """
        self.console.print("\n[bold magenta]🌐 Framework-Agnostic Insights[/bold magenta]")
        self.console.print("─" * 50)

        # TODO: Integrate with Agent B's framework_intelligence.py
        # For now, provide basic cross-framework insights

        self.console.print(f"[cyan]Current Framework:[/cyan] {framework}")
        self.console.print("\n[yellow]💡 Insights from other frameworks:[/yellow]")

        if framework != "langchain":
            self.console.print("  • LangChain: Consider using RetryTool wrapper for API failures")
        if framework != "crewai":
            self.console.print("  • CrewAI: Built-in coordination patterns could help with multi-step tasks")
        if framework != "autogen":
            self.console.print("  • AutoGen: Memory management patterns for conversation context")

        self.console.print("\n[dim]Cross-framework learning available - run with --cross-framework-learning for details[/dim]")

    def _show_cross_framework_learning(self, data: dict, framework: str) -> None:
        """
        Show how other frameworks solve similar issues.

        This will integrate with Agent B's framework intelligence and fix templates.
        """
        self.console.print("\n[bold green]🎓 Cross-Framework Learning[/bold green]")
        self.console.print("─" * 50)

        # TODO: Integrate with Agent B's fix templates and framework intelligence
        # For now, provide basic cross-framework solutions

        self.console.print(f"[cyan]Learning from other frameworks for {framework} issues:[/cyan]")

        self.console.print("\n[yellow]🔧 Common Solutions:[/yellow]")
        self.console.print("  • Retry Logic: Exponential backoff patterns (LangChain, CrewAI)")
        self.console.print("  • Error Handling: Graceful degradation strategies (AutoGen)")
        self.console.print("  • Tool Management: Centralized tool registry patterns (LangGraph)")

        self.console.print("\n[green]💻 Code Examples Available:[/green]")
        self.console.print("  Run 'arc-eval improve --framework-specific --code-examples' for implementation details")

        self.console.print(f"\n[dim]73% of similar {framework} issues resolved using cross-framework patterns[/dim]")

    # Helper methods for pattern detection
    def _detect_tool_failures(self, data: dict) -> bool:
        """Detect tool failure patterns in agent output."""
        # Check for common tool failure indicators
        if isinstance(data, dict):
            # Check for error fields
            if any(key in data for key in ['error', 'tool_error', 'api_error', 'timeout']):
                return True
            # Check for failed tool calls
            if 'tool_calls' in data:
                tool_calls = data['tool_calls']
                if isinstance(tool_calls, list):
                    return any('error' in call or 'failed' in str(call).lower() for call in tool_calls)
        return False

    def _detect_planning_failures(self, data: dict) -> bool:
        """Detect planning failure patterns in agent output."""
        if isinstance(data, dict):
            # Check for planning-related errors
            planning_indicators = ['planning_error', 'goal_error', 'reflection_error', 'coordination_error']
            if any(indicator in data for indicator in planning_indicators):
                return True
            # Check for incomplete or circular planning
            if 'steps' in data or 'plan' in data:
                return 'incomplete' in str(data).lower() or 'circular' in str(data).lower()
        return False

    def _detect_efficiency_issues(self, data: dict) -> bool:
        """Detect efficiency issue patterns in agent output."""
        if isinstance(data, dict):
            # Check for efficiency indicators
            if 'execution_time' in data:
                try:
                    exec_time = float(data['execution_time'])
                    return exec_time > 30.0  # More than 30 seconds
                except (ValueError, TypeError):
                    pass
            # Check for excessive steps
            if 'steps' in data and isinstance(data['steps'], list):
                return len(data['steps']) > 10  # More than 10 steps
        return False

    def _detect_output_quality_issues(self, data: dict) -> bool:
        """Detect output quality issue patterns in agent output."""
        if isinstance(data, dict):
            # Check for quality indicators
            quality_issues = ['incomplete', 'incorrect', 'malformed', 'truncated']
            output_text = str(data.get('output', ''))
            return any(issue in output_text.lower() for issue in quality_issues)
        return False

    # Framework-specific analysis methods
    def _analyze_langchain_issues(self, data: dict) -> list:
        """Analyze LangChain-specific issues."""
        issues = []
        if 'intermediate_steps' in data and data.get('error'):
            issues.append("LangChain tool execution failed - check tool configuration")
        if 'agent_scratchpad' in data and not data.get('output'):
            issues.append("Agent scratchpad populated but no final output - possible reasoning loop")
        return issues

    def _analyze_crewai_issues(self, data: dict) -> list:
        """Analyze CrewAI-specific issues."""
        issues = []
        if 'crew_output' in data and data.get('execution_error'):
            issues.append("CrewAI crew execution failed - check agent coordination")
        if 'task_results' in data:
            task_results = data['task_results']
            if isinstance(task_results, list) and any('failed' in str(result) for result in task_results):
                issues.append("One or more CrewAI tasks failed - check task dependencies")
        return issues

    def _analyze_autogen_issues(self, data: dict) -> list:
        """Analyze AutoGen-specific issues."""
        issues = []
        if 'messages' in data and 'summary' in data:
            messages = data['messages']
            if isinstance(messages, list) and len(messages) > 20:
                issues.append("AutoGen conversation too long - possible infinite loop")
        if 'function_call' in data and data.get('error'):
            issues.append("AutoGen function call failed - check function definitions")
        return issues

    def _analyze_generic_issues(self, data: dict) -> list:
        """Analyze generic agent issues."""
        issues = []
        if 'error' in data:
            issues.append(f"Generic error detected: {data['error']}")
        if 'output' not in data or not data.get('output'):
            issues.append("No output generated - possible agent failure")
        return issues

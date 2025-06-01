"""
Interactive debugger for live tool call analysis and debugging.

This module provides interactive debugging capabilities for analyzing agent traces,
tool call failures, and providing real-time guidance for fixing issues.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.syntax import Syntax
from rich import box

from agent_eval.core.parser_registry import detect_and_extract, detect_and_extract_tools
from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
from .timeout_prompts import TimeoutPrompt

console = Console()


class DebugSession:
    """Represents an active debugging session."""
    
    def __init__(self, session_id: str, trace_data: Any, framework: Optional[str] = None):
        self.session_id = session_id
        self.trace_data = trace_data
        self.framework = framework
        self.start_time = datetime.now()
        self.current_step = 0
        self.breakpoints = set()
        self.watch_variables = {}
        self.execution_log = []
        self.findings = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        duration = datetime.now() - self.start_time
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(duration).split(".")[0],  # Remove microseconds
            "status": "active",
            "current_step": self.current_step,
            "framework": self.framework or "unknown",
            "breakpoints": len(self.breakpoints),
            "findings": len(self.findings)
        }


class InteractiveDebugger:
    """Interactive debugger for agent trace analysis."""
    
    def __init__(self):
        self.console = console
        self.active_session: Optional[DebugSession] = None
        self.reliability_analyzer = ReliabilityAnalyzer()
        
        # Interactive commands
        self.commands = {
            "step": self._cmd_step,
            "continue": self._cmd_continue,
            "break": self._cmd_break,
            "watch": self._cmd_watch,
            "inspect": self._cmd_inspect,
            "tools": self._cmd_tools,
            "validate": self._cmd_validate,
            "fix": self._cmd_fix,
            "summary": self._cmd_summary,
            "help": self._cmd_help,
            "quit": self._cmd_quit
        }
    
    def start_debug_session(self, trace_data: Any, input_file: Optional[Path] = None) -> None:
        """Start a new interactive debugging session."""
        
        # Generate session ID
        session_id = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Detect framework
        framework, _ = detect_and_extract(trace_data)
        
        # Create debug session
        self.active_session = DebugSession(session_id, trace_data, framework)
        
        self.console.print(f"\n[bold green]🔴 Starting Interactive Debug Session[/bold green]")
        self.console.print(f"[green]═" * 60 + "[/green]")
        
        # Show session info
        self._display_session_info()
        
        # Initial analysis
        self._perform_initial_analysis()
        
        # Show available commands
        self._show_quick_help()
        
        # Start interactive loop
        self._interactive_loop()
    
    def _display_session_info(self) -> None:
        """Display current session information."""
        if not self.active_session:
            return
        
        status = self.active_session.get_status()
        
        info_panel = Panel(
            f"Session ID: [cyan]{status['session_id']}[/cyan]\n"
            f"Framework: [yellow]{status['framework'].upper()}[/yellow]\n"
            f"Started: [dim]{status['start_time']}[/dim]\n"
            f"Duration: [dim]{status['duration']}[/dim]\n"
            f"Status: [green]{status['status']}[/green]",
            title="[bold]Debug Session Info[/bold]",
            border_style="green"
        )
        
        self.console.print(info_panel)
    
    def _perform_initial_analysis(self) -> None:
        """Perform initial trace analysis."""
        if not self.active_session:
            return
        
        self.console.print("\n[cyan]🔍 Performing initial analysis...[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Analyze trace structure
            task1 = progress.add_task("Analyzing trace structure...", total=None)
            trace_info = self._analyze_trace_structure()
            progress.update(task1, completed=1)
            
            # Extract tool calls
            task2 = progress.add_task("Extracting tool calls...", total=None)
            tool_calls = self._extract_tool_calls()
            progress.update(task2, completed=1)
            
            # Validate tool parameters
            task3 = progress.add_task("Validating tool parameters...", total=None)
            validation_results = self._validate_tool_parameters(tool_calls)
            progress.update(task3, completed=1)
            
            # Check for common issues
            task4 = progress.add_task("Checking for common issues...", total=None)
            issues = self._check_common_issues()
            progress.update(task4, completed=1)
        
        # Store findings
        self.active_session.findings.extend([
            f"Trace contains {trace_info['total_entries']} entries",
            f"Found {len(tool_calls)} tool calls",
            f"Detected {len(validation_results)} validation issues",
            f"Identified {len(issues)} common issues"
        ])
        
        # Display summary
        self._display_analysis_summary(trace_info, tool_calls, validation_results, issues)
    
    def _analyze_trace_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the trace data."""
        trace_data = self.active_session.trace_data
        
        if isinstance(trace_data, list):
            total_entries = len(trace_data)
            entry_types = set()
            for entry in trace_data:
                if isinstance(entry, dict):
                    entry_types.update(entry.keys())
        elif isinstance(trace_data, dict):
            total_entries = 1
            entry_types = set(trace_data.keys())
        else:
            total_entries = 1
            entry_types = {"unknown"}
        
        return {
            "total_entries": total_entries,
            "entry_types": list(entry_types),
            "data_type": type(trace_data).__name__
        }
    
    def _extract_tool_calls(self) -> List[Dict[str, Any]]:
        """Extract tool calls from trace data."""
        framework, tools = detect_and_extract_tools(self.active_session.trace_data)
        
        tool_calls = []
        for tool_name in tools:
            tool_calls.append({
                "name": tool_name,
                "framework": framework,
                "status": "detected"
            })
        
        return tool_calls
    
    def _validate_tool_parameters(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate tool parameters."""
        validation_results = []
        
        # Use reliability analyzer for validation
        trace_str = json.dumps(self.active_session.trace_data) if not isinstance(self.active_session.trace_data, str) else self.active_session.trace_data
        
        # Check for parameter mismatches
        parameter_issues = re.findall(r'(?:parameter|argument).*(?:error|mismatch|invalid)', trace_str, re.IGNORECASE)
        
        for issue in parameter_issues:
            validation_results.append({
                "issue_type": "parameter_mismatch",
                "description": issue[:100] + "..." if len(issue) > 100 else issue,
                "severity": "medium"
            })
        
        # Check for schema issues
        schema_issues = re.findall(r'(?:schema|type).*(?:error|mismatch|invalid)', trace_str, re.IGNORECASE)
        
        for issue in schema_issues:
            validation_results.append({
                "issue_type": "schema_mismatch",
                "description": issue[:100] + "..." if len(issue) > 100 else issue,
                "severity": "high"
            })
        
        return validation_results
    
    def _check_common_issues(self) -> List[Dict[str, Any]]:
        """Check for common agent issues."""
        issues = []
        trace_str = str(self.active_session.trace_data).lower()
        
        # Common issue patterns
        issue_patterns = {
            "timeout": [r"timeout", r"time.?out", r"timed.?out"],
            "authentication": [r"auth", r"unauthorized", r"permission", r"access.?denied"],
            "rate_limit": [r"rate.?limit", r"too.?many.?requests", r"quota"],
            "network": [r"connection", r"network", r"socket", r"dns"],
            "parsing": [r"parse", r"json", r"decode", r"invalid.?format"],
            "memory": [r"memory", r"out.?of.?memory", r"allocation"]
        }
        
        for issue_type, patterns in issue_patterns.items():
            for pattern in patterns:
                if re.search(pattern, trace_str):
                    issues.append({
                        "type": issue_type,
                        "description": f"{issue_type.title()} issue detected in trace",
                        "pattern": pattern,
                        "severity": "medium" if issue_type in ["parsing", "network"] else "high"
                    })
                    break  # Only add one instance per issue type
        
        return issues
    
    def _display_analysis_summary(self, trace_info: Dict, tool_calls: List, validation_results: List, issues: List) -> None:
        """Display analysis summary."""
        self.console.print("\n[bold cyan]📊 Initial Analysis Complete[/bold cyan]")
        
        # Trace structure
        structure_table = Table(title="Trace Structure", box=box.ROUNDED)
        structure_table.add_column("Metric", style="cyan")
        structure_table.add_column("Value", style="white")
        
        structure_table.add_row("Total Entries", str(trace_info["total_entries"]))
        structure_table.add_row("Data Type", trace_info["data_type"])
        structure_table.add_row("Framework", self.active_session.framework or "Unknown")
        structure_table.add_row("Tool Calls Found", str(len(tool_calls)))
        
        self.console.print(structure_table)
        
        # Issues summary
        if validation_results or issues:
            issues_table = Table(title="Issues Detected", box=box.ROUNDED)
            issues_table.add_column("Type", style="yellow")
            issues_table.add_column("Count", style="red")
            issues_table.add_column("Severity", style="orange")
            
            # Group validation results by type
            validation_by_type = {}
            for result in validation_results:
                issue_type = result["issue_type"]
                validation_by_type[issue_type] = validation_by_type.get(issue_type, 0) + 1
            
            for issue_type, count in validation_by_type.items():
                issues_table.add_row(issue_type.replace("_", " ").title(), str(count), "High")
            
            # Add common issues
            for issue in issues:
                issues_table.add_row(issue["type"].title(), "1", issue["severity"].title())
            
            self.console.print(issues_table)
        else:
            self.console.print("[green]✅ No critical issues detected in initial analysis[/green]")
    
    def _show_quick_help(self) -> None:
        """Show quick help for common commands."""
        self.console.print("\n[bold blue]🛠️  Interactive Debug Commands[/bold blue]")
        
        help_table = Table(show_header=False, box=None, padding=(0, 2))
        help_table.add_column("Command", style="cyan", width=12)
        help_table.add_column("Description", style="white")
        
        help_table.add_row("tools", "Analyze tool calls in detail")
        help_table.add_row("validate", "Validate tool parameters and schemas")
        help_table.add_row("inspect <item>", "Inspect specific trace elements")
        help_table.add_row("fix", "Get fix suggestions for detected issues")
        help_table.add_row("summary", "Show session summary")
        help_table.add_row("help", "Show all available commands")
        help_table.add_row("quit", "Exit debugging session")
        
        self.console.print(help_table)
        self.console.print("\n[dim]Type a command to continue debugging...[/dim]")
    
    def _interactive_loop(self) -> None:
        """Main interactive debugging loop."""
        while self.active_session:
            try:
                # Get user input with timeout
                command_input = TimeoutPrompt.ask(
                    f"[bold green]debug[{self.active_session.framework or 'unknown'}][/bold green]",
                    default="help",
                    automation_default="quit"
                )
                
                # Parse command
                parts = command_input.strip().split()
                if not parts:
                    continue
                
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                if command in self.commands:
                    try:
                        self.commands[command](args)
                    except Exception as e:
                        self.console.print(f"[red]❌ Command error: {e}[/red]")
                else:
                    self.console.print(f"[yellow]Unknown command: {command}. Type 'help' for available commands.[/yellow]")
                
            except KeyboardInterrupt:
                if TimeoutPrompt.confirm("\nExit debugging session?", default=True, automation_default=True):
                    break
            except EOFError:
                break
        
        self._end_session()
    
    def _cmd_step(self, args: List[str]) -> None:
        """Step through trace execution."""
        if not self.active_session:
            return
        
        self.console.print("[cyan]🔄 Stepping through trace...[/cyan]")
        
        # For static traces, this means moving through entries
        trace_data = self.active_session.trace_data
        
        if isinstance(trace_data, list):
            if self.active_session.current_step < len(trace_data):
                current_entry = trace_data[self.active_session.current_step]
                self.console.print(f"\n[bold]Step {self.active_session.current_step + 1}/{len(trace_data)}:[/bold]")
                
                # Display entry
                self._display_trace_entry(current_entry, self.active_session.current_step)
                
                self.active_session.current_step += 1
            else:
                self.console.print("[yellow]End of trace reached[/yellow]")
        else:
            self.console.print("[yellow]Single entry trace - use 'inspect' for detailed analysis[/yellow]")
    
    def _cmd_continue(self, args: List[str]) -> None:
        """Continue to next breakpoint or end."""
        self.console.print("[cyan]▶️  Continuing execution...[/cyan]")
        
        # For static analysis, this means processing all remaining entries
        if self.active_session and isinstance(self.active_session.trace_data, list):
            remaining = len(self.active_session.trace_data) - self.active_session.current_step
            self.console.print(f"[dim]Processed {remaining} remaining entries[/dim]")
            self.active_session.current_step = len(self.active_session.trace_data)
    
    def _cmd_break(self, args: List[str]) -> None:
        """Set breakpoints."""
        if not args:
            self.console.print("[yellow]Usage: break <step_number|tool_name>[/yellow]")
            return
        
        breakpoint = args[0]
        self.active_session.breakpoints.add(breakpoint)
        self.console.print(f"[green]✅ Breakpoint set: {breakpoint}[/green]")
    
    def _cmd_watch(self, args: List[str]) -> None:
        """Watch variables or expressions."""
        if not args:
            # Show current watch variables
            if self.active_session.watch_variables:
                watch_table = Table(title="Watch Variables", box=box.ROUNDED)
                watch_table.add_column("Variable", style="cyan")
                watch_table.add_column("Value", style="white")
                
                for var, value in self.active_session.watch_variables.items():
                    watch_table.add_row(var, str(value)[:50] + "..." if len(str(value)) > 50 else str(value))
                
                self.console.print(watch_table)
            else:
                self.console.print("[dim]No watch variables set[/dim]")
            return
        
        variable = args[0]
        # For static traces, extract relevant information
        value = self._extract_variable_value(variable)
        self.active_session.watch_variables[variable] = value
        self.console.print(f"[green]👁️  Watching: {variable} = {value}[/green]")
    
    def _cmd_inspect(self, args: List[str]) -> None:
        """Inspect specific elements."""
        if not args:
            self.console.print("[yellow]Usage: inspect <tool_name|step_number|'all'>[/yellow]")
            return
        
        target = args[0]
        
        if target == "all":
            self._inspect_full_trace()
        elif target.isdigit():
            self._inspect_step(int(target))
        else:
            self._inspect_tool(target)
    
    def _cmd_tools(self, args: List[str]) -> None:
        """Analyze tool calls in detail."""
        self.console.print("\n[bold cyan]🔧 Tool Call Analysis[/bold cyan]")
        
        tool_calls = self._extract_tool_calls()
        
        if not tool_calls:
            self.console.print("[yellow]No tool calls detected in trace[/yellow]")
            return
        
        tools_table = Table(title="Detected Tool Calls", box=box.ROUNDED)
        tools_table.add_column("Tool Name", style="cyan")
        tools_table.add_column("Framework", style="yellow")
        tools_table.add_column("Status", style="green")
        tools_table.add_column("Issues", style="red")
        
        for tool in tool_calls:
            # Check for issues with this tool
            issues = self._check_tool_issues(tool["name"])
            status = "⚠️  Issues" if issues else "✅ OK"
            issues_str = f"{len(issues)} issues" if issues else "None"
            
            tools_table.add_row(
                tool["name"],
                tool["framework"] or "Unknown",
                status,
                issues_str
            )
        
        self.console.print(tools_table)
        
        # Show detailed issues if any
        for tool in tool_calls:
            issues = self._check_tool_issues(tool["name"])
            if issues:
                self.console.print(f"\n[bold red]Issues with {tool['name']}:[/bold red]")
                for issue in issues:
                    self.console.print(f"  • {issue}")
    
    def _cmd_validate(self, args: List[str]) -> None:
        """Validate tool parameters and schemas."""
        self.console.print("\n[bold cyan]✅ Parameter Validation[/bold cyan]")
        
        validation_results = self._validate_tool_parameters(self._extract_tool_calls())
        
        if not validation_results:
            self.console.print("[green]✅ All tool parameters appear valid[/green]")
            return
        
        validation_table = Table(title="Validation Issues", box=box.ROUNDED)
        validation_table.add_column("Issue Type", style="yellow")
        validation_table.add_column("Description", style="white")
        validation_table.add_column("Severity", style="red")
        
        for result in validation_results:
            validation_table.add_row(
                result["issue_type"].replace("_", " ").title(),
                result["description"],
                result["severity"].title()
            )
        
        self.console.print(validation_table)
    
    def _cmd_fix(self, args: List[str]) -> None:
        """Get fix suggestions for detected issues."""
        self.console.print("\n[bold cyan]🔨 Fix Suggestions[/bold cyan]")
        
        # Collect all issues
        validation_results = self._validate_tool_parameters(self._extract_tool_calls())
        common_issues = self._check_common_issues()
        
        all_issues = validation_results + [{"issue_type": issue["type"], "description": issue["description"], "severity": issue["severity"]} for issue in common_issues]
        
        if not all_issues:
            self.console.print("[green]✅ No issues detected - no fixes needed![/green]")
            return
        
        # Generate fix suggestions
        fix_suggestions = self._generate_fix_suggestions(all_issues)
        
        fix_table = Table(title="Fix Suggestions", box=box.ROUNDED)
        fix_table.add_column("Issue", style="red", width=20)
        fix_table.add_column("Suggested Fix", style="green", width=40)
        fix_table.add_column("Priority", style="yellow", width=10)
        
        for suggestion in fix_suggestions:
            fix_table.add_row(
                suggestion["issue"],
                suggestion["fix"],
                suggestion["priority"]
            )
        
        self.console.print(fix_table)
        
        # Offer to export fixes
        if Confirm.ask("\nExport fix suggestions to file?"):
            self._export_fix_suggestions(fix_suggestions)
    
    def _cmd_summary(self, args: List[str]) -> None:
        """Show session summary."""
        if not self.active_session:
            return
        
        status = self.active_session.get_status()
        
        summary_text = Text()
        summary_text.append("Debug Session Summary\n\n", style="bold cyan")
        summary_text.append(f"Session: {status['session_id']}\n", style="white")
        summary_text.append(f"Duration: {status['duration']}\n", style="white")
        summary_text.append(f"Framework: {status['framework'].upper()}\n", style="yellow")
        summary_text.append(f"Current Step: {status['current_step']}\n", style="white")
        summary_text.append(f"Findings: {status['findings']}\n", style="green")
        summary_text.append(f"Breakpoints: {status['breakpoints']}\n", style="cyan")
        
        if self.active_session.findings:
            summary_text.append("\nKey Findings:\n", style="bold")
            for finding in self.active_session.findings[-5:]:  # Show last 5
                summary_text.append(f"• {finding}\n", style="dim")
        
        summary_panel = Panel(summary_text, title="Session Summary", border_style="cyan")
        self.console.print(summary_panel)
    
    def _cmd_help(self, args: List[str]) -> None:
        """Show all available commands."""
        self.console.print("\n[bold blue]🔧 Interactive Debug Commands[/bold blue]")
        
        help_table = Table(title="Available Commands", box=box.ROUNDED)
        help_table.add_column("Command", style="cyan", width=15)
        help_table.add_column("Usage", style="yellow", width=25)
        help_table.add_column("Description", style="white")
        
        commands_help = [
            ("step", "step", "Step through trace entries one by one"),
            ("continue", "continue", "Process all remaining entries"),
            ("break", "break <target>", "Set breakpoint at step or tool"),
            ("watch", "watch [variable]", "Watch variable or show watched"),
            ("inspect", "inspect <target>", "Inspect tool, step, or 'all'"),
            ("tools", "tools", "Analyze all tool calls in detail"),
            ("validate", "validate", "Validate tool parameters"),
            ("fix", "fix", "Get suggestions for fixing issues"),
            ("summary", "summary", "Show session summary"),
            ("help", "help", "Show this help message"),
            ("quit", "quit", "Exit debugging session")
        ]
        
        for cmd, usage, desc in commands_help:
            help_table.add_row(cmd, usage, desc)
        
        self.console.print(help_table)
    
    def _cmd_quit(self, args: List[str]) -> None:
        """Exit debugging session."""
        if Confirm.ask("Exit debugging session?"):
            self.active_session = None
    
    # Helper methods
    
    def _display_trace_entry(self, entry: Any, step_number: int) -> None:
        """Display a single trace entry."""
        # Format entry for display
        if isinstance(entry, dict):
            # Show key fields
            entry_table = Table(title=f"Entry {step_number + 1}", box=box.ROUNDED)
            entry_table.add_column("Field", style="cyan")
            entry_table.add_column("Value", style="white")
            
            # Show important fields first
            important_fields = ["output", "tool_call", "error", "status", "timestamp"]
            
            for field in important_fields:
                if field in entry:
                    value = str(entry[field])
                    if len(value) > 100:
                        value = value[:97] + "..."
                    entry_table.add_row(field, value)
            
            # Show other fields
            for key, value in entry.items():
                if key not in important_fields:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    entry_table.add_row(key, value_str)
            
            self.console.print(entry_table)
        else:
            self.console.print(f"[white]{str(entry)[:200]}...[/white]" if len(str(entry)) > 200 else str(entry))
    
    def _extract_variable_value(self, variable: str) -> Any:
        """Extract variable value from trace."""
        trace_str = json.dumps(self.active_session.trace_data) if not isinstance(self.active_session.trace_data, str) else self.active_session.trace_data
        
        # Simple extraction based on variable name
        if variable in trace_str:
            # Try to extract value after variable name
            pattern = f'"{variable}"\\s*:\\s*"([^"]*)"'
            match = re.search(pattern, trace_str)
            if match:
                return match.group(1)
        
        return f"Variable '{variable}' not found"
    
    def _inspect_full_trace(self) -> None:
        """Inspect the full trace."""
        self.console.print("\n[bold cyan]🔍 Full Trace Inspection[/bold cyan]")
        
        # Show trace statistics
        trace_data = self.active_session.trace_data
        
        if isinstance(trace_data, list):
            self.console.print(f"[white]Trace contains {len(trace_data)} entries[/white]")
            
            # Show tree structure
            tree = Tree("Trace Structure")
            for i, entry in enumerate(trace_data[:10]):  # Show first 10
                if isinstance(entry, dict):
                    entry_node = tree.add(f"Entry {i+1}")
                    for key in list(entry.keys())[:5]:  # Show first 5 keys
                        entry_node.add(f"{key}: {type(entry[key]).__name__}")
                else:
                    tree.add(f"Entry {i+1}: {type(entry).__name__}")
            
            if len(trace_data) > 10:
                tree.add(f"... and {len(trace_data) - 10} more entries")
            
            self.console.print(tree)
        else:
            self.console.print("[white]Single entry trace[/white]")
            # Show JSON structure
            if isinstance(trace_data, dict):
                syntax = Syntax(json.dumps(trace_data, indent=2)[:1000], "json", theme="monokai", line_numbers=True)
                self.console.print(syntax)
    
    def _inspect_step(self, step_number: int) -> None:
        """Inspect a specific step."""
        trace_data = self.active_session.trace_data
        
        if isinstance(trace_data, list):
            if 0 <= step_number - 1 < len(trace_data):
                entry = trace_data[step_number - 1]
                self.console.print(f"\n[bold cyan]🔍 Inspecting Step {step_number}[/bold cyan]")
                self._display_trace_entry(entry, step_number - 1)
            else:
                self.console.print(f"[red]Step {step_number} not found (trace has {len(trace_data)} entries)[/red]")
        else:
            self.console.print("[yellow]Single entry trace - use 'inspect all' instead[/yellow]")
    
    def _inspect_tool(self, tool_name: str) -> None:
        """Inspect a specific tool."""
        self.console.print(f"\n[bold cyan]🔧 Inspecting Tool: {tool_name}[/bold cyan]")
        
        # Search for tool usage in trace
        trace_str = str(self.active_session.trace_data).lower()
        tool_usage_count = trace_str.count(tool_name.lower())
        
        if tool_usage_count > 0:
            self.console.print(f"[green]Tool '{tool_name}' found {tool_usage_count} times in trace[/green]")
            
            # Show tool-specific issues
            issues = self._check_tool_issues(tool_name)
            if issues:
                self.console.print(f"\n[red]Issues with {tool_name}:[/red]")
                for issue in issues:
                    self.console.print(f"  • {issue}")
            else:
                self.console.print(f"[green]No issues detected with {tool_name}[/green]")
        else:
            self.console.print(f"[yellow]Tool '{tool_name}' not found in trace[/yellow]")
    
    def _check_tool_issues(self, tool_name: str) -> List[str]:
        """Check for issues with a specific tool."""
        issues = []
        trace_str = str(self.active_session.trace_data).lower()
        
        # Look for error patterns related to this tool
        tool_context = f"(?:.*{tool_name.lower()}.*)"
        error_patterns = [
            (f"{tool_context}.*error", "Error detected in tool execution"),
            (f"{tool_context}.*timeout", "Timeout detected for tool"),
            (f"{tool_context}.*failed", "Tool execution failed"),
            (f"{tool_context}.*invalid", "Invalid parameters detected")
        ]
        
        for pattern, description in error_patterns:
            if re.search(pattern, trace_str):
                issues.append(description)
        
        return issues
    
    def _generate_fix_suggestions(self, issues: List[Dict]) -> List[Dict[str, str]]:
        """Generate fix suggestions for detected issues."""
        suggestions = []
        
        fix_map = {
            "parameter_mismatch": {
                "fix": "Check tool parameter types and schemas. Ensure all required parameters are provided.",
                "priority": "High"
            },
            "schema_mismatch": {
                "fix": "Validate tool schemas. Update parameter formats to match expected schemas.",
                "priority": "High"
            },
            "timeout": {
                "fix": "Increase timeout values or optimize tool execution. Check network connectivity.",
                "priority": "Medium"
            },
            "authentication": {
                "fix": "Verify API keys and authentication credentials. Check permission levels.",
                "priority": "High"
            },
            "rate_limit": {
                "fix": "Implement rate limiting and retry logic. Consider upgrading API plan.",
                "priority": "Medium"
            },
            "network": {
                "fix": "Check network connectivity and DNS resolution. Implement retry mechanisms.",
                "priority": "Medium"
            },
            "parsing": {
                "fix": "Validate JSON format and data structure. Check for encoding issues.",
                "priority": "Medium"
            },
            "memory": {
                "fix": "Optimize memory usage. Process data in smaller chunks or increase available memory.",
                "priority": "High"
            }
        }
        
        for issue in issues:
            issue_type = issue["issue_type"]
            if issue_type in fix_map:
                suggestions.append({
                    "issue": issue_type.replace("_", " ").title(),
                    "fix": fix_map[issue_type]["fix"],
                    "priority": fix_map[issue_type]["priority"]
                })
        
        return suggestions
    
    def _export_fix_suggestions(self, suggestions: List[Dict]) -> None:
        """Export fix suggestions to file."""
        output_dir = Path("debug_fixes")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"fix_suggestions_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Debug Fix Suggestions\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Session: {self.active_session.session_id}\n\n")
            
            for suggestion in suggestions:
                f.write(f"## {suggestion['issue']} (Priority: {suggestion['priority']})\n\n")
                f.write(f"{suggestion['fix']}\n\n")
        
        self.console.print(f"[green]✅ Fix suggestions exported to: {filename}[/green]")
    
    def _end_session(self) -> None:
        """End the debugging session."""
        if self.active_session:
            duration = datetime.now() - self.active_session.start_time
            self.console.print(f"\n[bold green]🏁 Debug Session Complete[/bold green]")
            self.console.print(f"[green]Session Duration: {str(duration).split('.')[0]}[/green]")
            self.console.print(f"[green]Findings: {len(self.active_session.findings)}[/green]")
            
            # Offer to save session log
            if Confirm.ask("Save session log?"):
                self._save_session_log()
            
            self.active_session = None
    
    def _save_session_log(self) -> None:
        """Save session log to file."""
        if not self.active_session:
            return
        
        output_dir = Path("debug_sessions")
        output_dir.mkdir(exist_ok=True)
        
        log_file = output_dir / f"{self.active_session.session_id}.json"
        
        session_data = {
            "session_id": self.active_session.session_id,
            "start_time": self.active_session.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "framework": self.active_session.framework,
            "findings": self.active_session.findings,
            "execution_log": self.active_session.execution_log,
            "breakpoints": list(self.active_session.breakpoints),
            "watch_variables": self.active_session.watch_variables
        }
        
        with open(log_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.console.print(f"[green]✅ Session log saved: {log_file}[/green]")
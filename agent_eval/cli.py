#!/usr/bin/env python3
"""
AgentEval CLI - Main command-line interface.

Provides domain-specific evaluation and compliance reporting for LLMs and AI agents.
"""

import sys
import json
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import EvaluationResult
from agent_eval.exporters.pdf import PDFExporter
from agent_eval.exporters.csv import CSVExporter


console = Console()


@click.command()
@click.option(
    "--domain",
    type=click.Choice(["finance", "security", "ml"]),
    default="finance",
    help="Select evaluation domain pack",
)
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="Input file containing agent/LLM outputs (JSON format)",
)
@click.option(
    "--stdin",
    is_flag=True,
    help="Read input from stdin (pipe) instead of file",
)
@click.option(
    "--endpoint",
    type=str,
    help="API endpoint to fetch agent outputs from (alternative to --input)",
)
@click.option(
    "--export",
    type=click.Choice(["pdf", "csv", "json"]),
    help="Export audit report in specified format",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format for CLI results",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Enable developer mode with verbose output",
)
@click.option(
    "--workflow",
    is_flag=True,
    help="Enable workflow/audit mode for compliance reporting",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Custom evaluation configuration file",
)
@click.option(
    "--help-input",
    is_flag=True,
    help="Show detailed input format documentation and examples",
)
@click.option(
    "--timing",
    is_flag=True,
    help="Show execution time and performance metrics",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging with detailed debugging information",
)
@click.version_option(version="0.1.0", prog_name="arc-eval")
def main(
    domain: str,
    input_file: Optional[Path],
    stdin: bool,
    endpoint: Optional[str],
    export: Optional[str],
    output: str,
    dev: bool,
    workflow: bool,
    config: Optional[Path],
    help_input: bool,
    timing: bool,
    verbose: bool,
) -> None:
    """
    AgentEval: Domain-specific evaluation and compliance reporting for LLMs and AI agents.
    
    Evaluate your AI agents for safety, reliability, and compliance with one command.
    Get actionable insights and audit-ready reports in seconds.
    
    Examples:
    
      # Evaluate finance compliance on agent outputs
      arc-eval --domain finance --input outputs.json
      
      # Generate audit report
      arc-eval --domain finance --input outputs.json --export pdf
      
      # Developer mode with verbose output  
      arc-eval --domain security --input logs.json --dev
      
      # Workflow mode for compliance teams
      arc-eval --domain finance --input outputs.json --workflow --export pdf
    """
    
    # Handle help-input flag
    if help_input:
        from agent_eval.core.validators import InputValidator
        console.print("[bold blue]AgentEval Input Format Documentation[/bold blue]")
        console.print(InputValidator.suggest_format_help())
        return
    
    # Import validation utilities
    from agent_eval.core.validators import (
        InputValidator, CLIValidator, ValidationError, format_validation_error
    )
    
    # Validate CLI arguments
    try:
        CLIValidator.validate_domain(domain)
        if export:
            CLIValidator.validate_export_format(export)
        CLIValidator.validate_output_format(output)
        if input_file:
            CLIValidator.validate_file_path(input_file)
    except ValidationError as e:
        console.print(format_validation_error(e))
        sys.exit(1)
    
    # Validate input sources
    input_sources = sum([bool(input_file), bool(stdin), bool(endpoint)])
    
    if input_sources == 0:
        # Check if stdin has data (for auto-detection)
        if not sys.stdin.isatty():
            stdin = True
        else:
            console.print(
                "[red]Error:[/red] Must specify input source: --input file, --stdin, or --endpoint URL",
                style="bold"
            )
            console.print("\nTry 'arc-eval --help' for usage information.")
            console.print("For piped input: echo '{\"output\": \"text\"}' | arc-eval --domain finance")
            sys.exit(1)
    
    if input_sources > 1:
        console.print(
            "[yellow]Warning:[/yellow] Multiple input sources specified. Priority: --input > --stdin > --endpoint",
            style="bold"
        )
    
    try:
        # Initialize evaluation engine
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Initializing ARC-Eval for domain: {domain}")
            if config:
                console.print(f"[cyan]Verbose:[/cyan] Using custom config: {config}")
            console.print(f"[cyan]Verbose:[/cyan] CLI Options - Export: {export}, Output: {output}, Dev: {dev}, Workflow: {workflow}")
        
        engine = EvaluationEngine(domain=domain, config=config)
        
        if dev:
            console.print(f"[blue]Debug:[/blue] Initializing evaluation engine for domain: {domain}")
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Engine initialized successfully")
        
        # Load input data based on priority: file > stdin > endpoint
        if verbose:
            input_sources = []
            if input_file: input_sources.append("file")
            if stdin: input_sources.append("stdin")
            if endpoint: input_sources.append("endpoint")
            console.print(f"[cyan]Verbose:[/cyan] Input sources detected: {', '.join(input_sources)}")
        
        if input_file:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Processing input file: {input_file}")
            try:
                with open(input_file, 'r') as f:
                    raw_data = f.read()
                agent_outputs, warnings = InputValidator.validate_json_input(raw_data, str(input_file))
                
                # Display warnings if any
                for warning in warnings:
                    console.print(f"[yellow]Warning:[/yellow] {warning}")
                
                if dev:
                    console.print(f"[blue]Debug:[/blue] Loaded {len(agent_outputs) if isinstance(agent_outputs, list) else 1} outputs from {input_file}")
            except ValidationError as e:
                console.print(format_validation_error(e))
                sys.exit(1)
            except FileNotFoundError:
                console.print(f"[red]Error:[/red] File not found: {input_file}")
                sys.exit(1)
                
        elif stdin:
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("[red]Error:[/red] No data received from stdin")
                    console.print("Expected: echo '{\"output\": \"agent response\"}' | arc-eval --domain finance")
                    sys.exit(1)
                
                agent_outputs, warnings = InputValidator.validate_json_input(stdin_data, "stdin")
                
                # Display warnings if any
                for warning in warnings:
                    console.print(f"[yellow]Warning:[/yellow] {warning}")
                
                if dev:
                    console.print(f"[blue]Debug:[/blue] Loaded {len(agent_outputs) if isinstance(agent_outputs, list) else 1} outputs from stdin")
            except ValidationError as e:
                console.print(format_validation_error(e))
                sys.exit(1)
        else:
            # TODO: Implement endpoint fetching
            console.print("[red]Error:[/red] Endpoint fetching not yet implemented")
            console.print("Use --input file or --stdin for now")
            sys.exit(1)
        
        # Run evaluations
        start_time = time.time()
        input_size = len(json.dumps(agent_outputs)) if isinstance(agent_outputs, (list, dict)) else len(str(agent_outputs))
        
        if verbose:
            output_count = len(agent_outputs) if isinstance(agent_outputs, list) else 1
            console.print(f"[cyan]Verbose:[/cyan] Starting evaluation of {output_count} outputs against {domain} domain scenarios")
            console.print(f"[cyan]Verbose:[/cyan] Input data size: {input_size} bytes")
        
        with console.status("[bold green]Running evaluations...", spinner="dots"):
            results = engine.evaluate(agent_outputs)
            
        evaluation_time = time.time() - start_time
        
        if verbose:
            passed = sum(1 for r in results if r.passed)
            failed = len(results) - passed
            console.print(f"[cyan]Verbose:[/cyan] Evaluation completed: {passed} passed, {failed} failed in {evaluation_time:.2f}s")
        
        # Display results
        _display_results(results, output_format=output, dev_mode=dev, workflow_mode=workflow, domain=domain)
        
        # Show timing information if requested
        if timing:
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Exporting results in {export} format")
            _export_results(results, export_format=export, domain=domain)
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Export completed successfully")
        
        # Set exit code based on critical failures
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Exit code determination: {critical_failures} critical failures detected")
        if critical_failures > 0:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Exiting with code 1 due to critical failures")
            sys.exit(1)
        elif verbose:
            console.print(f"[cyan]Verbose:[/cyan] Exiting with code 0 - no critical failures")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        if dev:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _display_results(
    results: list[EvaluationResult], 
    output_format: str, 
    dev_mode: bool, 
    workflow_mode: bool,
    domain: str = "finance"
) -> None:
    """Display evaluation results in the specified format."""
    
    if output_format == "json":
        click.echo(json.dumps([r.to_dict() for r in results], indent=2))
        return
    
    if output_format == "csv":
        # Simple CSV output for scripting
        click.echo("scenario,status,severity,compliance,description")
        for result in results:
            click.echo(f"{result.scenario_name},{result.status},{result.severity},{';'.join(result.compliance)},{result.description}")
        return
    
    # Table output (default)
    _display_table_results(results, dev_mode, workflow_mode, domain)


def _display_table_results(results: list[EvaluationResult], dev_mode: bool, workflow_mode: bool, domain: str = "finance") -> None:
    """Display results in a rich table format."""
    
    # Summary statistics
    total_scenarios = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
    high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
    medium_failures = sum(1 for r in results if r.severity == "medium" and not r.passed)
    
    # Dynamic header based on domain
    domain_names = {
        "finance": "Financial Services Compliance",
        "security": "Cybersecurity & AI Agent Security", 
        "ml": "ML Infrastructure & Safety"
    }
    domain_title = domain_names.get(domain, "Compliance")
    
    # Summary header
    console.print(f"\n[bold]AgentEval {domain_title} Results[/bold]", style="blue")
    console.print("=" * 60)
    
    if critical_failures > 0:
        console.print(f"❌ {critical_failures} Critical Failures", style="bold red")
    if high_failures > 0:
        console.print(f"⚠️  {high_failures} High Warnings", style="bold yellow")
    if medium_failures > 0:
        console.print(f"🔶 {medium_failures} Medium Issues", style="bold blue")
    if passed > 0:
        console.print(f"✅ {passed} Passes", style="bold green")
    
    console.print(f"\nTotal scenarios evaluated: {total_scenarios}")
    
    # Show compliance framework summary
    compliance_frameworks = set()
    failed_frameworks = set()
    for result in results:
        compliance_frameworks.update(result.compliance)
        if not result.passed:
            failed_frameworks.update(result.compliance)
    
    if failed_frameworks:
        console.print(f"📋 Regulatory frameworks with issues: {', '.join(sorted(failed_frameworks))}", style="yellow")
    
    # Detailed results table
    if failed > 0 or dev_mode:
        console.print("\n[bold]Detailed Results[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Status", style="bold")
        table.add_column("Severity")
        table.add_column("Scenario")
        table.add_column("Compliance")
        if dev_mode:
            table.add_column("Details")
        
        for result in results:
            status_icon = "✅" if result.passed else "❌"
            status_style = "green" if result.passed else "red"
            
            severity_style = {
                "critical": "red",
                "high": "yellow", 
                "medium": "blue",
                "low": "dim"
            }.get(result.severity, "")
            
            compliance_str = ", ".join(result.compliance)
            
            row = [
                f"[{status_style}]{status_icon} {result.status}[/{status_style}]",
                f"[{severity_style}]{result.severity.upper()}[/{severity_style}]",
                result.scenario_name,
                compliance_str,
            ]
            
            if dev_mode:
                row.append(result.failure_reason or "N/A")
            
            table.add_row(*row)
        
        console.print(table)
    
    # Recommendations
    failed_results = [r for r in results if not r.passed]
    if failed_results:
        console.print("\n[bold]Recommendations[/bold]", style="blue")
        for i, result in enumerate(failed_results[:5], 1):  # Show top 5
            if result.remediation:
                console.print(f"{i}. {result.remediation}")
        
        if len(failed_results) > 5:
            console.print(f"... and {len(failed_results) - 5} more recommendations")
    
    # Risk assessment for workflow mode
    if workflow_mode and critical_failures > 0:
        console.print("\n[bold red]Risk Assessment[/bold red]")
        console.print("🔴 Critical compliance violations detected")
        
        compliance_frameworks = set()
        for result in failed_results:
            compliance_frameworks.update(result.compliance)
        
        if compliance_frameworks:
            console.print(f"📋 Regulatory frameworks affected: {', '.join(sorted(compliance_frameworks))}")
        console.print("⚡ Immediate remediation required")


def _export_results(results: list[EvaluationResult], export_format: str, domain: str) -> None:
    """Export results to the specified format."""
    
    timestamp = Path().cwd().name + "_" + "2024-01-15_14-30"  # TODO: Use actual timestamp
    
    if export_format == "pdf":
        exporter = PDFExporter()
        filename = f"agent_eval_{domain}_{timestamp}.pdf"
        exporter.export(results, filename, domain)
        console.print(f"\n📄 Audit Report: [bold]{filename}[/bold]")
    
    elif export_format == "csv":
        exporter = CSVExporter()
        filename = f"agent_eval_{domain}_{timestamp}.csv"
        exporter.export(results, filename, domain)
        console.print(f"\n📊 Data Export: [bold]{filename}[/bold]")
    
    elif export_format == "json":
        filename = f"agent_eval_{domain}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        console.print(f"\n📋 JSON Export: [bold]{filename}[/bold]")


def _display_timing_metrics(evaluation_time: float, input_size: int, result_count: int) -> None:
    """Display timing and performance metrics."""
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]Performance Metrics[/bold cyan]")
    console.print("=" * 50)
    
    # Evaluation timing
    console.print(f"⏱️  Evaluation Time: [bold]{evaluation_time:.2f}s[/bold]")
    
    # Input size metrics
    if input_size < 1024:
        size_str = f"{input_size} bytes"
    elif input_size < 1024 * 1024:
        size_str = f"{input_size / 1024:.1f} KB"
    else:
        size_str = f"{input_size / (1024 * 1024):.1f} MB"
    
    console.print(f"📊 Input Size: [bold]{size_str}[/bold]")
    
    # Processing speed
    if evaluation_time > 0:
        scenarios_per_sec = result_count / evaluation_time
        console.print(f"🚀 Processing Speed: [bold]{scenarios_per_sec:.1f} scenarios/second[/bold]")
    
    # Memory warnings for large files
    if input_size > 10 * 1024 * 1024:  # 10MB
        console.print("[yellow]⚠️  Large input detected (>10MB). Consider processing in smaller batches.[/yellow]")
    
    if evaluation_time > 30:  # 30 seconds
        console.print("[yellow]⚠️  Long evaluation time (>30s). Consider optimizing input data.[/yellow]")


if __name__ == "__main__":
    main()
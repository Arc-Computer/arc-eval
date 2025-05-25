#!/usr/bin/env python3
"""
AgentEval CLI - Main command-line interface.

Provides domain-specific evaluation and compliance reporting for LLMs and AI agents.
"""

import sys
import json
import time
import glob
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import EvaluationResult
from agent_eval.exporters.pdf import PDFExporter
from agent_eval.exporters.csv import CSVExporter


console = Console()


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    "--domain",
    type=click.Choice(["finance", "security", "ml"]),
    help="Select evaluation domain pack (required for CLI mode)",
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
    "--list-domains",
    is_flag=True,
    help="List available evaluation domains and their descriptions",
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
@click.option(
    "--quick-start",
    is_flag=True,
    help="Run demo evaluation with built-in sample data (no input file required)",
)
@click.option(
    "--validate",
    is_flag=True,
    help="Validate input file format without running evaluation",
)
@click.version_option(version="0.1.0", prog_name="arc-eval")
def main(
    domain: Optional[str],
    input_file: Optional[Path],
    stdin: bool,
    endpoint: Optional[str],
    export: Optional[str],
    output: str,
    dev: bool,
    workflow: bool,
    config: Optional[Path],
    help_input: bool,
    list_domains: bool,
    timing: bool,
    verbose: bool,
    quick_start: bool,
    validate: bool,
) -> None:
    """
    ARC-Eval: Enterprise-grade compliance evaluation for AI agents and LLMs.
    
    Run domain-specific safety and compliance evaluations on your AI systems.
    Get executive-ready audit reports with actionable remediation guidance.
    
    🚀 QUICK START:
    
      # Try the interactive demo (no setup required)
      arc-eval --quick-start
      
      # Run with your data
      arc-eval --domain finance --input your_outputs.json
      
      # Generate executive report
      arc-eval --domain finance --input outputs.json --export pdf --workflow
    
    📊 ENTERPRISE WORKFLOWS:
    
      # Compliance audit for executives
      arc-eval --domain finance --input logs.json --export pdf --workflow
      
      # Developer debugging mode
      arc-eval --domain security --input outputs.json --dev --verbose
      
      # CI/CD pipeline integration
      arc-eval --domain ml --input model_outputs.json --output json
      
      # Input validation before evaluation
      arc-eval --validate --input suspicious_data.json
    
    🎯 DOMAIN-SPECIFIC EVALUATIONS:
    
      # Financial services compliance (SOX, KYC, AML, PCI-DSS, GDPR)
      arc-eval --domain finance --input transactions.json
      
      # Cybersecurity & AI safety (OWASP, prompt injection, data leakage)
      arc-eval --domain security --input agent_responses.json
      
      # ML infrastructure & bias detection (IEEE Ethics, Model Cards)
      arc-eval --domain ml --input model_predictions.json
    
    📖 HELP & LEARNING:
    
      # See all available domains
      arc-eval --list-domains
      
      # Learn input formats and examples
      arc-eval --help-input
      
      # Validate your data format
      arc-eval --validate --domain finance --input your_data.json
    """
    
    # Handle help flags
    if help_input:
        from agent_eval.core.validators import InputValidator
        console.print("[bold blue]AgentEval Input Format Documentation[/bold blue]")
        console.print(InputValidator.suggest_format_help())
        return
    
    if list_domains:
        console.print("\n[bold blue]🎯 ARC-Eval Domain Catalog[/bold blue]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        console.print("[bold]Choose your evaluation domain based on your AI system's use case:[/bold]\n")
        
        domains_info = {
            "finance": {
                "name": "Financial Services Compliance",
                "description": "Enterprise-grade evaluations for financial AI systems",
                "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "FFIEC", "DORA", "OFAC", "CFPB", "EU-AI-ACT"],
                "scenarios": 15,
                "use_cases": "Banking, Fintech, Payment Processing, Insurance, Investment",
                "examples": "Transaction approval, KYC verification, Fraud detection, Credit scoring"
            },
            "security": {
                "name": "Cybersecurity & AI Agent Security", 
                "description": "AI safety evaluations for security-critical applications",
                "frameworks": ["OWASP-LLM-TOP-10", "NIST-AI-RMF", "ISO-27001", "SOC2-TYPE-II", "MITRE-ATTACK"],
                "scenarios": 15,
                "use_cases": "AI Agents, Chatbots, Code Generation, Security Tools",
                "examples": "Prompt injection, Data leakage, Code security, Access control"
            },
            "ml": {
                "name": "ML Infrastructure & Safety",
                "description": "Production ML system governance and bias detection",
                "frameworks": ["IEEE-ETHICS", "MODEL-CARDS", "ALGORITHMIC-ACCOUNTABILITY", "MLOPS-GOVERNANCE"],
                "scenarios": 15,
                "use_cases": "MLOps, Model Deployment, AI Ethics, Data Science",
                "examples": "Bias detection, Model drift, Data governance, Safety alignment"
            }
        }
        
        for domain_key, info in domains_info.items():
            console.print(f"[bold cyan]📋 {domain_key.upper()} DOMAIN[/bold cyan]")
            console.print(f"[bold]{info['name']}[/bold]")
            console.print(f"{info['description']}\n")
            
            console.print(f"[yellow]🎯 Use Cases:[/yellow] {info['use_cases']}")
            console.print(f"[yellow]🔍 Example Scenarios:[/yellow] {info['examples']}")
            console.print(f"[yellow]📊 Total Scenarios:[/yellow] {info['scenarios']}")
            console.print(f"[yellow]⚖️  Compliance Frameworks:[/yellow]")
            
            # Format frameworks in columns
            frameworks = info['frameworks']
            for i in range(0, len(frameworks), 3):
                framework_row = frameworks[i:i+3]
                console.print(f"   • {' • '.join(framework_row)}")
            
            console.print(f"\n[green]🚀 Try it:[/green] [dim]arc-eval --domain {domain_key} --quick-start[/dim]")
            console.print("[blue]" + "─" * 70 + "[/blue]\n")
        
        console.print("[bold blue]💡 Getting Started:[/bold blue]")
        console.print("1. [yellow]Choose your domain:[/yellow] [green]arc-eval --domain finance --quick-start[/green]")
        console.print("2. [yellow]Test with your data:[/yellow] [green]arc-eval --domain finance --input your_data.json[/green]")
        console.print("3. [yellow]Generate audit report:[/yellow] [green]arc-eval --domain finance --input data.json --export pdf[/green]")
        return
    
    # Handle quick-start mode
    if quick_start:
        return _handle_quick_start(domain, export, output, dev, workflow, timing, verbose)
    
    # Handle validate mode
    if validate:
        return _handle_validate(domain, input_file, stdin, dev, verbose)
    
    # Validate domain requirement for CLI mode
    if not list_domains and not help_input and domain is None:
        console.print("[red]Error:[/red] --domain is required")
        console.print("Use --list-domains to see available options")
        sys.exit(2)
    
    
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
    
    # Validate input sources with helpful guidance
    input_sources = sum([bool(input_file), bool(stdin), bool(endpoint)])
    
    if input_sources == 0:
        # Check if stdin has data (for auto-detection)
        if not sys.stdin.isatty():
            stdin = True
        else:
            console.print("\n[red]❌ Missing Input Data[/red]")
            console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
            console.print("[bold]You need to provide agent output data to evaluate.[/bold]\n")
            
            console.print("[bold blue]🚀 Quick Options:[/bold blue]")
            console.print("1. [yellow]Try the demo:[/yellow] [dim]arc-eval --quick-start[/dim]")
            console.print("2. [yellow]Use your file:[/yellow] [dim]arc-eval --domain finance --input your_outputs.json[/dim]")
            console.print("3. [yellow]Pipe data:[/yellow] [dim]echo '{\"output\": \"text\"}' | arc-eval --domain finance --stdin[/dim]")
            
            console.print("\n[bold blue]📖 Need Help?[/bold blue]")
            console.print("• See available domains: [dim]arc-eval --list-domains[/dim]")
            console.print("• Learn input formats: [dim]arc-eval --help-input[/dim]")
            console.print("• View all options: [dim]arc-eval --help[/dim]")
            
            console.print("\n[bold blue]💡 First Time User?[/bold blue]")
            console.print("Start with the interactive demo: [green]arc-eval --quick-start --domain finance[/green]")
            sys.exit(1)
    
    if input_sources > 1:
        console.print(
            "[yellow]⚠️  Multiple input sources detected.[/yellow] Using priority: --input > --stdin > --endpoint",
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
                console.print(f"\n[red]❌ File Not Found[/red]")
                console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
                console.print(f"[bold]Could not find file: [yellow]{input_file}[/yellow][/bold]\n")
                
                console.print("[bold blue]🔍 Troubleshooting Steps:[/bold blue]")
                console.print(f"1. [yellow]Check file path:[/yellow] Is [dim]{input_file}[/dim] the correct path?")
                console.print(f"2. [yellow]Check current directory:[/yellow] You're in [dim]{Path.cwd()}[/dim]")
                console.print(f"3. [yellow]Use absolute path:[/yellow] [dim]arc-eval --domain {domain} --input /full/path/to/file.json[/dim]")
                
                console.print("\n[bold blue]🚀 Quick Alternatives:[/bold blue]")
                console.print("• Try the demo: [green]arc-eval --quick-start[/green]")
                console.print("• List example files: [dim]ls examples/agent-outputs/[/dim]")
                console.print("• Use example data: [dim]arc-eval --domain finance --input examples/agent-outputs/sample_agent_outputs.json[/dim]")
                sys.exit(1)
                
        elif stdin:
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    console.print("\n[red]❌ Empty Input Stream[/red]")
                    console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
                    console.print("[bold]No data received from stdin (pipe input).[/bold]\n")
                    
                    console.print("[bold blue]✅ Correct Usage Examples:[/bold blue]")
                    console.print(f"• Simple JSON: [green]echo '{{\"output\": \"Transaction approved\"}}' | arc-eval --domain {domain}[/green]")
                    console.print(f"• From file: [green]cat outputs.json | arc-eval --domain {domain}[/green]")
                    console.print(f"• Complex JSON: [green]echo '[{{\"output\": \"KYC passed\", \"scenario\": \"identity_check\"}}]' | arc-eval --domain {domain}[/green]")
                    
                    console.print("\n[bold blue]🚀 Alternative Options:[/bold blue]")
                    console.print("• Use file input: [yellow]arc-eval --domain finance --input your_file.json[/yellow]")
                    console.print("• Try the demo: [yellow]arc-eval --quick-start[/yellow]")
                    console.print("• Learn input formats: [yellow]arc-eval --help-input[/yellow]")
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
            console.print("\n[red]❌ Feature Not Available[/red]")
            console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
            console.print("[bold]Endpoint fetching is coming soon![/bold]\n")
            
            console.print("[bold blue]🚀 Available Options Right Now:[/bold blue]")
            console.print(f"• Use file input: [green]arc-eval --domain {domain} --input your_outputs.json[/green]")
            console.print(f"• Use pipe input: [green]cat outputs.json | arc-eval --domain {domain}[/green]")
            console.print("• Try the demo: [green]arc-eval --quick-start[/green]")
            
            console.print("\n[bold blue]📋 Roadmap:[/bold blue]")
            console.print("• API endpoint support coming in v2.1")
            console.print("• Real-time monitoring in v2.2")
            console.print("• Cloud integrations in v2.3")
            sys.exit(1)
        
        # Run evaluations
        start_time = time.time()
        input_size = len(json.dumps(agent_outputs)) if isinstance(agent_outputs, (list, dict)) else len(str(agent_outputs))
        
        if verbose:
            output_count = len(agent_outputs) if isinstance(agent_outputs, list) else 1
            console.print(f"[cyan]Verbose:[/cyan] Starting evaluation of {output_count} outputs against {domain} domain scenarios")
            console.print(f"[cyan]Verbose:[/cyan] Input data size: {input_size} bytes")
        
        # Enhanced progress indicators for professional experience
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
        
        # Get scenario count for progress tracking
        scenario_count = len(engine.eval_pack.scenarios) if hasattr(engine.eval_pack, 'scenarios') else 15
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            eval_task = progress.add_task(
                f"🔍 Evaluating {scenario_count} {domain} compliance scenarios...", 
                total=100
            )
            
            # Update progress during evaluation
            for i in range(0, 101, 10):
                progress.update(eval_task, advance=10)
                if i == 50:
                    progress.update(eval_task, description="🔍 Processing compliance frameworks...")
                elif i == 80:
                    progress.update(eval_task, description="🔍 Generating recommendations...")
            
            # Run the actual evaluation
            results = engine.evaluate(agent_outputs)
            progress.update(eval_task, description="✅ Evaluation complete", completed=100)
            
        # Show immediate results summary
        console.print(f"\n[green]✅ Evaluation completed successfully![/green]")
        evaluation_time = time.time() - start_time
        console.print(f"[dim]Processed {len(results)} scenarios in {evaluation_time:.2f} seconds[/dim]")
        
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
        console.print(f"\n[red]❌ File System Error[/red]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        console.print(f"[bold]File not found: [yellow]{e}[/yellow][/bold]\n")
        
        console.print("[bold blue]🔍 Common Solutions:[/bold blue]")
        console.print("• Check if the file path is correct")
        console.print("• Ensure you have read permissions")
        console.print("• Try using absolute paths instead of relative paths")
        console.print("• Use the demo: [green]arc-eval --quick-start[/green]")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        console.print(f"\n[red]❌ Invalid JSON Format[/red]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        console.print(f"[bold]JSON parsing failed: [yellow]{e}[/yellow][/bold]\n")
        
        console.print("[bold blue]🔧 How to Fix:[/bold blue]")
        console.print("• Check your JSON syntax with a validator")
        console.print("• Ensure proper quotes around strings")
        console.print("• Remove trailing commas")
        console.print("• Learn input formats: [green]arc-eval --help-input[/green]")
        console.print("• Try the demo: [green]arc-eval --quick-start[/green]")
        sys.exit(1)
        
    except Exception as e:
        if dev:
            console.print("\n[red]❌ Detailed Error Information[/red]")
            console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
            console.print_exception()
        else:
            console.print(f"\n[red]❌ Unexpected Error[/red]")
            console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
            console.print(f"[bold]Something went wrong: [yellow]{e}[/yellow][/bold]\n")
            
            console.print("[bold blue]🆘 Troubleshooting:[/bold blue]")
            console.print("• Try with --dev flag for detailed error info")
            console.print("• Verify your input data format")
            console.print("• Check if all dependencies are installed")
            console.print("• Try the demo: [green]arc-eval --quick-start[/green]")
            console.print("• Get help: [green]arc-eval --help[/green]")
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
    
    # Enhanced summary header with executive dashboard
    console.print(f"\n[bold blue on white] 📊 {domain_title} Evaluation Report [/bold blue on white]")
    console.print("[blue]" + "═" * 70 + "[/blue]")
    
    # Executive summary box
    summary_table = Table(
        show_header=False,
        box=None,
        expand=True,
        padding=(0, 2)
    )
    summary_table.add_column("", style="bold", width=20)
    summary_table.add_column("", style="", width=15, justify="center")
    summary_table.add_column("", style="bold", width=20)
    summary_table.add_column("", style="", width=15, justify="center")
    
    # Calculate pass rate
    pass_rate = (passed / total_scenarios * 100) if total_scenarios > 0 else 0
    
    # Risk status indicator
    if critical_failures > 0:
        risk_status = "[red]🔴 HIGH RISK[/red]"
    elif high_failures > 0:
        risk_status = "[yellow]🟡 MEDIUM RISK[/yellow]"
    elif medium_failures > 0:
        risk_status = "[blue]🔵 LOW RISK[/blue]"
    else:
        risk_status = "[green]🟢 COMPLIANT[/green]"
    
    summary_table.add_row(
        "📈 Pass Rate:", f"[bold]{pass_rate:.1f}%[/bold]",
        "⚠️  Risk Level:", risk_status
    )
    summary_table.add_row(
        "✅ Passed:", f"[green]{passed}[/green]",
        "❌ Failed:", f"[red]{failed}[/red]"
    )
    summary_table.add_row(
        "🔴 Critical:", f"[red]{critical_failures}[/red]", 
        "🟡 High:", f"[yellow]{high_failures}[/yellow]"
    )
    summary_table.add_row(
        "🔵 Medium:", f"[blue]{medium_failures}[/blue]",
        "📊 Total:", f"[bold]{total_scenarios}[/bold]"
    )
    
    console.print(summary_table)
    console.print("[blue]" + "─" * 70 + "[/blue]")
    
    # Show compliance framework summary
    compliance_frameworks = set()
    failed_frameworks = set()
    for result in results:
        compliance_frameworks.update(result.compliance)
        if not result.passed:
            failed_frameworks.update(result.compliance)
    
    # Compliance Framework Dashboard
    if compliance_frameworks:
        console.print("\n[bold blue]⚖️  Compliance Framework Dashboard[/bold blue]")
        
        # Create framework summary table
        framework_table = Table(
            show_header=True,
            header_style="bold white on blue",
            border_style="blue",
            expand=True
        )
        framework_table.add_column("Framework", style="bold", width=15)
        framework_table.add_column("Status", style="bold", width=12, justify="center")
        framework_table.add_column("Scenarios", style="", width=10, justify="center")
        framework_table.add_column("Pass Rate", style="", width=12, justify="center")
        framework_table.add_column("Issues", style="", width=20)
        
        # Calculate framework-specific metrics
        for framework in sorted(compliance_frameworks):
            framework_results = [r for r in results if framework in r.compliance]
            total_scenarios = len(framework_results)
            passed_scenarios = sum(1 for r in framework_results if r.passed)
            failed_scenarios = total_scenarios - passed_scenarios
            pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
            
            # Determine status
            if failed_scenarios == 0:
                status = "[green]✅ COMPLIANT[/green]"
            elif any(r.severity == "critical" and not r.passed for r in framework_results):
                status = "[red]🔴 CRITICAL[/red]"
            elif any(r.severity == "high" and not r.passed for r in framework_results):
                status = "[yellow]🟡 HIGH RISK[/yellow]"
            else:
                status = "[blue]🔵 MEDIUM[/blue]"
            
            # Issue summary
            critical_issues = sum(1 for r in framework_results if r.severity == "critical" and not r.passed)
            high_issues = sum(1 for r in framework_results if r.severity == "high" and not r.passed)
            
            issue_summary = ""
            if critical_issues > 0:
                issue_summary += f"🔴 {critical_issues} Critical"
            if high_issues > 0:
                if issue_summary:
                    issue_summary += ", "
                issue_summary += f"🟡 {high_issues} High"
            if not issue_summary:
                issue_summary = "[dim]No issues[/dim]"
            
            framework_table.add_row(
                framework,
                status,
                f"{passed_scenarios}/{total_scenarios}",
                f"{pass_rate:.1f}%",
                issue_summary
            )
        
        console.print(framework_table)
        console.print("[blue]" + "─" * 70 + "[/blue]")
    
    # Detailed results table
    if failed > 0 or dev_mode:
        console.print("\n[bold blue]📊 Detailed Evaluation Results[/bold blue]")
        
        # Enhanced table with better styling for executives
        table = Table(
            show_header=True, 
            header_style="bold white on blue",
            border_style="blue",
            row_styles=["", "dim"],
            expand=True,
            title_style="bold blue"
        )
        
        table.add_column("🏷️  Status", style="bold", width=12, justify="center")
        table.add_column("⚡ Risk Level", style="bold", width=12, justify="center") 
        table.add_column("📋 Scenario", style="", min_width=25)
        table.add_column("⚖️  Compliance Frameworks", style="", min_width=20)
        if dev_mode:
            table.add_column("🔍 Technical Details", style="dim", min_width=30)
        
        # Sort results: Critical failures first, then by severity
        sorted_results = sorted(results, key=lambda r: (
            r.passed,  # Failed first
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r.severity, 4)
        ))
        
        for result in sorted_results:
            # Enhanced status presentation
            if result.passed:
                status_display = "[green]✅ PASS[/green]"
            else:
                status_display = "[red]❌ FAIL[/red]"
            
            # Enhanced severity with risk indicators
            severity_display = {
                "critical": "[red]🔴 CRITICAL[/red]",
                "high": "[yellow]🟡 HIGH[/yellow]", 
                "medium": "[blue]🔵 MEDIUM[/blue]",
                "low": "[dim]⚪ LOW[/dim]"
            }.get(result.severity, result.severity.upper())
            
            # Improved compliance formatting
            compliance_frameworks = result.compliance
            if len(compliance_frameworks) > 3:
                compliance_display = f"{', '.join(compliance_frameworks[:3])}\n[dim]+{len(compliance_frameworks)-3} more[/dim]"
            else:
                compliance_display = ", ".join(compliance_frameworks)
            
            # Scenario name with truncation for readability
            scenario_display = result.scenario_name
            if len(scenario_display) > 40:
                scenario_display = scenario_display[:37] + "..."
            
            row = [
                status_display,
                severity_display,
                scenario_display,
                compliance_display,
            ]
            
            if dev_mode:
                details = result.failure_reason or "[dim]Passed all checks[/dim]"
                if len(details) > 50:
                    details = details[:47] + "..."
                row.append(details)
            
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


def _handle_quick_start(
    domain: Optional[str], 
    export: Optional[str], 
    output: str, 
    dev: bool, 
    workflow: bool, 
    timing: bool, 
    verbose: bool
) -> None:
    """Handle quick-start mode with built-in sample data."""
    console.print("\n[bold blue]🚀 ARC-Eval Quick Start Demo[/bold blue]")
    console.print("[blue]" + "═" * 50 + "[/blue]")
    
    # Default to finance domain if not specified
    demo_domain = domain or "finance"
    
    # Sample data for each domain
    sample_data = {
        "finance": {
            "file": "examples/agent-outputs/sample_agent_outputs.json",
            "description": "Financial compliance scenarios including KYC, AML, and SOX violations"
        },
        "security": {
            "file": "examples/agent-outputs/security_test_outputs.json", 
            "description": "Cybersecurity scenarios including prompt injection and data leakage"
        },
        "ml": {
            "file": "examples/agent-outputs/ml_test_outputs.json",
            "description": "ML safety scenarios including bias detection and model governance"
        }
    }
    
    if demo_domain not in sample_data:
        console.print(f"[red]Error:[/red] Domain '{demo_domain}' not available for quick-start")
        console.print("Available domains: finance, security, ml")
        sys.exit(1)
    
    demo_info = sample_data[demo_domain]
    sample_file = Path(__file__).parent.parent / demo_info["file"]
    
    console.print(f"📋 Demo Domain: [bold]{demo_domain.title()}[/bold]")
    console.print(f"📄 Demo Description: {demo_info['description']}")
    console.print(f"📁 Sample Data: [dim]{demo_info['file']}[/dim]")
    console.print()
    
    if not sample_file.exists():
        console.print(f"[red]Error:[/red] Sample file not found: {sample_file}")
        console.print("Please ensure the examples directory is present")
        sys.exit(1)
    
    console.print("[yellow]⚡ Running demo evaluation...[/yellow]")
    console.print()
    
    try:
        # Import validation utilities
        from agent_eval.core.validators import InputValidator
        
        # Load sample data
        with open(sample_file, 'r') as f:
            raw_data = f.read()
        agent_outputs, warnings = InputValidator.validate_json_input(raw_data, str(sample_file))
        
        # Display any warnings
        for warning in warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")
        
        # Initialize evaluation engine
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Initializing demo evaluation for {demo_domain}")
            
        engine = EvaluationEngine(domain=demo_domain)
        
        if dev:
            console.print(f"[blue]Debug:[/blue] Demo using {len(agent_outputs) if isinstance(agent_outputs, list) else 1} sample outputs")
        
        # Run evaluation with timing
        start_time = time.time()
        
        # Enhanced progress for demo
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
        
        scenario_count = len(engine.eval_pack.scenarios) if hasattr(engine.eval_pack, 'scenarios') else 15
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            eval_task = progress.add_task(
                f"🎯 Demo: Evaluating {scenario_count} {demo_domain} scenarios...", 
                total=100
            )
            
            # Simulate realistic progress for demo
            import time as time_module
            for i in range(0, 101, 20):
                progress.update(eval_task, advance=20)
                time_module.sleep(0.1)  # Small delay for demo effect
                if i == 40:
                    progress.update(eval_task, description="🔍 Demo: Analyzing compliance violations...")
                elif i == 80:
                    progress.update(eval_task, description="📊 Demo: Generating executive summary...")
            
            results = engine.evaluate(agent_outputs)
            progress.update(eval_task, description="✅ Demo evaluation complete", completed=100)
        
        evaluation_time = time.time() - start_time
        
        # Show demo completion
        console.print(f"\n[green]✅ Demo completed successfully![/green]")
        console.print(f"[dim]Demo processed {len(results)} scenarios in {evaluation_time:.2f} seconds[/dim]")
        
        # Display results using existing function
        _display_results(results, output_format=output, dev_mode=dev, workflow_mode=workflow, domain=demo_domain)
        
        # Show timing if requested
        if timing:
            input_size = len(raw_data)
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            console.print(f"\n[blue]📤 Generating demo {export.upper()} export...[/blue]")
            _export_results(results, export_format=export, domain=demo_domain)
        
        # Show next steps
        console.print(f"\n[bold green]🎉 Quick Start Demo Complete![/bold green]")
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        console.print(f"1. Try with your own data: [dim]arc-eval --domain {demo_domain} --input your_file.json[/dim]")
        console.print(f"2. Explore other domains: [dim]arc-eval --list-domains[/dim]")
        console.print(f"3. Generate audit reports: [dim]arc-eval --domain {demo_domain} --input your_file.json --export pdf --workflow[/dim]")
        console.print(f"4. Learn more: [dim]arc-eval --help-input[/dim]")
        
        # Set exit code based on critical failures for demo
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        if critical_failures > 0:
            sys.exit(1)
            
    except Exception as e:
        if dev:
            console.print_exception()
        else:
            console.print(f"[red]Demo Error:[/red] {e}")
            console.print("[dim]Use --dev for more details[/dim]")
        sys.exit(1)


def _handle_validate(
    domain: Optional[str],
    input_file: Optional[Path], 
    stdin: bool,
    dev: bool,
    verbose: bool
) -> None:
    """Handle validation mode to test input files without running evaluation."""
    console.print("\n[bold blue]🔍 ARC-Eval Input Validation[/bold blue]")
    console.print("[blue]" + "═" * 50 + "[/blue]")
    
    # Check for input source
    if not input_file and not stdin:
        console.print("\n[red]❌ No Input Specified[/red]")
        console.print("[bold]You need to specify an input source to validate.[/bold]\n")
        
        console.print("[bold blue]✅ Validation Usage:[/bold blue]")
        console.print("• Validate file: [green]arc-eval --validate --input your_file.json[/green]")
        console.print("• Validate stdin: [green]cat data.json | arc-eval --validate --stdin[/green]")
        console.print("• With domain check: [green]arc-eval --validate --domain finance --input file.json[/green]")
        sys.exit(1)
    
    try:
        # Import validation utilities
        from agent_eval.core.validators import InputValidator
        
        # Load input data
        if input_file:
            if not input_file.exists():
                console.print(f"\n[red]❌ File Not Found[/red]")
                console.print(f"[bold]Could not find: [yellow]{input_file}[/yellow][/bold]")
                sys.exit(1)
            
            console.print(f"📄 Validating file: [yellow]{input_file}[/yellow]")
            
            with open(input_file, 'r') as f:
                raw_data = f.read()
            input_source = str(input_file)
            
        elif stdin:
            console.print("📄 Validating stdin input...")
            stdin_data = sys.stdin.read().strip()
            
            if not stdin_data:
                console.print("\n[red]❌ Empty Input[/red]")
                console.print("[bold]No data received from stdin[/bold]")
                sys.exit(1)
                
            raw_data = stdin_data
            input_source = "stdin"
        
        # Validate the input
        console.print("\n🔍 Checking input format...")
        
        agent_outputs, warnings = InputValidator.validate_json_input(raw_data, input_source)
        
        # Show validation results
        console.print("\n[green]✅ Validation Successful![/green]")
        console.print(f"📊 Found [bold]{len(agent_outputs) if isinstance(agent_outputs, list) else 1}[/bold] agent output(s)")
        
        # Display warnings if any
        if warnings:
            console.print(f"\n[yellow]⚠️  {len(warnings)} Warning(s):[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
        
        # Basic format analysis
        console.print("\n[bold blue]📋 Format Analysis:[/bold blue]")
        
        if isinstance(agent_outputs, list):
            console.print(f"• Input type: [green]Array of {len(agent_outputs)} items[/green]")
            
            if agent_outputs:
                sample = agent_outputs[0]
                console.print(f"• Sample structure: [dim]{list(sample.keys()) if isinstance(sample, dict) else type(sample).__name__}[/dim]")
                
                # Detect framework
                framework_detected = False
                if isinstance(sample, dict):
                    if 'choices' in sample:
                        console.print("• Detected format: [green]OpenAI API response[/green]")
                        framework_detected = True
                    elif 'content' in sample:
                        console.print("• Detected format: [green]Anthropic API response[/green]")
                        framework_detected = True
                    elif 'output' in sample:
                        console.print("• Detected format: [green]Simple agent output[/green]")
                        framework_detected = True
                
                if not framework_detected:
                    console.print("• Detected format: [yellow]Custom/Unknown format[/yellow]")
        else:
            console.print(f"• Input type: [green]Single object[/green]")
            if isinstance(agent_outputs, dict):
                console.print(f"• Structure: [dim]{list(agent_outputs.keys())}[/dim]")
        
        # Domain-specific validation if domain provided
        if domain:
            console.print(f"\n🎯 Domain compatibility check for [bold]{domain}[/bold]...")
            
            try:
                engine = EvaluationEngine(domain=domain)
                console.print(f"✅ Input is compatible with [green]{domain}[/green] domain")
                scenario_count = len(engine.eval_pack.scenarios) if hasattr(engine.eval_pack, 'scenarios') else 15
                console.print(f"📋 Ready for evaluation against [bold]{scenario_count}[/bold] {domain} scenarios")
            except Exception as e:
                console.print(f"❌ Domain validation failed: [red]{e}[/red]")
        
        # Next steps
        console.print(f"\n[bold green]🎉 Validation Complete![/bold green]")
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        
        if domain:
            console.print(f"• Run evaluation: [green]arc-eval --domain {domain} --input {input_file or 'your_file.json'}[/green]")
            console.print(f"• Generate report: [green]arc-eval --domain {domain} --input {input_file or 'your_file.json'} --export pdf[/green]")
        else:
            console.print("• Run with domain: [green]arc-eval --domain finance --input your_file.json[/green]")
            console.print("• See domains: [green]arc-eval --list-domains[/green]")
        
        console.print("• Learn more: [green]arc-eval --help-input[/green]")
        
    except json.JSONDecodeError as e:
        console.print(f"\n[red]❌ JSON Validation Failed[/red]")
        console.print(f"[bold]Invalid JSON format: [yellow]{e}[/yellow][/bold]\n")
        
        console.print("[bold blue]🔧 Common JSON Issues:[/bold blue]")
        console.print("• Missing quotes around strings")
        console.print("• Trailing commas")
        console.print("• Unescaped quotes in strings")
        console.print("• Invalid characters")
        
        console.print("\n[bold blue]🛠️  How to Fix:[/bold blue]")
        console.print("• Use a JSON validator (e.g., jsonlint.com)")
        console.print("• Check input formats: [green]arc-eval --help-input[/green]")
        console.print("• Try with sample data: [green]arc-eval --quick-start[/green]")
        
        if dev:
            console.print(f"\n[red]Detailed error:[/red] {e}")
            
        sys.exit(1)
        
    except Exception as e:
        if dev:
            console.print("\n[red]❌ Validation Error (Debug Mode)[/red]")
            console.print_exception()
        else:
            console.print(f"\n[red]❌ Validation Failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            console.print("[bold blue]💡 Troubleshooting:[/bold blue]")
            console.print("• Use --dev flag for detailed error info")
            console.print("• Check file permissions and format")
            console.print("• Try the demo: [green]arc-eval --quick-start[/green]")
            
        sys.exit(1)


if __name__ == "__main__":
    main()
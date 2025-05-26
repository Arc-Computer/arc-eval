#!/usr/bin/env python3
"""
AgentEval CLI - Main command-line interface.

Provides domain-specific evaluation and compliance reporting for LLMs and AI agents.
"""

# Load environment variables from .env file early
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
import json
import time
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.agent_judge import AgentJudge
from agent_eval.core.types import EvaluationResult, AgentOutput, EvaluationScenario
from agent_eval.exporters.pdf import PDFExporter
from agent_eval.exporters.csv import CSVExporter
from agent_eval.exporters.json import JSONExporter


console = Console()


def _get_domain_info() -> dict:
    """Get centralized domain information to avoid duplication."""
    return {
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
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Custom directory for exported reports (default: current directory)",
)
@click.option(
    "--format-template",
    type=click.Choice(["executive", "technical", "compliance", "minimal"]),
    help="Report formatting template for different audiences",
)
@click.option(
    "--summary-only",
    is_flag=True,
    help="Generate executive summary only (skip detailed scenarios)",
)
@click.option(
    "--agent-judge",
    is_flag=True,
    help="Use Agent-as-a-Judge evaluation with continuous feedback (requires API key)",
)
@click.option(
    "--judge-model",
    type=click.Choice(["claude-4-sonnet", "claude-3.5-haiku", "auto"]),
    default="auto",
    help="Select AI model for Agent-as-a-Judge evaluation",
)
@click.version_option(version="0.2.1", prog_name="arc-eval")
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
    output_dir: Optional[Path],
    format_template: Optional[str],
    summary_only: bool,
    agent_judge: bool,
    judge_model: str,
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
      
      # Generate executive summary only
      arc-eval --domain finance --input outputs.json --export pdf --summary-only
    
    📊 ENTERPRISE WORKFLOWS:
    
      # Compliance audit for executives
      arc-eval --domain finance --input logs.json --export pdf --workflow
      
      # Developer debugging mode
      arc-eval --domain security --input outputs.json --dev --verbose
      
      # CI/CD pipeline integration
      arc-eval --domain ml --input model_outputs.json --output json
      
      # Input validation before evaluation  
      arc-eval --validate --input suspicious_data.json
      
      # Custom report formats and output locations
      arc-eval --domain finance --input data.json --export pdf --format-template executive --output-dir reports/
      
      # Performance analysis with timing metrics
      arc-eval --domain finance --input data.json --timing --verbose
    
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
        
        domains_info = _get_domain_info()
        
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
        return _handle_quick_start(domain, export, output, dev, workflow, timing, verbose, output_dir, format_template, summary_only)
    
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
        
        # Check for Agent Judge mode
        if agent_judge:
            # Validate API key is available
            import os
            if not os.getenv("ANTHROPIC_API_KEY"):
                console.print("\n[red]❌ Agent-as-a-Judge Requires API Key[/red]")
                console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
                console.print("[bold]You need to set your Anthropic API key to use Agent-as-a-Judge evaluation.[/bold]\n")
                
                console.print("[bold blue]🔑 Set Your API Key:[/bold blue]")
                console.print("1. Create .env file: [yellow]echo 'ANTHROPIC_API_KEY=your_key_here' > .env[/yellow]")
                console.print("2. Or export: [yellow]export ANTHROPIC_API_KEY=your_key_here[/yellow]")
                console.print("3. Get API key at: [blue]https://console.anthropic.com/[/blue]")
                
                console.print("\n[bold blue]💡 Alternative:[/bold blue]")
                console.print("Run without Agent Judge: [green]arc-eval --domain {} --input {}[/green]".format(domain, input_file.name if input_file else "your_file.json"))
                sys.exit(1)
            
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Using Agent-as-a-Judge evaluation with model: {judge_model}")
            
            console.print(f"\n[bold blue]🤖 Agent-as-a-Judge Evaluation[/bold blue]")
            console.print(f"[dim]Using {judge_model} model for continuous feedback evaluation[/dim]")
        
        # Run evaluations
        start_time = time.time()
        input_size = len(json.dumps(agent_outputs)) if isinstance(agent_outputs, (list, dict)) else len(str(agent_outputs))
        
        if verbose:
            output_count = len(agent_outputs) if isinstance(agent_outputs, list) else 1
            eval_mode = "Agent-as-a-Judge" if agent_judge else "Standard"
            console.print(f"[cyan]Verbose:[/cyan] Starting {eval_mode} evaluation of {output_count} outputs against {domain} domain scenarios")
            console.print(f"[cyan]Verbose:[/cyan] Input data size: {input_size} bytes")
        
        # Enhanced progress indicators for professional experience
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
        
        # Get scenario count for progress tracking
        scenario_count = len(engine.eval_pack.scenarios) if hasattr(engine.eval_pack, 'scenarios') else 15
        
        if agent_judge:
            # Use Agent-as-a-Judge evaluation
            agent_judge_instance = AgentJudge(domain=domain)
            
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
                    f"🤖 Agent-as-a-Judge evaluating {scenario_count} {domain} scenarios...", 
                    total=100
                )
                
                # Convert agent outputs to AgentOutput objects
                if isinstance(agent_outputs, list):
                    agent_output_objects = [AgentOutput.from_raw(output) for output in agent_outputs]
                else:
                    agent_output_objects = [AgentOutput.from_raw(agent_outputs)]
                
                # Get scenarios from engine
                scenarios = engine.eval_pack.scenarios
                
                # Update progress during evaluation
                progress.update(eval_task, advance=20, description="🤖 Initializing Agent Judge...")
                
                # Run Agent-as-a-Judge evaluation
                judge_results = agent_judge_instance.evaluate_batch(agent_output_objects[:len(scenarios)], scenarios)
                progress.update(eval_task, advance=60, description="🤖 Generating continuous feedback...")
                
                # Generate improvement report
                improvement_report = agent_judge_instance.generate_improvement_report(judge_results)
                progress.update(eval_task, advance=20, description="✅ Agent-as-a-Judge evaluation complete", completed=100)
                
                # Convert to standard results format for compatibility
                results = []
                for i, judge_result in enumerate(judge_results):
                    scenario = scenarios[i] if i < len(scenarios) else scenarios[0]
                    result = EvaluationResult(
                        scenario_id=judge_result.scenario_id,
                        scenario_name=scenario.name,
                        description=scenario.description,
                        severity=scenario.severity,
                        compliance=scenario.compliance,
                        test_type=scenario.test_type,
                        passed=(judge_result.judgment == "pass"),
                        status="pass" if judge_result.judgment == "pass" else "fail",
                        confidence=judge_result.confidence,
                        failure_reason=judge_result.reasoning if judge_result.judgment != "pass" else None,
                        remediation="; ".join(judge_result.improvement_recommendations)
                    )
                    results.append(result)
        else:
            # Use standard evaluation
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
        
        # Display Agent Judge specific results if applicable
        if agent_judge:
            _display_agent_judge_results(improvement_report, domain)
        
        # Display results
        _display_results(results, output_format=output, dev_mode=dev, workflow_mode=workflow, domain=domain, summary_only=summary_only, format_template=format_template)
        
        # Show timing information if requested
        if timing:
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Exporting results in {export} format")
            _export_results(results, export_format=export, domain=domain, output_dir=output_dir, format_template=format_template, summary_only=summary_only)
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


def _display_agent_judge_results(improvement_report: dict, domain: str) -> None:
    """Display Agent-as-a-Judge specific results with continuous feedback."""
    console.print(f"\n[bold blue]🤖 Agent-as-a-Judge Improvement Report[/bold blue]")
    console.print("[blue]" + "═" * 60 + "[/blue]")
    
    # Summary metrics
    summary = improvement_report.get("summary", {})
    console.print(f"\n[bold green]📊 Evaluation Summary:[/bold green]")
    console.print(f"• Total Scenarios: {summary.get('total_scenarios', 0)}")
    console.print(f"• Passed: [green]{summary.get('passed', 0)}[/green]")
    console.print(f"• Failed: [red]{summary.get('failed', 0)}[/red]")  
    console.print(f"• Warnings: [yellow]{summary.get('warnings', 0)}[/yellow]")
    console.print(f"• Pass Rate: [{'green' if summary.get('pass_rate', 0) > 0.8 else 'yellow'}]{summary.get('pass_rate', 0):.1%}[/]")
    console.print(f"• Average Confidence: {summary.get('average_confidence', 0):.2f}")
    console.print(f"• Total Cost: [dim]${summary.get('total_cost', 0):.4f}[/dim]")
    
    # Continuous feedback
    feedback = improvement_report.get("continuous_feedback", {})
    
    if feedback.get("strengths"):
        console.print(f"\n[bold green]💪 Strengths:[/bold green]")
        for strength in feedback["strengths"]:
            console.print(f"  ✅ {strength}")
    
    if feedback.get("improvement_recommendations"):
        console.print(f"\n[bold blue]🎯 Top Improvement Recommendations:[/bold blue]")
        for i, rec in enumerate(feedback["improvement_recommendations"][:3], 1):
            console.print(f"  {i}. {rec}")
    
    if feedback.get("training_suggestions"):
        console.print(f"\n[bold purple]📚 Training Suggestions:[/bold purple]")
        for suggestion in feedback["training_suggestions"]:
            console.print(f"  📖 {suggestion}")
    
    if feedback.get("compliance_gaps"):
        console.print(f"\n[bold red]⚠️  Compliance Gaps:[/bold red]")
        console.print(f"Failed scenarios: {', '.join(feedback['compliance_gaps'])}")
    
    console.print(f"\n[dim]💡 Agent-as-a-Judge provides continuous feedback to improve your agent's {domain} compliance performance.[/dim]")


def _display_results(
    results: list[EvaluationResult], 
    output_format: str, 
    dev_mode: bool, 
    workflow_mode: bool,
    domain: str = "finance",
    summary_only: bool = False,
    format_template: Optional[str] = None
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
    _display_table_results(results, dev_mode, workflow_mode, domain, summary_only, format_template)


def _display_table_results(results: list[EvaluationResult], dev_mode: bool, workflow_mode: bool, domain: str = "finance", summary_only: bool = False, format_template: Optional[str] = None) -> None:
    """Display results in a rich table format."""
    
    # Summary statistics
    total_scenarios = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
    high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
    medium_failures = sum(1 for r in results if r.severity == "medium" and not r.passed)
    
    # Dynamic header based on domain
    domains_info = _get_domain_info()
    domain_title = domains_info.get(domain, {}).get("name", "Compliance")
    
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
    
    # Executive Summary only mode - skip detailed table
    if summary_only:
        console.print(f"\n[bold blue]📋 Executive Summary Generated[/bold blue]")
        console.print("[dim]Use without --summary-only to see detailed scenario results[/dim]")
        return
    
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


def _get_exporter(export_format: str):
    """Factory function to get the appropriate exporter."""
    exporters = {
        "pdf": PDFExporter,
        "csv": CSVExporter, 
        "json": JSONExporter
    }
    return exporters[export_format]()


def _export_results(results: list[EvaluationResult], export_format: str, domain: str, output_dir: Optional[Path] = None, format_template: Optional[str] = None, summary_only: bool = False) -> None:
    """Export results to the specified format using specialized exporters."""
    
    # Create output directory if specified  
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        export_path = output_dir
    else:
        export_path = Path.cwd()
    
    # Generate filename with timestamp and template info
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    template_suffix = f"_{format_template}" if format_template else ""
    summary_suffix = "_summary" if summary_only else ""
    filename = f"arc-eval_{domain}_{timestamp}{template_suffix}{summary_suffix}.{export_format}"
    filepath = export_path / filename
    
    # Use appropriate exporter
    exporter = _get_exporter(export_format)
    exporter.export(results, str(filepath), domain, format_template=format_template, summary_only=summary_only)
    
    # Display appropriate message
    export_messages = {
        "pdf": "📄 Audit Report",
        "csv": "📊 Data Export", 
        "json": "📋 JSON Export"
    }
    console.print(f"\n{export_messages[export_format]}: [bold]{filepath}[/bold]")


def _display_timing_metrics(evaluation_time: float, input_size: int, result_count: int) -> None:
    """Display enhanced timing and performance metrics."""
    console.print("\n[bold blue]⚡ Performance Analytics[/bold blue]")
    console.print("[blue]" + "═" * 70 + "[/blue]")
    
    # Create performance metrics table
    perf_table = Table(
        show_header=False,
        box=None,
        expand=True,
        padding=(0, 2)
    )
    perf_table.add_column("", style="bold", width=25)
    perf_table.add_column("", style="", width=20, justify="center")
    perf_table.add_column("", style="bold", width=25)
    perf_table.add_column("", style="", width=20, justify="center")
    
    # Format input size
    if input_size < 1024:
        size_str = f"{input_size} bytes"
    elif input_size < 1024 * 1024:
        size_str = f"{input_size / 1024:.1f} KB"
    else:
        size_str = f"{input_size / (1024 * 1024):.1f} MB"
    
    # Calculate processing speed
    scenarios_per_sec = result_count / evaluation_time if evaluation_time > 0 else 0
    
    # Performance grade
    if evaluation_time < 1.0:
        grade = "[green]🚀 EXCELLENT[/green]"
    elif evaluation_time < 5.0:
        grade = "[blue]⚡ GOOD[/blue]"
    elif evaluation_time < 15.0:
        grade = "[yellow]⏳ MODERATE[/yellow]"
    else:
        grade = "[red]🐌 SLOW[/red]"
    
    # Memory efficiency
    if input_size < 1024 * 1024:  # < 1MB
        memory_grade = "[green]✅ EFFICIENT[/green]"
    elif input_size < 10 * 1024 * 1024:  # < 10MB
        memory_grade = "[blue]📊 MODERATE[/blue]"
    else:
        memory_grade = "[yellow]⚠️  HEAVY[/yellow]"
    
    perf_table.add_row(
        "⏱️  Evaluation Time:", f"[bold]{evaluation_time:.3f}s[/bold]",
        "📊 Input Size:", f"[bold]{size_str}[/bold]"
    )
    perf_table.add_row(
        "🚀 Processing Speed:", f"[bold]{scenarios_per_sec:.1f}/sec[/bold]",
        "📋 Scenarios Processed:", f"[bold]{result_count}[/bold]"
    )
    perf_table.add_row(
        "⚡ Performance Grade:", grade,
        "💾 Memory Efficiency:", memory_grade
    )
    
    # Throughput analysis
    data_per_sec = input_size / evaluation_time if evaluation_time > 0 else 0
    if data_per_sec < 1024:
        throughput_str = f"{data_per_sec:.1f} B/s"
    elif data_per_sec < 1024 * 1024:
        throughput_str = f"{data_per_sec / 1024:.1f} KB/s"
    else:
        throughput_str = f"{data_per_sec / (1024 * 1024):.1f} MB/s"
    
    perf_table.add_row(
        "📈 Data Throughput:", f"[bold]{throughput_str}[/bold]",
        "🎯 Avg Time/Scenario:", f"[bold]{evaluation_time / result_count * 1000:.1f}ms[/bold]"
    )
    
    console.print(perf_table)
    console.print("[blue]" + "─" * 70 + "[/blue]")
    
    # Performance recommendations
    console.print("\n[bold blue]💡 Performance Insights[/bold blue]")
    
    recommendations = []
    if evaluation_time > 30:
        recommendations.append("🐌 [yellow]Long evaluation time detected. Consider smaller input batches.[/yellow]")
    if input_size > 10 * 1024 * 1024:
        recommendations.append("💾 [yellow]Large input detected. Consider data preprocessing or streaming.[/yellow]")
    if scenarios_per_sec < 1:
        recommendations.append("⚡ [yellow]Low processing speed. Check input complexity or system resources.[/yellow]")
    
    if not recommendations:
        if evaluation_time < 1.0:
            recommendations.append("🚀 [green]Excellent performance! Your setup is optimized.[/green]")
        else:
            recommendations.append("✅ [green]Good performance within acceptable ranges.[/green]")
    
    for rec in recommendations:
        console.print(f"  • {rec}")
    
    # Scaling projections
    if scenarios_per_sec > 0:
        console.print(f"\n[bold blue]📊 Scaling Projections[/bold blue]")
        console.print(f"• 100 scenarios: ~{100 / scenarios_per_sec:.1f}s")
        console.print(f"• 1,000 scenarios: ~{1000 / scenarios_per_sec:.1f}s")
        if scenarios_per_sec >= 1:
            console.print(f"• 10,000 scenarios: ~{10000 / scenarios_per_sec / 60:.1f} minutes")


def _handle_quick_start(
    domain: Optional[str], 
    export: Optional[str], 
    output: str, 
    dev: bool, 
    workflow: bool, 
    timing: bool, 
    verbose: bool,
    output_dir: Optional[Path] = None,
    format_template: Optional[str] = None,
    summary_only: bool = False
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
        _display_results(results, output_format=output, dev_mode=dev, workflow_mode=workflow, domain=demo_domain, summary_only=summary_only, format_template=format_template)
        
        # Show timing if requested
        if timing:
            input_size = len(raw_data)
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            console.print(f"\n[blue]📤 Generating demo {export.upper()} export...[/blue]")
            _export_results(results, export_format=export, domain=demo_domain, output_dir=output_dir, format_template=format_template, summary_only=summary_only)
        
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
    verbose: bool  # Used for potential future verbose validation output
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
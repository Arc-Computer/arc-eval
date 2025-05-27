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
import yaml
import logging
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import EvaluationResult, AgentOutput, EvaluationScenario
from agent_eval.evaluation.agent_judge import AgentJudge
from agent_eval.benchmarks.adapter import QuickBenchmarkAdapter
from agent_eval.analysis.judge_comparison import JudgeComparison, JudgeConfig
from agent_eval.analysis.self_improvement import SelfImprovementEngine
from agent_eval.exporters.pdf import PDFExporter
from agent_eval.exporters.csv import CSVExporter
from agent_eval.exporters.json import JSONExporter

logger = logging.getLogger(__name__)


console = Console()


def failed_scenarios_exist(results: List[EvaluationResult]) -> bool:
    """Check if any scenarios failed."""
    return any(not r.passed for r in results)


def _find_best_matching_output(scenario: EvaluationScenario, agent_output_objects: List[AgentOutput]) -> Optional[AgentOutput]:
    """Find the best matching output for a scenario, or return the first available output."""
    # Look for exact scenario_id match first
    for output in agent_output_objects:
        if (hasattr(output, 'metadata') and output.metadata and 
            isinstance(output.metadata, dict) and 
            output.metadata.get('scenario_id') == scenario.id):
            return output
    
    # If no exact match, use the first available output
    return agent_output_objects[0] if agent_output_objects else None


def _get_domain_info() -> dict:
    """Get centralized domain information to avoid duplication."""
    return {
        "finance": {
            "name": "Financial Services Compliance",
            "description": "Enterprise-grade evaluations for financial AI systems",
            "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "FFIEC", "DORA", "OFAC", "CFPB", "EU-AI-ACT"],
            "scenarios": 110,
            "use_cases": "Banking, Fintech, Payment Processing, Insurance, Investment",
            "examples": "Transaction approval, KYC verification, Fraud detection, Credit scoring",
            "categories": [
                "SOX & Financial Reporting Compliance",
                "KYC & AML Compliance Framework", 
                "PCI-DSS & Data Protection",
                "Fraud Detection & Risk Management",
                "Investment & Trading Compliance",
                "Insurance & Actuarial Analysis",
                "Digital Banking & API Security"
            ]
        },
        "security": {
            "name": "Cybersecurity & AI Agent Security", 
            "description": "AI safety evaluations for security-critical applications",
            "frameworks": ["OWASP-LLM-TOP-10", "NIST-AI-RMF", "ISO-27001", "SOC2-TYPE-II", "MITRE-ATTACK"],
            "scenarios": 120,
            "use_cases": "AI Agents, Chatbots, Code Generation, Security Tools",
            "examples": "Prompt injection, Data leakage, Code security, Access control",
            "categories": [
                "OWASP LLM Top 10 (Prompt Injection, Data Leakage, etc.)",
                "Purple Llama CyberSecEval Benchmarks",
                "Agent-Specific Security Testing",
                "Multi-Step Attack Chain Detection",
                "Automated Patch Generation Assessment"
            ]
        },
        "ml": {
            "name": "ML Infrastructure & Safety",
            "description": "Production ML system governance and bias detection",
            "frameworks": ["EU-AI-ACT", "ISO-23053", "NIST-AI-RMF", "IEEE-ETHICS", "MODEL-CARDS", "ALGORITHMIC-ACCOUNTABILITY"],
            "scenarios": 107,
            "use_cases": "MLOps, Model Deployment, AI Ethics, Data Science",
            "examples": "Bias detection, Model drift, Data governance, Safety alignment",
            "categories": [
                "Model Performance & Accuracy",
                "Bias & Fairness Detection",
                "Data Quality & Governance", 
                "Operational Reliability",
                "Safety & Alignment",
                "Enterprise MLOps Governance"
            ]
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
    "--performance",
    is_flag=True,
    help="Enable comprehensive performance tracking (runtime, memory, cost efficiency)",
)
@click.option(
    "--reliability",
    is_flag=True,
    help="Enable reliability evaluation (tool call validation, error recovery analysis)",
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
    type=click.Choice(["claude-sonnet-4-20250514", "claude-3-5-haiku-latest", "auto"]),
    default="auto",
    help="Select AI model: claude-sonnet-4-20250514 (primary), claude-3-5-haiku-latest (cost-optimized), auto (smart selection)",
)
@click.option(
    "--benchmark",
    type=click.Choice(["mmlu", "humeval", "gsm8k"]),
    help="Use external benchmark for evaluation (MMLU, HumanEval, GSM8K)",
)
@click.option(
    "--subset",
    type=str,
    help="Benchmark subset (e.g., 'anatomy' for MMLU)",
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Limit number of benchmark scenarios to evaluate (default: 10)",
)
@click.option(
    "--verify",
    is_flag=True,
    help="Enable verification layer for improved judgment reliability",
)
@click.option(
    "--confidence-calibration",
    is_flag=True,
    help="Enable confidence calibration with enhanced uncertainty quantification",
)
@click.option(
    "--compare-judges",
    type=click.Path(exists=True, path_type=Path),
    help="A/B test different judge configurations using YAML config file",
)
@click.version_option(version="0.2.3", prog_name="arc-eval")
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
    performance: bool,
    reliability: bool,
    verbose: bool,
    quick_start: bool,
    validate: bool,
    output_dir: Optional[Path],
    format_template: Optional[str],
    summary_only: bool,
    agent_judge: bool,
    judge_model: str,
    benchmark: Optional[str],
    subset: Optional[str],
    limit: int,
    verify: bool,
    confidence_calibration: bool,
    compare_judges: Optional[Path],
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
    
    📊 BENCHMARK EVALUATION:
    
      # MMLU academic benchmark
      arc-eval --benchmark mmlu --subset anatomy --limit 20
      
      # HumanEval code generation benchmark
      arc-eval --benchmark humeval --limit 10 --agent-judge
      
      # GSM8K mathematical reasoning benchmark
      arc-eval --benchmark gsm8k --limit 15 --export pdf
    
    🔍 VERIFICATION & QUALITY ASSURANCE:
    
      # Enable verification layer for improved reliability
      arc-eval --domain finance --input outputs.json --agent-judge --verify
      
      # Enhanced confidence calibration with uncertainty quantification
      arc-eval --domain security --input outputs.json --agent-judge --confidence-calibration
      
      # Combined verification and confidence calibration
      arc-eval --domain ml --input outputs.json --agent-judge --verify --confidence-calibration
      
      # Benchmark evaluation with verification
      arc-eval --benchmark mmlu --subset anatomy --limit 10 --agent-judge --verify
      
      # A/B test different judge configurations
      arc-eval --compare-judges config/judge_comparison_templates.yaml --input outputs.json
    
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
        from agent_eval.evaluation.validators import InputValidator
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
            
            # Show evaluation categories
            console.print(f"[yellow]📂 Evaluation Categories:[/yellow]")
            for category in info['categories']:
                console.print(f"   • {category}")
            
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
    
    # Handle benchmark mode
    if benchmark:
        return _handle_benchmark_evaluation(
            benchmark, subset, limit, domain, agent_judge, judge_model, 
            export, output, dev, workflow, timing, verbose, output_dir, 
            format_template, summary_only, verify
        )
    
    # Validate domain requirement for CLI mode
    if not list_domains and not help_input and domain is None:
        console.print("[red]Error:[/red] --domain is required")
        console.print("Use --list-domains to see available options")
        sys.exit(2)
    
    
    # Import validation utilities
    from agent_eval.evaluation.validators import (
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
        
        # Handle judge comparison mode
        if compare_judges:
            _handle_judge_comparison(compare_judges, agent_outputs, domain)
            return
        
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
            # Use Agent-as-a-Judge evaluation with model preference
            agent_judge_instance = AgentJudge(domain=domain, preferred_model=judge_model)
            
            # Initialize performance tracking if requested
            performance_tracker = None
            if performance:
                from agent_eval.evaluation.performance_tracker import PerformanceTracker
                performance_tracker = PerformanceTracker()
                performance_tracker.__enter__()
            
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
                
                # Filter scenarios based on input data scenario_ids if available
                all_scenarios = engine.eval_pack.scenarios
                input_scenario_ids = set()
                
                # Extract scenario_ids from input data
                if isinstance(agent_outputs, list):
                    for output in agent_outputs:
                        if isinstance(output, dict) and 'scenario_id' in output:
                            input_scenario_ids.add(output['scenario_id'])
                elif isinstance(agent_outputs, dict) and 'scenario_id' in agent_outputs:
                    input_scenario_ids.add(agent_outputs['scenario_id'])
                
                # Filter scenarios to only those matching input data
                if input_scenario_ids:
                    scenarios = [s for s in all_scenarios if s.id in input_scenario_ids]
                    if verbose:
                        console.print(f"[cyan]Verbose:[/cyan] Filtered to {len(scenarios)} scenarios matching input data (scenario_ids: {sorted(input_scenario_ids)})")
                else:
                    scenarios = all_scenarios
                    if verbose:
                        console.print(f"[cyan]Verbose:[/cyan] No scenario_ids found in input data, evaluating all {len(scenarios)} scenarios")
                
                # Update progress during evaluation
                progress.update(eval_task, advance=20, description="🤖 Initializing Agent Judge...")
                
                # Run Agent-as-a-Judge evaluation
                # Evaluate each scenario against all available outputs (matches standard evaluation behavior)
                judge_results = []
                for i, scenario in enumerate(scenarios):
                    best_output = _find_best_matching_output(scenario, agent_output_objects)
                    
                    if best_output:
                        try:
                            scenario_start_time = time.time()
                            
                            # Track judge execution time if performance monitoring is enabled
                            if performance_tracker:
                                with performance_tracker.track_judge_execution():
                                    result = agent_judge_instance.evaluate_scenario(best_output, scenario)
                            else:
                                result = agent_judge_instance.evaluate_scenario(best_output, scenario)
                            
                            judge_results.append(result)
                            
                            # Track scenario completion for performance metrics
                            if performance_tracker:
                                scenario_time = time.time() - scenario_start_time
                                performance_tracker.track_scenario_completion(scenario_time)
                                
                        except Exception as e:
                            logger.error(f"Failed to evaluate scenario {scenario.id}: {e}")
                            continue
                progress.update(eval_task, advance=40, description="🤖 Agent evaluation complete...")
                
                # Run verification if requested
                if verify:
                    progress.update(eval_task, advance=0, description="🔍 Running verification layer...")
                    from agent_eval.evaluation.verification_judge import VerificationJudge
                    
                    verification_judge = VerificationJudge(domain, agent_judge_instance.api_manager)
                    verification_results = verification_judge.batch_verify(
                        judge_results, 
                        agent_output_objects[:len(scenarios)], 
                        scenarios
                    )
                    
                    # Add verification summaries to judge results
                    for judge_result, verification_result in zip(judge_results, verification_results):
                        judge_result.verification = verification_judge.create_verification_summary(verification_result)
                    
                    progress.update(eval_task, advance=20, description="🔍 Verification complete...")
                else:
                    progress.update(eval_task, advance=20, description="🤖 Generating continuous feedback...")
                
                # Generate improvement report with bias detection
                improvement_report = agent_judge_instance.generate_improvement_report(judge_results, agent_output_objects[:len(judge_results)])
                
                # Record evaluation results in self-improvement engine for training data generation
                try:
                    self_improvement_engine = SelfImprovementEngine()
                    
                    # Convert judge results to self-improvement format
                    eval_results_for_training = []
                    for judge_result in judge_results:
                        eval_result = {
                            'scenario_id': judge_result.scenario_id,
                            'reward_signals': judge_result.reward_signals,
                            'improvement_recommendations': judge_result.improvement_recommendations,
                            'compliance_gaps': improvement_report.get('continuous_feedback', {}).get('compliance_gaps', []),
                            'performance_metrics': {
                                'confidence': judge_result.confidence,
                                'evaluation_time': judge_result.evaluation_time,
                                'model_used': judge_result.model_used
                            },
                            'category': 'agent_judge_evaluation',
                            'severity': 'high' if judge_result.judgment == 'fail' else 'low',
                            'agent_output': judge_result.reasoning
                        }
                        eval_results_for_training.append(eval_result)
                    
                    # Record in self-improvement engine
                    agent_id = f"agent_{domain}_{int(time.time())}"  # Generate unique agent ID
                    self_improvement_engine.record_evaluation_result(
                        agent_id=agent_id,
                        domain=domain,
                        evaluation_results=eval_results_for_training
                    )
                    
                    if verbose:
                        console.print(f"[dim]✅ Recorded {len(eval_results_for_training)} evaluation results for future training data generation[/dim]")
                        
                except ImportError as e:
                    logger.warning(f"Failed to import self-improvement engine: {e}")
                    if verbose:
                        console.print(f"[dim yellow]⚠️  Self-improvement module import failed: {e}[/dim yellow]")
                except (AttributeError, TypeError, ValueError) as e:
                    logger.warning(f"Failed to record results in self-improvement engine: {e}")
                    if verbose:
                        console.print(f"[dim yellow]⚠️  Self-improvement recording failed: {e}[/dim yellow]")
                except OSError as e:
                    logger.warning(f"Failed to create retraining data files: {e}")
                    if verbose:
                        console.print(f"[dim yellow]⚠️  Could not write training data to disk: {e}[/dim yellow]")
                except Exception as e:
                    logger.warning(f"Unexpected error in self-improvement recording: {e}")
                    if verbose:
                        console.print(f"[dim yellow]⚠️  Unexpected self-improvement error: {e}[/dim yellow]")
                
                # Finalize performance tracking if enabled
                performance_metrics = None
                if performance_tracker:
                    try:
                        # Add final cost tracking
                        performance_tracker.add_cost(agent_judge_instance.api_manager.total_cost)
                        performance_tracker.__exit__(None, None, None)
                        performance_metrics = performance_tracker.get_performance_summary()
                    except Exception as e:
                        logger.warning(f"Failed to generate performance metrics: {e}")
                        performance_metrics = None
                
                # Run reliability evaluation if enabled
                reliability_metrics = None
                if reliability:
                    try:
                        from agent_eval.evaluation.reliability_validator import ReliabilityValidator
                        from agent_eval.core.parser_registry import detect_and_extract_tools
                        
                        reliability_validator = ReliabilityValidator()
                        
                        # Extract tool calls from agent outputs
                        validations = []
                        for i, agent_output in enumerate(agent_output_objects[:len(scenarios)]):
                            scenario = scenarios[i]
                            
                            # Get expected tools from scenario (if available)
                            expected_tools = []
                            # For demo purposes, define some expected tools based on scenario content
                            scenario_text = f"{scenario.name} {scenario.description}".lower()
                            if "fact" in scenario_text or "validation" in scenario_text:
                                expected_tools = ["search", "validate", "verify"]
                            elif "mathematical" in scenario_text or "calculation" in scenario_text:
                                expected_tools = ["calculator", "compute", "verify"]
                            elif "bias" in scenario_text or "fairness" in scenario_text:
                                expected_tools = ["analyze", "evaluate", "metrics"]
                            elif "multi-modal" in scenario_text:
                                expected_tools = ["image_process", "text_analyze", "align"]
                            
                            # Validate tool calls
                            validation = reliability_validator.validate_tool_calls(
                                agent_output.normalized_output,
                                expected_tools,
                                {"scenario_id": scenario.id, "scenario_name": scenario.name}
                            )
                            validations.append(validation)
                        
                        # Generate reliability metrics
                        reliability_metrics = reliability_validator.generate_reliability_metrics(validations)
                        
                    except Exception as e:
                        logger.warning(f"Failed to generate reliability metrics: {e}")
                        reliability_metrics = None
                
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
                
                # Filter scenarios based on input data scenario_ids if available
                all_scenarios = engine.eval_pack.scenarios
                input_scenario_ids = set()
                
                # Extract scenario_ids from input data
                if isinstance(agent_outputs, list):
                    for output in agent_outputs:
                        if isinstance(output, dict) and 'scenario_id' in output:
                            input_scenario_ids.add(output['scenario_id'])
                elif isinstance(agent_outputs, dict) and 'scenario_id' in agent_outputs:
                    input_scenario_ids.add(agent_outputs['scenario_id'])
                
                # Filter scenarios to only those matching input data
                if input_scenario_ids:
                    scenarios = [s for s in all_scenarios if s.id in input_scenario_ids]
                    if verbose:
                        console.print(f"[cyan]Verbose:[/cyan] Filtered to {len(scenarios)} scenarios matching input data (scenario_ids: {sorted(input_scenario_ids)})")
                else:
                    scenarios = all_scenarios
                    if verbose:
                        console.print(f"[cyan]Verbose:[/cyan] No scenario_ids found in input data, evaluating all {len(scenarios)} scenarios")
                
                # Run the actual evaluation with filtered scenarios
                results = engine.evaluate(agent_outputs, scenarios)
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
            _display_agent_judge_results(
                improvement_report, 
                domain, 
                performance_metrics if 'performance_metrics' in locals() else None,
                reliability_metrics if 'reliability_metrics' in locals() else None
            )
        
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


def _display_agent_judge_results(improvement_report: dict, domain: str, performance_metrics: Optional[dict] = None, reliability_metrics: Optional[dict] = None) -> None:
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
    
    # Check if verification was used and display verification metrics
    detailed_results = improvement_report.get("detailed_results", [])
    verification_used = any(
        hasattr(result, "verification") and result.get("verification") 
        for result in detailed_results
    )
    
    if verification_used:
        console.print(f"\n[bold cyan]🔍 Verification Layer:[/bold cyan]")
        # Calculate verification stats from detailed results
        verified_count = 0
        total_with_verification = 0
        avg_confidence_delta = 0
        
        for result in detailed_results:
            verification = result.get("verification")
            if verification:
                total_with_verification += 1
                if verification.get("verified", False):
                    verified_count += 1
                avg_confidence_delta += abs(verification.get("confidence_delta", 0))
        
        if total_with_verification > 0:
            verification_rate = verified_count / total_with_verification
            avg_confidence_delta = avg_confidence_delta / total_with_verification
            
            console.print(f"• Verification Rate: [{'green' if verification_rate > 0.8 else 'yellow'}]{verification_rate:.1%}[/]")
            console.print(f"• Avg Confidence Delta: {avg_confidence_delta:.2f}")
            console.print(f"• Verified Judgments: [green]{verified_count}[/green]/{total_with_verification}")
    
    # Display bias detection results
    bias_detection = improvement_report.get("bias_detection")
    if bias_detection:
        console.print(f"\n[bold magenta]⚖️ Bias Detection:[/bold magenta]")
        
        # Overall bias risk with color coding
        risk_level = bias_detection.get("overall_risk", "unknown")
        risk_color = "green" if risk_level == "low" else "yellow" if risk_level == "medium" else "red"
        console.print(f"• Overall Bias Risk: [{risk_color}]{risk_level.upper()}[/{risk_color}]")
        
        # Individual bias scores
        length_bias = bias_detection.get("length_bias", 0)
        position_bias = bias_detection.get("position_bias", 0)
        style_bias = bias_detection.get("style_bias", 0)
        
        console.print(f"• Length Bias Score: {length_bias:.3f}")
        console.print(f"• Position Bias Score: {position_bias:.3f}")
        console.print(f"• Style Bias Score: {style_bias:.3f}")
        console.print(f"• Evaluations Analyzed: {bias_detection.get('total_evaluations', 0)}")
        
        # Show bias recommendations if any
        recommendations = bias_detection.get("recommendations", [])
        if recommendations:
            console.print(f"\n[bold magenta]🔧 Bias Mitigation:[/bold magenta]")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3 recommendations
                console.print(f"  {i}. {rec}")
    
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
    
    # Performance metrics display
    if performance_metrics:
        console.print(f"\n[bold cyan]⚡ Performance Metrics:[/bold cyan]")
        
        runtime = performance_metrics.get("runtime", {})
        memory = performance_metrics.get("memory", {})
        latency = performance_metrics.get("latency", {})
        cost_efficiency = performance_metrics.get("cost_efficiency", {})
        resources = performance_metrics.get("resources", {})
        
        console.print(f"• Total Execution Time: {runtime.get('total_execution_time', 0):.2f}s")
        console.print(f"• Judge Execution Time: {runtime.get('judge_execution_time', 0):.2f}s")
        console.print(f"• Throughput: {runtime.get('scenarios_per_second', 0):.2f} scenarios/sec")
        console.print(f"• Peak Memory: {memory.get('peak_memory_mb', 0):.1f} MB")
        console.print(f"• P95 Latency: {latency.get('p95_seconds', 0):.3f}s")
        console.print(f"• Cost per Scenario: ${cost_efficiency.get('cost_per_scenario', 0):.4f}")
        
        if resources.get('avg_cpu_percent'):
            console.print(f"• Avg CPU Usage: {resources.get('avg_cpu_percent', 0):.1f}%")
    
    # Reliability metrics display
    if reliability_metrics:
        console.print(f"\n[bold magenta]🔧 Reliability Metrics:[/bold magenta]")
        
        console.print(f"• Overall Reliability Score: {reliability_metrics.get('overall_reliability_score', 0):.2f}")
        console.print(f"• Tool Call Accuracy: {reliability_metrics.get('tool_call_accuracy', 0):.1%}")
        console.print(f"• Error Recovery Rate: {reliability_metrics.get('error_recovery_rate', 0):.1%}")
        console.print(f"• Framework Detection Rate: {reliability_metrics.get('framework_detection_rate', 0):.1%}")
        
        # Show framework distribution
        framework_dist = reliability_metrics.get('framework_distribution', {})
        if framework_dist:
            frameworks = ', '.join([f"{fw}: {count}" for fw, count in framework_dist.items()])
            console.print(f"• Framework Distribution: {frameworks}")
        
        # Show reliability issues if any
        issues = reliability_metrics.get('reliability_issues', [])
        if issues and issues != ["No major reliability issues detected"]:
            console.print(f"\n[bold red]⚠️  Reliability Issues:[/bold red]")
            for issue in issues[:3]:  # Show top 3 issues
                console.print(f"  • {issue}")
    
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
    """Handle enhanced quick-start mode with interactive features."""
    
    # Import our new interactive modules
    from agent_eval.ui.interactive_menu import InteractiveMenu
    from agent_eval.ui.streaming_evaluator import StreamingEvaluator
    from agent_eval.ui.next_steps_guide import NextStepsGuide
    
    # Step 1: Interactive domain selection (if not specified)
    if not domain:
        menu = InteractiveMenu()
        demo_domain = menu.domain_selection_menu()
        
        # Step 2: Get user context for personalization
        user_context = menu.get_user_context(demo_domain)
    else:
        demo_domain = domain
        # Create minimal user context for specified domain
        user_context = {
            "domain": demo_domain,
            "role": "user", 
            "experience": "intermediate",
            "goal": "compliance_audit"
        }
    
    console.print(f"\n[bold blue]🚀 ARC-Eval Streaming Demo - {demo_domain.title()} Domain[/bold blue]")
    console.print("[blue]" + "═" * 70 + "[/blue]")
    
    # Use demo-optimized sample data files (5 scenarios each for fast demo)
    sample_data = {
        "finance": {
            "file": "examples/demo-data/finance.json",
            "description": "5 key financial compliance scenarios including SOX, KYC, AML violations",
            "scenarios_count": 5,
            "full_suite": "110 total scenarios available"
        },
        "security": {
            "file": "examples/demo-data/security.json", 
            "description": "5 critical cybersecurity scenarios including prompt injection, data leakage",
            "scenarios_count": 5,
            "full_suite": "120 total scenarios available"
        },
        "ml": {
            "file": "examples/demo-data/ml.json",
            "description": "5 essential ML safety scenarios including bias detection, model governance",
            "scenarios_count": 5,
            "full_suite": "107 total scenarios available"
        }
    }
    
    if demo_domain not in sample_data:
        console.print(f"[red]Error:[/red] Domain '{demo_domain}' not available for quick-start")
        console.print("Available domains: finance, security, ml")
        sys.exit(1)
    
    demo_info = sample_data[demo_domain]
    sample_file = Path(__file__).parent.parent / demo_info["file"]
    
    # Show personalized demo intro
    console.print(f"📋 [bold]{demo_domain.title()} Compliance Evaluation[/bold]")
    console.print(f"📄 {demo_info['description']}")
    console.print(f"📊 Evaluating [bold]{demo_info['scenarios_count']} scenarios[/bold] with real-time streaming")
    console.print(f"[dim]({demo_info['full_suite']} - this demo shows a curated subset)[/dim]")
    
    # Show personalized context if available
    if user_context.get("role") != "user":
        role_display = user_context.get("role", "").replace("_", " ").title()
        goal_display = user_context.get("goal", "").replace("_", " ").title()
        console.print(f"👤 Customized for: [bold]{role_display}[/bold] | Goal: [bold]{goal_display}[/bold]")
    
    console.print()
    
    if not sample_file.exists():
        console.print(f"[red]Error:[/red] Sample file not found: {sample_file}")
        console.print("Please ensure the examples directory is present")
        sys.exit(1)
    
    try:
        # Import validation utilities
        from agent_eval.evaluation.validators import InputValidator
        
        # Load sample data
        with open(sample_file, 'r') as f:
            raw_data = f.read()
        agent_outputs, warnings = InputValidator.validate_json_input(raw_data, str(sample_file))
        
        # Display any warnings
        for warning in warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")
        
        # Initialize evaluation engine
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Initializing streaming evaluation for {demo_domain}")
            
        engine = EvaluationEngine(domain=demo_domain)
        
        if dev:
            console.print(f"[blue]Debug:[/blue] Demo using {len(agent_outputs) if isinstance(agent_outputs, list) else 1} sample outputs")
        
        # Step 3: Run streaming evaluation with real-time updates
        start_time = time.time()
        
        console.print("[bold yellow]🚀 Starting Real-Time Evaluation Stream...[/bold yellow]")
        console.print("[dim]Watch as each scenario is evaluated live with instant results[/dim]\n")
        
        # Use our new streaming evaluator
        streaming_evaluator = StreamingEvaluator(engine, user_context)
        results = streaming_evaluator.stream_evaluation(agent_outputs)
        
        evaluation_time = time.time() - start_time
        
        # Show streaming completion summary
        console.print(f"\n[green]✅ Streaming evaluation completed![/green]")
        console.print(f"[dim]Processed {len(results)} scenarios in {evaluation_time:.2f} seconds with live updates[/dim]")
        
        # Skip redundant results display since streaming already showed comprehensive results
        # Only show detailed table if specifically requested or in dev mode
        if dev and not summary_only:
            console.print("\n[bold blue]📊 Detailed Results (Dev Mode)[/bold blue]")
            _display_results(results, output_format=output, dev_mode=dev, workflow_mode=workflow, domain=demo_domain, summary_only=True, format_template=format_template)
        
        # Show timing if requested
        if timing:
            input_size = len(raw_data)
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            console.print(f"\n[blue]📤 Generating demo {export.upper()} export...[/blue]")
            _export_results(results, export_format=export, domain=demo_domain, output_dir=output_dir, format_template=format_template, summary_only=summary_only)
        
        # Step 4: Show personalized next steps guide
        next_steps_guide = NextStepsGuide()
        next_steps_guide.generate_personalized_guide(user_context, results)
        
        # Show copy-paste ready commands
        console.print("\n[bold blue]📋 Ready-to-Use Commands[/bold blue]")
        console.print("[dim]Copy and paste these commands to continue your evaluation journey[/dim]\n")
        
        commands = next_steps_guide.generate_copy_paste_commands(user_context)
        for command in commands:
            if command.startswith("#"):
                console.print(f"[dim]{command}[/dim]")
            else:
                console.print(f"[green]{command}[/green]")
        
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
        from agent_eval.evaluation.validators import InputValidator
        
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


def _handle_benchmark_evaluation(
    benchmark: str,
    subset: Optional[str],
    limit: int,
    domain: Optional[str],
    agent_judge: bool,
    judge_model: str,
    export: Optional[str],
    output: str,
    dev: bool,
    workflow: bool,
    timing: bool,
    verbose: bool,
    output_dir: Optional[Path],
    format_template: Optional[str],
    summary_only: bool,
    verify: bool,
) -> None:
    """Handle benchmark evaluation mode."""
    console.print(f"\n[bold blue]📊 ARC-Eval Benchmark Evaluation[/bold blue]")
    console.print("[blue]" + "═" * 60 + "[/blue]")
    
    # Default domain if not specified
    if not domain:
        domain = "ml"  # Default to ML domain for benchmarks
        console.print(f"[yellow]No domain specified, defaulting to 'ml' for benchmark evaluation[/yellow]")
    
    console.print(f"📋 Benchmark: [bold]{benchmark.upper()}[/bold]")
    if subset:
        console.print(f"📂 Subset: [bold]{subset}[/bold]")
    console.print(f"📊 Limit: [bold]{limit}[/bold] scenarios")
    console.print(f"🎯 Domain: [bold]{domain}[/bold]")
    
    if agent_judge:
        console.print(f"🤖 Using Agent-as-a-Judge with [bold]{judge_model}[/bold] model")
    
    console.print()
    
    try:
        # Initialize benchmark adapter
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Initializing {benchmark} benchmark adapter")
        
        adapter = QuickBenchmarkAdapter()
        
        # Validate benchmark
        if not adapter.validate_benchmark_name(benchmark):
            console.print(f"[red]Error:[/red] Unsupported benchmark: {benchmark}")
            console.print(f"Supported benchmarks: {', '.join(adapter.get_supported_benchmarks())}")
            sys.exit(1)
        
        # Load benchmark scenarios
        console.print(f"[yellow]📥 Loading {benchmark.upper()} benchmark scenarios...[/yellow]")
        
        try:
            scenarios = adapter.load_benchmark(benchmark, subset=subset, limit=limit)
            
            if not scenarios:
                console.print(f"[red]Error:[/red] No scenarios loaded from {benchmark}")
                sys.exit(1)
            
            console.print(f"[green]✅ Loaded {len(scenarios)} scenarios from {benchmark.upper()}[/green]")
            
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Scenarios loaded: {[s.id for s in scenarios[:3]]}{'...' if len(scenarios) > 3 else ''}")
            
        except ImportError as e:
            console.print(f"\n[red]❌ Missing Dependency[/red]")
            console.print(f"[bold]{e}[/bold]\n")
            
            console.print("[bold blue]🔧 Installation Required:[/bold blue]")
            console.print("Install datasets library: [green]pip install datasets[/green]")
            console.print("Then retry: [green]arc-eval --benchmark {} --limit {}[/green]".format(benchmark, limit))
            sys.exit(1)
            
        except Exception as e:
            console.print(f"\n[red]❌ Benchmark Loading Failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            console.print("[bold blue]💡 Troubleshooting:[/bold blue]")
            console.print(f"• Check internet connection (datasets downloads from HuggingFace)")
            console.print(f"• Try smaller limit: [green]arc-eval --benchmark {benchmark} --limit 5[/green]")
            if subset:
                console.print(f"• Try without subset: [green]arc-eval --benchmark {benchmark} --limit {limit}[/green]")
            console.print("• Use --dev for detailed error info")
            
            if dev:
                console.print(f"\n[red]Detailed error:[/red] {e}")
            
            sys.exit(1)
        
        # Generate synthetic agent outputs for benchmark scenarios
        console.print(f"[yellow]🔄 Generating sample agent outputs for evaluation...[/yellow]")
        
        # Create sample outputs that can be evaluated
        agent_outputs = []
        for scenario in scenarios:
            # Create a simple agent output for each scenario
            sample_output = {
                "output": f"Sample response for {scenario.name}",
                "scenario": scenario.id,
                "benchmark": benchmark
            }
            agent_outputs.append(sample_output)
        
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Generated {len(agent_outputs)} sample outputs for evaluation")
        
        # Run evaluation
        start_time = time.time()
        
        if agent_judge:
            # Check for API key
            import os
            if not os.getenv("ANTHROPIC_API_KEY"):
                console.print("\n[red]❌ Agent-as-a-Judge Requires API Key[/red]")
                console.print("[bold]Set ANTHROPIC_API_KEY environment variable[/bold]")
                console.print("Get key at: [blue]https://console.anthropic.com/[/blue]")
                sys.exit(1)
            
            console.print(f"\n[bold blue]🤖 Running Agent-as-a-Judge evaluation on {benchmark.upper()}...[/bold blue]")
            
            # Use Agent-as-a-Judge evaluation
            agent_judge_instance = AgentJudge(domain=domain)
            
            # Convert outputs to AgentOutput objects
            agent_output_objects = [AgentOutput.from_raw(output) for output in agent_outputs]
            
            # Run evaluation
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            
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
                    f"🤖 Evaluating {len(scenarios)} {benchmark.upper()} scenarios...", 
                    total=100
                )
                
                progress.update(eval_task, advance=20, description="🤖 Initializing Agent Judge...")
                
                judge_results = agent_judge_instance.evaluate_batch(agent_output_objects, scenarios)
                progress.update(eval_task, advance=40, description="🤖 Benchmark evaluation complete...")
                
                # Run verification if requested
                if verify:
                    progress.update(eval_task, advance=0, description="🔍 Running verification layer...")
                    from agent_eval.evaluation.verification_judge import VerificationJudge
                    
                    verification_judge = VerificationJudge(domain, agent_judge_instance.api_manager)
                    verification_results = verification_judge.batch_verify(
                        judge_results, 
                        agent_output_objects, 
                        scenarios
                    )
                    
                    # Add verification summaries to judge results
                    for judge_result, verification_result in zip(judge_results, verification_results):
                        judge_result.verification = verification_judge.create_verification_summary(verification_result)
                    
                    progress.update(eval_task, advance=20, description="🔍 Verification complete...")
                else:
                    progress.update(eval_task, advance=20, description="🤖 Analyzing benchmark performance...")
                
                improvement_report = agent_judge_instance.generate_improvement_report(judge_results, agent_output_objects[:len(judge_results)])
                progress.update(eval_task, advance=20, description="✅ Benchmark evaluation complete", completed=100)
            
            # Convert to standard results format
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
            
            # Display Agent Judge results
            _display_agent_judge_results(improvement_report, f"{benchmark.upper()} Benchmark")
            
        else:
            # Use standard evaluation engine
            console.print(f"\n[bold blue]🔍 Running standard evaluation on {benchmark.upper()}...[/bold blue]")
            
            engine = EvaluationEngine(domain=domain)
            
            # Use benchmark scenarios instead of domain scenarios
            engine.eval_pack.scenarios = scenarios
            
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            
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
                    f"🔍 Evaluating {len(scenarios)} {benchmark.upper()} scenarios...", 
                    total=100
                )
                
                for i in range(0, 101, 20):
                    progress.update(eval_task, advance=20)
                    if i == 40:
                        progress.update(eval_task, description=f"🔍 Processing {benchmark.upper()} scenarios...")
                    elif i == 80:
                        progress.update(eval_task, description="🔍 Generating benchmark report...")
                
                results = engine.evaluate(agent_outputs)
                progress.update(eval_task, description="✅ Benchmark evaluation complete", completed=100)
        
        evaluation_time = time.time() - start_time
        
        # Show results summary
        console.print(f"\n[green]✅ {benchmark.upper()} benchmark evaluation completed![/green]")
        console.print(f"[dim]Evaluated {len(results)} scenarios in {evaluation_time:.2f} seconds[/dim]")
        
        if verbose:
            passed = sum(1 for r in results if r.passed)
            failed = len(results) - passed
            console.print(f"[cyan]Verbose:[/cyan] Results: {passed} passed, {failed} failed")
        
        # Display results
        _display_results(
            results, 
            output_format=output, 
            dev_mode=dev, 
            workflow_mode=workflow, 
            domain=f"{benchmark.upper()}_benchmark",
            summary_only=summary_only,
            format_template=format_template
        )
        
        # Show timing if requested
        if timing:
            input_size = len(json.dumps(agent_outputs))
            _display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            console.print(f"\n[blue]📤 Exporting {benchmark.upper()} benchmark results...[/blue]")
            _export_results(
                results, 
                export_format=export, 
                domain=f"{benchmark}_{domain}", 
                output_dir=output_dir, 
                format_template=format_template, 
                summary_only=summary_only
            )
        
        # Show next steps
        console.print(f"\n[bold green]🎉 {benchmark.upper()} Benchmark Complete![/bold green]")
        console.print("\n[bold blue]📊 Benchmark Insights:[/bold blue]")
        
        # Calculate pass rate
        passed = sum(1 for r in results if r.passed)
        pass_rate = (passed / len(results) * 100) if results else 0
        
        if pass_rate >= 80:
            console.print(f"✅ [green]Strong performance on {benchmark.upper()}: {pass_rate:.1f}% pass rate[/green]")
        elif pass_rate >= 60:
            console.print(f"⚡ [yellow]Moderate performance on {benchmark.upper()}: {pass_rate:.1f}% pass rate[/yellow]")
        else:
            console.print(f"🔴 [red]Needs improvement on {benchmark.upper()}: {pass_rate:.1f}% pass rate[/red]")
        
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        console.print(f"1. Try other benchmarks: [green]arc-eval --benchmark {'mmlu' if benchmark != 'mmlu' else 'humeval'} --limit {limit}[/green]")
        console.print(f"2. Increase test size: [green]arc-eval --benchmark {benchmark} --limit {limit * 2}[/green]")
        if benchmark == "mmlu" and not subset:
            console.print(f"3. Try specific subject: [green]arc-eval --benchmark mmlu --subset anatomy --limit {limit}[/green]")
        console.print(f"4. Use with your data: [green]arc-eval --domain {domain} --input your_outputs.json[/green]")
        
        # Set exit code based on critical failures
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        if critical_failures > 0:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Exiting with code 1 due to {critical_failures} critical failures")
            sys.exit(1)
            
    except Exception as e:
        if dev:
            console.print("\n[red]❌ Benchmark Evaluation Error (Debug Mode)[/red]")
            console.print_exception()
        else:
            console.print(f"\n[red]❌ Benchmark Evaluation Failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            console.print("[bold blue]💡 Troubleshooting:[/bold blue]")
            console.print("• Use --dev flag for detailed error info")
            console.print("• Check internet connection for dataset downloads")
            console.print("• Try with smaller limit")
            console.print("• Try without subset parameter")
            
        sys.exit(1)


def _handle_judge_comparison(compare_judges_config: Path, agent_outputs: List[AgentOutput], default_domain: Optional[str]) -> None:
    """Handle judge comparison mode evaluation."""
    console.print("\n[bold blue]🔬 Judge Comparison Mode[/bold blue]")
    console.print("[dim]A/B testing different judge configurations for optimization[/dim]")
    
    try:
        # Load comparison configuration
        with open(compare_judges_config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Extract judge configurations
        judge_configs = []
        if 'judges' in config_data:
            # Direct configuration
            judges_config = config_data['judges']
        elif 'default_comparison' in config_data:
            # Use default comparison template
            judges_config = config_data['default_comparison']['judges']
        else:
            # Try first available template
            first_key = list(config_data.keys())[0]
            judges_config = config_data[first_key]['judges']
        
        for judge_config in judges_config:
            config = JudgeConfig(
                name=judge_config['name'],
                domain=judge_config.get('domain', default_domain or 'security'),
                enable_confidence_calibration=judge_config.get('enable_confidence_calibration', False),
                enable_verification=judge_config.get('enable_verification', False),
                description=judge_config.get('description', '')
            )
            judge_configs.append(config)
        
        console.print(f"🧪 Comparing {len(judge_configs)} judge configurations:")
        for config in judge_configs:
            console.print(f"  • {config.name}: {config.description}")
        
        # Create sample scenarios for comparison
        from agent_eval.core.engine import EvaluationEngine
        sample_domain = judge_configs[0].domain if judge_configs else (default_domain or 'security')
        engine = EvaluationEngine(sample_domain)
        
        # Use first few scenarios for comparison
        scenarios = engine.eval_pack.scenarios[:min(5, len(agent_outputs))]
        
        # Convert raw agent outputs to AgentOutput objects
        agent_output_objects = [AgentOutput.from_raw(output) for output in agent_outputs]
        
        # Run comparison
        comparison = JudgeComparison()
        
        console.print("\n⚡ Running judge comparison...")
        with console.status("[bold green]Evaluating with different judges..."):
            report = comparison.compare_judges(
                judge_configs=judge_configs,
                scenarios=scenarios,
                agent_outputs=agent_output_objects[:len(scenarios)],
                max_workers=2
            )
        
        # Display results
        console.print("\n[bold green]📊 Judge Comparison Results[/bold green]")
        console.print(f"Execution time: {report.execution_time:.2f}s")
        console.print(f"Best configuration: [yellow]{report.best_judge_config}[/yellow]")
        
        # Show agreement scores
        console.print("\n[bold blue]🤝 Inter-Judge Agreement:[/bold blue]")
        agreement_table = Table(show_header=True, header_style="bold blue")
        agreement_table.add_column("Judge Configuration")
        agreement_table.add_column("Agreement Score")
        agreement_table.add_column("Performance")
        
        for judge_name, agreement in report.judge_agreements.items():
            performance = "🟢 Excellent" if agreement > 0.8 else "🟡 Good" if agreement > 0.6 else "🔴 Needs Work"
            agreement_table.add_row(judge_name, f"{agreement:.3f}", performance)
        
        console.print(agreement_table)
        
        # Show recommendations
        if report.recommendations:
            console.print("\n[bold blue]💡 Recommendations:[/bold blue]")
            for i, rec in enumerate(report.recommendations, 1):
                console.print(f"{i}. {rec}")
        
        # Show performance metrics if available
        if report.performance_metrics:
            console.print("\n[bold blue]⚡ Performance Metrics:[/bold blue]")
            perf_table = Table(show_header=True, header_style="bold blue")
            perf_table.add_column("Judge")
            perf_table.add_column("Avg Time (s)")
            perf_table.add_column("Consistency")
            
            for judge_name, metrics in report.performance_metrics.items():
                consistency = f"{metrics.consistency_score:.3f}"
                perf_table.add_row(
                    judge_name, 
                    f"{metrics.avg_evaluation_time:.2f}",
                    consistency
                )
            
            console.print(perf_table)
        
        console.print("\n[bold green]✅ Judge comparison completed successfully![/bold green]")
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        console.print(f"1. Use best config: [green]arc-eval --domain {sample_domain} --input your_data.json --agent-judge[/green]")
        console.print("2. Try different templates in config/judge_comparison_templates.yaml")
        console.print("3. Customize configurations based on recommendations")
        
    except Exception as e:
        console.print(f"\n[red]❌ Judge Comparison Failed[/red]")
        console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
        
        console.print("[bold blue]💡 Troubleshooting:[/bold blue]")
        console.print("• Check YAML configuration file format")
        console.print("• Ensure ANTHROPIC_API_KEY is set")
        console.print("• Try with --dev flag for detailed error info")
        console.print("• Use provided template: config/judge_comparison_templates.yaml")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
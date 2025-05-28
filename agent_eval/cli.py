#!/usr/bin/env python3
"""
ARC-Eval CLI - Lightweight command router.

Provides domain-specific evaluation and compliance reporting for LLMs and AI agents.
Routes commands to specialized handlers for better maintainability.
"""

# Load environment variables from .env file early
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

# Import command handlers
from agent_eval.commands import (
    ReliabilityCommandHandler,
    ComplianceCommandHandler,
    WorkflowCommandHandler,
    BenchmarkCommandHandler
)

console = Console()


def _get_domain_info() -> dict:
    """Get centralized domain information to avoid duplication."""
    return {
        "finance": {
            "name": "Financial Services Compliance",
            "description": "Enterprise-grade evaluations for financial AI systems",
            "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "FFIEC", "DORA", "OFAC", "CFPB", "EU-AI-ACT"],
            "scenarios": 110,
            "use_cases": "Banking, Fintech, Payment Processing, Insurance, Investment",
            "examples": "Transaction approval, KYC verification, Fraud detection, Credit scoring"
        },
        "security": {
            "name": "Cybersecurity & AI Agent Security", 
            "description": "AI safety evaluations for security-critical applications",
            "frameworks": ["OWASP-LLM-TOP-10", "NIST-AI-RMF", "ISO-27001", "SOC2-TYPE-II", "MITRE-ATTACK"],
            "scenarios": 120,
            "use_cases": "AI Agents, Chatbots, Code Generation, Security Tools",
            "examples": "Prompt injection, Data leakage, Code security, Access control"
        },
        "ml": {
            "name": "ML Infrastructure & Safety",
            "description": "ML ops, safety, and bias evaluation for AI systems",
            "frameworks": ["NIST-AI-RMF", "IEEE-2857", "ISO-23053", "GDPR-AI", "EU-AI-ACT"],
            "scenarios": 107,
            "use_cases": "ML Models, AI Pipelines, Model Serving, Training",
            "examples": "Bias detection, Model safety, Explainability, Performance"
        }
    }


def _display_list_domains() -> None:
    """Display available domains and their information."""
    domains_info = _get_domain_info()
    
    console.print("\n[bold blue]🎯 Available Evaluation Domains[/bold blue]")
    console.print("[blue]" + "═" * 70 + "[/blue]")
    
    for domain_key, domain_data in domains_info.items():
        console.print(f"\n[bold cyan]{domain_key.upper()}[/bold cyan] - {domain_data['name']}")
        console.print(f"📄 {domain_data['description']}")
        console.print(f"📊 {domain_data['scenarios']} scenarios | Use cases: {domain_data['use_cases']}")
        console.print(f"⚖️  Frameworks: {', '.join(domain_data['frameworks'][:3])}{'...' if len(domain_data['frameworks']) > 3 else ''}")
        console.print(f"💡 Examples: {domain_data['examples']}")
        console.print(f"🚀 Quick start: [green]arc-eval --domain {domain_key} --quick-start[/green]")
        console.print("[blue]" + "─" * 70 + "[/blue]")
    
    console.print("\n[bold blue]💡 Getting Started:[/bold blue]")
    console.print("1. [yellow]Choose your domain:[/yellow] [green]arc-eval --domain finance --quick-start[/green]")
    console.print("2. [yellow]Test with your data:[/yellow] [green]arc-eval --domain finance --input your_data.json[/green]")
    console.print("3. [yellow]Generate audit report:[/yellow] [green]arc-eval --domain finance --input data.json --export pdf[/green]")


def _display_help_input() -> None:
    """Display detailed input format documentation."""
    console.print("\n[bold blue]📖 Input Format Documentation[/bold blue]")
    console.print("[blue]" + "═" * 70 + "[/blue]")
    
    console.print("\n[bold green]✅ Supported Input Formats:[/bold green]")
    console.print("1. [yellow]Simple Agent Output (Recommended):[/yellow]")
    console.print('   {"output": "Transaction approved", "metadata": {"scenario_id": "fin_001"}}')
    
    console.print("\n2. [yellow]OpenAI API Format:[/yellow]")
    console.print('   {"choices": [{"message": {"content": "Analysis complete"}}]}')
    
    console.print("\n3. [yellow]Anthropic API Format:[/yellow]")
    console.print('   {"content": [{"text": "Compliance check passed"}]}')
    
    console.print("\n4. [yellow]Array of Outputs:[/yellow]")
    console.print('   [{"output": "Result 1"}, {"output": "Result 2"}]')
    
    console.print("\n[bold blue]📊 Complete Example:[/bold blue]")
    example = """{
  "output": "Transaction approved after KYC verification",
  "metadata": {
    "scenario_id": "fin_kyc_001",
    "timestamp": "2024-05-27T10:30:00Z",
    "agent_version": "v1.2.3"
  },
  "reasoning": "Customer passed all verification checks",
  "confidence": 0.95
}"""
    console.print(f"[dim]{example}[/dim]")
    
    console.print("\n[bold blue]🚀 Quick Testing:[/bold blue]")
    console.print("• Validate format: [green]arc-eval --validate --input your_file.json[/green]")
    console.print("• Test with demo: [green]arc-eval --quick-start --domain finance[/green]")
    console.print("• Pipe input: [green]echo '{\"output\": \"test\"}' | arc-eval --domain finance --stdin[/green]")


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option("--domain", type=click.Choice(["finance", "security", "ml"]), help="Select evaluation domain pack (required for CLI mode)")
@click.option("--input", "input_file", type=click.Path(exists=True, path_type=Path), help="Input file containing agent/LLM outputs (JSON format)")
@click.option("--stdin", is_flag=True, help="Read input from stdin (pipe) instead of file")
@click.option("--endpoint", type=str, help="API endpoint to fetch agent outputs from (alternative to --input)")
@click.option("--export", type=click.Choice(["pdf", "csv", "json"]), help="Export audit report in specified format")
@click.option("--output", type=click.Choice(["table", "json", "csv"]), default="table", help="Output format for CLI results")
@click.option("--dev", is_flag=True, help="Enable developer mode with verbose output")
@click.option("--workflow", is_flag=True, help="Enable workflow/audit mode for compliance reporting")
@click.option("--config", type=click.Path(exists=True, path_type=Path), help="Custom evaluation configuration file")
@click.option("--help-input", is_flag=True, help="Show detailed input format documentation and examples")
@click.option("--list-domains", is_flag=True, help="List available evaluation domains and their descriptions")
@click.option("--timing", is_flag=True, help="Show execution time and performance metrics")
@click.option("--performance", is_flag=True, help="Enable comprehensive performance tracking (runtime, memory, cost efficiency)")
@click.option("--reliability", is_flag=True, help="Enable reliability evaluation (tool call validation, error recovery analysis)")
@click.option("--verbose", is_flag=True, help="Enable verbose logging with detailed debugging information")
@click.option("--quick-start", is_flag=True, help="Run demo evaluation with built-in sample data (no input file required)")
@click.option("--validate", is_flag=True, help="Validate input file format without running evaluation")
@click.option("--output-dir", type=click.Path(path_type=Path), help="Custom directory for exported reports (default: current directory)")
@click.option("--format-template", type=click.Choice(["executive", "technical", "compliance", "minimal"]), help="Report formatting template for different audiences")
@click.option("--summary-only", is_flag=True, help="Generate executive summary only (skip detailed scenarios)")
@click.option("--agent-judge", is_flag=True, help="Use Agent-as-a-Judge evaluation with continuous feedback (requires API key)")
@click.option("--judge-model", type=click.Choice(["claude-sonnet-4-20250514", "claude-3-5-haiku-latest", "auto"]), default="auto", help="Select AI model: claude-sonnet-4-20250514 (primary), claude-3-5-haiku-latest (cost-optimized), auto (smart selection)")
@click.option("--benchmark", type=click.Choice(["mmlu", "humeval", "gsm8k"]), help="Use external benchmark for evaluation (MMLU, HumanEval, GSM8K)")
@click.option("--subset", type=str, help="Benchmark subset (e.g., 'anatomy' for MMLU)")
@click.option("--limit", type=int, default=10, help="Limit number of benchmark scenarios to evaluate (default: 10)")
@click.option("--verify", is_flag=True, help="Enable verification layer for improved judgment reliability")
@click.option("--confidence-calibration", is_flag=True, help="Enable confidence calibration with enhanced uncertainty quantification")
@click.option("--compare-judges", type=click.Path(exists=True, path_type=Path), help="A/B test different judge configurations using YAML config file")
@click.option("--no-interaction", is_flag=True, help="Skip interactive Q&A session after evaluation results")
@click.option("--improvement-plan", is_flag=True, help="Generate actionable improvement plan from evaluation results")
@click.option("--from-evaluation", "from_evaluation", type=click.Path(exists=True, path_type=Path), help="Source evaluation file for improvement plan generation")
@click.option("--baseline", type=click.Path(exists=True, path_type=Path), help="Baseline evaluation file for before/after comparison")
@click.option("--continue", "continue_workflow", is_flag=True, help="Continue from the most recent evaluation (auto-detects workflow state)")
@click.option("--audit", is_flag=True, help="Audit mode: enables agent-judge + PDF export + compliance template (enterprise workflow)")
@click.option("--dev-mode", "dev_mode", is_flag=True, help="Developer mode: enables agent-judge + haiku model + dev + verbose (cost-optimized)")
@click.option("--full-cycle", "full_cycle", is_flag=True, help="Full workflow: evaluation → improvement plan → comparison (complete automation)")
@click.option("--debug-agent", is_flag=True, help="Launch unified agent debugging mode with failure analysis")
@click.option("--workflow-reliability", is_flag=True, help="Focus evaluation on workflow reliability metrics")
@click.option("--unified-debug", is_flag=True, help="Single view of tool calls, prompts, memory, timeouts, hallucinations")
@click.option("--framework", type=click.Choice(["langchain", "langgraph", "crewai", "autogen", "openai", "anthropic", "google_adk", "nvidia_aiq", "agno", "generic"]), help="Optimize analysis for specific agent framework (auto-detected if not specified)")
@click.version_option(version="0.2.5", prog_name="arc-eval")
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
    no_interaction: bool,
    improvement_plan: bool,
    from_evaluation: Optional[Path],
    baseline: Optional[Path],
    continue_workflow: bool,
    audit: bool,
    dev_mode: bool,
    full_cycle: bool,
    debug_agent: bool,
    workflow_reliability: bool,
    unified_debug: bool,
    framework: Optional[str],
) -> None:
    """
    ARC-Eval: Agentic Workflow Reliability Platform + Enterprise Compliance.
    
    Debug agent failures with unified visibility across the entire stack.
    Built-in compliance frameworks: 355 scenarios across finance, security, ML.
    Get AI-powered reliability analysis with actionable remediation guidance.
    
    🚀 QUICK START:
    
      # Debug agent workflow failures (NEW!)
      arc-eval --debug-agent --input agent_outputs.json
      
      # Unified debugging view (NEW!)
      arc-eval --unified-debug --input workflow_trace.json
      
      # Framework-specific reliability analysis (NEW!)
      arc-eval --workflow-reliability --framework langchain --input outputs.json
      
      # Traditional compliance evaluation (355 scenarios available)
      arc-eval --domain finance --input your_outputs.json --agent-judge
      
      # Generate executive compliance report
      arc-eval --domain finance --input outputs.json --export pdf --workflow
    """
    
    # Handle informational commands first
    if help_input:
        _display_help_input()
        return
    
    if list_domains:
        _display_list_domains()
        return
    
    # Handle judge comparison mode (special case)
    if compare_judges:
        from agent_eval.analysis.judge_comparison import JudgeComparison, JudgeConfig
        
        # Load agent outputs for comparison
        try:
            from agent_eval.evaluation.validators import InputValidator
            
            if input_file:
                with open(input_file, 'r') as f:
                    raw_data = f.read()
                agent_outputs, _ = InputValidator.validate_json_input(raw_data, str(input_file))
            elif stdin:
                raw_data = sys.stdin.read()
                agent_outputs, _ = InputValidator.validate_json_input(raw_data, "stdin")
            else:
                console.print("[red]Error:[/red] --input or --stdin required for judge comparison")
                sys.exit(1)
                
            # Run judge comparison
            comparison = JudgeComparison(compare_judges, default_domain=domain)
            comparison.run_comparison(agent_outputs)
            return
            
        except Exception as e:
            console.print(f"[red]Judge comparison failed:[/red] {e}")
            if dev:
                console.print_exception()
            sys.exit(1)
    
    # Collect all parameters for handlers
    handler_kwargs = {
        'domain': domain,
        'input_file': input_file,
        'stdin': stdin,
        'endpoint': endpoint,
        'export': export,
        'output': output,
        'dev': dev,
        'workflow': workflow,
        'config': config,
        'timing': timing,
        'performance': performance,
        'reliability': reliability,
        'verbose': verbose,
        'output_dir': output_dir,
        'format_template': format_template,
        'summary_only': summary_only,
        'agent_judge': agent_judge,
        'judge_model': judge_model,
        'verify': verify,
        'confidence_calibration': confidence_calibration,
        'no_interaction': no_interaction,
        'baseline': baseline,
        'framework': framework
    }
    
    # Apply shortcut command modifications
    if audit:
        console.print("[blue]🔧 Audit Mode:[/blue] Enabling enterprise compliance workflow")
        handler_kwargs['agent_judge'] = True
        handler_kwargs['export'] = handler_kwargs['export'] or 'pdf'
        handler_kwargs['format_template'] = handler_kwargs['format_template'] or 'compliance'
        console.print("  ✓ Agent-as-a-Judge enabled")
        console.print("  ✓ PDF export enabled")
        console.print("  ✓ Compliance template selected")
    
    if dev_mode:
        console.print("[blue]🔧 Developer Mode:[/blue] Enabling cost-optimized development workflow")
        handler_kwargs['agent_judge'] = True
        handler_kwargs['judge_model'] = 'claude-3-5-haiku-latest'
        handler_kwargs['dev'] = True
        handler_kwargs['verbose'] = True
        console.print("  ✓ Agent-as-a-Judge enabled with Haiku model")
        console.print("  ✓ Development and verbose logging enabled")
    
    # Route to appropriate command handler based on primary command
    exit_code = 0
    
    try:
        # Reliability commands (highest priority)
        if debug_agent or unified_debug or workflow_reliability:
            handler_kwargs.update({
                'debug_agent': debug_agent,
                'unified_debug': unified_debug,
                'workflow_reliability': workflow_reliability
            })
            handler = ReliabilityCommandHandler()
            exit_code = handler.execute(**handler_kwargs)
        
        # Benchmark commands
        elif benchmark or quick_start or validate:
            handler_kwargs.update({
                'benchmark': benchmark,
                'subset': subset,
                'limit': limit,
                'quick_start': quick_start,
                'validate': validate
            })
            handler = BenchmarkCommandHandler()
            exit_code = handler.execute(**handler_kwargs)
        
        # Workflow commands
        elif improvement_plan or continue_workflow or full_cycle:
            handler_kwargs.update({
                'improvement_plan': improvement_plan,
                'from_evaluation': from_evaluation,
                'continue_workflow': continue_workflow,
                'full_cycle': full_cycle
            })
            handler = WorkflowCommandHandler()
            exit_code = handler.execute(**handler_kwargs)
        
        # Compliance commands (domain-specific evaluation)
        elif domain:
            handler = ComplianceCommandHandler()
            exit_code = handler.execute(**handler_kwargs)
        
        # No command specified
        else:
            console.print("[red]Error:[/red] No command specified")
            console.print("Use [green]arc-eval --help[/green] to see available options")
            console.print("Quick start: [green]arc-eval --quick-start[/green]")
            exit_code = 1
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        exit_code = 130
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if dev or verbose:
            console.print_exception()
        exit_code = 1
    
    # Handle baseline comparison if specified
    if baseline and exit_code == 0:
        try:
            # Load current evaluation data for comparison
            import json
            
            # Find the most recent evaluation file
            cwd = Path.cwd()
            pattern = "*evaluation_*.json"
            evaluation_files = list(cwd.glob(pattern))
            
            if evaluation_files:
                # Sort by modification time, newest first
                evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                current_evaluation_file = evaluation_files[0]
                
                # Load evaluation data
                with open(current_evaluation_file, 'r') as f:
                    current_evaluation_data = json.load(f)
                
                # Run baseline comparison
                console.print(f"\n[bold blue]📊 Baseline Comparison[/bold blue]")
                console.print(f"Comparing with baseline: {baseline}")
                
                workflow_handler = WorkflowCommandHandler()
                workflow_handler._handle_baseline_comparison(
                    current_evaluation_data=current_evaluation_data,
                    baseline=baseline,
                    domain=domain or "generic",
                    output_dir=output_dir,
                    dev=dev,
                    verbose=verbose
                )
                
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Baseline comparison failed: {e}")
            if dev:
                console.print_exception()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
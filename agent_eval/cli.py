#!/usr/bin/env python3
"""
ARC-Eval CLI - Unified command interface with backward compatibility.

Provides three simple workflows:
- debug: Why is my agent failing?
- compliance: Does it meet requirements?
- improve: How do I make it better?

Legacy CLI with 20+ flags is maintained for backward compatibility.
"""

# Load environment variables from .env file early
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box
from rich.prompt import Prompt, Confirm

# Import command handlers
from agent_eval.commands import (
    ReliabilityCommandHandler,
    ComplianceCommandHandler,
    WorkflowCommandHandler,
    BenchmarkCommandHandler
)
from agent_eval.core.constants import DOMAIN_SCENARIO_COUNTS
from agent_eval.ui.result_renderer import ResultRenderer

console = Console()

# Workflow tracking file
WORKFLOW_STATE_FILE = Path(".arc-eval-workflow-state.json")


# ==================== Workflow State Management ====================

def load_workflow_state() -> Dict[str, Any]:
    """Load workflow state from disk."""
    if WORKFLOW_STATE_FILE.exists():
        with open(WORKFLOW_STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_workflow_state(state: Dict[str, Any]) -> None:
    """Save workflow state to disk."""
    with open(WORKFLOW_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def update_workflow_progress(workflow: str, **kwargs) -> None:
    """Update workflow progress tracking."""
    state = load_workflow_state()
    
    if 'current_cycle' not in state:
        state['current_cycle'] = {
            'started_at': datetime.now().isoformat(),
            'debug': None,
            'compliance': None,
            'improve': None
        }
    
    state['current_cycle'][workflow] = {
        'completed_at': datetime.now().isoformat(),
        **kwargs
    }
    
    # Track history
    if 'history' not in state:
        state['history'] = []
    
    # If all three workflows completed, archive the cycle
    if all(state['current_cycle'].get(w) for w in ['debug', 'compliance', 'improve']):
        state['history'].append(state['current_cycle'])
        state['current_cycle'] = {
            'started_at': datetime.now().isoformat(),
            'debug': None,
            'compliance': None,
            'improve': None
        }
    
    save_workflow_state(state)


def get_next_workflow_suggestion(current_workflow: str) -> str:
    """Get suggested next command based on current workflow."""
    state = load_workflow_state()
    cycle = state.get('current_cycle', {})
    
    suggestions = {
        'debug': {
            'next': 'compliance',
            'command': lambda: f"arc-eval compliance --domain [finance|security|ml] --input {cycle.get('debug', {}).get('input_file', 'outputs.json')}"
        },
        'compliance': {
            'next': 'improve',
            'command': lambda: f"arc-eval improve --from-evaluation {cycle.get('compliance', {}).get('evaluation_file', 'latest')}"
        },
        'improve': {
            'next': 'debug',
            'command': lambda: "arc-eval debug --input improved_outputs.json"
        }
    }
    
    if current_workflow in suggestions:
        next_wf = suggestions[current_workflow]
        return f"\n🔄 Next Step: Run '{next_wf['command']()}' to continue the improvement cycle"
    
    return ""


# ==================== Unified CLI Commands ====================

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.2.5", prog_name="arc-eval")
def cli(ctx):
    """
    ARC-Eval: Debug, Comply, Improve - The complete agent improvement lifecycle.
    
    Three simple commands:
    
    \b
    • debug      - Why is my agent failing?
    • compliance - Does it meet requirements?  
    • improve    - How do I make it better?
    
    Run 'arc-eval COMMAND --help' for more information on a command.
    """
    # If no command provided, show interactive workflow selector
    if ctx.invoked_subcommand is None:
        show_workflow_selector()


def show_workflow_selector():
    """Interactive workflow selector when no command is specified."""
    console.print("\n[bold blue]🚀 ARC-Eval Unified Workflow[/bold blue]")
    console.print("=" * 60)
    
    # Create workflow options table
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Option", style="cyan", width=12)
    table.add_column("Workflow", style="bold")
    table.add_column("Purpose")
    
    table.add_row("1", "debug", "Why is my agent failing?")
    table.add_row("2", "compliance", "Does it meet requirements?")
    table.add_row("3", "improve", "How do I make it better?")
    
    console.print(table)
    console.print()
    
    # Check workflow state for suggestions
    state = load_workflow_state()
    if state.get('current_cycle'):
        cycle = state['current_cycle']
        if cycle.get('debug') and not cycle.get('compliance'):
            console.print("[yellow]💡 Suggestion: You've completed debug. Consider running compliance next.[/yellow]\n")
        elif cycle.get('compliance') and not cycle.get('improve'):
            console.print("[yellow]💡 Suggestion: You've completed compliance. Consider running improve next.[/yellow]\n")
    
    choice = Prompt.ask(
        "Select workflow",
        choices=["1", "2", "3", "debug", "compliance", "improve", "q"],
        default="q"
    )
    
    if choice in ["1", "debug"]:
        console.print("\n[green]Run:[/green] arc-eval debug --input <your_agent_trace.json>")
    elif choice in ["2", "compliance"]:
        console.print("\n[green]Run:[/green] arc-eval compliance --domain [finance|security|ml] --input <outputs.json>")
    elif choice in ["3", "improve"]:
        console.print("\n[green]Run:[/green] arc-eval improve --from-evaluation <evaluation_file.json>")
    else:
        console.print("\n[dim]Exiting...[/dim]")


@cli.command()
@click.option('--input', 'input_file', type=click.Path(exists=True, path_type=Path), required=True, help='Agent trace or output file to debug')
@click.option('--framework', type=click.Choice(['langchain', 'langgraph', 'crewai', 'autogen', 'openai', 'anthropic', 'generic']), help='Framework (auto-detected if not specified)')
@click.option('--output-format', type=click.Choice(['console', 'json', 'html']), default='console', help='Output format')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def debug(input_file: Path, framework: Optional[str], output_format: str, verbose: bool):
    """
    Debug agent failures with comprehensive analysis.
    
    Analyzes your agent's outputs to identify:
    • Framework-specific performance issues
    • Tool call failures and schema mismatches
    • Memory bloat and timeout problems
    • Hallucinations and error patterns
    
    Example:
        arc-eval debug --input agent_trace.json
    """
    console.print("\n[bold blue]🔍 Agent Debug Analysis[/bold blue]")
    console.print("=" * 60)
    
    try:
        # Use ReliabilityCommandHandler with unified debugging enabled
        handler = ReliabilityCommandHandler()
        
        # Execute with unified debugging features
        exit_code = handler.execute(
            input_file=input_file,
            framework=framework,
            unified_debug=True,  # Enable unified debugging
            workflow_reliability=True,  # Enable workflow analysis
            schema_validation=True,  # Enable schema validation
            verbose=verbose,
            output=output_format,
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
            console.print(get_next_workflow_suggestion('debug'))
        
        return exit_code
        
    except Exception as e:
        console.print(f"[red]Debug failed:[/red] {e}")
        if verbose:
            console.print_exception()
        return 1


@cli.command()
@click.option('--domain', type=click.Choice(['finance', 'security', 'ml']), required=True, help='Evaluation domain')
@click.option('--input', 'input_file', type=click.Path(exists=True, path_type=Path), required=True, help='Agent outputs to evaluate')
@click.option('--export', type=click.Choice(['pdf', 'csv', 'json']), help='Export format (auto-exports PDF by default)')
@click.option('--no-export', is_flag=True, help='Disable automatic PDF export')
@click.option('--quick-start', is_flag=True, help='Run with sample data')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def compliance(domain: str, input_file: Optional[Path], export: Optional[str], no_export: bool, quick_start: bool, verbose: bool):
    """
    Evaluate agent compliance against domain requirements.
    
    Runs comprehensive evaluation across:
    • Finance: SOX, KYC, AML, PCI-DSS, GDPR (110 scenarios)
    • Security: OWASP, NIST AI-RMF, ISO 27001 (120 scenarios)
    • ML: EU AI Act, IEEE Ethics, Model Cards (148 scenarios)
    
    Example:
        arc-eval compliance --domain finance --input outputs.json
    """
    console.print(f"\n[bold blue]✅ Compliance Evaluation - {domain.upper()}[/bold blue]")
    console.print("=" * 60)
    
    try:
        # Use ComplianceCommandHandler with smart defaults
        handler = ComplianceCommandHandler()
        
        # Smart defaults for compliance workflow
        if not no_export and not export:
            export = 'pdf'  # Auto-export PDF for audit trail
        
        # Execute compliance evaluation
        exit_code = handler.execute(
            domain=domain,
            input_file=input_file,
            quick_start=quick_start,
            agent_judge=True,  # Always use agent-judge for compliance
            export=export,
            format_template='compliance',  # Use compliance template
            workflow=True,  # Enable workflow mode
            verbose=verbose,
            output='table',
            # Performance tracking for compliance
            performance=True,
            timing=True
        )
        
        if exit_code == 0:
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
            
            # Show next step suggestion
            console.print(get_next_workflow_suggestion('compliance'))
        
        return exit_code
        
    except Exception as e:
        console.print(f"[red]Compliance evaluation failed:[/red] {e}")
        if verbose:
            console.print_exception()
        return 1


@cli.command()
@click.option('--from-evaluation', 'evaluation_file', type=click.Path(exists=True, path_type=Path), help='Generate plan from evaluation file')
@click.option('--baseline', type=click.Path(exists=True, path_type=Path), help='Baseline evaluation for comparison')
@click.option('--current', type=click.Path(exists=True, path_type=Path), help='Current evaluation for comparison')
@click.option('--auto-detect', is_flag=True, help='Auto-detect latest evaluation file')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def improve(evaluation_file: Optional[Path], baseline: Optional[Path], current: Optional[Path], auto_detect: bool, verbose: bool):
    """
    Generate and track improvement plans.
    
    Creates actionable improvement plans with:
    • Prioritized fixes for failed scenarios
    • Expected improvement projections
    • Step-by-step implementation guidance
    • Progress tracking between versions
    
    Examples:
        arc-eval improve --from-evaluation latest
        arc-eval improve --baseline v1.json --current v2.json
    """
    console.print("\n[bold blue]📈 Improvement Workflow[/bold blue]")
    console.print("=" * 60)
    
    try:
        # Auto-detect latest evaluation if needed
        if not evaluation_file and (auto_detect or not (baseline and current)):
            state = load_workflow_state()
            cycle = state.get('current_cycle', {})
            
            # Try to get evaluation file from workflow state
            if cycle.get('compliance', {}).get('evaluation_file'):
                evaluation_file = Path(cycle['compliance']['evaluation_file'])
                console.print(f"[green]Auto-detected evaluation:[/green] {evaluation_file}")
            else:
                # Find latest evaluation file
                evaluation_files = list(Path.cwd().glob("*_evaluation_*.json"))
                if evaluation_files:
                    evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    evaluation_file = evaluation_files[0]
                    console.print(f"[green]Using latest evaluation:[/green] {evaluation_file}")
        
        # Use WorkflowCommandHandler
        handler = WorkflowCommandHandler()
        
        if baseline and current:
            # Comparison mode
            exit_code = handler.execute(
                baseline=baseline,
                input_file=current,  # Current file as input
                domain='generic',  # Will be detected from files
                verbose=verbose,
                output='table'
            )
        else:
            # Improvement plan generation
            exit_code = handler.execute(
                improvement_plan=True,
                from_evaluation=evaluation_file,
                verbose=verbose,
                output='table',
                # Auto-generate training data
                dev=True  # Enable self-improvement features
            )
        
        if exit_code == 0:
            update_workflow_progress('improve',
                evaluation_file=str(evaluation_file) if evaluation_file else None,
                baseline=str(baseline) if baseline else None,
                current=str(current) if current else None,
                timestamp=datetime.now().isoformat()
            )
            
            # Show next step suggestion
            console.print(get_next_workflow_suggestion('improve'))
        
        return exit_code
        
    except Exception as e:
        console.print(f"[red]Improvement workflow failed:[/red] {e}")
        if verbose:
            console.print_exception()
        return 1


# ==================== Legacy CLI Support ====================

def _get_domain_info() -> dict:
    """Get centralized domain information to avoid duplication."""
    return {
        "finance": {
            "name": "Financial Services Compliance",
            "description": "Enterprise-grade evaluations for financial AI systems",
            "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "FFIEC", "DORA", "OFAC", "CFPB", "EU-AI-ACT"],
            "scenarios": DOMAIN_SCENARIO_COUNTS["finance"],
            "use_cases": "Banking, Fintech, Payment Processing, Insurance, Investment",
            "examples": "Transaction approval, KYC verification, Fraud detection, Credit scoring"
        },
        "security": {
            "name": "Cybersecurity & AI Agent Security", 
            "description": "AI safety evaluations for security-critical applications",
            "frameworks": ["OWASP-LLM-TOP-10", "NIST-AI-RMF", "ISO-27001", "SOC2-TYPE-II", "MITRE-ATTACK"],
            "scenarios": DOMAIN_SCENARIO_COUNTS["security"],
            "use_cases": "AI Agents, Chatbots, Code Generation, Security Tools",
            "examples": "Prompt injection, Data leakage, Code security, Access control"
        },
        "ml": {
            "name": "ML Infrastructure & Safety",
            "description": "ML ops, safety, and bias evaluation for AI systems",
            "frameworks": ["NIST-AI-RMF", "IEEE-2857", "ISO-23053", "GDPR-AI", "EU-AI-ACT"],
            "scenarios": DOMAIN_SCENARIO_COUNTS["ml"],
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


@cli.command('legacy', hidden=True)
@click.pass_context
def legacy_cli(ctx):
    """Legacy CLI interface (deprecated)."""
    console.print("[yellow]Warning: You're using the legacy CLI interface.[/yellow]")
    console.print("[yellow]Please migrate to the new unified commands: debug, compliance, improve[/yellow]\n")
    
    # Pass through to legacy CLI
    sys.argv = ['arc-eval'] + sys.argv[2:]  # Remove 'legacy' from args
    legacy_main()


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
@click.option("--schema-validation", is_flag=True, help="Detect prompt-tool mismatch and auto-generate LLM-friendly schemas")
@click.version_option(version="0.2.5", prog_name="arc-eval")
def legacy_main(
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
    schema_validation: bool,
) -> None:
    """
    ARC-Eval: Agentic Workflow Reliability Platform + Enterprise Compliance.
    
    Debug agent failures with unified visibility across the entire stack.
    Built-in compliance frameworks: 378 scenarios across finance, security, ML.
    Get AI-powered reliability analysis with actionable remediation guidance.
    
    🚀 QUICK START:
    
      # Debug agent workflow failures (NEW!)
      arc-eval --debug-agent --input agent_outputs.json
      
      # Unified debugging view (NEW!)
      arc-eval --unified-debug --input workflow_trace.json
      
      # Framework-specific reliability analysis (NEW!)
      arc-eval --workflow-reliability --framework langchain --input outputs.json
      
      # Traditional compliance evaluation (378 scenarios available)
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
        from agent_eval.analysis.judge_comparison import JudgeComparison
        
        # Load agent outputs for comparison
        try:
            from agent_eval.evaluation.validators import InputValidator
            from agent_eval.core.types import AgentOutput
            
            if input_file:
                with open(input_file, 'r') as f:
                    raw_data = f.read()
                parsed_data, _ = InputValidator.validate_json_input(raw_data, str(input_file))
            elif stdin:
                raw_data = sys.stdin.read()
                parsed_data, _ = InputValidator.validate_json_input(raw_data, "stdin")
            else:
                console.print("[red]Error:[/red] --input or --stdin required for judge comparison")
                sys.exit(1)
            
            # Convert to AgentOutput objects
            agent_outputs = []
            if isinstance(parsed_data, list):
                for item in parsed_data:
                    agent_outputs.append(AgentOutput.from_raw(item))
            else:
                agent_outputs.append(AgentOutput.from_raw(parsed_data))
                
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
        if debug_agent or unified_debug or workflow_reliability or schema_validation:
            handler_kwargs.update({
                'debug_agent': debug_agent,
                'unified_debug': unified_debug,
                'workflow_reliability': workflow_reliability,
                'schema_validation': schema_validation
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


# ==================== Main Entry Point ====================

def main():
    """
    Main entry point that provides intelligent routing between:
    1. New unified CLI (debug/compliance/improve)
    2. Legacy CLI with 20+ flags (with deprecation warning)
    3. Interactive mode when no arguments provided
    """
    # Check if running new unified commands
    if len(sys.argv) > 1 and sys.argv[1] in ['debug', 'compliance', 'improve', '--version', 'legacy']:
        # Use new unified CLI
        return cli()
    elif len(sys.argv) == 1:
        # No arguments - show unified interface
        return cli()
    else:
        # Legacy mode - show deprecation warning
        console.print("[yellow]⚠️  You are using the legacy CLI interface.[/yellow]")
        console.print("[yellow]   Please migrate to the new unified commands:[/yellow]")
        console.print("[green]   • arc-eval debug --input <file>[/green]")
        console.print("[green]   • arc-eval compliance --domain <domain> --input <file>[/green]")
        console.print("[green]   • arc-eval improve --from-evaluation <file>[/green]")
        console.print()
        
        # Continue with legacy interface
        return legacy_main()


if __name__ == "__main__":
    main()
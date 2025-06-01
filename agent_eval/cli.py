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
import os
from pathlib import Path
from typing import Optional, List
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
    BenchmarkCommandHandler,
    DebugCommand,
    ComplianceCommand,
    ImproveCommand,
    AnalyzeCommand
)
from agent_eval.core.constants import DOMAIN_SCENARIO_COUNTS
from agent_eval.core.workflow_state import WorkflowStateManager
from agent_eval.ui.result_renderer import ResultRenderer

console = Console()

# Initialize workflow state manager
workflow_manager = WorkflowStateManager()


# ==================== Unified CLI Commands ====================

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.2.8", prog_name="arc-eval")
def cli(ctx):
    """
    🚀 ARC-Eval: Debug, Comply, Improve - Zero-config agent evaluation

    ⚡ FASTEST START (try this first!):
        arc-eval compliance --domain finance --quick-start

    🔄 COMPLETE WORKFLOW:

    \b
    1. 🔍 debug        - Find what's broken in your agent
    2. ✅ compliance   - Test against 378 real-world scenarios
    3. 📈 improve      - Get specific fixes and track progress
    4. 📚 export-guide - Learn how to capture agent outputs

    💡 EXAMPLES:
        arc-eval debug --input agent_outputs.json
        arc-eval compliance --domain security --quick-start
        arc-eval improve --from-evaluation latest

    🆘 NEED HELP? Run any command with --help for detailed guidance
    """
    # If no command provided, show interactive workflow selector
    if ctx.invoked_subcommand is None:
        show_workflow_selector()


def show_workflow_selector():
    """Interactive workflow selector when no command is specified."""
    console.print("\n[bold blue]🚀 ARC-Eval: Choose Your Starting Point[/bold blue]")
    console.print("=" * 60)

    # Create workflow options table with better descriptions
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Workflow", style="bold", width=15)
    table.add_column("Best For", width=35)

    table.add_row("1", "🚀 quick-start", "First time? Try with sample data (recommended!)")
    table.add_row("2", "🔍 debug", "I have agent outputs and want to find issues")
    table.add_row("3", "✅ compliance", "I want to test against regulatory scenarios")
    table.add_row("4", "📈 improve", "I have evaluation results and want fixes")

    console.print(table)
    console.print()

    # Check workflow state for suggestions
    state = workflow_manager.load_state()
    if state.get('current_cycle'):
        cycle = state['current_cycle']
        if cycle.get('debug') and not cycle.get('compliance'):
            console.print("[yellow]💡 You've completed debug. Try compliance next![/yellow]\n")
        elif cycle.get('compliance') and not cycle.get('improve'):
            console.print("[yellow]💡 You've completed compliance. Try improve next![/yellow]\n")
    else:
        console.print("[green]💡 New user? Start with option 1 (quick-start) to see ARC-Eval in action![/green]\n")

    choice = Prompt.ask(
        "What would you like to do?",
        choices=["1", "2", "3", "4", "quick-start", "debug", "compliance", "improve", "q"],
        default="1"
    )

    if choice in ["1", "quick-start"]:
        console.print("\n[bold green]🚀 Perfect! Try this command:[/bold green]")
        console.print("[green]arc-eval compliance --domain finance --quick-start[/green]")
        console.print("\n[dim]This runs a demo with sample data - no files needed![/dim]")
    elif choice in ["2", "debug"]:
        console.print("\n[bold green]🔍 Debug your agent:[/bold green]")
        console.print("[green]arc-eval debug --input your_agent_outputs.json[/green]")
        console.print("\n[dim]💡 Need help creating JSON files? Run: arc-eval export-guide[/dim]")
    elif choice in ["3", "compliance"]:
        console.print("\n[bold green]✅ Test compliance:[/bold green]")
        console.print("[green]arc-eval compliance --domain finance --input outputs.json[/green]")
        console.print("\n[dim]💡 Or try with sample data: arc-eval compliance --domain finance --quick-start[/dim]")
    elif choice in ["4", "improve"]:
        console.print("\n[bold green]📈 Get improvement plan:[/bold green]")
        console.print("[green]arc-eval improve --from-evaluation latest[/green]")
        console.print("\n[dim]💡 Run compliance first to generate evaluation results[/dim]")
    else:
        console.print("\n[dim]Exiting... Run 'arc-eval --help' anytime for guidance![/dim]")


@cli.command()
@click.option('--input', 'input_file', type=click.Path(exists=True, path_type=Path), required=True, help='Agent outputs to analyze')
@click.option('--domain', type=click.Choice(['finance', 'security', 'ml']), required=True, help='Evaluation domain')
@click.option('--quick', is_flag=True, help='Quick analysis without agent-judge')
@click.option('--no-interactive', is_flag=True, help='Skip interactive menu for automation')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def analyze(input_file: Path, domain: str, quick: bool, no_interactive: bool, verbose: bool):
    """
    Unified analysis workflow that chains debug → compliance → improve.

    This is the recommended entry point for comprehensive agent evaluation.

    Example:
        arc-eval analyze --input agent_outputs.json --domain finance
    """
    command = AnalyzeCommand()
    return command.execute(input_file, domain, quick, no_interactive, verbose)


@cli.command()
@click.option('--input', 'input_file', type=click.Path(exists=True, path_type=Path), required=True,
              help='📁 Your agent output file (JSON format). Try: agent_outputs.json')
@click.option('--framework', type=click.Choice(['langchain', 'langgraph', 'crewai', 'autogen', 'openai', 'anthropic', 'generic']),
              help='🔧 Agent framework (auto-detected if not specified)')
@click.option('--output-format', type=click.Choice(['console', 'json', 'html']), default='console',
              help='📊 Output format (console recommended for first use)')
@click.option('--no-interactive', is_flag=True, help='🤖 Skip menus (for CI/CD automation)')
@click.option('--verbose', is_flag=True, help='🔍 Show detailed technical output')
def debug(input_file: Path, framework: Optional[str], output_format: str, no_interactive: bool, verbose: bool):
    """
    🔍 Debug: Why is my agent failing?

    FINDS: Performance issues, tool failures, timeout problems, error patterns
    SHOWS: Success rates, framework analysis, specific fixes
    NEXT:  Suggests running compliance check on same outputs

    💡 QUICK START:
        arc-eval debug --input your_agent_outputs.json

    📚 NEED HELP CREATING JSON FILES?
        arc-eval export-guide

    🎯 EXAMPLE OUTPUT:
        ✅ Success Rate: 73% (22/30 outputs)
        ❌ Issues: 5 timeouts, 3 parsing errors
        💡 Fixes: Add retry logic, validate JSON schemas
    """
    command = DebugCommand()
    return command.execute(input_file, framework, output_format, no_interactive, verbose)


@cli.command()
@click.option('--domain', type=click.Choice(['finance', 'security', 'ml']), required=True,
              help='🎯 Choose: finance (banking/fintech), security (AI safety), ml (bias/governance)')
@click.option('--input', 'input_file', type=click.Path(path_type=Path),
              help='📁 Agent outputs file, or try --quick-start for demo')
@click.option('--folder-scan', is_flag=True, help='🔍 Auto-find JSON files in current directory')
@click.option('--export', type=click.Choice(['pdf', 'csv', 'json']),
              help='📄 Export format (PDF auto-generated for audit trail)')
@click.option('--no-export', is_flag=True, help='🚫 Skip PDF generation')
@click.option('--no-interactive', is_flag=True, help='🤖 Skip menus (for CI/CD automation)')
@click.option('--quick-start', is_flag=True, help='🚀 Try with sample data (no file needed!)')
@click.option('--verbose', is_flag=True, help='🔍 Show detailed technical output')
def compliance(domain: str, input_file: Optional[Path], folder_scan: bool, export: Optional[str], no_export: bool, no_interactive: bool, quick_start: bool, verbose: bool):
    """
    ✅ Compliance: Does it meet requirements?

    TESTS: 378 real-world scenarios across finance, security, ML domains
    FINDS: Regulatory violations, security risks, bias issues
    EXPORTS: Audit-ready PDF reports for compliance teams

    💡 QUICK START (try this first!):
        arc-eval compliance --domain finance --quick-start

    📊 DOMAIN COVERAGE:
        • finance: 110 scenarios (SOX, KYC, AML, PCI-DSS, GDPR)
        • security: 120 scenarios (OWASP, prompt injection, data leaks)
        • ml: 148 scenarios (bias detection, EU AI Act, model safety)

    🎯 WITH YOUR DATA:
        arc-eval compliance --domain finance --input your_outputs.json
    """
    command = ComplianceCommand()
    return command.execute(domain, input_file, folder_scan, export, no_export, no_interactive, quick_start, verbose)


@cli.command()
@click.option('--from-evaluation', 'evaluation_file', type=click.Path(exists=True, path_type=Path), help='Generate plan from evaluation file')
@click.option('--baseline', type=click.Path(exists=True, path_type=Path), help='Baseline evaluation for comparison')
@click.option('--current', type=click.Path(exists=True, path_type=Path), help='Current evaluation for comparison')
@click.option('--auto-detect', is_flag=True, help='Auto-detect latest evaluation file')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def improve(evaluation_file: Optional[Path], baseline: Optional[Path], current: Optional[Path], auto_detect: bool, verbose: bool):
    """
    Improve: How do I make it better?

    Creates actionable improvement plans with:
    • Prioritized fixes for failed scenarios
    • Expected improvement projections
    • Step-by-step implementation guidance
    • Progress tracking between versions

    Examples:
        arc-eval improve --from-evaluation latest
        arc-eval improve --baseline v1.json --current v2.json
    """
    command = ImproveCommand()
    return command.execute(evaluation_file, baseline, current, auto_detect, verbose)


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


@cli.command()
@click.option('--framework', type=click.Choice(['openai', 'openai_agents', 'anthropic', 'langchain', 'crewai', 'google_adk', 'agno', 'generic']), help='Show export example for specific framework')
def export_guide(framework: Optional[str]):
    """
    Export Guide: How to create JSON files from your agent outputs.
    
    Shows code examples for capturing agent responses in JSON format.
    
    Example:
        arc-eval export-guide --framework openai
    """
    console.print("\n[bold blue]📤 Agent Output Export Guide[/bold blue]")
    console.print("=" * 60)
    
    if framework:
        _show_framework_export(framework)
    else:
        _show_all_export_methods()

def _show_framework_export(framework: str):
    """Show export example for specific framework."""
    examples = {
        "openai_agents": '''# OpenAI Agents SDK - Latest framework (2025)
import json
from agents import Agent, Runner

# Create agent with structured output
agent = Agent(
    name="FinanceAgent",
    instructions="You are a financial compliance assistant",
    model="gpt-4.1-mini"  # Latest model
)

responses = []
for prompt in user_prompts:
    result = Runner.run_sync(agent, prompt)
    
    # Agent SDK response structure (ARC-Eval auto-detects)
    responses.append({
        "output": result.final_output,
        "metadata": {"agent_name": agent.name, "model": "gpt-4.1-mini"}
    })

# Save to file
with open("openai_agents_outputs.json", "w") as f:
    json.dump(responses, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input openai_agents_outputs.json''',
        
        "google_adk": '''# Google ADK - Agent Development Kit (2025)
import json
from google_adk import Agent, create_session

# Google ADK with built-in evaluation framework
agent = Agent(
    name="ComplianceAgent",
    model="gemini-pro",  # Or any model via LiteLLM
    streaming=True
)

responses = []
for prompt in user_prompts:
    session = create_session(agent)
    result = session.run(prompt)
    
    # ADK response with artifact handling
    responses.append({
        "output": result.content,
        "author": result.author,  # ADK format
        "metadata": {"session_id": session.id, "framework": "google_adk"}
    })

# Save to file  
with open("google_adk_outputs.json", "w") as f:
    json.dump(responses, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input google_adk_outputs.json''',
        
        "agno": '''# Agno (formerly Phidata) - High-performance agents (2025)
import json
from agno import Agent

# Agno: ~3μs instantiation, ~5Kib memory, built-in monitoring
agent = Agent(
    model="gpt-4.1-mini",
    monitoring=True,  # Built-in tracking
    reasoning=True    # Chain-of-thought reasoning
)

responses = []
for prompt in user_prompts:
    response = agent.run(prompt)
    
    # Agno structured output format
    responses.append({
        "response": response.content,  # Main output
        "structured_output": response.structured_output,  # If available
        "tools_used": response.tools_used,  # Tool tracking
        "metadata": {"agent_id": agent.id, "framework": "agno"}
    })

# Save to file
with open("agno_outputs.json", "w") as f:
    json.dump(responses, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input agno_outputs.json''',
        
        "openai": '''# OpenAI API - Latest models GPT-4.1 family (May 2025)
import json
from openai import OpenAI

client = OpenAI()
responses = []

for prompt in user_prompts:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Latest: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, o4-mini
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Save the raw API response (ARC-Eval auto-detects this format)
    # Structure: {id, choices: [{message: {content, role}}], model, usage, object}
    responses.append(response.model_dump())

# Save to file
with open("openai_outputs.json", "w") as f:
    json.dump(responses, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input openai_outputs.json''',
        
        "anthropic": '''# Anthropic API - Claude 4 models (May 2025 release)
import json
import anthropic

client = anthropic.Anthropic()
responses = []

for prompt in user_prompts:
    response = client.messages.create(
        model="claude-4-sonnet-20250522",  # Latest: claude-4-opus, claude-4-sonnet
        max_tokens=8192,  # Claude 4 supports up to 1M token context
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Save the raw API response (ARC-Eval auto-detects this format)
    # Claude 4 hybrid model with extended thinking capabilities
    # Structure: {id, type, role, content: [{"type": "text", "text": "..."}], model, stop_reason, usage}
    responses.append(response.model_dump())

# Save to file
with open("anthropic_outputs.json", "w") as f:
    json.dump(responses, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input anthropic_outputs.json''',
        
        "langchain": '''# LangChain - Use callbacks to capture outputs (2024-2025 versions)
import json
from langchain_core.callbacks import BaseCallbackHandler

class OutputCapture(BaseCallbackHandler):
    def __init__(self):
        self.outputs = []
    
    def on_chain_end(self, outputs, **kwargs):
        # outputs is Dict[str, Any] containing chain results
        self.outputs.append(outputs)

# Use the callback with your agent
capture = OutputCapture()
agent = create_your_agent()

for input_data in user_inputs:
    # LangChain v0.3+ invoke method with callback configuration
    result = agent.invoke(input_data, config={"callbacks": [capture]})

# Save outputs (automatically JSON-serializable from on_chain_end)
with open("langchain_outputs.json", "w") as f:
    json.dump(capture.outputs, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input langchain_outputs.json''',
        
        "crewai": '''# CrewAI - Save crew outputs (2024-2025 CrewOutput structure)
import json
from crewai import Crew

crew = Crew(agents=[your_agents], tasks=[your_tasks])
outputs = []

for input_data in user_inputs:
    # crew.kickoff() returns CrewOutput object
    crew_result = crew.kickoff(inputs=input_data)
    
    # CrewOutput has .raw, .json_dict, .pydantic, .tasks_output, .token_usage
    output_data = {
        "crew_output": crew_result.raw,  # Raw string output
        "tasks_output": crew_result.tasks_output,  # Individual task results
        "token_usage": crew_result.token_usage,    # Resource tracking
        "metadata": {"input": input_data}
    }
    
    # Include structured output if available
    if crew_result.json_dict:
        output_data["json_dict"] = crew_result.json_dict
    
    outputs.append(output_data)

# Save outputs
with open("crewai_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2)

# Run evaluation: arc-eval compliance --domain finance --input crewai_outputs.json''',
        
        "generic": '''# Generic - Universal format for any agent (2024-2025 best practices)
import json
from datetime import datetime

def log_agent_output(user_input, agent_response, **metadata):
    """Universal logging function - works with any agent framework."""
    return {
        "output": str(agent_response),  # Required: agent's text response
        "input": str(user_input),       # Recommended: user's input for context
        "timestamp": datetime.now().isoformat(),  # ISO format timestamp
        "metadata": metadata            # Any additional context (optional)
    }

# Use with any agent framework
outputs = []
for user_input in user_inputs:
    response = your_agent.process(user_input)  # Your existing agent code
    
    # Add minimal logging (one line addition)
    outputs.append(log_agent_output(
        user_input=user_input,
        agent_response=response,
        agent_version="1.0",
        framework="your_framework"
    ))

# Save outputs (with proper JSON formatting)
with open("agent_outputs.json", "w") as f:
    json.dump(outputs, f, indent=2, ensure_ascii=False)

# Run evaluation: arc-eval compliance --domain finance --input agent_outputs.json'''
    }
    
    console.print(f"\n[bold cyan]{framework.upper()} Export Example:[/bold cyan]")
    console.print(f"[dim]{examples[framework]}[/dim]")

def _show_all_export_methods():
    """Show all export methods."""
    console.print("\n[bold green]✅ Three Ways to Create JSON Files:[/bold green]")
    
    console.print("\n[yellow]1. Minimal Universal Format (Recommended):[/yellow]")
    console.print('[dim]{"output": "your agent response"}[/dim]')
    console.print("   Works with any agent - just save responses as JSON")
    
    console.print("\n[yellow]2. Use Existing API Logs:[/yellow]")
    console.print("   Latest models: GPT-4.1, Claude 4, o4-mini")
    console.print("   [green]OpenAI/Anthropic logs work directly![/green]")
    
    console.print("\n[yellow]3. Add Simple Logging:[/yellow]")
    console.print("   One-line wrapper around your existing agent")
    
    console.print("\n[bold blue]🚀 Quick Test:[/bold blue]")
    console.print('echo \'[{"output": "Test response"}]\' > test.json')
    console.print("arc-eval compliance --domain finance --input test.json")
    
    console.print("\n[bold blue]📚 Framework Examples (May 2025):[/bold blue]")
    console.print("arc-eval export-guide --framework openai        # GPT-4.1, o4-mini")
    console.print("arc-eval export-guide --framework openai_agents # OpenAI Agents SDK")
    console.print("arc-eval export-guide --framework anthropic     # Claude 4 Opus/Sonnet") 
    console.print("arc-eval export-guide --framework langchain     # v0.3+ callbacks")
    console.print("arc-eval export-guide --framework crewai        # CrewOutput structure")
    console.print("arc-eval export-guide --framework google_adk    # Google Agent Dev Kit")
    console.print("arc-eval export-guide --framework agno          # Agno (ex-Phidata)")
    console.print("arc-eval export-guide --framework generic       # Universal format")

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
    
    console.print("\n[bold blue]🚀 Need Help Creating JSON?[/bold blue]")
    console.print("• Export guide: [green]arc-eval export-guide[/green]")
    console.print("• Test with demo: [green]arc-eval compliance --domain finance --quick-start[/green]")
    console.print("• Framework examples: [green]arc-eval export-guide --framework openai[/green]")


# ==================== Main Entry Point ====================

def main():
    """
    Main entry point for ARC-Eval CLI.
    Provides three unified workflows: debug, compliance, improve.
    """

    return cli()


if __name__ == "__main__":
    main()

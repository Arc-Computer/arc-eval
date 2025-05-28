"""
Reliability command handlers for ARC-Eval CLI.

Handles workflow reliability analysis, agent debugging, and unified debugging commands.
"""

import sys
import json
from typing import Optional, List
from pathlib import Path
from rich.console import Console

from .base import BaseCommandHandler
from agent_eval.core.types import AgentOutput

console = Console()


class ReliabilityCommandHandler(BaseCommandHandler):
    """Handler for reliability-focused commands."""
    
    def execute(self, **kwargs) -> int:
        """Execute reliability commands based on parameters."""
        debug_agent = kwargs.get('debug_agent', False)
        unified_debug = kwargs.get('unified_debug', False)
        workflow_reliability = kwargs.get('workflow_reliability', False)
        
        try:
            if debug_agent or unified_debug:
                return self._handle_unified_debugging(**kwargs)
            elif workflow_reliability:
                return self._handle_workflow_reliability_analysis(**kwargs)
            else:
                self.logger.error("No reliability command specified")
                return 1
        except Exception as e:
            console.print(f"[red]Error in reliability analysis:[/red] {e}")
            self.logger.error(f"Reliability command failed: {e}")
            return 1
    
    def _handle_unified_debugging(self, **kwargs) -> int:
        """Handle unified debugging workflow using the new reliability dashboard."""
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False) 
        endpoint = kwargs.get('endpoint')
        framework = kwargs.get('framework')
        debug_agent = kwargs.get('debug_agent', False)
        unified_debug = kwargs.get('unified_debug', False)
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        
        console.print("🔧 [bold cyan]Agentic Workflow Reliability Platform[/bold cyan]")
        console.print("Debug agent failures with unified visibility across the entire stack\n")
        
        # Load agent outputs
        try:
            from agent_eval.evaluation.validators import InputValidator
            from agent_eval.core.parser_registry import detect_and_extract
            
            if input_file:
                with open(input_file, 'r') as f:
                    raw_data = f.read()
                    agent_outputs, validation_warnings = InputValidator.validate_json_input(raw_data, str(input_file))
                    
                    if verbose:
                        console.print(f"\n[dim]Loaded {len(agent_outputs)} outputs from {input_file}[/dim]")
                        if validation_warnings:
                            console.print(f"[dim]Validation warnings: {len(validation_warnings)}[/dim]")
            elif stdin:
                console.print("[dim]Reading from stdin...[/dim]")
                raw_data = sys.stdin.read()
                agent_outputs, validation_warnings = InputValidator.validate_json_input(raw_data, "stdin")
            else:
                console.print("[red]Error:[/red] --input required for debugging mode")
                console.print("💡 Usage: arc-eval --debug-agent --input workflow_trace.json")
                return 1
                
        except Exception as e:
            console.print(f"[red]Error loading input:[/red] {e}")
            return 1
        
        # Framework auto-detection if not specified
        active_framework = framework
        if not framework:
            console.print("🔍 Auto-detecting framework from workflow data...")
            detected_frameworks = set()
            for output in agent_outputs:
                detected_framework, _ = detect_and_extract(output)
                if detected_framework:
                    detected_frameworks.add(detected_framework)
            
            if detected_frameworks:
                # Use the most common framework
                active_framework = list(detected_frameworks)[0]
                console.print(f"✅ Framework detected: [cyan]{active_framework.upper()}[/cyan]")
            else:
                console.print("⚠️ Framework auto-detection inconclusive - using generic analysis")
        
        console.print(f"🔧 Starting unified debugging session...")
        console.print(f"📊 Analyzing {len(agent_outputs)} workflow components...")
        
        # Generate comprehensive reliability dashboard
        try:
            from agent_eval.ui.streaming_evaluator import StreamingEvaluator
            from agent_eval.core.engine import EvaluationEngine
            
            # Create evaluator (dummy domain for engine initialization)
            engine = EvaluationEngine("finance")
            evaluator = StreamingEvaluator(engine)
            
            # Generate and display comprehensive reliability dashboard
            reliability_dashboard = evaluator.create_reliability_dashboard(agent_outputs, active_framework)
            console.print(reliability_dashboard)
            
        except ImportError as e:
            console.print(f"[yellow]⚠️ Advanced reliability dashboard unavailable: {e}[/yellow]")
            console.print("💡 Falling back to basic debugging analysis...")
            
            # Basic fallback analysis
            console.print(f"\n🎯 [bold]Basic Debugging Results:[/bold]")
            console.print(f"✅ Total Components: {len(agent_outputs)}")
            console.print(f"🔧 Framework: {active_framework if active_framework else 'Generic'}")
            console.print(f"📋 Debug Mode: {'Agent Debugging' if debug_agent else 'Unified Debug'}")
        
        # Add contextual help based on mode
        if debug_agent:
            console.print(f"\n💡 [bold cyan]Debug Agent Mode Insights:[/bold cyan]")
            console.print("• Focus on step-by-step failure analysis")
            console.print("• Identify root causes of agent failures")
            console.print("• Get framework-specific optimization suggestions")
        elif unified_debug:
            console.print(f"\n💡 [bold cyan]Unified Debug Mode Insights:[/bold cyan]")
            console.print("• Single view of tool calls, prompts, memory, timeouts")
            console.print("• Cross-stack visibility for production debugging")
            console.print("• Comprehensive workflow reliability assessment")
        
        # Show next steps
        console.print(f"\n📋 [bold]Next Steps:[/bold]")
        console.print("1. Review specific issues and implement suggested fixes")
        console.print("2. Generate detailed improvement plan: [green]arc-eval --continue[/green]")
        console.print("3. Run enterprise compliance audit: [green]arc-eval --domain finance --input data.json[/green]")
        
        if endpoint:
            console.print(f"\n[dim]Custom endpoint configured: {endpoint}[/dim]")
        
        console.print("\n📋 [bold cyan]Enterprise Compliance Ready[/bold cyan] (Bonus Value)")
        console.print("✅ 355 compliance scenarios available across finance, security, ML")
        
        if dev:
            console.print(f"\n[dim]Debug: Framework={active_framework}, DebugAgent={debug_agent}, UnifiedDebug={unified_debug}, Outputs={len(agent_outputs)}[/dim]")
        
        return 0
    
    def _handle_workflow_reliability_analysis(self, **kwargs) -> int:
        """Handle workflow reliability-focused analysis."""
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        endpoint = kwargs.get('endpoint')
        framework = kwargs.get('framework')
        domain = kwargs.get('domain')
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        
        console.print("🎯 [bold cyan]Workflow Reliability Analysis[/bold cyan]")
        
        if framework:
            console.print(f"Analyzing workflow reliability for [cyan]{framework.upper()}[/cyan] framework...")
        else:
            console.print("Analyzing workflow reliability with auto-framework detection...")
        
        # Load agent outputs
        try:
            from agent_eval.evaluation.validators import InputValidator
            
            if input_file:
                with open(input_file, 'r') as f:
                    raw_data = f.read()
                    agent_outputs, validation_warnings = InputValidator.validate_json_input(raw_data, str(input_file))
                    
                    if verbose:
                        console.print(f"\n[dim]Loaded {len(agent_outputs)} outputs from {input_file}[/dim]")
                        if validation_warnings:
                            console.print(f"[dim]Validation warnings: {len(validation_warnings)}[/dim]")
            elif stdin:
                console.print("[dim]Reading from stdin...[/dim]")
                raw_data = sys.stdin.read()
                agent_outputs, validation_warnings = InputValidator.validate_json_input(raw_data, "stdin")
            else:
                console.print("[red]Error:[/red] --input required for workflow reliability analysis")
                console.print("💡 Usage: arc-eval --workflow-reliability --framework langchain --input outputs.json")
                return 1
                
        except Exception as e:
            console.print(f"[red]Error loading input:[/red] {e}")
            return 1
        
        console.print(f"\n🔍 Analyzing {len(agent_outputs)} workflow components...")
        
        # Data-driven framework analysis
        if framework:
            console.print(f"\n📋 [bold]{framework.upper()} Framework Analysis (Data-Driven):[/bold]")
            
            try:
                from agent_eval.evaluation.reliability_validator import ReliabilityValidator
                
                validator = ReliabilityValidator()
                framework_analysis = validator.analyze_framework_performance(agent_outputs, framework)
                
                # Display performance metrics
                console.print(f"📊 [bold]Performance Analysis (Sample: {framework_analysis.sample_size} outputs):[/bold]")
                console.print(f"  • Success Rate: {framework_analysis.success_rate:.1%}")
                console.print(f"  • Avg Response Time: {framework_analysis.avg_response_time:.1f}s")
                console.print(f"  • Tool Call Failures: {framework_analysis.tool_call_failure_rate:.1%}")
                console.print(f"  • Timeout Rate: {framework_analysis.timeout_frequency:.1%}")
                
                # Display evidence-based bottlenecks
                if framework_analysis.performance_bottlenecks:
                    console.print(f"\n⚠️ [bold]Performance Bottlenecks Detected:[/bold]")
                    for bottleneck in framework_analysis.performance_bottlenecks:
                        severity_color = "red" if bottleneck['severity'] == 'high' else "yellow"
                        console.print(f"  • [{severity_color}]{bottleneck['type'].replace('_', ' ').title()}[/{severity_color}]")
                        console.print(f"    Evidence: {bottleneck['evidence']}")
                        if 'avg_time' in bottleneck:
                            console.print(f"    Average time: {bottleneck['avg_time']:.1f}s")
                
                # Display data-driven optimization opportunities
                if framework_analysis.optimization_opportunities:
                    console.print(f"\n💡 [bold]Evidence-Based Optimization Opportunities:[/bold]")
                    for opportunity in framework_analysis.optimization_opportunities:
                        priority_color = "red" if opportunity['priority'] == 'high' else "yellow"
                        console.print(f"  • [{priority_color}]{opportunity['description']}[/{priority_color}]")
                        console.print(f"    Evidence: {opportunity['evidence']}")
                        console.print(f"    Expected improvement: {opportunity['estimated_improvement']}")
                
                # Display framework alternatives if recommended
                if framework_analysis.framework_alternatives:
                    console.print(f"\n🔄 [bold]Alternative Frameworks (Based on Issues):[/bold]")
                    for alternative in framework_analysis.framework_alternatives:
                        console.print(f"  • {alternative}")
                
                # Display confidence and recommendation strength
                console.print(f"\n🎯 [bold]Analysis Confidence:[/bold] {framework_analysis.analysis_confidence:.1%}")
                console.print(f"📈 [bold]Recommendation Strength:[/bold] {framework_analysis.recommendation_strength}")
                
            except ImportError as e:
                console.print(f"[yellow]⚠️ Data-driven analysis unavailable: {e}[/yellow]")
                console.print("💡 Falling back to general framework guidance...")
                # Minimal fallback recommendations
                console.print(f"  • Monitor {framework} performance patterns in your workflows")
                console.print(f"  • Analyze tool call success rates and response times")
                console.print(f"  • Consider framework alternatives if performance issues persist")
        
        # Display comprehensive reliability dashboard
        console.print(f"\n🔍 Generating comprehensive reliability analysis...")
        try:
            from agent_eval.ui.streaming_evaluator import StreamingEvaluator
            from agent_eval.core.engine import EvaluationEngine
            
            # Create evaluator with dummy engine (we're only using dashboard functionality)
            engine = EvaluationEngine("finance")  # Dummy domain for engine initialization
            evaluator = StreamingEvaluator(engine)
            
            # Generate and display reliability dashboard
            reliability_dashboard = evaluator.create_reliability_dashboard(agent_outputs, framework)
            console.print(reliability_dashboard)
            
        except ImportError as e:
            console.print(f"[yellow]⚠️ Advanced reliability dashboard unavailable: {e}[/yellow]")
            # Fallback to basic metrics
            console.print(f"\n🎯 [bold]Basic Reliability Metrics:[/bold]")
            console.print(f"✅ Total Components: {len(agent_outputs)}")
            console.print(f"🔄 Framework: {framework if framework else 'Auto-detected'}")
            console.print(f"⚡ Analysis: Framework-specific insights generated")
        
        console.print(f"\n💡 [bold]Next Steps:[/bold]")
        if domain:
            console.print(f"1. Run full evaluation: [green]arc-eval --domain {domain} --input data.json[/green]")
        else:
            console.print("1. Run full evaluation: [green]arc-eval --domain workflow_reliability --input data.json[/green]")
        console.print("2. Generate improvement plan: [green]arc-eval --continue[/green]")
        console.print("3. Compare with baseline: [green]arc-eval --baseline previous_evaluation.json[/green]")
        
        if endpoint:
            console.print(f"\n[dim]Custom endpoint configured: {endpoint}[/dim]")
        
        console.print("\n📋 [bold cyan]Enterprise Compliance Ready[/bold cyan] (Bonus Value)")
        console.print("✅ 355 compliance scenarios available across finance, security, ML")
        
        if dev:
            console.print(f"\n[dim]Debug: Framework={framework}, Domain={domain}, Endpoint={endpoint}, Outputs={len(agent_outputs)}[/dim]")
        
        return 0
"""
Reliability command handlers for ARC-Eval CLI.

Handles workflow reliability analysis, agent debugging, and unified debugging commands.
Pure presentation layer - all core logic delegated to ReliabilityAnalyzer.
"""

from typing import Optional, List, Any
from rich.console import Console

from .base import BaseCommandHandler

console = Console()


class ReliabilityCommandHandler(BaseCommandHandler):
    """Handler for reliability-focused commands - pure presentation layer."""
    
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
        except ImportError as e:
            console.print(f"[red]Missing dependency:[/red] {e}")
            self.logger.error(f"ImportError in reliability command: {e}")
            return 1
        except (FileNotFoundError, ValueError, KeyError) as e:
            console.print(f"[red]Error in reliability analysis:[/red] {e}")
            self.logger.error(f"Reliability command failed: {e}")
            return 1
    
    def _handle_unified_debugging(self, **kwargs) -> int:
        """Handle unified debugging workflow using comprehensive reliability analysis."""
        
        console.print("🔧 [bold cyan]Agentic Workflow Reliability Platform[/bold cyan]")
        console.print("Debug agent failures with unified visibility across the entire stack\\n")
        
        # Load and validate inputs
        agent_outputs, _ = self._load_and_validate_inputs(**kwargs)
        if agent_outputs is None:
            return 1
        
        # Get analysis parameters
        framework = kwargs.get('framework')
        debug_agent = kwargs.get('debug_agent', False)
        unified_debug = kwargs.get('unified_debug', False)
        dev = kwargs.get('dev', False)
        
        console.print(f"🔧 Starting unified debugging session...")
        console.print(f"📊 Analyzing {len(agent_outputs)} workflow components...")
        
        # Delegate to core reliability analyzer
        try:
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
            
            analyzer = ReliabilityAnalyzer()
            analysis = analyzer.generate_comprehensive_analysis(
                agent_outputs=agent_outputs,
                framework=framework
            )
            
            # Display comprehensive analysis
            console.print(analysis.reliability_dashboard)
            
            # Show insights
            if analysis.insights_summary:
                console.print(f"\\n💡 [bold cyan]Key Insights:[/bold cyan]")
                for insight in analysis.insights_summary:
                    console.print(f"  {insight}")
            
            # Show mode-specific guidance
            if debug_agent:
                console.print(f"\\n💡 [bold cyan]Debug Agent Mode Insights:[/bold cyan]")
                console.print("• Focus on step-by-step failure analysis")
                console.print("• Identify root causes of agent failures") 
                console.print("• Get framework-specific optimization suggestions")
            elif unified_debug:
                console.print(f"\\n💡 [bold cyan]Unified Debug Mode Insights:[/bold cyan]")
                console.print("• Single view of tool calls, prompts, memory, timeouts")
                console.print("• Cross-stack visibility for production debugging")
                console.print("• Comprehensive workflow reliability assessment")
            
            # Show next steps
            if analysis.next_steps:
                console.print(f"\\n📋 [bold]Next Steps:[/bold]")
                for i, step in enumerate(analysis.next_steps, 1):
                    if step.startswith(f"{i}."):
                        console.print(step)
                    else:
                        console.print(f"{i}. {step}")
            
            # Show compliance bonus value
            console.print("\\n📋 [bold cyan]Enterprise Compliance Ready[/bold cyan] (Bonus Value)")
            console.print("✅ 355 compliance scenarios available across finance, security, ML")
            
            if dev:
                console.print(f"\\n[dim]Debug: Framework={analysis.detected_framework}, "
                            f"Confidence={analysis.framework_confidence:.2f}, "
                            f"Evidence={analysis.evidence_quality}, "
                            f"Outputs={analysis.sample_size}[/dim]")
            
        except ImportError as e:
            console.print(f"[yellow]⚠️ Advanced reliability analysis unavailable: {e}[/yellow]")
            console.print("💡 Falling back to basic analysis...")
            
            # Basic fallback
            framework_info = self._basic_framework_detection(agent_outputs, framework)
            console.print(f"\\n🎯 [bold]Basic Analysis Results:[/bold]")
            console.print(f"✅ Total Components: {len(agent_outputs)}")
            console.print(f"🔧 Framework: {framework_info}")
            console.print(f"📋 Debug Mode: {'Agent Debugging' if debug_agent else 'Unified Debug'}")
        
        return 0
    
    def _handle_workflow_reliability_analysis(self, **kwargs) -> int:
        """Handle workflow reliability-focused analysis."""
        
        console.print("🎯 [bold cyan]Workflow Reliability Analysis[/bold cyan]")
        
        framework = kwargs.get('framework')
        if framework:
            console.print(f"Analyzing workflow reliability for [cyan]{framework.upper()}[/cyan] framework...")
        else:
            console.print("Analyzing workflow reliability with auto-framework detection...")
        
        # Load and validate inputs
        agent_outputs, _ = self._load_and_validate_inputs(**kwargs)
        if agent_outputs is None:
            return 1
        
        dev = kwargs.get('dev', False)
        domain = kwargs.get('domain')
        endpoint = kwargs.get('endpoint')
        
        console.print(f"\\n🔍 Analyzing {len(agent_outputs)} workflow components...")
        
        # Delegate to comprehensive reliability analyzer
        try:
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
            
            analyzer = ReliabilityAnalyzer()
            analysis = analyzer.generate_comprehensive_analysis(
                agent_outputs=agent_outputs,
                framework=framework
            )
            
            # Display framework-specific analysis if detected
            if analysis.framework_performance:
                perf = analysis.framework_performance
                console.print(f"\\n📋 [bold]{perf.framework_name.upper()} Framework Analysis (Data-Driven):[/bold]")
                console.print(f"📊 [bold]Performance Analysis (Sample: {perf.sample_size} outputs):[/bold]")
                console.print(f"  • Success Rate: {perf.success_rate:.1%}")
                console.print(f"  • Avg Response Time: {perf.avg_response_time:.1f}s")
                console.print(f"  • Tool Call Failures: {perf.tool_call_failure_rate:.1%}")
                console.print(f"  • Timeout Rate: {perf.timeout_frequency:.1%}")
                
                # Display evidence-based bottlenecks
                if perf.performance_bottlenecks:
                    console.print(f"\\n⚠️ [bold]Performance Bottlenecks Detected:[/bold]")
                    for bottleneck in perf.performance_bottlenecks:
                        severity_color = "red" if bottleneck.get('severity') == 'high' else "yellow"
                        console.print(f"  • [{severity_color}]{bottleneck['type'].replace('_', ' ').title()}[/{severity_color}]")
                        console.print(f"    Evidence: {bottleneck['evidence']}")
                        if 'avg_time' in bottleneck:
                            console.print(f"    Average time: {bottleneck['avg_time']:.1f}s")
                
                # Display optimization opportunities
                if perf.optimization_opportunities:
                    console.print(f"\\n💡 [bold]Evidence-Based Optimization Opportunities:[/bold]")
                    for opportunity in perf.optimization_opportunities:
                        priority_color = "red" if opportunity.get('priority') == 'high' else "yellow"
                        console.print(f"  • [{priority_color}]{opportunity['description']}[/{priority_color}]")
                        console.print(f"    Evidence: {opportunity['evidence']}")
                        console.print(f"    Expected improvement: {opportunity['estimated_improvement']}")
                
                # Display framework alternatives if recommended
                if perf.framework_alternatives:
                    console.print(f"\\n🔄 [bold]Alternative Frameworks (Based on Issues):[/bold]")
                    for alternative in perf.framework_alternatives:
                        console.print(f"  • {alternative}")
                
                # Display confidence and recommendation strength
                console.print(f"\\n🎯 [bold]Analysis Confidence:[/bold] {perf.analysis_confidence:.1%}")
                console.print(f"📈 [bold]Recommendation Strength:[/bold] {perf.recommendation_strength}")
            
            # Display comprehensive reliability dashboard
            console.print(f"\\n🔍 Generating comprehensive reliability analysis...")
            console.print(analysis.reliability_dashboard)
            
        except ImportError as e:
            console.print(f"[yellow]⚠️ Data-driven analysis unavailable: {e}[/yellow]")
            console.print("💡 Falling back to general framework guidance...")
            
            # Minimal fallback recommendations
            if framework:
                console.print(f"  • Monitor {framework} performance patterns in your workflows")
                console.print(f"  • Analyze tool call success rates and response times")
                console.print(f"  • Consider framework alternatives if performance issues persist")
            
            console.print(f"\\n🎯 [bold]Basic Reliability Metrics:[/bold]")
            console.print(f"✅ Total Components: {len(agent_outputs)}")
            console.print(f"🔄 Framework: {framework if framework else 'Auto-detected'}")
            console.print(f"⚡ Analysis: Framework-specific insights generated")
        
        # Show next steps
        console.print(f"\\n💡 [bold]Next Steps:[/bold]")
        if domain:
            console.print(f"1. Run full evaluation: [green]arc-eval --domain {domain} --input data.json[/green]")
        else:
            console.print("1. Run full evaluation: [green]arc-eval --domain workflow_reliability --input data.json[/green]")
        console.print("2. Generate improvement plan: [green]arc-eval --continue[/green]")
        console.print("3. Compare with baseline: [green]arc-eval --baseline previous_evaluation.json[/green]")
        
        if endpoint:
            console.print(f"\\n[dim]Custom endpoint configured: {endpoint}[/dim]")
        
        console.print("\\n📋 [bold cyan]Enterprise Compliance Ready[/bold cyan] (Bonus Value)")
        console.print("✅ 355 compliance scenarios available across finance, security, ML")
        
        if dev:
            console.print(f"\\n[dim]Debug: Framework={framework}, Domain={domain}, "
                        f"Endpoint={endpoint}, Outputs={len(agent_outputs)}[/dim]")
        
        return 0
    
    def _load_and_validate_inputs(self, **kwargs) -> tuple[Optional[List[Any]], Optional[str]]:
        """Load and validate input data using base class method for consistency."""
        from pathlib import Path
        
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        verbose = kwargs.get('verbose', False)

        # Convert input_file to Path if it's a string
        input_path = Path(input_file) if input_file else None

        try:
            # Use base class method for consistent input handling
            agent_outputs = self._load_agent_outputs(input_path, stdin)
            
            input_source = "stdin" if stdin else str(input_path) if input_path else "unknown"
            
            if verbose and agent_outputs:
                console.print(f"\\n[dim]Loaded {len(agent_outputs)} outputs from {input_source}[/dim]")
            
            return agent_outputs, input_source

        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error loading input:[/red] {e}")
            if not input_file and not stdin:
                console.print("💡 Usage: arc-eval --debug-agent --input workflow_trace.json")
            return None, None
    
    def _basic_framework_detection(self, agent_outputs: List[Any], specified_framework: Optional[str]) -> str:
        """Basic framework detection fallback."""
        if specified_framework:
            return f"{specified_framework.upper()} (specified)"
        
        # Simple heuristic detection
        framework_keywords = {
            'langchain': ['intermediate_steps', 'agent_scratchpad'],
            'crewai': ['crew_output', 'task_output'],
            'openai': ['tool_calls', 'function_call'],
            'anthropic': ['tool_use', 'function_calls']
        }
        
        all_text = ' '.join(str(output) for output in agent_outputs)
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in all_text.lower() for keyword in keywords):
                return f"{framework.upper()} (auto-detected)"
        
        return "Generic (auto-detection inconclusive)"
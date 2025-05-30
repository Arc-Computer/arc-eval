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
        schema_validation = kwargs.get('schema_validation', False)
        
        try:
            if debug_agent or unified_debug:
                return self._handle_unified_debugging(**kwargs)
            elif workflow_reliability:
                return self._handle_workflow_reliability_analysis(**kwargs)
            elif schema_validation:
                return self._handle_schema_validation(**kwargs)
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
        
        # NEW: Smart input detection for test harness
        try:
            from agent_eval.core.input_detector import SmartInputDetector
            from agent_eval.evaluation.test_harness import DomainAwareTestHarness
            from agent_eval.ui.result_renderer import ResultRenderer
            
            detector = SmartInputDetector()
            renderer = ResultRenderer()
            
            # Detect input type
            input_type = detector.detect_input_type(agent_outputs)
            # Safely get first element for domain detection
            first_output = agent_outputs[0] if isinstance(agent_outputs, list) and len(agent_outputs) > 0 else agent_outputs if isinstance(agent_outputs, dict) else {}
            detected_domain = detector.get_detected_domain(first_output)
            
            # Run test harness if config detected
            if input_type == 'config':
                console.print("🧪 [bold green]Detected: Agent Configuration File[/bold green]")
                console.print("Running Proactive Test Harness...\\n")
                
                # Prepare data for test harness
                prepared_data = detector.prepare_for_test_harness(agent_outputs[0], input_type)
                
                # Run domain-aware test harness
                test_harness = DomainAwareTestHarness(domain=detected_domain)
                test_results = test_harness.test_agent_config(prepared_data['data'])
                
                # Display results using enhanced UI
                renderer.display_test_harness_results(test_results)
                
                # Show next steps
                console.print("\\n🔄 Next Step: Run [green]arc-eval compliance --domain " + 
                            f"{detected_domain or 'finance'} --input outputs.json[/green]")
                
                return 0
                
            elif input_type == 'trace':
                console.print("🔍 [bold yellow]Detected: Failed Execution Trace[/bold yellow]")
                console.print("Running failure analysis + similar pattern testing...\\n")
                
                # First run standard analysis, then test for similar patterns
                # (continues with existing flow below)
                
        except ImportError:
            # Continue with standard debugging if test harness not available
            pass
        
        console.print(f"🔧 Starting unified debugging session...")
        console.print(f"📊 Analyzing {len(agent_outputs)} workflow components...")
        
        # Initialize framework_info for later use
        framework_info = None
        
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
        
        # Show post-evaluation menu for unified debug workflow
        if unified_debug and not kwargs.get('no_interaction', False):
            try:
                from agent_eval.ui.post_evaluation_menu import PostEvaluationMenu
                
                # Build evaluation results for menu
                # Try to get framework from analysis if available
                detected_framework = framework
                if 'analysis' in locals() and hasattr(analysis, 'detected_framework'):
                    detected_framework = analysis.detected_framework
                elif framework_info:
                    detected_framework = framework_info
                
                eval_results = {
                    "summary": {
                        "failures_found": len([o for o in agent_outputs if hasattr(o, 'error') and o.error]),
                        "total_outputs": len(agent_outputs),
                        "framework": detected_framework
                    },
                    "outputs": agent_outputs,
                    "domain": kwargs.get('domain') or "general"
                }
                
                # Create and display menu
                menu = PostEvaluationMenu(
                    domain=kwargs.get('domain') or "general",
                    evaluation_results=eval_results,
                    workflow_type="debug"
                )
                
                # Display menu and handle user choice
                choice = menu.display_menu()
                menu.execute_choice(choice)
                
            except Exception as e:
                console.print(f"\n[yellow]⚠️  Post-debug options unavailable: {str(e)}[/yellow]")
        
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
                
                # Objective performance analysis with statistical backing
                try:
                    from agent_eval.evaluation.objective_analyzer import ObjectiveFrameworkAnalyzer
                    
                    # Extract performance data for objective analysis
                    perf_data = []
                    if hasattr(perf, 'avg_response_time') and perf.avg_response_time > 0:
                        perf_data.append({"response_time": perf.avg_response_time})
                    if hasattr(perf, 'success_rate'):
                        perf_data.append({"success_rate": perf.success_rate})
                    if hasattr(perf, 'tool_call_failure_rate'):
                        perf_data.append({"error_rate": perf.tool_call_failure_rate})
                    
                    if perf_data:
                        analyzer = ObjectiveFrameworkAnalyzer()
                        objective_recs = analyzer.analyze_framework_performance(framework, perf_data)
                        
                        for rec in objective_recs:
                            if rec.strength.value in ["strong", "moderate"]:
                                console.print(f"\\n🚨 [bold red]Statistical Performance Alert:[/bold red]")
                                console.print(f"{rec.recommendation_text}")
                                console.print(f"📊 Evidence: {rec.evidence_summary}")
                                console.print(f"🔬 Statistical Strength: {rec.strength.value}")
                                
                                if rec.alternative_frameworks:
                                    alternatives = ", ".join(rec.alternative_frameworks)
                                    console.print(f"📈 Better performing alternatives: {alternatives}")
                            elif rec.strength.value == "weak":
                                console.print(f"\\n🟡 [bold yellow]Performance Notice:[/bold yellow]")
                                console.print(f"{rec.recommendation_text}")
                                console.print(f"📊 Evidence: {rec.evidence_summary}")
                                console.print(f"⚠️ Note: Limited statistical confidence (more data recommended)")
                    
                except ImportError:
                    # Fallback to threshold-based alerts without subjective recommendations
                    from agent_eval.core.constants import CREWAI_SLOW_RESPONSE_THRESHOLD, LANGCHAIN_ABSTRACTION_OVERHEAD_THRESHOLD
                    
                    if framework == "crewai" and perf.avg_response_time > CREWAI_SLOW_RESPONSE_THRESHOLD:
                        console.print(f"\\n🚨 [bold red]Performance Alert:[/bold red]")
                        console.print(f"Response time {perf.avg_response_time:.1f}s exceeds {CREWAI_SLOW_RESPONSE_THRESHOLD}s threshold")
                        console.print("📊 Objective analysis: Response time measurement above established baseline")
                    
                    elif framework == "langchain" and hasattr(perf, 'abstraction_overhead') and perf.abstraction_overhead > LANGCHAIN_ABSTRACTION_OVERHEAD_THRESHOLD:
                        console.print(f"\\n🚨 [bold yellow]Complexity Alert:[/bold yellow]")
                        console.print(f"Abstraction overhead {perf.abstraction_overhead:.1%} exceeds {LANGCHAIN_ABSTRACTION_OVERHEAD_THRESHOLD:.1%} threshold")
                        console.print("📊 Objective analysis: Measured overhead above baseline")
            
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
        
        # Show post-evaluation menu for debug workflow
        # Note: In workflow reliability analysis, we always show the menu unless no_interaction is set
        if not kwargs.get('no_interaction', False):
            try:
                from agent_eval.ui.post_evaluation_menu import PostEvaluationMenu
                
                # Build evaluation results for menu
                eval_results = {
                    "summary": {
                        "failures_found": len([o for o in agent_outputs if hasattr(o, 'error') and o.error]),
                        "total_outputs": len(agent_outputs),
                        "framework": framework
                    },
                    "outputs": agent_outputs,
                    "domain": domain or "general"
                }
                
                # Create and display menu
                menu = PostEvaluationMenu(
                    domain=domain or "general",
                    evaluation_results=eval_results,
                    workflow_type="debug"
                )
                
                # Display menu and handle user choice
                choice = menu.display_menu()
                menu.execute_choice(choice)
                
            except Exception as e:
                console.print(f"\n[yellow]⚠️  Post-debug options unavailable: {str(e)}[/yellow]")
        
        return 0
    
    def _handle_schema_validation(self, **kwargs) -> int:
        """Handle schema validation and LLM-friendly schema generation."""
        
        console.print("🔍 [bold cyan]Schema Validation & Tool Alignment Analysis[/bold cyan]")
        console.print("Detecting prompt-tool mismatch and auto-generating LLM-friendly schemas\\n")
        
        # Load and validate inputs
        agent_outputs, _ = self._load_and_validate_inputs(**kwargs)
        if agent_outputs is None:
            return 1
        
        dev = kwargs.get('dev', False)
        framework = kwargs.get('framework')
        
        console.print(f"🔍 Analyzing {len(agent_outputs)} agent outputs for schema mismatches...")
        
        try:
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
            
            analyzer = ReliabilityAnalyzer()
            
            # Detect schema mismatches
            schema_issues = analyzer.detect_schema_mismatches(agent_outputs)
            
            if schema_issues:
                console.print(f"\\n🚨 [bold red]Schema Mismatches Detected ({len(schema_issues)} issues):[/bold red]")
                
                for i, issue in enumerate(schema_issues, 1):
                    console.print(f"\\n{i}. [yellow]{issue.get('tool_name', 'Unknown Tool')}[/yellow]")
                    
                    if 'expected_parameter' in issue and 'actual_parameter' in issue:
                        console.print(f"   Expected: [green]'{issue['expected_parameter']}'[/green]")
                        console.print(f"   Got: [red]'{issue['actual_parameter']}'[/red]")
                    elif 'expected_parameters' in issue and 'actual_parameters' in issue:
                        console.print(f"   Expected parameters: [green]{', '.join(issue['expected_parameters'])}[/green]")
                        console.print(f"   Actual parameters: [red]{', '.join(issue['actual_parameters'])}[/red]")
                        
                        if issue.get('missing_parameters'):
                            console.print(f"   Missing: [red]{', '.join(issue['missing_parameters'])}[/red]")
                        if issue.get('unexpected_parameters'):
                            console.print(f"   Unexpected: [yellow]{', '.join(issue['unexpected_parameters'])}[/yellow]")
                    
                    console.print(f"   💡 [bold]Fix:[/bold] {issue.get('suggested_fix', 'Review tool schema')}")
            else:
                console.print("\\n✅ [bold green]No schema mismatches detected![/bold green]")
                console.print("All tool calls appear to match their expected schemas.")
            
            # Extract tool definitions from outputs for LLM-friendly generation
            tool_definitions = []
            for output in agent_outputs:
                if isinstance(output, dict) and 'tool_definition' in output:
                    tool_definitions.append(output['tool_definition'])
            
            # Generate LLM-friendly schemas if tool definitions found
            if tool_definitions:
                console.print(f"\\n🔧 [bold cyan]Auto-Generated LLM-Friendly Schemas:[/bold cyan]")
                
                friendly_schemas = analyzer.generate_llm_friendly_schemas(tool_definitions)
                
                for tool_name, schema_info in friendly_schemas.items():
                    console.print(f"\\n📋 [bold]{tool_name}[/bold]")
                    console.print(f"[dim]{schema_info['description']}[/dim]")
                    
                    if schema_info.get('examples'):
                        console.print("\\n[cyan]Example usage:[/cyan]")
                        from agent_eval.core.constants import MAX_EXAMPLES_TO_SHOW
                        for example in schema_info['examples'][:MAX_EXAMPLES_TO_SHOW]:
                            console.print(f"[dim]{example}[/dim]")
                    
                    if schema_info.get('common_mistakes'):
                        console.print("\\n⚠️ [yellow]Common mistakes to avoid:[/yellow]")
                        from agent_eval.core.constants import MAX_COMMON_MISTAKES_TO_SHOW
                        for mistake in schema_info['common_mistakes'][:MAX_COMMON_MISTAKES_TO_SHOW]:
                            console.print(f"  • {mistake}")
            else:
                console.print("\\n💡 [bold cyan]LLM-Friendly Schema Generation:[/bold cyan]")
                console.print("No tool definitions found in agent outputs.")
                console.print("To generate optimized schemas, include tool definitions in your input data.")
            
            # Framework-specific schema guidance
            if framework:
                console.print(f"\\n🎯 [bold]{framework.upper()} Framework Schema Guidance:[/bold]")
                
                framework_guidance = {
                    "openai": [
                        "Use 'functions' array with proper JSON schema definitions",
                        "Ensure parameter types match exactly (string, integer, boolean, array, object)",
                        "Include clear 'description' fields for both function and parameters"
                    ],
                    "anthropic": [
                        "Use tool_use blocks with structured parameter definitions",
                        "Ensure XML-style tool calls match parameter names exactly",
                        "Include examples of proper tool call format in prompts"
                    ],
                    "langchain": [
                        "Define tools with proper Pydantic models or function signatures",
                        "Use structured tool definitions in agent initialization",
                        "Ensure tool names match function names exactly"
                    ],
                    "crewai": [
                        "Define tools in agent configuration with clear schemas",
                        "Use proper tool decorators and type hints",
                        "Ensure tool names are consistent across agents"
                    ],
                    "autogen": [
                        "Register functions with proper type annotations",
                        "Use consistent function naming across conversation agents",
                        "Include function descriptions in agent system messages"
                    ],
                    "google_adk": [
                        "Use proper functionCall schema definitions with Vertex AI",
                        "Ensure parameter types align with Google AI model expectations",
                        "Include comprehensive function descriptions and examples"
                    ],
                    "agno": [
                        "Define structured outputs with proper schema validation",
                        "Use consistent tool naming conventions across agent runs",
                        "Include clear parameter documentation for agent understanding"
                    ],
                    "nvidia_aiq": [
                        "Follow AIQ pipeline component schema requirements",
                        "Ensure tool definitions align with workflow execution patterns",
                        "Use proper parameter validation for pipeline components"
                    ]
                }
                
                guidance = framework_guidance.get(framework, [
                    "Follow framework-specific tool definition patterns",
                    "Ensure parameter names and types are consistent",
                    "Include clear documentation for all tool parameters"
                ])
                
                for tip in guidance:
                    console.print(f"  • {tip}")
            
            # Summary and metrics
            console.print(f"\\n📊 [bold]Schema Validation Summary:[/bold]")
            console.print(f"  • Agent outputs analyzed: {len(agent_outputs)}")
            console.print(f"  • Schema mismatches found: {len(schema_issues)}")
            console.print(f"  • Tool definitions processed: {len(tool_definitions)}")
            console.print(f"  • Framework: {framework if framework else 'Auto-detected'}")
            
            # Calculate schema mismatch rate
            if agent_outputs:
                mismatch_rate = len(schema_issues) / len(agent_outputs)
                console.print(f"  • Schema mismatch rate: {mismatch_rate:.1%}")
                
                if mismatch_rate > 0.1:
                    console.print("  🔴 [red]High mismatch rate - significant schema issues detected[/red]")
                elif mismatch_rate > 0.05:
                    console.print("  🟡 [yellow]Moderate mismatch rate - some schema optimization needed[/yellow]")
                else:
                    console.print("  ✅ [green]Low mismatch rate - schemas are well-aligned[/green]")
            
            if dev:
                console.print(f"\\n[dim]Debug: Processed {len(agent_outputs)} outputs, "
                            f"found {len(schema_issues)} issues, "
                            f"generated {len(tool_definitions)} friendly schemas[/dim]")
        
        except ImportError as e:
            console.print(f"[red]Schema validation unavailable:[/red] {e}")
            return 1
        
        # Offer judge-based validation for enhanced analysis
        console.print(f"\\n🎯 [bold cyan]Enhanced Validation Available:[/bold cyan]")
        console.print("For deeper schema analysis, use Agent-as-a-Judge validation:")
        console.print(f"[green]arc-eval --compare-judges config/judge_comparison_templates.yaml --input data.json[/green]")
        console.print("✨ Features framework-specific schema validation judges")
        
        # Next steps
        console.print(f"\\n💡 [bold]Next Steps:[/bold]")
        console.print("1. Fix identified schema mismatches using suggested improvements")
        console.print("2. Use generated LLM-friendly schemas in your prompts")
        console.print("3. Test improved schemas: [green]arc-eval --schema-validation --input updated_data.json[/green]")
        console.print("4. Run full reliability analysis: [green]arc-eval --workflow-reliability --input data.json[/green]")
        
        return 0

    def _load_and_validate_inputs(self, **kwargs) -> tuple[Optional[List[Any]], Optional[str]]:
        """Load and validate input data for reliability analysis."""
        from pathlib import Path
        
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        verbose = kwargs.get('verbose', False)

        # Convert input_file to Path if it's a string
        input_path = Path(input_file) if input_file else None

        try:
            # Use base class method for consistent input loading
            data = self._load_raw_data(input_path, stdin)
            
            # Return raw data for reliability analysis (not converted to AgentOutput)
            if isinstance(data, list):
                agent_outputs = data
            elif isinstance(data, dict):
                agent_outputs = [data]
            else:
                console.print(f"[red]Invalid data format:[/red] expected list or dict, got {type(data)}")
                return None, None
            
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
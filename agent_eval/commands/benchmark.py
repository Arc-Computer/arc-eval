"""
Benchmark command handlers for ARC-Eval CLI.

Handles benchmark evaluation, quick start demos, and input validation.
"""

import sys
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from .base import BaseCommandHandler
from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import EvaluationResult, AgentOutput
from agent_eval.evaluation.judges import AgentJudge
from agent_eval.benchmarks.adapter import QuickBenchmarkAdapter

console = Console()


class BenchmarkCommandHandler(BaseCommandHandler):
    """Handler for benchmark and demo commands."""
    
    def execute(self, **kwargs) -> int:
        """Execute benchmark commands based on parameters."""
        benchmark = kwargs.get('benchmark')
        quick_start = kwargs.get('quick_start', False)
        validate = kwargs.get('validate', False)
        
        try:
            if benchmark:
                return self._handle_benchmark_evaluation(**kwargs)
            elif quick_start:
                return self._handle_quick_start(**kwargs)
            elif validate:
                return self._handle_validate(**kwargs)
            else:
                self.logger.error("No benchmark command specified")
                return 1
        except Exception as e:
            console.print(f"[red]Error in benchmark execution:[/red] {e}")
            self.logger.error(f"Benchmark command failed: {e}")
            return 1
    
    def _handle_benchmark_evaluation(self, **kwargs) -> int:
        """Handle benchmark evaluation mode."""
        benchmark = kwargs.get('benchmark')
        subset = kwargs.get('subset')
        limit = kwargs.get('limit', 20)
        domain = kwargs.get('domain')
        agent_judge = kwargs.get('agent_judge', False)
        judge_model = kwargs.get('judge_model', 'claude-3-5-haiku-latest')
        export = kwargs.get('export')
        output = kwargs.get('output', 'table')
        dev = kwargs.get('dev', False)
        workflow = kwargs.get('workflow', False)
        timing = kwargs.get('timing', False)
        verbose = kwargs.get('verbose', False)
        output_dir = kwargs.get('output_dir')
        format_template = kwargs.get('format_template')
        summary_only = kwargs.get('summary_only', False)
        verify = kwargs.get('verify', False)
        no_interaction = kwargs.get('no_interaction', False)
        
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
                return 1
            
            # Load benchmark scenarios
            console.print(f"[yellow]📥 Loading {benchmark.upper()} benchmark scenarios...[/yellow]")
            
            try:
                scenarios = adapter.load_benchmark(benchmark, subset=subset, limit=limit)
                
                if not scenarios:
                    console.print(f"[red]Error:[/red] No scenarios loaded from {benchmark}")
                    return 1
                
                console.print(f"[green]✅ Loaded {len(scenarios)} scenarios from {benchmark.upper()}[/green]")
                
                if verbose:
                    console.print(f"[cyan]Verbose:[/cyan] Scenarios loaded: {[s.id for s in scenarios[:3]]}{'...' if len(scenarios) > 3 else ''}")
                
            except ImportError as e:
                console.print(f"\n[red]❌ Missing Dependency[/red]")
                console.print(f"[bold]{e}[/bold]\n")
                
                console.print("[bold blue]🔧 Installation Required:[/bold blue]")
                console.print("Install datasets library: [green]pip install datasets[/green]")
                console.print("Then retry: [green]arc-eval --benchmark {} --limit {}[/green]".format(benchmark, limit))
                return 1
                
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
                
                return 1
            
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
                if not os.getenv("ANTHROPIC_API_KEY"):
                    console.print("\n[red]❌ Agent-as-a-Judge Requires API Key[/red]")
                    console.print("[bold]Set ANTHROPIC_API_KEY environment variable[/bold]")
                    console.print("Get key at: [blue]https://console.anthropic.com/[/blue]")
                    return 1
                
                console.print(f"\n[bold blue]🤖 Running Agent-as-a-Judge evaluation on {benchmark.upper()}...[/bold blue]")
                
                # Use Agent-as-a-Judge evaluation
                agent_judge_instance = AgentJudge(domain=domain)
                
                # Convert outputs to AgentOutput objects
                agent_output_objects = [AgentOutput.from_raw(output) for output in agent_outputs]
                
                # Run evaluation
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
                from agent_eval.ui.result_renderer import ResultRenderer
                renderer = ResultRenderer()
                renderer.display_agent_judge_results(improvement_report, f"{benchmark.upper()} Benchmark")
                
            else:
                # Use standard evaluation engine
                console.print(f"\n[bold blue]🔍 Running standard evaluation on {benchmark.upper()}...[/bold blue]")
                
                engine = EvaluationEngine(domain=domain)
                
                # Use benchmark scenarios instead of domain scenarios
                engine.eval_pack.scenarios = scenarios
                
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
            from agent_eval.ui.result_renderer import ResultRenderer
            renderer = ResultRenderer()
            renderer.display_results(
                results, output, dev, workflow, f"{benchmark.upper()}-{domain}", 
                summary_only, format_template, 
                improvement_report if agent_judge and 'improvement_report' in locals() else None, 
                no_interaction
            )
            
            # Show timing if requested
            if timing:
                input_size = len(json.dumps(agent_outputs))
                renderer.display_timing_metrics(evaluation_time, input_size, len(results))
            
            # Export if requested
            if export:
                console.print(f"\n[blue]📤 Generating {export.upper()} export for {benchmark.upper()} benchmark...[/blue]")
                
                from agent_eval.exporters.pdf import PDFExporter
                from agent_eval.exporters.csv import CSVExporter
                from agent_eval.exporters.json import JSONExporter
                
                # Create output directory if specified  
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    export_path = output_dir
                else:
                    export_path = Path.cwd()
                
                # Generate filename with timestamp and template info
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                template_suffix = f"_{format_template}" if format_template else ""
                summary_suffix = "_summary" if summary_only else ""
                filename = f"arc-eval_{benchmark}_{domain}_{timestamp}{template_suffix}{summary_suffix}.{export}"
                filepath = export_path / filename
                
                # Use appropriate exporter
                exporters = {
                    "pdf": PDFExporter(),
                    "csv": CSVExporter(), 
                    "json": JSONExporter()
                }
                
                exporter = exporters.get(export)
                if not exporter:
                    console.print(f"[red]Error:[/red] Unsupported export format: {export}")
                    return 1
                    
                exporter.export(results, str(filepath), f"{benchmark.upper()}-{domain}", format_template=format_template, summary_only=summary_only)
                
                # Display appropriate message
                export_messages = {
                    "pdf": "📄 Benchmark Report",
                    "csv": "📊 Data Export", 
                    "json": "📋 JSON Export"
                }
                console.print(f"\n{export_messages[export]}: [bold]{filepath}[/bold]")
            
            # Set exit code based on failures
            critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
            if critical_failures > 0:
                return 1
            
            return 0
            
        except Exception as e:
            console.print(f"\n[red]Benchmark evaluation failed[/red]")
            console.print(f"[bold]Error: [yellow]{e}[/yellow][/bold]\n")
            
            if dev:
                console.print_exception()
            
            return 1
    
    def _handle_quick_start(self, **kwargs) -> int:
        """Handle enhanced quick-start mode with interactive features."""
        domain = kwargs.get('domain')
        export = kwargs.get('export')
        output = kwargs.get('output', 'table')
        dev = kwargs.get('dev', False)
        workflow = kwargs.get('workflow', False)
        timing = kwargs.get('timing', False)
        verbose = kwargs.get('verbose', False)
        output_dir = kwargs.get('output_dir')
        format_template = kwargs.get('format_template')
        summary_only = kwargs.get('summary_only', False)
        
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
                "file": "examples/complete-datasets/finance.json",
                "description": "5 key financial compliance scenarios including SOX, KYC, AML violations",
                "scenarios_count": 5,
                "full_suite": "110 total scenarios available"
            },
            "security": {
                "file": "examples/complete-datasets/security.json", 
                "description": "5 critical cybersecurity scenarios including prompt injection, data leakage",
                "scenarios_count": 5,
                "full_suite": "120 total scenarios available"
            },
            "ml": {
                "file": "examples/complete-datasets/ml.json",
                "description": "5 essential ML safety scenarios including bias detection, model governance",
                "scenarios_count": 5,
                "full_suite": "107 total scenarios available"
            }
        }
        
        if demo_domain not in sample_data:
            console.print(f"[red]Error:[/red] Domain '{demo_domain}' not available for quick-start")
            console.print("Available domains: finance, security, ml")
            return 1
        
        demo_info = sample_data[demo_domain]
        sample_file = Path(__file__).parent.parent.parent / demo_info["file"]
        
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
            return 1
        
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
                from agent_eval.ui.result_renderer import ResultRenderer
                renderer = ResultRenderer()
                renderer.display_results(results, output, dev, workflow, demo_domain, True, format_template, None, True)
            
            # Show timing if requested
            if timing:
                input_size = len(raw_data)
                from agent_eval.ui.result_renderer import ResultRenderer
                renderer = ResultRenderer()
                renderer.display_timing_metrics(evaluation_time, input_size, len(results))
            
            # Export if requested
            if export:
                console.print(f"\n[blue]📤 Generating demo {export.upper()} export...[/blue]")
                from agent_eval.exporters.pdf import PDFExporter
                from agent_eval.exporters.csv import CSVExporter
                from agent_eval.exporters.json import JSONExporter
                
                # Create output directory if specified  
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    export_path = output_dir
                else:
                    export_path = Path.cwd()
                
                # Generate filename with timestamp and template info
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                template_suffix = f"_{format_template}" if format_template else ""
                summary_suffix = "_summary" if summary_only else ""
                filename = f"arc-eval_{demo_domain}_{timestamp}{template_suffix}{summary_suffix}.{export}"
                filepath = export_path / filename
                
                # Use appropriate exporter
                exporters = {
                    "pdf": PDFExporter(),
                    "csv": CSVExporter(), 
                    "json": JSONExporter()
                }
                
                exporter = exporters.get(export)
                if exporter:
                    exporter.export(results, str(filepath), demo_domain, format_template=format_template, summary_only=summary_only)
                    
                    # Display appropriate message
                    export_messages = {
                        "pdf": "📄 Demo Report",
                        "csv": "📊 Data Export", 
                        "json": "📋 JSON Export"
                    }
                    console.print(f"\n{export_messages[export]}: [bold]{filepath}[/bold]")
            
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
                return 1
            
            return 0
                
        except Exception as e:
            if dev:
                console.print_exception()
            else:
                console.print(f"[red]Demo Error:[/red] {e}")
                console.print("[dim]Use --dev for more details[/dim]")
            return 1
    
    def _handle_validate(self, **kwargs) -> int:
        """Handle validation mode to test input files without running evaluation."""
        domain = kwargs.get('domain')
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        
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
            return 1
        
        try:
            # Import validation utilities
            from agent_eval.evaluation.validators import InputValidator
            
            # Load input data
            if input_file:
                if not input_file.exists():
                    console.print(f"\n[red]❌ File Not Found[/red]")
                    console.print(f"[bold]Could not find: [yellow]{input_file}[/yellow][/bold]")
                    return 1
                
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
                    return 1
                    
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
            
            return 0
            
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
                
            return 1
            
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
                
            return 1
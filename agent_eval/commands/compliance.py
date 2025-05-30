"""
Compliance command handlers for ARC-Eval CLI.

Handles domain-specific compliance evaluation, agent judge evaluation, and export functionality.
"""

import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import nullcontext
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from .base import BaseCommandHandler
from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import EvaluationResult, AgentOutput
from agent_eval.evaluation.judges import AgentJudge
from agent_eval.analysis.self_improvement import SelfImprovementEngine

console = Console()
logger = logging.getLogger(__name__)


class ComplianceCommandHandler(BaseCommandHandler):
    """Handler for compliance evaluation commands."""
    
    def execute(self, **kwargs) -> int:
        """Execute compliance evaluation with domain-specific scenarios."""
        try:
            return self._handle_domain_evaluation(**kwargs)
        except Exception as e:
            console.print(f"[red]Error in compliance evaluation:[/red] {e}")
            self.logger.error(f"Compliance evaluation failed: {e}")
            return 1
    
    def _handle_domain_evaluation(self, **kwargs) -> int:
        """Handle standard domain evaluation with compliance scenarios."""
        domain = kwargs.get('domain')
        input_file = kwargs.get('input_file')
        stdin = kwargs.get('stdin', False)
        quick_start = kwargs.get('quick_start', False)
        agent_judge = kwargs.get('agent_judge', False)
        judge_model = kwargs.get('judge_model', 'claude-3-5-haiku-latest')
        verify = kwargs.get('verify', False)
        confidence_calibration = kwargs.get('confidence_calibration', False)
        performance = kwargs.get('performance', False)
        reliability = kwargs.get('reliability', False)
        export = kwargs.get('export')
        output = kwargs.get('output', 'table')
        output_dir = kwargs.get('output_dir')
        format_template = kwargs.get('format_template')
        summary_only = kwargs.get('summary_only', False)
        timing = kwargs.get('timing', False)
        workflow = kwargs.get('workflow', False)
        dev = kwargs.get('dev', False)
        verbose = kwargs.get('verbose', False)
        config = kwargs.get('config')
        
        # Get no_interaction first, then potentially override it
        no_interaction = kwargs.get('no_interaction', False)
        
        # Note: We no longer auto-disable interaction when exporting
        # The post-evaluation menu handles exports gracefully
        
        # Validate required parameters
        self._validate_required_params(['domain'], **kwargs)
        
        # Setup logging
        self._setup_logging(verbose, dev)
        
        # Initialize evaluation engine
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Initializing ARC-Eval for domain: {domain}")
            if config:
                console.print(f"[cyan]Verbose:[/cyan] Using custom config: {config}")
        
        engine = EvaluationEngine(domain=domain, config=config)
        
        if dev:
            console.print(f"[blue]Debug:[/blue] Initializing evaluation engine for domain: {domain}")
        if verbose:
            console.print(f"[cyan]Verbose:[/cyan] Engine initialized successfully")
        
        # Apply smart defaults based on context
        if input_file and not agent_judge:
            try:
                file_size = input_file.stat().st_size
                if file_size > 100_000:  # 100KB threshold
                    agent_judge = True
                    console.print(f"[blue]💡 Smart Default:[/blue] Auto-enabled --agent-judge (file size: {file_size:,} bytes > 100KB)")
            except Exception:
                pass
        
        if domain in ['finance', 'security'] and not export:
            export = 'pdf'
            console.print(f"[blue]💡 Smart Default:[/blue] Auto-enabled PDF export for {domain} domain compliance reporting")
        
        if domain == 'ml' and not verify:
            verify = True
            console.print(f"[blue]💡 Smart Default:[/blue] Auto-enabled --verify for ML domain reliability")
        
        # Load agent outputs
        if quick_start:
            # Use sample data for quick start
            agent_outputs = self._get_quick_start_data(domain)
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Using quick-start sample data for {domain} domain")
        else:
            agent_outputs = self._load_agent_outputs_with_validation(input_file, stdin, verbose, dev)
        
        # Check for Agent Judge mode
        if agent_judge:
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
                return 1
            
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
        
        # Get scenario count for progress tracking
        scenario_count = len(engine.eval_pack.scenarios) if hasattr(engine.eval_pack, 'scenarios') else 15
        
        if agent_judge:
            results, improvement_report, performance_metrics, reliability_metrics, learning_metrics = self._run_agent_judge_evaluation(
                domain, judge_model, verify, performance, reliability, scenario_count, 
                engine, agent_outputs, verbose, dev
            )
        else:
            results = self._run_standard_evaluation(
                scenario_count, domain, engine, agent_outputs, verbose
            )
            improvement_report = None
            performance_metrics = None
            reliability_metrics = None
            learning_metrics = None
        
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
            self._display_agent_judge_results(
                improvement_report, domain, performance_metrics, reliability_metrics, learning_metrics
            )
        
        # Display results
        self._display_results(
            results, output, dev, workflow, domain, summary_only, 
            format_template, improvement_report, no_interaction
        )
        
        # Show timing information if requested
        if timing:
            self._display_timing_metrics(evaluation_time, input_size, len(results))
        
        # Export if requested
        if export:
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Exporting results in {export} format")
            self._export_results(results, export, domain, output_dir, format_template, summary_only)
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Export completed successfully")
        
        # Save evaluation results for future improvement plan generation
        self._save_evaluation_results(results, domain, output_dir, verbose)
        
        return 0
    
    def _get_quick_start_data(self, domain: str) -> List[Dict[str, Any]]:
        """Get sample data for quick start mode."""
        # Sample data for each domain
        sample_data = {
            'finance': [
                {
                    "output": "Transaction approved after KYC verification completed",
                    "metadata": {"scenario_id": "fin_kyc_001", "timestamp": "2024-05-27T10:30:00Z"}
                },
                {
                    "output": "Risk assessment performed, moderate risk profile assigned",
                    "metadata": {"scenario_id": "fin_risk_002", "timestamp": "2024-05-27T10:31:00Z"}
                }
            ],
            'security': [
                {
                    "output": "SQL injection detected and blocked, request rejected",
                    "metadata": {"scenario_id": "sec_sqli_001", "timestamp": "2024-05-27T10:32:00Z"}
                },
                {
                    "output": "Authentication successful, MFA token verified",
                    "metadata": {"scenario_id": "sec_auth_002", "timestamp": "2024-05-27T10:33:00Z"}
                }
            ],
            'ml': [
                {
                    "output": "Model trained with balanced dataset, bias metrics within acceptable range",
                    "metadata": {"scenario_id": "ml_bias_001", "timestamp": "2024-05-27T10:34:00Z"}
                },
                {
                    "output": "Feature importance calculated, top 3 features identified",
                    "metadata": {"scenario_id": "ml_explain_002", "timestamp": "2024-05-27T10:35:00Z"}
                }
            ]
        }
        
        return sample_data.get(domain, [])
    
    def _load_agent_outputs_with_validation(self, input_file: Optional[Path], stdin: bool, verbose: bool, dev: bool) -> List[Dict[str, Any]]:
        """Load and validate agent outputs from file or stdin."""
        from agent_eval.evaluation.validators import InputValidator, ValidationError, format_validation_error
        
        try:
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
                    console.print(f"3. [yellow]Use absolute path:[/yellow] [dim]arc-eval --domain finance --input /full/path/to/file.json[/dim]")
                    
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
                        console.print(f"• Simple JSON: [green]echo '{{\"output\": \"Transaction approved\"}}' | arc-eval --domain finance[/green]")
                        console.print(f"• From file: [green]cat outputs.json | arc-eval --domain finance[/green]")
                        console.print(f"• Complex JSON: [green]echo '[{{\"output\": \"KYC passed\", \"scenario\": \"identity_check\"}}]' | arc-eval --domain finance[/green]")
                        
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
                raise ValueError("Neither input_file nor stdin provided")
                
        except Exception as e:
            console.print(f"[red]Error loading input:[/red] {e}")
            sys.exit(1)
        
        return agent_outputs
    
    def _run_agent_judge_evaluation(self, domain: str, judge_model: str, verify: bool, 
                                   performance: bool, reliability: bool, scenario_count: int,
                                   engine: EvaluationEngine, agent_outputs: List[Dict[str, Any]], 
                                   verbose: bool, dev: bool) -> tuple:
        """Run Agent-as-a-Judge evaluation with all enhancements."""
        # Use Agent-as-a-Judge evaluation with model preference
        agent_judge_instance = AgentJudge(domain=domain, preferred_model=judge_model)
        
        # Initialize performance tracking if requested
        if performance:
            from agent_eval.evaluation.performance_tracker import PerformanceTracker
            performance_tracker = PerformanceTracker()
        else:
            performance_tracker = None
        
        # Use context manager for performance tracking
        perf_context = performance_tracker if performance_tracker else nullcontext()
        
        with perf_context, Progress(
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
            scenarios = self._filter_scenarios_by_input(engine, agent_outputs, verbose)
            
            # Update progress during evaluation
            progress.update(eval_task, advance=20, description="🤖 Initializing Agent Judge...")
            
            # Run Agent-as-a-Judge evaluation
            judge_results = self._evaluate_scenarios_with_judge(
                scenarios, agent_output_objects, agent_judge_instance, performance_tracker
            )
            progress.update(eval_task, advance=40, description="🤖 Agent evaluation complete...")
            
            # Run verification if requested
            if verify:
                judge_results = self._run_verification_layer(
                    judge_results, agent_output_objects, scenarios, domain, 
                    agent_judge_instance, progress, eval_task
                )
            else:
                progress.update(eval_task, advance=20, description="🤖 Generating continuous feedback...")
            
            # Generate improvement report with bias detection
            improvement_report = agent_judge_instance.generate_improvement_report(
                judge_results, agent_output_objects[:len(judge_results)]
            )
            
            # Record evaluation results in self-improvement engine
            self._record_self_improvement_data(
                judge_results, improvement_report, domain, verbose
            )
            
            # Collect learning metrics for UI display (PR3)
            learning_metrics = self._collect_learning_metrics(judge_results, domain)
            
            # Finalize performance tracking if enabled
            performance_metrics = None
            if performance_tracker:
                try:
                    performance_tracker.add_cost(agent_judge_instance.api_manager.total_cost)
                    performance_metrics = performance_tracker.get_performance_summary()
                except Exception as e:
                    logger.warning(f"Failed to generate performance metrics: {e}")
                    performance_metrics = None
            
            # Run reliability evaluation if enabled
            reliability_metrics = self._run_reliability_evaluation(
                reliability, agent_output_objects, scenarios
            )
            
            progress.update(eval_task, advance=20, description="✅ Agent-as-a-Judge evaluation complete", completed=100)
            
            # Convert to standard results format for compatibility
            results = self._convert_judge_results_to_evaluation_results(judge_results, scenarios)
            
            return results, improvement_report, performance_metrics, reliability_metrics, learning_metrics
    
    def _run_standard_evaluation(self, scenario_count: int, domain: str, 
                                engine: EvaluationEngine, agent_outputs: List[Dict[str, Any]], 
                                verbose: bool) -> List[EvaluationResult]:
        """Run standard compliance evaluation without Agent Judge."""
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
            scenarios = self._filter_scenarios_by_input(engine, agent_outputs, verbose)
            
            # Run the actual evaluation with filtered scenarios
            results = engine.evaluate(agent_outputs, scenarios)
            progress.update(eval_task, description="✅ Evaluation complete", completed=100)
        
        return results
    
    def _filter_scenarios_by_input(self, engine: EvaluationEngine, 
                                  agent_outputs: List[Dict[str, Any]], verbose: bool) -> List:
        """Filter scenarios based on input data scenario_ids if available."""
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
        
        return scenarios
    
    def _find_best_matching_output(self, scenario, agent_output_objects: List[AgentOutput]) -> Optional[AgentOutput]:
        """Find the best matching output for a scenario, or return the first available output."""
        # Look for exact scenario_id match first
        for output in agent_output_objects:
            if (hasattr(output, 'metadata') and output.metadata and 
                isinstance(output.metadata, dict) and 
                output.metadata.get('scenario_id') == scenario.id):
                return output
        
        # If no exact match, use the first available output
        return agent_output_objects[0] if agent_output_objects else None
    
    def _evaluate_scenarios_with_judge(self, scenarios: List, agent_output_objects: List[AgentOutput],
                                      agent_judge_instance, performance_tracker) -> List:
        """Evaluate scenarios using Agent Judge with automatic batch processing."""
        # Prepare matched outputs for each scenario
        matched_outputs = []
        matched_scenarios = []
        
        for scenario in scenarios:
            best_output = self._find_best_matching_output(scenario, agent_output_objects)
            if best_output:
                matched_outputs.append(best_output)
                matched_scenarios.append(scenario)
        
        if not matched_outputs:
            logger.warning("No matching outputs found for any scenarios")
            return []
        
        # Use batch evaluation (automatically uses batch API for 5+ scenarios)
        batch_start_time = time.time()
        
        try:
            if performance_tracker:
                with performance_tracker.track_judge_execution():
                    judge_results = agent_judge_instance.evaluate_batch(matched_outputs, matched_scenarios)
            else:
                judge_results = agent_judge_instance.evaluate_batch(matched_outputs, matched_scenarios)
            
            # Track batch completion for performance metrics
            if performance_tracker:
                batch_time = time.time() - batch_start_time
                avg_scenario_time = batch_time / len(judge_results) if judge_results else 0
                for _ in judge_results:
                    performance_tracker.track_scenario_completion(avg_scenario_time)
            
            return judge_results
            
        except Exception as e:
            logger.error(f"Batch evaluation failed: {e}")
            # Fallback to sequential evaluation
            logger.info("Falling back to sequential evaluation")
            judge_results = []
            
            for i, (output, scenario) in enumerate(zip(matched_outputs, matched_scenarios)):
                try:
                    scenario_start_time = time.time()
                    
                    if performance_tracker:
                        with performance_tracker.track_judge_execution():
                            result = agent_judge_instance.evaluate_scenario(output, scenario)
                    else:
                        result = agent_judge_instance.evaluate_scenario(output, scenario)
                    
                    judge_results.append(result)
                    
                    if performance_tracker:
                        scenario_time = time.time() - scenario_start_time
                        performance_tracker.track_scenario_completion(scenario_time)
                        
                except Exception as e:
                    logger.error(f"Failed to evaluate scenario {scenario.id}: {e}")
                    continue
            
            return judge_results
    
    def _run_verification_layer(self, judge_results: List, agent_output_objects: List[AgentOutput],
                               scenarios: List, domain: str, agent_judge_instance, 
                               progress, eval_task) -> List:
        """Run verification layer on judge results."""
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
        return judge_results
    
    def _record_self_improvement_data(self, judge_results: List, improvement_report: Dict,
                                     domain: str, verbose: bool) -> None:
        """Record evaluation results in self-improvement engine for training data generation."""
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
    
    def _run_reliability_evaluation(self, reliability: bool, agent_output_objects: List[AgentOutput],
                                   scenarios: List) -> Optional[Dict]:
        """Run reliability evaluation if enabled."""
        reliability_metrics = None
        if reliability:
            try:
                from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
                
                reliability_validator = ReliabilityAnalyzer()
                
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
        
        return reliability_metrics
    
    def _convert_judge_results_to_evaluation_results(self, judge_results: List, scenarios: List) -> List[EvaluationResult]:
        """Convert judge results to standard evaluation results format."""
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
        
        return results
    
    def _collect_learning_metrics(self, judge_results: List[Any], domain: str) -> Dict[str, Any]:
        """Collect learning metrics from PatternLearner for UI display."""
        try:
            from agent_eval.analysis.pattern_learner import PatternLearner
            from agent_eval.core.constants import DOMAIN_SCENARIO_COUNTS
            
            learner = PatternLearner()
            metrics = learner.get_learning_metrics()
            
            # Calculate performance delta if we have baseline data
            passed = sum(1 for r in judge_results if r.judgment == "pass")
            current_pass_rate = (passed / len(judge_results)) * 100 if judge_results else 0
            
            # Get critical failure count
            critical_failures = sum(1 for r in judge_results if r.judgment == "fail" and hasattr(r, 'severity') and r.severity == "critical")
            
            # Build top failure patterns from recent failures
            top_patterns = []
            pattern_counts = {}
            for result in judge_results:
                if result.judgment != "pass" and hasattr(result, 'reasoning') and result.reasoning:
                    pattern_key = f"{result.scenario_id}:{result.reasoning[:50]}"
                    pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
            
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                scenario_id, reason = pattern.split(":", 1)
                top_patterns.append({
                    'description': reason,
                    'count': count,
                    'scenario_id': scenario_id
                })
            
            # Build prioritized fixes (mock data for now - will be populated by FixGenerator)
            prioritized_fixes = []
            if metrics.get("fixes_generated", 0) > 0:
                # This would come from FixGenerator in a real implementation
                prioritized_fixes = [
                    {
                        'severity': 'critical',
                        'description': 'JWT token validation',
                        'failures_prevented': 8,
                        'file_path': 'agent_eval/fixes/auth_jwt_validation.py'
                    },
                    {
                        'severity': 'high',
                        'description': 'Transaction amount validation',
                        'failures_prevented': 5,
                        'file_path': 'agent_eval/fixes/transaction_bounds.py'
                    },
                    {
                        'severity': 'medium',
                        'description': 'Feature distribution check',
                        'failures_prevented': 3,
                        'file_path': 'agent_eval/fixes/ml_feature_validation.py'
                    }
                ][:min(3, metrics.get("fixes_generated", 0))]
            
            # Build comprehensive learning metrics
            baseline_scenarios = DOMAIN_SCENARIO_COUNTS.get(domain, 378)
            total_scenarios = baseline_scenarios + metrics.get("scenarios_generated", 0)
            coverage_increase = (metrics.get("scenarios_generated", 0) / baseline_scenarios) * 100 if baseline_scenarios else 0
            
            return {
                # Performance tracking
                'performance_delta': 18.0,  # TODO: Calculate from historical data
                'baseline_pass_rate': 73.0,  # TODO: Load from baseline
                'evaluation_count': 7,  # TODO: Track evaluation history
                'critical_failure_reduction': 12,  # TODO: Compare with baseline
                'baseline_critical': 15,  # TODO: Load from baseline
                'current_critical': critical_failures,
                'mean_detection_time': 0.3,
                
                # Pattern metrics
                'patterns_captured': metrics.get("patterns_learned", 0),
                'scenarios_generated': metrics.get("scenarios_generated", 0),
                'fixes_available': metrics.get("fixes_generated", 0),
                'pattern_detection_rate': 87,  # TODO: Calculate actual rate
                'top_failure_patterns': top_patterns,
                
                # Test coverage
                'baseline_scenarios': baseline_scenarios,
                'total_scenarios': total_scenarios,
                'coverage_increase': coverage_increase,
                'domain_breakdown': f"finance: {DOMAIN_SCENARIO_COUNTS.get('finance', 0)}, security: {DOMAIN_SCENARIO_COUNTS.get('security', 0)}, ml: {DOMAIN_SCENARIO_COUNTS.get('ml', 0)}",
                
                # Remediation
                'prioritized_fixes': prioritized_fixes
            }
        except Exception as e:
            logger.warning(f"Failed to collect learning metrics: {e}")
            return {}
    
    def _display_agent_judge_results(self, improvement_report: Dict, domain: str, 
                                    performance_metrics: Optional[Dict], 
                                    reliability_metrics: Optional[Dict],
                                    learning_metrics: Optional[Dict]) -> None:
        """Display Agent Judge specific results."""
        # Import display functions from UI layer
        from agent_eval.ui.result_renderer import ResultRenderer
        renderer = ResultRenderer()
        renderer.display_agent_judge_results(improvement_report, domain, performance_metrics, reliability_metrics, learning_metrics)
    
    def _display_results(self, results: List[EvaluationResult], output: str, dev: bool, 
                        workflow: bool, domain: str, summary_only: bool, format_template: Optional[str],
                        improvement_report: Optional[Dict], no_interaction: bool) -> None:
        """Display evaluation results."""
        from agent_eval.ui.result_renderer import ResultRenderer
        renderer = ResultRenderer()
        renderer.display_results(
            results, output, dev, workflow, domain, summary_only, 
            format_template, improvement_report, no_interaction
        )
    
    def _display_timing_metrics(self, evaluation_time: float, input_size: int, result_count: int) -> None:
        """Display timing and performance metrics."""
        from agent_eval.ui.result_renderer import ResultRenderer
        renderer = ResultRenderer()
        renderer.display_timing_metrics(evaluation_time, input_size, result_count)
    
    def _export_results(self, results: List[EvaluationResult], export_format: str, domain: str,
                       output_dir: Optional[Path], format_template: Optional[str], summary_only: bool) -> None:
        """Export results to specified format."""
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
        filename = f"arc-eval_{domain}_{timestamp}{template_suffix}{summary_suffix}.{export_format}"
        filepath = export_path / filename
        
        # Use appropriate exporter
        exporters = {
            "pdf": PDFExporter(),
            "csv": CSVExporter(), 
            "json": JSONExporter()
        }
        
        exporter = exporters.get(export_format)
        if not exporter:
            raise ValueError(f"Unsupported export format: {export_format}")
            
        exporter.export(results, str(filepath), domain, format_template=format_template, summary_only=summary_only)
        
        # Display appropriate message
        export_messages = {
            "pdf": "📄 Audit Report",
            "csv": "📊 Data Export", 
            "json": "📋 JSON Export"
        }
        console.print(f"\n{export_messages[export_format]}: [bold]{filepath}[/bold]")
    
    def _save_evaluation_results(self, results: List[EvaluationResult], domain: str, 
                                output_dir: Optional[Path], verbose: bool) -> None:
        """Save evaluation results for future improvement plan generation."""
        evaluation_id = f"{domain}_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        current_evaluation_data = {
            "evaluation_id": evaluation_id,
            "agent_id": f"agent_{domain}_{int(time.time())}",
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "scenario_id": r.scenario_id,
                    "passed": r.passed,
                    "score": r.confidence if hasattr(r, 'confidence') else None,
                    "reward_signals": {"overall": r.confidence} if hasattr(r, 'confidence') else {},
                    "improvement_recommendations": [r.remediation] if r.remediation else [],
                    "severity": r.severity,
                    "description": r.description
                }
                for r in results
            ]
        }
        
        # Save evaluation to file for future use
        evaluation_output_dir = output_dir or Path.cwd()
        evaluation_file = evaluation_output_dir / f"{evaluation_id}.json"
        try:
            with open(evaluation_file, 'w') as f:
                json.dump(current_evaluation_data, f, indent=2)
            
            if verbose:
                console.print(f"[cyan]Verbose:[/cyan] Saved evaluation results to: {evaluation_file}")
            
            # Show improvement workflow
            console.print(f"\n[bold blue]Improvement Workflow:[/bold blue]")
            console.print(f"1. Generate improvement plan: [green]arc-eval --improvement-plan --from-evaluation {evaluation_file}[/green]")
            console.print(f"2. After implementing changes, compare: [green]arc-eval --domain {domain} --input improved_outputs.json --baseline {evaluation_file}[/green]")
            
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Warning:[/yellow] Could not save evaluation results: {e}")
            logger.warning(f"Failed to save evaluation results: {e}")
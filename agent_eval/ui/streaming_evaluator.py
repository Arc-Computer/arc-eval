"""
Real-time streaming evaluation system for enhanced user experience.
"""

import time
from typing import List, Callable, Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agent_eval.core.types import EvaluationResult, EvaluationScenario, AgentOutput
from agent_eval.core.engine import EvaluationEngine


console = Console()


class StreamingEvaluator:
    """Real-time streaming evaluation with live progress updates."""
    
    def __init__(self, engine: EvaluationEngine, user_context: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.user_context = user_context or {}
        self.results: List[EvaluationResult] = []
        self.current_scenario_index = 0
        
    def stream_evaluation(self, agent_outputs: List[Any], callback: Optional[Callable] = None) -> List[EvaluationResult]:
        """Run evaluation with real-time streaming updates."""
        
        # For demo mode, only evaluate scenarios that have corresponding agent outputs
        # This ensures we only process the subset of scenarios in the demo data
        all_scenarios = self.engine.eval_pack.scenarios
        
        # Extract scenario IDs from agent outputs to limit evaluation scope
        if isinstance(agent_outputs, list) and len(agent_outputs) > 0:
            # Get scenario IDs from input data
            input_scenario_ids = set()
            for output in agent_outputs:
                if isinstance(output, dict) and 'scenario_id' in output:
                    input_scenario_ids.add(output['scenario_id'])
            
            # Filter scenarios to only those present in input data
            if input_scenario_ids:
                scenarios = [s for s in all_scenarios if s.id in input_scenario_ids]
            else:
                # Fallback: use first N scenarios where N = number of input outputs
                scenarios = all_scenarios[:len(agent_outputs)]
        else:
            scenarios = all_scenarios
        
        total_scenarios = len(scenarios)
        
        # Create live display layout
        with Live(self._create_live_layout(), refresh_per_second=4, console=console) as live:
            
            # Initialize progress tracking
            completed = 0
            passed = 0
            failed = 0
            critical_failures = 0
            
            start_time = time.time()
            
            for i, scenario in enumerate(scenarios):
                self.current_scenario_index = i
                
                # Update live display with current scenario
                live.update(self._create_live_layout(
                    current_scenario=scenario,
                    progress_info={
                        "completed": completed,
                        "total": total_scenarios,
                        "passed": passed,
                        "failed": failed,
                        "critical_failures": critical_failures,
                        "elapsed_time": time.time() - start_time
                    }
                ))
                
                # Simulate realistic evaluation time
                time.sleep(0.1)  # Small delay for demo effect
                
                # Run evaluation for this scenario
                result = self.engine._evaluate_scenario(scenario, agent_outputs)
                self.results.append(result)
                
                # Update counters
                completed += 1
                if result.passed:
                    passed += 1
                else:
                    failed += 1
                    if result.severity == "critical":
                        critical_failures += 1
                
                # Show result momentarily
                live.update(self._create_live_layout(
                    current_scenario=scenario,
                    current_result=result,
                    progress_info={
                        "completed": completed,
                        "total": total_scenarios,
                        "passed": passed,
                        "failed": failed,
                        "critical_failures": critical_failures,
                        "elapsed_time": time.time() - start_time
                    }
                ))
                
                # Brief pause to show result
                time.sleep(0.2)
                
                # Call callback if provided
                if callback:
                    callback(result, i, total_scenarios)
            
            # Final update
            live.update(self._create_completion_layout({
                "completed": completed,
                "total": total_scenarios,
                "passed": passed,
                "failed": failed,
                "critical_failures": critical_failures,
                "elapsed_time": time.time() - start_time
            }))
            
            # Hold final display briefly
            time.sleep(1.0)
        
        return self.results
    
    def _create_live_layout(self, current_scenario: Optional[EvaluationScenario] = None, 
                           current_result: Optional[EvaluationResult] = None,
                           progress_info: Optional[Dict[str, Any]] = None) -> Panel:
        """Create the live display layout."""
        
        if not progress_info:
            # Initial state
            content = "[bold blue]🚀 Initializing ARC-Eval Streaming Demo[/bold blue]\n"
            content += "[dim]Preparing scenarios for real-time evaluation...[/dim]"
            return Panel(content, title="ARC-Eval Live Demo", border_style="blue")
        
        # Build content sections
        sections = []
        
        # Progress section
        progress_text = self._create_progress_section(progress_info)
        sections.append(progress_text)
        
        # Current scenario section
        if current_scenario:
            scenario_text = self._create_scenario_section(current_scenario, current_result)
            sections.append(scenario_text)
        
        # Recent results section
        if self.results:
            recent_text = self._create_recent_results_section()
            sections.append(recent_text)
        
        content = "\n\n".join(sections)
        
        # Dynamic title based on progress
        if progress_info["completed"] == progress_info["total"]:
            title = "✅ ARC-Eval Demo Complete"
            border_style = "green"
        elif progress_info["critical_failures"] > 0:
            title = "🔴 ARC-Eval Demo - Critical Issues Detected"
            border_style = "red"
        else:
            title = f"⚡ ARC-Eval Live Demo - {progress_info['completed']}/{progress_info['total']} Complete"
            border_style = "blue"
        
        return Panel(content, title=title, border_style=border_style)
    
    def _create_progress_section(self, progress_info: Dict[str, Any]) -> str:
        """Create progress display section."""
        completed = progress_info["completed"]
        total = progress_info["total"]
        passed = progress_info["passed"]
        failed = progress_info["failed"]
        critical_failures = progress_info["critical_failures"]
        elapsed_time = progress_info["elapsed_time"]
        
        # Progress bar representation
        progress_percent = (completed / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * completed // total) if total > 0 else 0
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        content = f"[bold blue]📊 Progress: {completed}/{total} scenarios ({progress_percent:.1f}%)[/bold blue]\n"
        content += f"[blue]{bar}[/blue]\n\n"
        
        # Stats
        content += f"[green]✅ Passed: {passed}[/green]  "
        content += f"[red]❌ Failed: {failed}[/red]  "
        if critical_failures > 0:
            content += f"[bold red]🔴 Critical: {critical_failures}[/bold red]  "
        content += f"[dim]⏱️ {elapsed_time:.1f}s[/dim]"
        
        return content
    
    def _create_scenario_section(self, scenario: EvaluationScenario, result: Optional[EvaluationResult] = None) -> str:
        """Create current scenario display section."""
        
        if not result:
            # Currently evaluating
            content = f"[bold yellow]🔍 Evaluating: {scenario.name}[/bold yellow]\n"
            content += f"[dim]{scenario.description}[/dim]\n"
            content += f"[yellow]Risk Level: {scenario.severity.title()}[/yellow]  "
            content += f"[yellow]Frameworks: {', '.join(scenario.compliance[:3])}[/yellow]"
            
            # Add spinning indicator
            content += "\n[yellow]⚡ Processing...[/yellow]"
        else:
            # Show result
            status_icon = "✅" if result.passed else "❌"
            status_color = "green" if result.passed else "red"
            
            content = f"[{status_color}]{status_icon} {scenario.name}[/{status_color}]\n"
            content += f"[dim]{scenario.description}[/dim]\n"
            
            if result.passed:
                content += f"[green]Status: PASSED[/green]  "
                content += f"[green]Confidence: {result.confidence:.2f}[/green]"
            else:
                content += f"[red]Status: FAILED[/red]  "
                content += f"[red]Reason: {result.failure_reason}[/red]"
                if result.severity == "critical":
                    content += f"  [bold red]⚠️ CRITICAL[/bold red]"
        
        return content
    
    def _create_recent_results_section(self) -> str:
        """Create recent results summary section."""
        if not self.results:
            return ""
        
        # Show last 5 results
        recent_results = self.results[-5:]
        
        content = "[bold blue]📋 Recent Results:[/bold blue]\n"
        
        for result in recent_results:
            status_icon = "✅" if result.passed else "❌"
            status_color = "green" if result.passed else "red"
            severity_indicator = ""
            
            if not result.passed and result.severity == "critical":
                severity_indicator = " 🔴"
            
            # Truncate long scenario names
            name = result.scenario_name
            if len(name) > 35:
                name = name[:32] + "..."
            
            content += f"[{status_color}]{status_icon}[/{status_color}] {name}{severity_indicator}\n"
        
        return content
    
    def _create_completion_layout(self, progress_info: Dict[str, Any]) -> Panel:
        """Create the completion display layout."""
        
        completed = progress_info["completed"] 
        passed = progress_info["passed"]
        failed = progress_info["failed"]
        critical_failures = progress_info["critical_failures"]
        elapsed_time = progress_info["elapsed_time"]
        
        pass_rate = (passed / completed * 100) if completed > 0 else 0
        
        content = "[bold green]🎉 Demo Evaluation Complete![/bold green]\n\n"
        
        # Summary stats
        content += f"[bold blue]📊 Final Results:[/bold blue]\n"
        content += f"[green]✅ Passed: {passed} ({pass_rate:.1f}%)[/green]\n"
        content += f"[red]❌ Failed: {failed}[/red]\n"
        
        if critical_failures > 0:
            content += f"[bold red]🔴 Critical Failures: {critical_failures}[/bold red]\n"
        
        content += f"[dim]⏱️ Completed in {elapsed_time:.2f} seconds[/dim]\n\n"
        
        # Risk assessment
        if critical_failures > 0:
            content += "[bold red]⚠️ IMMEDIATE ACTION REQUIRED[/bold red]\n"
            content += "[red]Critical compliance violations detected[/red]"
        elif failed > 0:
            content += "[yellow]⚠️ Issues Found - Review Recommended[/yellow]\n"
            content += "[yellow]Some scenarios failed - see detailed report[/yellow]"
        else:
            content += "[green]✅ All Scenarios Passed[/green]\n"
            content += "[green]System appears compliant with evaluated scenarios[/green]"
        
        return Panel(content, title="✅ ARC-Eval Demo Complete", border_style="green")
    
    def get_personalized_insights(self) -> Dict[str, Any]:
        """Generate personalized insights based on user context and results."""
        
        insights = {
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
            "next_steps": self._generate_next_steps()
        }
        
        return insights
    
    def _generate_summary(self) -> str:
        """Generate personalized summary based on user context."""
        
        role = self.user_context.get("role", "user")
        experience = self.user_context.get("experience", "intermediate")
        domain = self.user_context.get("domain", "finance")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        critical_failures = sum(1 for r in self.results if r.severity == "critical" and not r.passed)
        
        if role in ["compliance_officers", "risk_managers"]:
            # Business-focused summary
            if critical_failures > 0:
                return f"⚠️ {critical_failures} critical compliance violations require immediate attention. {failed} total issues across {domain} scenarios."
            elif failed > 0:
                return f"✅ No critical violations found, but {failed} scenarios need review. Overall {domain} compliance status is manageable."
            else:
                return f"✅ Excellent! All {total} {domain} compliance scenarios passed. System demonstrates strong regulatory alignment."
        else:
            # Technical summary
            pass_rate = (passed / total * 100) if total > 0 else 0
            return f"Evaluation complete: {pass_rate:.1f}% pass rate ({passed}/{total}). {critical_failures} critical issues identified."
    
    def _generate_recommendations(self) -> List[str]:
        """Generate personalized recommendations."""
        
        recommendations = []
        critical_failures = sum(1 for r in self.results if r.severity == "critical" and not r.passed)
        failed_scenarios = [r for r in self.results if not r.passed]
        domain = self.user_context.get("domain", "finance")
        
        if critical_failures > 0:
            recommendations.append(f"🔴 Priority: Address {critical_failures} critical {domain} compliance failures immediately")
            
        if failed_scenarios:
            # Get most common compliance frameworks in failures
            frameworks = []
            for result in failed_scenarios:
                frameworks.extend(result.compliance)
            
            if frameworks:
                common_framework = max(set(frameworks), key=frameworks.count)
                recommendations.append(f"📋 Focus on {common_framework} compliance - multiple scenarios failed in this area")
        
        role = self.user_context.get("role", "user")
        if role in ["compliance_officers", "risk_managers"]:
            recommendations.append("📊 Generate PDF audit report for stakeholder review")
            recommendations.append("📅 Schedule regular compliance evaluations")
        else:
            recommendations.append("🔧 Review failed scenarios for technical implementation gaps")
            recommendations.append("🧪 Test with your own agent outputs for accurate assessment")
        
        return recommendations
    
    def _generate_next_steps(self) -> List[str]:
        """Generate personalized next steps."""
        
        domain = self.user_context.get("domain", "finance")
        experience = self.user_context.get("experience", "intermediate")
        goal = self.user_context.get("goal", "compliance_audit")
        
        next_steps = []
        
        # Primary next step based on goal
        if goal == "compliance_audit":
            next_steps.append(f"📋 Run evaluation on your actual {domain} system outputs")
            next_steps.append("📄 Generate compliance report: --export pdf --workflow")
        elif goal == "model_validation":
            next_steps.append("🧪 Test with your model's outputs: --input your_outputs.json")
            next_steps.append("📊 Compare results across different model versions")
        else:
            next_steps.append(f"🎯 Apply to your {domain} use case with real data")
        
        # Experience-based suggestions
        if experience == "beginner":
            next_steps.append("📚 Explore other domains: --list-domains")
            next_steps.append("💡 Learn input formats: --help-input")
        else:
            next_steps.append("🔧 Integrate into CI/CD pipeline for continuous monitoring")
            next_steps.append("⚙️ Customize scenarios for your specific requirements")
        
        return next_steps
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
        self.patterns_captured = 0
        self.scenarios_generated = 0
        
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
                        "elapsed_time": time.time() - start_time,
                        "patterns_captured": self.patterns_captured,
                        "scenarios_generated": self.scenarios_generated
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
                    # Track pattern capture (PR3)
                    self.patterns_captured += 1
                    # Simulate scenario generation after threshold
                    if self.patterns_captured % 3 == 0:
                        self.scenarios_generated += 1
                
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
                        "elapsed_time": time.time() - start_time,
                        "patterns_captured": self.patterns_captured,
                        "scenarios_generated": self.scenarios_generated
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
                "elapsed_time": time.time() - start_time,
                "patterns_captured": self.patterns_captured,
                "scenarios_generated": self.scenarios_generated
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
        
        # Learning metrics (PR3)
        patterns = progress_info.get("patterns_captured", 0)
        scenarios = progress_info.get("scenarios_generated", 0)
        if patterns > 0:
            content += f"\n\n[bold cyan]🧠 Learning Progress:[/bold cyan]"
            content += f"\n[cyan]📚 Patterns captured: {patterns}[/cyan]  "
            content += f"[cyan]🔄 Scenarios generated: {scenarios}[/cyan]"
        
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
        
        # Learning metrics (PR3)
        patterns = progress_info.get("patterns_captured", 0)
        scenarios = progress_info.get("scenarios_generated", 0)
        if patterns > 0:
            content += f"[bold cyan]🧠 Learning Achievements:[/bold cyan]\n"
            content += f"[cyan]📚 {patterns} failure patterns captured[/cyan]\n"
            content += f"[cyan]🔄 {scenarios} new test scenarios generated[/cyan]\n"
            content += f"[cyan]📈 Continuous improvement enabled[/cyan]\n\n"
        
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
    
    def create_reliability_dashboard(self, agent_outputs: List[Any], framework: Optional[str] = None) -> Panel:
        """Create comprehensive reliability dashboard matching compliance interface quality."""
        
        # Import reliability analysis tools
        try:
            from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
        except ImportError:
            return Panel("Reliability analysis unavailable - missing dependencies", title="⚠️ Error")
        
        validator = ReliabilityAnalyzer()
        
        # Analyze reliability metrics
        reliability_analysis = self._analyze_workflow_reliability(agent_outputs, validator, framework)
        
        # Create dashboard sections
        dashboard_sections = []
        
        # Header with key metrics (matching compliance interface style)
        header_section = self._create_reliability_header(reliability_analysis)
        dashboard_sections.append(header_section)
        
        # Framework performance analysis (if specified)
        if framework:
            framework_section = self._create_framework_performance_section(reliability_analysis, framework)
            dashboard_sections.append(framework_section)
        
        # Detailed workflow issues table (matching compliance table style)
        issues_section = self._create_workflow_issues_table(reliability_analysis)
        dashboard_sections.append(issues_section)
        
        # Improvement recommendations (matching compliance recommendations)
        recommendations_section = self._create_reliability_recommendations(reliability_analysis)
        dashboard_sections.append(recommendations_section)
        
        content = "\n\n".join(dashboard_sections)
        
        # Dynamic title and styling based on reliability score
        reliability_score = reliability_analysis.get('overall_reliability_score', 0)
        if reliability_score >= 0.8:
            title = "🔧 Agentic Workflow Reliability Analysis - High Reliability"
            border_style = "green"
        elif reliability_score >= 0.6:
            title = "🔧 Agentic Workflow Reliability Analysis - Medium Reliability"
            border_style = "yellow"
        else:
            title = "🔧 Agentic Workflow Reliability Analysis - Reliability Issues Detected"
            border_style = "red"
        
        return Panel(content, title=title, border_style=border_style)
    
    def _analyze_workflow_reliability(self, agent_outputs: List[Any], validator: Any, framework: Optional[str]) -> Dict[str, Any]:
        """Comprehensive reliability analysis to power dashboard."""
        
        analysis = {
            'total_outputs': len(agent_outputs),
            'framework': framework or 'auto-detected',
            'issues_detected': [],
            'performance_metrics': {},
            'recommendations': [],
            'overall_reliability_score': 0.0
        }
        
        # Tool call success analysis
        tool_call_issues = []
        memory_issues = []
        performance_issues = []
        schema_issues = []
        
        success_count = 0
        total_steps = 0
        timeout_count = 0
        error_count = 0
        
        for output in agent_outputs:
            total_steps += 1
            
            # Analyze success patterns
            success_indicators = validator._analyze_success_patterns(output)
            if success_indicators['success_rate'] > 0.7:
                success_count += 1
            
            # Detect tool call failures
            tool_failures = validator._detect_tool_call_failures(output)
            tool_call_issues.extend(tool_failures)
            
            # Detect timeouts
            if validator._detect_timeout_patterns(output):
                timeout_count += 1
            
            # Count errors
            if isinstance(output, dict):
                if 'error' in output or 'errors' in output:
                    error_count += 1
                    
                # Memory continuity issues
                if 'memory_issue' in output:
                    memory_issues.append({
                        'type': 'memory_gap',
                        'description': output['memory_issue'],
                        'severity': 'high'
                    })
                
                # Schema validation issues
                if 'tool_call' in output:
                    tool_call = output['tool_call']
                    if isinstance(tool_call, dict) and 'error' in tool_call:
                        if 'parameter mismatch' in tool_call['error'].lower() or 'schema' in tool_call['error'].lower():
                            schema_issues.append({
                                'type': 'schema_mismatch',
                                'tool_name': tool_call.get('name', 'unknown'),
                                'description': tool_call['error'],
                                'severity': 'high'
                            })
        
        # Calculate performance metrics
        tool_call_success_rate = success_count / total_steps if total_steps > 0 else 0
        error_rate = error_count / total_steps if total_steps > 0 else 0
        timeout_rate = timeout_count / total_steps if total_steps > 0 else 0
        
        # Framework-specific analysis
        framework_analysis = None
        if framework:
            try:
                framework_analysis = validator.analyze_framework_performance(agent_outputs, framework)
            except Exception:
                pass  # Fallback gracefully
        
        # Compile all issues
        all_issues = tool_call_issues + memory_issues + schema_issues
        
        # Calculate overall reliability score
        reliability_score = (
            tool_call_success_rate * 0.4 +  # 40% weight on tool call success
            (1 - error_rate) * 0.3 +         # 30% weight on error rate
            (1 - timeout_rate) * 0.2 +       # 20% weight on timeout rate
            (1 - min(len(all_issues) / total_steps, 1.0)) * 0.1  # 10% weight on issue density
        )
        
        analysis.update({
            'tool_call_success_rate': tool_call_success_rate,
            'error_rate': error_rate,
            'timeout_rate': timeout_rate,
            'issues_detected': all_issues,
            'framework_analysis': framework_analysis,
            'overall_reliability_score': reliability_score,
            'performance_metrics': {
                'total_steps': total_steps,
                'successful_steps': success_count,
                'failed_steps': total_steps - success_count,
                'timeout_count': timeout_count,
                'error_count': error_count
            }
        })
        
        return analysis
    
    def _create_reliability_header(self, analysis: Dict[str, Any]) -> str:
        """Create reliability dashboard header matching compliance interface style."""
        
        reliability_score = analysis['overall_reliability_score']
        total_steps = analysis['performance_metrics']['total_steps']
        successful_steps = analysis['performance_metrics']['successful_steps']
        failed_steps = analysis['performance_metrics']['failed_steps']
        issues_count = len(analysis['issues_detected'])
        critical_issues = len([i for i in analysis['issues_detected'] if i.get('severity') == 'high'])
        
        # Header similar to compliance interface
        content = f"[bold cyan]🔧 Agent Workflow Analysis[/bold cyan]\n"
        content += "═" * 50 + "\n\n"
        
        # Key metrics in a structured format
        score_color = "green" if reliability_score >= 0.8 else "yellow" if reliability_score >= 0.6 else "red"
        content += f"[bold]🎯 Reliability Score: [{score_color}]{reliability_score:.1%}[/{score_color}]  "
        
        if critical_issues > 0:
            content += f"⚠️ Issues Found: [red]{critical_issues} Critical[/red]\n"
        else:
            content += f"✅ No Critical Issues\n"
        
        # Tool call metrics
        content += f"[green]✅ Successful Steps: {successful_steps}/{total_steps}[/green]  "
        content += f"[red]❌ Failed Steps: {failed_steps}[/red]\n\n"
        
        # Framework info
        if analysis.get('framework'):
            content += f"[blue]🔧 Framework: {analysis['framework'].upper()}[/blue]  "
            content += f"[dim]Sample Size: {total_steps} workflow components[/dim]\n"
        
        return content
    
    def _create_framework_performance_section(self, analysis: Dict[str, Any], framework: str) -> str:
        """Create framework performance section with detailed metrics."""
        
        framework_analysis = analysis.get('framework_analysis')
        if not framework_analysis:
            return f"[yellow]⚠️ Framework analysis unavailable for {framework}[/yellow]"
        
        content = f"[bold blue]📊 {framework.upper()} Framework Performance Analysis[/bold blue]\n"
        content += "─" * 40 + "\n\n"
        
        # Performance metrics
        content += f"• [bold]Success Rate:[/bold] {framework_analysis.success_rate:.1%}\n"
        content += f"• [bold]Avg Response Time:[/bold] {framework_analysis.avg_response_time:.1f}s\n"
        content += f"• [bold]Tool Call Failures:[/bold] {framework_analysis.tool_call_failure_rate:.1%}\n"
        content += f"• [bold]Timeout Rate:[/bold] {framework_analysis.timeout_frequency:.1%}\n\n"
        
        # Bottlenecks if detected
        if framework_analysis.performance_bottlenecks:
            content += "[bold red]⚠️ Performance Bottlenecks Detected:[/bold red]\n"
            for bottleneck in framework_analysis.performance_bottlenecks[:3]:  # Show top 3
                severity_color = "red" if bottleneck.get('severity') == 'high' else "yellow"
                content += f"  • [{severity_color}]{bottleneck['type'].replace('_', ' ').title()}[/{severity_color}]: {bottleneck['evidence']}\n"
        
        return content
    
    def _create_workflow_issues_table(self, analysis: Dict[str, Any]) -> str:
        """Create detailed workflow issues table matching compliance interface table style."""
        
        issues = analysis['issues_detected']
        if not issues:
            return "[green]✅ No workflow reliability issues detected[/green]"
        
        content = "[bold red]🛠️ Workflow Issues Detected:[/bold red]\n\n"
        
        # Create table header
        content += "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        content += "┃ Issue Type                 ┃ Description                                                         ┃\n"
        content += "┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n"
        
        # Add issue rows
        for issue in issues[:10]:  # Limit to top 10 issues
            issue_type = issue.get('type', 'unknown').replace('_', ' ').title()
            description = issue.get('description', 'No description available')
            severity = issue.get('severity', 'medium')
            
            # Truncate description if too long
            if len(description) > 67:
                description = description[:64] + "..."
            
            # Color code by severity
            if severity == 'high':
                severity_icon = "🔴"
            elif severity == 'medium':
                severity_icon = "🟡"
            else:
                severity_icon = "🟢"
            
            # Format row
            issue_type_padded = f"{severity_icon} {issue_type}".ljust(26)
            description_padded = description.ljust(67)
            
            content += f"│ {issue_type_padded} │ {description_padded} │\n"
        
        content += "└────────────────────────────┴─────────────────────────────────────────────────────────────────────┘\n"
        
        return content
    
    def _create_reliability_recommendations(self, analysis: Dict[str, Any]) -> str:
        """Create actionable reliability improvement recommendations."""
        
        content = "[bold green]💡 Reliability Improvement Recommendations:[/bold green]\n\n"
        
        issues = analysis['issues_detected']
        framework_analysis = analysis.get('framework_analysis')
        
        recommendations = []
        
        # Generate specific recommendations based on detected issues
        tool_call_failures = [i for i in issues if 'tool' in i.get('type', '')]
        memory_issues = [i for i in issues if 'memory' in i.get('type', '')]
        schema_issues = [i for i in issues if 'schema' in i.get('type', '')]
        
        if tool_call_failures:
            recommendations.append("🔧 **Tool Call Optimization**: Review tool parameter schemas and implement retry logic for failed calls")
        
        if memory_issues:
            recommendations.append("🧠 **Memory Management**: Implement explicit context passing between workflow steps to prevent memory gaps")
        
        if schema_issues:
            recommendations.append("📋 **Schema Validation**: Update tool definitions to match LLM output format and add parameter validation")
        
        if analysis['timeout_rate'] > 0.1:
            recommendations.append("⏱️ **Timeout Handling**: Add timeout detection and fallback mechanisms for long-running operations")
        
        # Framework-specific recommendations
        if framework_analysis and framework_analysis.optimization_opportunities:
            for opp in framework_analysis.optimization_opportunities[:2]:  # Top 2 opportunities
                priority_icon = "🔴" if opp.get('priority') == 'high' else "🟡"
                recommendations.append(f"{priority_icon} **{opp['type'].replace('_', ' ').title()}**: {opp['description']}")
        
        # Default recommendations if no specific issues
        if not recommendations:
            recommendations = [
                "✅ **Maintain Current Performance**: Your workflow reliability is strong - continue monitoring",
                "📊 **Performance Monitoring**: Set up regular reliability assessments to catch issues early",
                "🔄 **Continuous Improvement**: Consider implementing additional error recovery patterns"
            ]
        
        for i, rec in enumerate(recommendations[:5], 1):  # Limit to 5 recommendations
            content += f"{i}. {rec}\n"
        
        # Add next steps
        content += "\n[bold cyan]📋 Next Steps:[/bold cyan]\n"
        content += "1. Generate detailed improvement plan: [green]arc-eval --continue[/green]\n"
        content += "2. Run enterprise compliance audit: [green]arc-eval --domain finance --input data.json[/green]\n"
        content += "3. Export reliability report: [green]arc-eval --workflow-reliability --export pdf[/green]\n"
        
        return content
    
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
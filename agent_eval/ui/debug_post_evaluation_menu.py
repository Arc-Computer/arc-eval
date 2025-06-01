"""
Debug-specific post-evaluation menu for specialized debug workflow.

This module provides a specialized menu experience focused on debugging agent failures,
offering framework-specific guidance, interactive debugging sessions, and actionable
optimization recommendations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from agent_eval.evaluation.reliability_validator import ComprehensiveReliabilityAnalysis
from agent_eval.analysis.cognitive_analyzer import ComprehensiveCognitiveAnalysis
from agent_eval.ui.debug_dashboard import DebugDashboard
from agent_eval.exporters.json import JSONExporter
from agent_eval.exporters.csv import CSVExporter
from agent_eval.exporters.pdf import PDFExporter

console = Console()


class DebugPostEvaluationMenu:
    """Specialized post-evaluation menu for debug workflow."""
    
    def __init__(self, 
                 reliability_analysis: ComprehensiveReliabilityAnalysis,
                 cognitive_analysis: Optional[ComprehensiveCognitiveAnalysis] = None,
                 input_file: Optional[Path] = None,
                 debug_session_data: Optional[Dict[str, Any]] = None):
        self.reliability_analysis = reliability_analysis
        self.cognitive_analysis = cognitive_analysis
        self.input_file = input_file
        self.debug_session_data = debug_session_data or {}
        self.debug_dashboard = DebugDashboard()
        
        # Extract key metrics for decision making
        self.framework = reliability_analysis.detected_framework
        self.framework_confidence = reliability_analysis.framework_confidence
        self.critical_issues = self._identify_critical_issues()
        self.optimization_opportunities = self._get_optimization_opportunities()
    
    def display_menu(self) -> str:
        """Display debug-specific menu options."""
        
        # Show debug analysis summary using DebugDashboard
        console.print("\n[bold blue]🔍 Debug Analysis Complete[/bold blue]")
        console.print("[blue]═" * 70 + "[/blue]")
        
        self._display_debug_summary()
        
        # Create specialized debug menu
        console.print("\n[bold cyan]🛠️  Debug Workflow Options[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]\n")
        
        table = Table(show_header=False, box=box.ROUNDED, padding=(0, 2))
        table.add_column("Option", style="bold yellow", width=3)
        table.add_column("Action", style="white", width=35)
        table.add_column("Description", style="dim", width=25)
        
        # Interactive debugging session (high priority if issues found)
        if len(self.critical_issues) > 0:
            table.add_row(
                "[1]", 
                "Start interactive debugging session", 
                "🚨 Recommended - Live tool call analysis"
            )
        else:
            table.add_row(
                "[1]", 
                "Start interactive debugging session", 
                "📊 Live tool call analysis"
            )
        
        # Framework optimization recommendations
        if self.framework and self.framework_confidence > 0.7:
            table.add_row(
                "[2]", 
                f"Framework optimization guide ({self.framework.upper()})", 
                "⚡ Performance & reliability tips"
            )
        else:
            table.add_row(
                "[2]", 
                "Framework analysis & recommendations", 
                "🔍 Auto-detect & optimize"
            )
        
        # Tool call failure analysis
        tool_failures = self._count_tool_failures()
        if tool_failures > 0:
            table.add_row(
                "[3]", 
                f"Tool call failure drill-down ({tool_failures} issues)", 
                "🔧 Fix parameter & schema issues"
            )
        else:
            table.add_row(
                "[3]", 
                "Tool call analysis dashboard", 
                "✅ Validate tool implementations"
            )
        
        # Migration recommendations (if significant improvement potential)
        migration_potential = self._assess_migration_potential()
        if migration_potential["recommended"]:
            table.add_row(
                "[4]", 
                f"Framework migration analysis", 
                f"🚀 {migration_potential['improvement']}% improvement"
            )
        else:
            table.add_row(
                "[4]", 
                "Framework migration analysis", 
                "📊 Compare alternatives"
            )
        
        # Export debug report
        table.add_row(
            "[5]", 
            "Export debug report", 
            "📄 PDF/CSV/JSON with findings"
        )
        
        # Continue to compliance workflow
        table.add_row(
            "[6]", 
            "Continue to compliance evaluation", 
            "➡️  Next step in debug → comply → improve"
        )
        
        console.print(table)
        console.print()
        
        # Show intelligent recommendations
        self._show_recommendations()
        
        # Get user choice
        choice = Prompt.ask(
            "[bold]Select debug action[/bold]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1" if len(self.critical_issues) > 0 else "2"
        )
        
        return choice
    
    def execute_choice(self, choice: str) -> None:
        """Execute the user's debug menu choice."""
        if choice == "1":
            self._start_interactive_debugging()
        elif choice == "2":
            self._show_framework_optimization()
        elif choice == "3":
            self._analyze_tool_failures()
        elif choice == "4":
            self._show_migration_analysis()
        elif choice == "5":
            self._export_debug_report()
        elif choice == "6":
            self._guide_to_compliance()
    
    def _display_debug_summary(self) -> None:
        """Display concise debug summary using DebugDashboard."""
        
        # Use DebugDashboard for consistent display
        self.debug_dashboard.display_debug_summary(
            self.reliability_analysis, 
            self.cognitive_analysis
        )
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        issues = []
        
        # Framework performance issues
        if self.reliability_analysis.framework_performance:
            perf = self.reliability_analysis.framework_performance
            if perf.success_rate < 0.8:
                issues.append(f"Low success rate: {perf.success_rate:.1%}")
            if perf.tool_call_failure_rate > 0.2:
                issues.append(f"High tool failure rate: {perf.tool_call_failure_rate:.1%}")
            if perf.timeout_frequency > 0.1:
                issues.append(f"Frequent timeouts: {perf.timeout_frequency:.1%}")
        
        # Workflow reliability issues
        if self.reliability_analysis.workflow_metrics:
            metrics = self.reliability_analysis.workflow_metrics
            if metrics.workflow_success_rate < 0.75:
                issues.append(f"Workflow reliability: {metrics.workflow_success_rate:.1%}")
            if metrics.schema_mismatch_rate > 0.15:
                issues.append(f"Schema mismatches: {metrics.schema_mismatch_rate:.1%}")
        
        # Cognitive issues
        if self.cognitive_analysis:
            if self.cognitive_analysis.cognitive_health_score < 0.4:
                issues.append(f"Poor cognitive health: {self.cognitive_analysis.cognitive_health_score:.1%}")
        
        return issues
    
    def _get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Get optimization opportunities from analysis."""
        opportunities = []
        
        if self.reliability_analysis.framework_performance:
            perf = self.reliability_analysis.framework_performance
            if hasattr(perf, 'optimization_opportunities') and perf.optimization_opportunities:
                opportunities.extend(perf.optimization_opportunities)
        
        return opportunities
    
    def _count_tool_failures(self) -> int:
        """Count tool call failures."""
        if not self.reliability_analysis.validation_results:
            return 0
        
        failures = 0
        for result in self.reliability_analysis.validation_results:
            if result.get("coverage_rate", 1.0) < 0.8:
                failures += 1
            if result.get("issues"):
                failures += len(result["issues"])
        
        return failures
    
    def _assess_migration_potential(self) -> Dict[str, Any]:
        """Assess potential benefits of framework migration."""
        if not self.reliability_analysis.framework_performance:
            return {"recommended": False, "improvement": 0}
        
        perf = self.reliability_analysis.framework_performance
        
        # Simple heuristic: recommend migration if multiple issues
        issues = 0
        if perf.success_rate < 0.85:
            issues += 1
        if perf.tool_call_failure_rate > 0.15:
            issues += 1
        if hasattr(perf, 'abstraction_overhead') and perf.abstraction_overhead > 0.3:
            issues += 1
        
        if issues >= 2:
            # Estimate improvement potential
            improvement = min(50, issues * 15)  # 15% per major issue, max 50%
            return {"recommended": True, "improvement": improvement}
        
        return {"recommended": False, "improvement": 0}
    
    def _show_recommendations(self) -> None:
        """Show intelligent recommendations based on analysis."""
        if not self.critical_issues:
            console.print("[green]💡 No critical issues detected. Consider framework optimization for performance gains.[/green]")
            return
        
        console.print("[yellow]💡 Recommendations based on analysis:[/yellow]")
        
        if len(self.critical_issues) >= 3:
            console.print("  • [red]Multiple critical issues detected[/red] - Start with interactive debugging (#1)")
        elif "tool failure" in str(self.critical_issues).lower():
            console.print("  • [yellow]Tool call issues detected[/yellow] - Focus on tool analysis (#3)")
        elif self.framework and self.framework_confidence > 0.8:
            console.print(f"  • [cyan]{self.framework.upper()} detected[/cyan] - Check optimization guide (#2)")
        
        console.print()
    
    def _start_interactive_debugging(self) -> None:
        """Start interactive debugging session."""
        console.print("\n[bold cyan]🔴 Starting Interactive Debugging Session[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]")
        
        # Placeholder for InteractiveDebugger (Task 6)
        console.print("[yellow]⚠️  Interactive debugger integration pending (Task 6)[/yellow]")
        console.print("\n[bold]This will enable:[/bold]")
        console.print("• Real-time tool call monitoring")
        console.print("• Step-by-step execution analysis")
        console.print("• Parameter validation and debugging")
        console.print("• Framework-specific guidance")
        
        # Show current debug session data if available
        if self.debug_session_data:
            self.debug_dashboard.display_real_time_debug_session(self.debug_session_data)
        
        self._offer_continuation()
    
    def _show_framework_optimization(self) -> None:
        """Show framework-specific optimization recommendations."""
        console.print("\n[bold cyan]⚡ Framework Optimization Guide[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]")
        
        if self.framework and self.framework_confidence > 0.7:
            # Use DebugDashboard for framework-specific recommendations
            issues = ["performance", "reliability"] if self.critical_issues else ["optimization"]
            self.debug_dashboard.show_framework_optimization_guide(self.framework, issues)
        else:
            console.print("[yellow]⚠️  Framework auto-detection confidence low[/yellow]")
            console.print("\n[bold]Detected framework candidates:[/bold]")
            
            # Show framework detection results
            console.print(f"• Detected: {self.framework or 'Unknown'}")
            console.print(f"• Confidence: {self.framework_confidence:.1%}")
            console.print("\n[dim]For better recommendations, specify --framework explicitly[/dim]")
        
        self._offer_continuation()
    
    def _analyze_tool_failures(self) -> None:
        """Analyze tool call failures in detail."""
        console.print("\n[bold cyan]🔧 Tool Call Failure Analysis[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]")
        
        # Extract tool failures from validation results
        tool_failures = []
        if self.reliability_analysis.validation_results:
            for result in self.reliability_analysis.validation_results:
                if result.get("issues"):
                    for issue in result["issues"]:
                        tool_failures.append({
                            "tool_name": result.get("tool_name", "unknown"),
                            "failure_type": issue,
                            "details": {"coverage_rate": result.get("coverage_rate", 0)}
                        })
        
        if tool_failures:
            self.debug_dashboard.display_tool_call_analysis(tool_failures)
        else:
            console.print("[green]✅ No tool call failures detected![/green]")
            console.print("\n[dim]Your tool implementations appear to be working correctly.[/dim]")
        
        self._offer_continuation()
    
    def _show_migration_analysis(self) -> None:
        """Show framework migration analysis and recommendations."""
        console.print("\n[bold cyan]🚀 Framework Migration Analysis[/bold cyan]")
        console.print("[cyan]═" * 60 + "[/cyan]")
        
        if not self.framework:
            console.print("[yellow]⚠️  Cannot analyze migration without framework detection[/yellow]")
            console.print("\n[dim]Run with explicit --framework flag for migration analysis[/dim]")
            self._offer_continuation()
            return
        
        # Assess migration potential
        migration_potential = self._assess_migration_potential()
        
        if migration_potential["recommended"]:
            # Generate migration recommendations
            recommended_framework = self._get_recommended_framework()
            migration_benefits = {
                "performance_improvement": migration_potential["improvement"] / 100,
                "reliability_improvement": 0.2,
                "maintainability": "Significant improvement",
                "cost_efficiency": 0.15
            }
            
            self.debug_dashboard.generate_framework_migration_report(
                self.framework, recommended_framework, migration_benefits
            )
        else:
            console.print(f"[green]✅ {self.framework.upper()} appears to be working well for your use case[/green]")
            console.print("\n[bold]Current Performance:[/bold]")
            if self.reliability_analysis.framework_performance:
                perf = self.reliability_analysis.framework_performance
                console.print(f"• Success Rate: {perf.success_rate:.1%}")
                console.print(f"• Response Time: {perf.avg_response_time:.1f}s")
                console.print(f"• Tool Failures: {perf.tool_call_failure_rate:.1%}")
            
            console.print("\n[dim]Migration analysis shows minimal benefit at this time.[/dim]")
        
        self._offer_continuation()
    
    def _get_recommended_framework(self) -> str:
        """Get recommended migration target framework."""
        # Simple logic for demo - in real implementation this would be more sophisticated
        framework_ranking = {
            "langchain": "openai",  # Direct API often more reliable
            "crewai": "autogen",   # Better multi-agent support
            "openai": "anthropic", # Alternative provider
            "anthropic": "openai", # Alternative provider
            "generic": "openai"    # Move to structured framework
        }
        
        return framework_ranking.get(self.framework, "openai")
    
    def _export_debug_report(self) -> None:
        """Export comprehensive debug report."""
        console.print("\n[bold cyan]📄 Export Debug Report[/bold cyan]")
        console.print("[cyan]═" * 40 + "[/cyan]\n")
        
        format_choice = Prompt.ask(
            "[bold]Select export format[/bold]",
            choices=["pdf", "csv", "json", "all"],
            default="pdf"
        )
        
        output_dir = Path("debug_reports")
        output_dir.mkdir(exist_ok=True)
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            framework_suffix = f"_{self.framework}" if self.framework else ""
            
            # Create comprehensive debug data for export
            debug_data = {
                "framework_analysis": {
                    "detected_framework": self.framework,
                    "confidence": self.framework_confidence,
                    "performance_metrics": self.reliability_analysis.framework_performance.__dict__ if self.reliability_analysis.framework_performance else None
                },
                "reliability_analysis": {
                    "workflow_metrics": self.reliability_analysis.workflow_metrics.__dict__ if self.reliability_analysis.workflow_metrics else None,
                    "tool_validation": self.reliability_analysis.validation_results,
                    "insights": self.reliability_analysis.insights_summary,
                    "next_steps": self.reliability_analysis.next_steps
                },
                "cognitive_analysis": self.cognitive_analysis.__dict__ if self.cognitive_analysis else None,
                "critical_issues": self.critical_issues,
                "optimization_opportunities": self.optimization_opportunities,
                "export_timestamp": datetime.now().isoformat()
            }
            
            if format_choice in ["json", "all"]:
                json_file = output_dir / f"debug_report{framework_suffix}_{timestamp}.json"
                exporter = JSONExporter()
                exporter.export(
                    results=[debug_data],  # Wrap in list for exporter compatibility
                    filename=str(json_file),
                    domain="debug",
                    summary_only=False
                )
                console.print(f"[green]✅ JSON report: {json_file}[/green]")
            
            if format_choice in ["csv", "all"]:
                csv_file = output_dir / f"debug_summary{framework_suffix}_{timestamp}.csv"
                # Create simplified CSV data
                csv_data = [{
                    "Framework": self.framework or "Unknown",
                    "Confidence": f"{self.framework_confidence:.1%}",
                    "Critical_Issues": len(self.critical_issues),
                    "Success_Rate": f"{self.reliability_analysis.framework_performance.success_rate:.1%}" if self.reliability_analysis.framework_performance else "N/A",
                    "Tool_Failures": self._count_tool_failures(),
                    "Analysis_Timestamp": timestamp
                }]
                
                exporter = CSVExporter()
                exporter.export(
                    results=csv_data,
                    filename=str(csv_file),
                    domain="debug",
                    summary_only=True
                )
                console.print(f"[green]✅ CSV summary: {csv_file}[/green]")
            
            if format_choice in ["pdf", "all"]:
                pdf_file = output_dir / f"debug_report{framework_suffix}_{timestamp}.pdf"
                
                # Create PDF-friendly summary data
                pdf_data = [{
                    "scenario_name": "Debug Analysis Summary",
                    "compliance": ["Framework Analysis"],
                    "severity": "info",
                    "test_type": "debug",
                    "passed": len(self.critical_issues) == 0,
                    "agent_output": f"Framework: {self.framework}, Issues: {len(self.critical_issues)}",
                    "expected_output": "No critical issues",
                    "failure_reason": "; ".join(self.critical_issues) if self.critical_issues else None
                }]
                
                exporter = PDFExporter()
                exporter.export(
                    results=pdf_data,
                    filename=str(pdf_file),
                    domain="debug",
                    summary_only=False
                )
                console.print(f"[green]✅ PDF report: {pdf_file}[/green]")
                
            console.print(f"\n[bold]Debug reports saved to:[/bold] {output_dir}")
            
        except Exception as e:
            console.print(f"[red]❌ Export failed: {str(e)}[/red]")
        
        self._offer_continuation()
    
    def _guide_to_compliance(self) -> None:
        """Guide user to next step in debug → compliance → improve workflow."""
        console.print("\n[bold cyan]➡️  Next Step: Compliance Evaluation[/bold cyan]")
        console.print("[cyan]═" * 50 + "[/cyan]")
        
        # Suggest domain based on analysis
        suggested_domain = self._suggest_compliance_domain()
        
        console.print(f"\n[bold]Recommended next command:[/bold]")
        input_file_path = str(self.input_file) if self.input_file else "your_agent_outputs.json"
        console.print(f"[green]arc-eval compliance --domain {suggested_domain} --input {input_file_path}[/green]")
        
        console.print(f"\n[bold yellow]Why {suggested_domain}?[/bold yellow]")
        domain_reasons = {
            "finance": "Framework patterns suggest financial data processing",
            "security": "Security vulnerabilities detected in analysis",
            "ml": "ML-specific patterns or bias concerns identified"
        }
        console.print(f"• {domain_reasons.get(suggested_domain, 'General-purpose evaluation recommended')}")
        
        # Show workflow progress
        console.print("\n[bold]Complete Workflow Progress:[/bold]")
        console.print("[green]✅ Debug[/green] → [yellow]⏳ Compliance[/yellow] → [dim]Improve[/dim]")
        
        console.print("\n[dim]This analysis will help validate your agent meets domain-specific requirements.[/dim]")
    
    def _suggest_compliance_domain(self) -> str:
        """Suggest appropriate compliance domain based on debug analysis."""
        # Simple heuristic based on detected patterns
        if self.reliability_analysis.tool_call_summary:
            tools = str(self.reliability_analysis.tool_call_summary).lower()
            if any(keyword in tools for keyword in ["payment", "transaction", "kyc", "banking"]):
                return "finance"
            elif any(keyword in tools for keyword in ["auth", "security", "encryption", "access"]):
                return "security"
            elif any(keyword in tools for keyword in ["model", "train", "predict", "dataset"]):
                return "ml"
        
        # Default suggestion
        return "finance"
    
    def _offer_continuation(self) -> None:
        """Offer user to continue with other debug actions."""
        console.print("\n[dim]Press Enter to return to debug menu, or 'q' to quit[/dim]")
        response = input()
        
        if response.lower() != 'q':
            # Re-display menu
            choice = self.display_menu()
            self.execute_choice(choice)
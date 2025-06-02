"""
Analyze command implementation for ARC-Eval CLI.

Handles the unified analysis workflow: debug → compliance → improve
Enhanced with framework intelligence and business intelligence features.
Separated from main CLI for better maintainability and testing.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agent_eval.commands.reliability_handler import ReliabilityHandler
from agent_eval.commands.compliance_handler import ComplianceHandler
from agent_eval.core.framework_intelligence import FrameworkIntelligence
from agent_eval.analysis.universal_failure_classifier import UniversalFailureClassifier
from agent_eval.analysis.remediation_engine import RemediationEngine
from agent_eval.templates.fixes.template_manager import TemplateManager


class AnalyzeCommand:
    """Handles unified analysis workflow execution with framework intelligence and business insights."""

    def __init__(self) -> None:
        """Initialize analyze command with console, handlers, and intelligence systems."""
        self.console = Console()
        self.framework_intelligence = FrameworkIntelligence()
        self.failure_classifier = UniversalFailureClassifier()
        self.remediation_engine = RemediationEngine()
        self.template_manager = TemplateManager()
    
    def execute(
        self,
        input_file: Path,
        domain: str,
        quick: bool = False,
        no_interactive: bool = False,
        verbose: bool = False,
        executive_summary: bool = False,
        benchmark_comparison: bool = False,
        framework_insights: bool = False,
        input_folder: Optional[Path] = None
    ) -> int:
        """
        Execute unified analysis workflow that chains debug → compliance → improve.
        Enhanced with framework intelligence and business intelligence features.

        Args:
            input_file: Agent outputs to analyze
            domain: Evaluation domain (finance, security, ml)
            quick: Quick analysis without agent-judge
            no_interactive: Skip interactive menus
            verbose: Enable verbose output
            executive_summary: Generate executive summary with business insights
            benchmark_comparison: Compare against industry benchmarks
            framework_insights: Show framework-specific insights and cross-framework learning
            input_folder: Analyze multiple files in folder (batch mode)

        Returns:
            Exit code (0 for success, 1 for failure)

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If invalid domain provided
        """
        self.console.print("\n[bold blue]🔄 Unified Analysis Workflow[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Handle batch mode if input_folder is provided
            if input_folder:
                return self._execute_batch_analysis(
                    input_folder, domain, quick, verbose,
                    executive_summary, benchmark_comparison, framework_insights
                )

            # Validate inputs for single file analysis
            if not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")

            if domain not in ['finance', 'security', 'ml']:
                raise ValueError(f"Invalid domain: {domain}. Must be one of: finance, security, ml")

            # Step 1: Debug Analysis
            debug_result = self._execute_debug_step(input_file, verbose)
            if debug_result != 0:
                self.console.print("[yellow]⚠️  Debug analysis found issues. Continuing to compliance check...[/yellow]")

            # Step 2: Compliance Check
            compliance_result = self._execute_compliance_step(input_file, domain, quick, verbose)

            # Step 3: Enhanced Analysis Features
            if executive_summary or benchmark_comparison or framework_insights:
                self._execute_enhanced_analysis(
                    input_file, domain, executive_summary,
                    benchmark_comparison, framework_insights
                )

            # Step 4: Show unified menu with all options (unless no_interactive)
            if not no_interactive:
                self._show_unified_menu(domain)

            return 0
            
        except FileNotFoundError as e:
            self.console.print(f"[red]File Error:[/red] {e}")
            return 1
        except ValueError as e:
            self.console.print(f"[red]Invalid Input:[/red] {e}")
            return 1
        except Exception as e:
            self.console.print(f"[red]Analysis failed:[/red] {e}")
            if verbose:
                self.console.print_exception()
            return 1
    
    def _execute_debug_step(self, input_file: Path, verbose: bool) -> int:
        """Execute debug analysis step."""
        self.console.print("\n[bold cyan]Step 1: Debug Analysis[/bold cyan]")
        
        handler = ReliabilityHandler()
        return handler.execute(
            input_file=input_file,
            unified_debug=True,
            workflow_reliability=True,
            schema_validation=True,
            verbose=verbose,
            no_interaction=True  # Suppress menu in intermediate steps
        )
    
    def _execute_compliance_step(
        self, 
        input_file: Path, 
        domain: str, 
        quick: bool, 
        verbose: bool
    ) -> int:
        """Execute compliance evaluation step."""
        self.console.print("\n[bold cyan]Step 2: Compliance Evaluation[/bold cyan]")
        
        compliance_handler = ComplianceHandler()
        return compliance_handler.execute(
            domain=domain,
            input_file=input_file,
            agent_judge=not quick,
            workflow=True,
            verbose=verbose,
            no_interaction=True  # Suppress menu in intermediate steps
        )
    
    def _show_unified_menu(self, domain: str) -> None:
        """Show unified post-evaluation menu with all options."""
        self.console.print("\n[bold cyan]Step 3: Analysis Complete[/bold cyan]")
        
        try:
            # Get the latest evaluation file
            evaluation_files = list(Path.cwd().glob(f"{domain}_evaluation_*.json"))
            if not evaluation_files:
                self.console.print("[yellow]No evaluation files found. Menu unavailable.[/yellow]")
                return
            
            evaluation_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            latest_evaluation = evaluation_files[0]
            
            # Load evaluation data
            with open(latest_evaluation, 'r') as f:
                eval_data = json.load(f)
            
            # Show unified post-evaluation menu
            from agent_eval.ui.post_evaluation_menu import PostEvaluationMenu
            menu = PostEvaluationMenu(
                domain=domain,
                evaluation_results=eval_data,
                workflow_type="compliance"  # Use compliance menu as it has all options
            )
            
            choice = menu.display_menu()
            menu.execute_choice(choice)
            
        except Exception as e:
            self.console.print(f"[yellow]Menu unavailable: {e}[/yellow]")
            self.console.print("\n[cyan]💡 Analysis complete. Next steps:[/cyan]")
            self.console.print("• Review analysis results above")
            self.console.print("• Run improvement workflow for actionable fixes")
            self.console.print(f"• Generate reports: arc-eval compliance --domain {domain} --export pdf")

    def _execute_batch_analysis(
        self,
        input_folder: Path,
        domain: str,
        quick: bool,
        verbose: bool,
        executive_summary: bool,
        benchmark_comparison: bool,
        framework_insights: bool
    ) -> int:
        """Execute batch analysis on multiple files."""
        self.console.print(f"\n[bold cyan]📁 Batch Analysis Mode[/bold cyan]")

        if not input_folder.exists() or not input_folder.is_dir():
            self.console.print(f"[red]Error:[/red] Folder not found: {input_folder}")
            return 1

        # Find all JSON files in the folder
        json_files = list(input_folder.glob("*.json"))
        if not json_files:
            self.console.print(f"[yellow]Warning:[/yellow] No JSON files found in {input_folder}")
            return 1

        self.console.print(f"Found {len(json_files)} files to analyze")

        batch_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing files...", total=len(json_files))

            for file_path in json_files:
                progress.update(task, description=f"Analyzing {file_path.name}")

                try:
                    # Load and analyze file
                    with open(file_path, 'r') as f:
                        trace_data = json.load(f)

                    # Perform framework intelligence analysis
                    file_result = self._analyze_single_trace(trace_data, file_path.name)
                    batch_results.append(file_result)

                except Exception as e:
                    self.console.print(f"[red]Error analyzing {file_path.name}:[/red] {e}")

                progress.advance(task)

        # Generate batch insights
        if executive_summary:
            self._generate_batch_executive_summary(batch_results, domain)

        if benchmark_comparison:
            self._generate_batch_benchmark_comparison(batch_results, domain)

        if framework_insights:
            self._generate_batch_framework_insights(batch_results)

        return 0

    def _execute_enhanced_analysis(
        self,
        input_file: Path,
        domain: str,
        executive_summary: bool,
        benchmark_comparison: bool,
        framework_insights: bool
    ) -> None:
        """Execute enhanced analysis features."""
        self.console.print("\n[bold cyan]🧠 Enhanced Analysis[/bold cyan]")

        # Load trace data
        with open(input_file, 'r') as f:
            trace_data = json.load(f)

        # Analyze with framework intelligence
        analysis_result = self._analyze_single_trace(trace_data, input_file.name)

        if executive_summary:
            self._display_executive_summary(analysis_result, domain)

        if benchmark_comparison:
            self._display_benchmark_comparison(analysis_result, domain)

        if framework_insights:
            self._display_framework_insights(analysis_result)

    def _analyze_single_trace(self, trace_data: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Analyze a single trace with framework intelligence."""
        # Classify failures using universal classifier
        classification_result = self.failure_classifier.classify_failure_universal(trace_data)

        # Get framework-specific insights
        framework_insights = self.framework_intelligence.analyze_framework_specific_context(trace_data)

        # Get cross-framework insights if failures detected
        cross_framework_insights = []
        if classification_result.universal_patterns:
            detected_framework = classification_result.universal_patterns[0].framework
            if detected_framework:
                cross_framework_insights = self.framework_intelligence.get_cross_framework_insights(
                    detected_framework, classification_result.universal_patterns
                )

        # Get remediation suggestions
        remediation_result = None
        if classification_result.universal_patterns:
            detected_framework = classification_result.universal_patterns[0].framework
            if detected_framework:
                remediation_result = self.remediation_engine.analyze_remediation_impact(
                    classification_result.universal_patterns, detected_framework
                )

        return {
            "filename": filename,
            "classification": classification_result,
            "framework_insights": framework_insights,
            "cross_framework_insights": cross_framework_insights,
            "remediation": remediation_result,
            "trace_data": trace_data
        }

    def _display_executive_summary(self, analysis_result: Dict[str, Any], domain: str) -> None:
        """Display executive summary with business insights."""
        self.console.print("\n[bold blue]📊 Executive Summary[/bold blue]")

        classification = analysis_result["classification"]
        remediation = analysis_result["remediation"]

        # Business impact assessment
        business_impact_score = classification.business_impact_score
        impact_level = "Low" if business_impact_score < 0.3 else "Medium" if business_impact_score < 0.7 else "High"

        # Create executive summary table
        summary_table = Table(title="Business Impact Assessment", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Business Impact", style="yellow")

        summary_table.add_row(
            "Overall Risk Level",
            impact_level,
            f"Score: {business_impact_score:.1%}"
        )

        if classification.universal_patterns:
            critical_issues = len([p for p in classification.universal_patterns if p.severity == "critical"])
            high_issues = len([p for p in classification.universal_patterns if p.severity == "high"])

            summary_table.add_row(
                "Critical Issues",
                str(critical_issues),
                "Immediate attention required" if critical_issues > 0 else "None detected"
            )

            summary_table.add_row(
                "High Priority Issues",
                str(high_issues),
                "Schedule remediation" if high_issues > 0 else "None detected"
            )

        if remediation and remediation.estimated_roi:
            roi_data = remediation.estimated_roi
            summary_table.add_row(
                "Estimated ROI",
                f"{roi_data['roi_ratio']:.1f}x",
                f"Payback in {roi_data.get('payback_period_days', 'N/A')} days"
            )

        self.console.print(summary_table)

        # Key recommendations
        if classification.remediation_priority:
            self.console.print("\n[bold yellow]🎯 Key Recommendations[/bold yellow]")
            for i, recommendation in enumerate(classification.remediation_priority[:3], 1):
                self.console.print(f"{i}. {recommendation}")

    def _display_benchmark_comparison(self, analysis_result: Dict[str, Any], domain: str) -> None:
        """Display benchmark comparison against industry standards."""
        self.console.print("\n[bold blue]📈 Industry Benchmark Comparison[/bold blue]")

        classification = analysis_result["classification"]

        # Industry benchmarks (simplified for demo)
        industry_benchmarks = {
            "finance": {"failure_rate": 0.15, "critical_issues": 0.05, "efficiency_score": 0.75},
            "security": {"failure_rate": 0.10, "critical_issues": 0.02, "efficiency_score": 0.80},
            "ml": {"failure_rate": 0.20, "critical_issues": 0.08, "efficiency_score": 0.70}
        }

        benchmark = industry_benchmarks.get(domain, industry_benchmarks["ml"])

        # Calculate current metrics
        total_patterns = len(classification.universal_patterns)
        critical_patterns = len([p for p in classification.universal_patterns if p.severity == "critical"])

        current_failure_rate = classification.business_impact_score
        current_critical_rate = critical_patterns / max(total_patterns, 1)
        current_efficiency = 1.0 - current_failure_rate  # Simplified efficiency calculation

        # Create comparison table
        comparison_table = Table(title=f"{domain.title()} Domain Benchmarks", show_header=True, header_style="bold magenta")
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column("Your Performance", style="green")
        comparison_table.add_column("Industry Average", style="yellow")
        comparison_table.add_column("Status", style="bold")

        # Failure rate comparison
        failure_status = "✅ Better" if current_failure_rate < benchmark["failure_rate"] else "⚠️ Below Average"
        comparison_table.add_row(
            "Failure Rate",
            f"{current_failure_rate:.1%}",
            f"{benchmark['failure_rate']:.1%}",
            failure_status
        )

        # Critical issues comparison
        critical_status = "✅ Better" if current_critical_rate < benchmark["critical_issues"] else "⚠️ Below Average"
        comparison_table.add_row(
            "Critical Issues Rate",
            f"{current_critical_rate:.1%}",
            f"{benchmark['critical_issues']:.1%}",
            critical_status
        )

        # Efficiency comparison
        efficiency_status = "✅ Better" if current_efficiency > benchmark["efficiency_score"] else "⚠️ Below Average"
        comparison_table.add_row(
            "Efficiency Score",
            f"{current_efficiency:.1%}",
            f"{benchmark['efficiency_score']:.1%}",
            efficiency_status
        )

        self.console.print(comparison_table)

        # Improvement suggestions
        self.console.print("\n[bold yellow]📋 Benchmark Insights[/bold yellow]")
        if current_failure_rate > benchmark["failure_rate"]:
            self.console.print("• Focus on reducing overall failure rate through better error handling")
        if current_critical_rate > benchmark["critical_issues"]:
            self.console.print("• Prioritize addressing critical issues to meet industry standards")
        if current_efficiency < benchmark["efficiency_score"]:
            self.console.print("• Optimize agent performance to improve efficiency metrics")

    def _display_framework_insights(self, analysis_result: Dict[str, Any]) -> None:
        """Display framework-specific insights and cross-framework learning."""
        self.console.print("\n[bold blue]🧠 Framework Intelligence[/bold blue]")

        framework_insights = analysis_result["framework_insights"]
        cross_framework_insights = analysis_result["cross_framework_insights"]
        classification = analysis_result["classification"]

        # Detected framework
        detected_framework = "Unknown"
        if classification.universal_patterns:
            detected_framework = classification.universal_patterns[0].framework or "Unknown"

        self.console.print(f"[cyan]Detected Framework:[/cyan] {detected_framework}")

        # Framework-specific insights
        if framework_insights:
            insights_table = Table(title="Framework-Specific Insights", show_header=True, header_style="bold magenta")
            insights_table.add_column("Type", style="cyan")
            insights_table.add_column("Insight", style="green")
            insights_table.add_column("Business Impact", style="yellow")

            for insight in framework_insights[:5]:  # Show top 5 insights
                insights_table.add_row(
                    insight.insight_type.title(),
                    insight.title,
                    insight.business_impact
                )

            self.console.print(insights_table)

        # Cross-framework learning
        if cross_framework_insights:
            self.console.print("\n[bold yellow]🔄 Cross-Framework Learning[/bold yellow]")
            for insight in cross_framework_insights[:3]:  # Show top 3 cross-framework insights
                source = insight.source_framework or "Other frameworks"
                panel_content = f"[bold]{insight.title}[/bold]\n\n{insight.description}"
                if insight.source_framework:
                    panel_content += f"\n\n[dim]💡 Insight from {source.title()}[/dim]"

                panel = Panel(
                    panel_content,
                    title=f"Learn from {source.title()}",
                    border_style="blue"
                )
                self.console.print(panel)

        # Code examples from templates
        if classification.universal_patterns:
            self._display_code_examples(classification.universal_patterns[0], detected_framework)

    def _display_code_examples(self, failure_pattern, framework: str) -> None:
        """Display relevant code examples from template library."""
        templates = self.template_manager.get_fix_templates(
            framework, failure_pattern.pattern_type, failure_pattern.subtype
        )

        if templates:
            self.console.print("\n[bold green]💻 Code Examples[/bold green]")

            # Show the best template (highest priority/quality)
            best_template = templates[0]

            code_panel = Panel(
                f"[bold]{best_template.title}[/bold]\n\n"
                f"{best_template.description}\n\n"
                f"[dim]Difficulty: {best_template.difficulty} | "
                f"Business Impact: {best_template.business_impact}[/dim]",
                title="Recommended Fix",
                border_style="green"
            )
            self.console.print(code_panel)

            # Show implementation steps
            if best_template.implementation_steps:
                self.console.print("\n[bold cyan]📋 Implementation Steps[/bold cyan]")
                for i, step in enumerate(best_template.implementation_steps[:5], 1):
                    self.console.print(f"{i}. {step}")

    def _generate_batch_executive_summary(self, batch_results: List[Dict[str, Any]], domain: str) -> None:
        """Generate executive summary for batch analysis."""
        self.console.print("\n[bold blue]📊 Batch Executive Summary[/bold blue]")

        total_files = len(batch_results)
        total_issues = sum(len(result["classification"].universal_patterns) for result in batch_results)
        critical_issues = sum(
            len([p for p in result["classification"].universal_patterns if p.severity == "critical"])
            for result in batch_results
        )

        # Framework distribution
        framework_counts = {}
        for result in batch_results:
            if result["classification"].universal_patterns:
                framework = result["classification"].universal_patterns[0].framework
                if framework:
                    framework_counts[framework] = framework_counts.get(framework, 0) + 1

        # Create summary table
        summary_table = Table(title="Batch Analysis Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Impact", style="yellow")

        summary_table.add_row("Files Analyzed", str(total_files), "Complete coverage")
        summary_table.add_row("Total Issues Found", str(total_issues), f"Avg {total_issues/total_files:.1f} per file")
        summary_table.add_row("Critical Issues", str(critical_issues), "Immediate attention needed" if critical_issues > 0 else "None")

        if framework_counts:
            most_common_framework = max(framework_counts.items(), key=lambda x: x[1])
            summary_table.add_row("Primary Framework", most_common_framework[0], f"{most_common_framework[1]} files")

        self.console.print(summary_table)

    def _generate_batch_benchmark_comparison(self, batch_results: List[Dict[str, Any]], domain: str) -> None:
        """Generate benchmark comparison for batch analysis."""
        self.console.print("\n[bold blue]📈 Batch Benchmark Analysis[/bold blue]")

        # Calculate aggregate metrics
        total_files = len(batch_results)
        avg_business_impact = sum(
            result["classification"].business_impact_score for result in batch_results
        ) / total_files if total_files > 0 else 0

        # Industry benchmark
        industry_benchmarks = {
            "finance": 0.15, "security": 0.10, "ml": 0.20
        }
        benchmark = industry_benchmarks.get(domain, 0.15)

        performance_status = "✅ Above Average" if avg_business_impact < benchmark else "⚠️ Below Average"

        self.console.print(f"[cyan]Average Business Impact Score:[/cyan] {avg_business_impact:.1%}")
        self.console.print(f"[cyan]Industry Benchmark ({domain}):[/cyan] {benchmark:.1%}")
        self.console.print(f"[cyan]Performance Status:[/cyan] {performance_status}")

    def _generate_batch_framework_insights(self, batch_results: List[Dict[str, Any]]) -> None:
        """Generate framework insights for batch analysis."""
        self.console.print("\n[bold blue]🧠 Batch Framework Intelligence[/bold blue]")

        # Collect all frameworks and insights
        framework_insights = {}
        for result in batch_results:
            if result["classification"].universal_patterns:
                framework = result["classification"].universal_patterns[0].framework
                if framework:
                    if framework not in framework_insights:
                        framework_insights[framework] = []
                    framework_insights[framework].extend(result["framework_insights"])

        # Display insights by framework
        for framework, insights in framework_insights.items():
            if insights:
                self.console.print(f"\n[bold cyan]{framework.title()} Insights:[/bold cyan]")

                # Group insights by type
                insight_types = {}
                for insight in insights:
                    if insight.insight_type not in insight_types:
                        insight_types[insight.insight_type] = []
                    insight_types[insight.insight_type].append(insight)

                for insight_type, type_insights in insight_types.items():
                    self.console.print(f"  [yellow]{insight_type.title()}:[/yellow] {len(type_insights)} recommendations")

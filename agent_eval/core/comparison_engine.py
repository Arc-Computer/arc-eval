"""
Comparison Engine for ARC-Eval Core Loop
Provides before/after evaluation analysis and improvement tracking.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from agent_eval.analysis.self_improvement import SelfImprovementEngine


@dataclass
class ScenarioComparison:
    """Comparison result for a single scenario."""
    
    scenario_id: str
    baseline_passed: bool
    current_passed: bool
    improvement_status: str  # "improved", "degraded", "unchanged"
    baseline_score: Optional[float]
    current_score: Optional[float]
    score_delta: Optional[float]
    

@dataclass
class ComparisonReport:
    """Complete comparison report between baseline and current evaluation."""
    
    baseline_evaluation: str
    current_evaluation: str
    agent_id: str
    domain: str
    comparison_date: str
    summary: Dict[str, Any]
    scenario_comparisons: List[ScenarioComparison]
    trend_analysis: Dict[str, Any]
    recommendations: List[str]
    

class ComparisonEngine:
    """Engine for comparing evaluation results and tracking improvements."""
    
    def __init__(self):
        self.self_improvement_engine = SelfImprovementEngine()
    
    def compare_evaluations(self, 
                          current_evaluation_data: Dict[str, Any],
                          baseline_file: Path,
                          output_file: Optional[Path] = None) -> ComparisonReport:
        """Compare current evaluation with baseline evaluation."""
        
        # Load baseline evaluation
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        # Extract metadata
        agent_id = current_evaluation_data.get('agent_id', 'unknown_agent')
        domain = current_evaluation_data.get('domain', 'unknown')
        
        # Get evaluation results
        current_results = current_evaluation_data.get('results', [])
        baseline_results = baseline_data.get('results', [])
        
        if not current_results or not baseline_results:
            raise ValueError("Missing evaluation results in current or baseline data")
        
        # Create scenario-level comparisons
        scenario_comparisons = self._compare_scenarios(baseline_results, current_results)
        
        # Generate summary statistics
        summary = self._create_comparison_summary(scenario_comparisons, baseline_results, current_results)
        
        # Generate trend analysis using self-improvement engine
        trend_analysis = self._analyze_trends(agent_id, domain)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scenario_comparisons, summary)
        
        # Create comparison report
        comparison_report = ComparisonReport(
            baseline_evaluation=baseline_data.get('evaluation_id', 'baseline'),
            current_evaluation=current_evaluation_data.get('evaluation_id', 'current'),
            agent_id=agent_id,
            domain=domain,
            comparison_date=datetime.now().isoformat(),
            summary=summary,
            scenario_comparisons=scenario_comparisons,
            trend_analysis=trend_analysis,
            recommendations=recommendations
        )
        
        # Save report if output file specified
        if output_file:
            self._save_comparison_report(comparison_report, output_file)
        
        return comparison_report
    
    def _compare_scenarios(self, 
                          baseline_results: List[Dict[str, Any]], 
                          current_results: List[Dict[str, Any]]) -> List[ScenarioComparison]:
        """Compare individual scenarios between baseline and current."""
        
        # Create lookup maps for efficient comparison
        baseline_map = {r.get('scenario_id'): r for r in baseline_results if r.get('scenario_id')}
        current_map = {r.get('scenario_id'): r for r in current_results if r.get('scenario_id')}
        
        comparisons = []
        
        # Get all scenario IDs from both evaluations
        all_scenario_ids = set(baseline_map.keys()) | set(current_map.keys())
        
        for scenario_id in all_scenario_ids:
            baseline_result = baseline_map.get(scenario_id)
            current_result = current_map.get(scenario_id)
            
            # Handle missing scenarios
            if not baseline_result or not current_result:
                continue
            
            # Extract pass/fail status
            baseline_passed = baseline_result.get('passed', False)
            current_passed = current_result.get('passed', False)
            
            # Extract scores if available
            baseline_score = self._extract_score(baseline_result)
            current_score = self._extract_score(current_result)
            
            score_delta = None
            if baseline_score is not None and current_score is not None:
                score_delta = current_score - baseline_score
            
            # Determine improvement status
            improvement_status = self._determine_improvement_status(
                baseline_passed, current_passed, score_delta
            )
            
            comparison = ScenarioComparison(
                scenario_id=scenario_id,
                baseline_passed=baseline_passed,
                current_passed=current_passed,
                improvement_status=improvement_status,
                baseline_score=baseline_score,
                current_score=current_score,
                score_delta=score_delta
            )
            
            comparisons.append(comparison)
        
        return comparisons
    
    def _extract_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Extract numeric score from evaluation result."""
        
        # Try different score field names
        score_fields = ['score', 'confidence', 'reward_signal', 'pass_rate']
        
        for field in score_fields:
            if field in result and isinstance(result[field], (int, float)):
                return float(result[field])
        
        # Try extracting from reward_signals dict
        reward_signals = result.get('reward_signals', {})
        if isinstance(reward_signals, dict) and reward_signals:
            # Use average of all reward signals
            scores = [v for v in reward_signals.values() if isinstance(v, (int, float))]
            if scores:
                return sum(scores) / len(scores)
        
        return None
    
    def _determine_improvement_status(self, 
                                    baseline_passed: bool, 
                                    current_passed: bool, 
                                    score_delta: Optional[float]) -> str:
        """Determine if scenario improved, degraded, or unchanged."""
        
        # Pass/fail status change takes precedence
        if not baseline_passed and current_passed:
            return "improved"
        elif baseline_passed and not current_passed:
            return "degraded"
        
        # If pass/fail status is same, check score delta
        if score_delta is not None:
            if score_delta > 0.05:  # Threshold for meaningful improvement
                return "improved"
            elif score_delta < -0.05:  # Threshold for meaningful degradation
                return "degraded"
        
        return "unchanged"
    
    def _create_comparison_summary(self, 
                                 comparisons: List[ScenarioComparison], 
                                 baseline_results: List[Dict], 
                                 current_results: List[Dict]) -> Dict[str, Any]:
        """Create summary statistics for the comparison."""
        
        total_scenarios = len(comparisons)
        
        # Count improvements and degradations
        improved = len([c for c in comparisons if c.improvement_status == "improved"])
        degraded = len([c for c in comparisons if c.improvement_status == "degraded"])
        unchanged = len([c for c in comparisons if c.improvement_status == "unchanged"])
        
        # Calculate pass rates
        baseline_passed = len([c for c in comparisons if c.baseline_passed])
        current_passed = len([c for c in comparisons if c.current_passed])
        
        baseline_pass_rate = (baseline_passed / total_scenarios) * 100 if total_scenarios > 0 else 0
        current_pass_rate = (current_passed / total_scenarios) * 100 if total_scenarios > 0 else 0
        pass_rate_delta = current_pass_rate - baseline_pass_rate
        
        # Calculate score improvements
        score_deltas = [c.score_delta for c in comparisons if c.score_delta is not None]
        avg_score_improvement = sum(score_deltas) / len(score_deltas) if score_deltas else 0
        
        return {
            "total_scenarios": total_scenarios,
            "scenarios_improved": improved,
            "scenarios_degraded": degraded,
            "scenarios_unchanged": unchanged,
            "baseline_pass_rate": f"{baseline_pass_rate:.1f}%",
            "current_pass_rate": f"{current_pass_rate:.1f}%",
            "pass_rate_change": f"{pass_rate_delta:+.1f}%",
            "avg_score_improvement": f"{avg_score_improvement:+.3f}" if avg_score_improvement != 0 else "0.000",
            "improvement_percentage": f"{(improved / total_scenarios) * 100:.1f}%" if total_scenarios > 0 else "0%",
            "net_improvement": improved - degraded
        }
    
    def _analyze_trends(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """Analyze performance trends using self-improvement engine."""
        
        try:
            trends = self.self_improvement_engine.get_performance_trends(
                agent_id=agent_id,
                domain=domain,
                lookback_days=30
            )
            
            if "error" in trends:
                return {"status": "no_historical_data", "message": trends["error"]}
            
            return {
                "status": "success",
                "evaluation_count": trends.get("evaluation_count", 0),
                "date_range": trends.get("date_range", {}),
                "reward_trends": trends.get("reward_trends", {}),
                "improvement_velocity": trends.get("improvement_velocity", 0.0)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _generate_recommendations(self, 
                                comparisons: List[ScenarioComparison], 
                                summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison results."""
        
        recommendations = []
        
        # Check overall improvement
        net_improvement = summary.get("net_improvement", 0)
        improved_count = summary.get("scenarios_improved", 0)
        degraded_count = summary.get("scenarios_degraded", 0)
        
        if net_improvement > 0:
            recommendations.append(f"Net improvement: {improved_count} scenarios improved, {degraded_count} degraded")
        elif net_improvement < 0:
            recommendations.append(f"Performance regression: {degraded_count} scenarios worse, {improved_count} improved")
        else:
            recommendations.append("Mixed results: equal improvements and degradations")
        
        # Check pass rate change
        pass_rate_change = float(summary.get("pass_rate_change", "0%").replace("%", "").replace("+", ""))
        if pass_rate_change > 5:
            recommendations.append(f"Pass rate improved by {pass_rate_change:.1f}%")
        elif pass_rate_change < -5:
            recommendations.append(f"Pass rate declined by {abs(pass_rate_change):.1f}%")
        
        # Identify specific areas needing attention
        degraded_scenarios = [c for c in comparisons if c.improvement_status == "degraded"]
        if degraded_scenarios:
            scenario_ids = [c.scenario_id for c in degraded_scenarios[:3]]  # Top 3
            recommendations.append(f"Review degraded scenarios: {', '.join(scenario_ids)}")
        
        # Check for consistent improvement
        improved_scenarios = [c for c in comparisons if c.improvement_status == "improved"]
        if len(improved_scenarios) > len(degraded_scenarios) * 2:
            recommendations.append("Improvement pattern suggests effective changes")
        
        return recommendations
    
    def _save_comparison_report(self, report: ComparisonReport, output_file: Path) -> None:
        """Save comparison report as JSON."""
        
        # Convert dataclasses to dictionaries for JSON serialization
        report_dict = {
            "baseline_evaluation": report.baseline_evaluation,
            "current_evaluation": report.current_evaluation,
            "agent_id": report.agent_id,
            "domain": report.domain,
            "comparison_date": report.comparison_date,
            "summary": report.summary,
            "scenario_comparisons": [
                {
                    "scenario_id": c.scenario_id,
                    "baseline_passed": c.baseline_passed,
                    "current_passed": c.current_passed,
                    "improvement_status": c.improvement_status,
                    "baseline_score": c.baseline_score,
                    "current_score": c.current_score,
                    "score_delta": c.score_delta
                }
                for c in report.scenario_comparisons
            ],
            "trend_analysis": report.trend_analysis,
            "recommendations": report.recommendations
        }
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON report
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    def display_comparison_summary(self, report: ComparisonReport) -> None:
        """Display comparison summary in console."""
        
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Create summary panel
        summary_text = f"""
**Agent:** {report.agent_id} ({report.domain})
**Baseline:** {report.baseline_evaluation}
**Current:** {report.current_evaluation}

**Pass Rate:** {report.summary['baseline_pass_rate']} → {report.summary['current_pass_rate']} ({report.summary['pass_rate_change']})
**Scenarios:** {report.summary['scenarios_improved']} improved, {report.summary['scenarios_degraded']} degraded, {report.summary['scenarios_unchanged']} unchanged
**Net Improvement:** {report.summary['net_improvement']} scenarios
        """
        
        console.print(Panel(summary_text.strip(), title="Evaluation Comparison", border_style="blue"))
        
        # Display analysis
        if report.recommendations:
            console.print("\n**Analysis:**")
            for rec in report.recommendations:
                console.print(f"  • {rec}")
        
        # Create detailed table for significant changes
        significant_changes = [
            c for c in report.scenario_comparisons 
            if c.improvement_status in ["improved", "degraded"]
        ]
        
        if significant_changes:
            table = Table(title="Scenario Changes")
            table.add_column("Scenario ID", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Baseline", style="red")
            table.add_column("Current", style="green")
            table.add_column("Score Delta", style="bold")
            
            for change in significant_changes[:10]:  # Show top 10 changes
                status_emoji = "✅" if change.improvement_status == "improved" else "❌"
                baseline_status = "✅" if change.baseline_passed else "❌"
                current_status = "✅" if change.current_passed else "❌"
                
                score_change = ""
                if change.score_delta is not None:
                    score_change = f"{change.score_delta:+.3f}"
                
                table.add_row(
                    change.scenario_id,
                    f"{status_emoji} {change.improvement_status}",
                    baseline_status,
                    current_status,
                    score_change
                )
            
            console.print(table)
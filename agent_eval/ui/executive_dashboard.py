"""
Executive Dashboard for ARC-Eval.

This module provides business-focused insights and reporting for stakeholders,
including compliance risk scoring, cost efficiency analysis, and ROI calculations.

Key Features:
- Executive summary generation
- Business impact assessment
- Industry benchmarking
- Trend analysis and reporting
- Compliance risk scoring
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter

from agent_eval.analysis.universal_failure_classifier import FailurePattern, analyze_failure_patterns_batch
from agent_eval.analysis.remediation_engine import RemediationEngine, RemediationSuggestion

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummary:
    """Executive summary of agent evaluation results."""
    overall_health_score: float  # 0-100
    compliance_risk_score: float  # 0-100
    cost_efficiency_score: float  # 0-100
    improvement_opportunities: List[str]
    critical_issues: List[str]
    business_impact: str
    recommended_actions: List[str]
    roi_projection: Dict[str, Any]


@dataclass
class IndustryBenchmark:
    """Industry benchmarking data."""
    industry_average: float
    percentile_ranking: int  # 1-100
    peer_comparison: str
    improvement_potential: float


@dataclass
class TrendAnalysis:
    """Trend analysis over time."""
    metric_name: str
    current_value: float
    previous_value: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    change_percentage: float
    projection: Optional[float]


class ExecutiveDashboard:
    """
    Executive dashboard generator for business-focused insights.
    
    Provides high-level metrics, industry benchmarking, and actionable
    recommendations for business stakeholders.
    """
    
    def __init__(self):
        """Initialize executive dashboard with industry benchmarks."""
        self.remediation_engine = RemediationEngine()
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.historical_data = []
    
    def generate_executive_summary(self, evaluation_results: List[Dict[str, Any]]) -> ExecutiveSummary:
        """
        Generate business-focused insights for stakeholders.
        
        Args:
            evaluation_results: List of evaluation results from agent testing
            
        Returns:
            Executive summary with business metrics and recommendations
        """
        # Analyze failure patterns
        traces = [result.get("trace", {}) for result in evaluation_results if result.get("trace")]
        batch_analysis = analyze_failure_patterns_batch(traces)
        
        # Calculate core metrics
        health_score = self._calculate_health_score(evaluation_results, batch_analysis)
        risk_score = self._calculate_compliance_risk_score(batch_analysis)
        efficiency_score = self._calculate_cost_efficiency_score(evaluation_results)
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(batch_analysis)
        
        # Generate improvement opportunities
        improvement_opportunities = self._identify_improvement_opportunities(batch_analysis)
        
        # Calculate business impact
        business_impact = self._assess_business_impact(batch_analysis, evaluation_results)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(batch_analysis)
        
        # Project ROI
        roi_projection = self._calculate_roi_projection(batch_analysis)
        
        return ExecutiveSummary(
            overall_health_score=health_score,
            compliance_risk_score=risk_score,
            cost_efficiency_score=efficiency_score,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            business_impact=business_impact,
            recommended_actions=recommended_actions,
            roi_projection=roi_projection
        )
    
    def calculate_business_impact(
        self, 
        failure_patterns: List[FailurePattern], 
        remediation_suggestions: List[RemediationSuggestion]
    ) -> Dict[str, Any]:
        """
        Calculate ROI and business impact of implementing fixes.
        
        Args:
            failure_patterns: Detected failure patterns
            remediation_suggestions: Suggested remediation actions
            
        Returns:
            Business impact analysis with ROI calculations
        """
        # Calculate current costs
        current_costs = self._calculate_current_costs(failure_patterns)
        
        # Calculate remediation costs
        remediation_costs = self._calculate_remediation_costs(remediation_suggestions)
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(failure_patterns, remediation_suggestions)
        
        # Calculate ROI
        roi = (potential_savings - remediation_costs) / remediation_costs if remediation_costs > 0 else 0
        
        # Calculate payback period
        monthly_savings = potential_savings / 12  # Assume annual savings
        payback_months = remediation_costs / monthly_savings if monthly_savings > 0 else float('inf')
        
        return {
            "current_annual_costs": current_costs,
            "remediation_investment": remediation_costs,
            "potential_annual_savings": potential_savings,
            "net_annual_benefit": potential_savings - remediation_costs,
            "roi_percentage": roi * 100,
            "payback_period_months": payback_months,
            "business_impact_summary": self._generate_business_impact_summary(
                current_costs, potential_savings, roi
            )
        }
    
    def generate_trend_analysis(self, historical_data: List[Dict[str, Any]]) -> List[TrendAnalysis]:
        """
        Show improvement trends over time.
        
        Args:
            historical_data: Historical evaluation data
            
        Returns:
            List of trend analyses for key metrics
        """
        if len(historical_data) < 2:
            return []
        
        trends = []
        
        # Analyze key metrics over time
        metrics = ["health_score", "compliance_risk", "cost_efficiency", "failure_rate"]
        
        for metric in metrics:
            trend = self._analyze_metric_trend(historical_data, metric)
            if trend:
                trends.append(trend)
        
        return trends
    
    def compare_to_industry_benchmark(self, evaluation_results: List[Dict[str, Any]]) -> IndustryBenchmark:
        """
        Compare performance to industry benchmarks.
        
        Args:
            evaluation_results: Current evaluation results
            
        Returns:
            Industry benchmark comparison
        """
        # Calculate current performance score
        current_score = self._calculate_overall_performance_score(evaluation_results)
        
        # Get industry benchmark
        industry_avg = self.industry_benchmarks.get("overall_performance", 75.0)
        
        # Calculate percentile ranking
        percentile = min(100, max(1, int((current_score / industry_avg) * 50)))
        
        # Generate comparison text
        if current_score > industry_avg * 1.1:
            comparison = "Significantly above industry average"
        elif current_score > industry_avg:
            comparison = "Above industry average"
        elif current_score > industry_avg * 0.9:
            comparison = "Near industry average"
        else:
            comparison = "Below industry average"
        
        # Calculate improvement potential
        improvement_potential = max(0, industry_avg * 1.2 - current_score)
        
        return IndustryBenchmark(
            industry_average=industry_avg,
            percentile_ranking=percentile,
            peer_comparison=comparison,
            improvement_potential=improvement_potential
        )
    
    def _calculate_health_score(
        self, 
        evaluation_results: List[Dict[str, Any]], 
        batch_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall health score (0-100)."""
        if not evaluation_results:
            return 0.0
        
        # Base score from pass rate
        total_evaluations = len(evaluation_results)
        passed_evaluations = sum(1 for result in evaluation_results if result.get("passed", False))
        pass_rate = passed_evaluations / total_evaluations if total_evaluations > 0 else 0
        
        base_score = pass_rate * 100
        
        # Adjust for failure severity
        failure_rate = batch_analysis.get("summary", {}).get("failure_rate", 0)
        severity_penalty = failure_rate * 20  # Up to 20 point penalty
        
        # Adjust for framework diversity (bonus for multi-framework success)
        frameworks_detected = batch_analysis.get("summary", {}).get("frameworks_detected", 1)
        diversity_bonus = min(10, frameworks_detected * 2)  # Up to 10 point bonus
        
        final_score = max(0, min(100, base_score - severity_penalty + diversity_bonus))
        return round(final_score, 1)
    
    def _calculate_compliance_risk_score(self, batch_analysis: Dict[str, Any]) -> float:
        """Calculate compliance risk score (0-100, higher = more risk)."""
        all_patterns = batch_analysis.get("all_patterns", [])
        
        if not all_patterns:
            return 0.0
        
        # Weight patterns by severity
        severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        total_risk = 0
        
        for pattern in all_patterns:
            if hasattr(pattern, 'severity') and hasattr(pattern, 'confidence'):
                weight = severity_weights.get(pattern.severity, 5)
                total_risk += weight * pattern.confidence
        
        # Normalize to 0-100 scale
        max_possible_risk = len(all_patterns) * 25  # Assuming all critical
        risk_score = min(100, (total_risk / max_possible_risk) * 100) if max_possible_risk > 0 else 0
        
        return round(risk_score, 1)
    
    def _calculate_cost_efficiency_score(self, evaluation_results: List[Dict[str, Any]]) -> float:
        """Calculate cost efficiency score (0-100)."""
        if not evaluation_results:
            return 0.0
        
        # Simple heuristic based on evaluation success and resource usage
        total_cost = sum(result.get("cost", 0) for result in evaluation_results)
        total_success = sum(1 for result in evaluation_results if result.get("passed", False))
        
        if total_cost == 0:
            return 100.0  # No cost data available
        
        # Cost per successful evaluation
        cost_per_success = total_cost / total_success if total_success > 0 else float('inf')
        
        # Industry benchmark: $0.10 per successful evaluation
        benchmark_cost = 0.10
        
        if cost_per_success <= benchmark_cost:
            return 100.0
        elif cost_per_success <= benchmark_cost * 2:
            return 75.0
        elif cost_per_success <= benchmark_cost * 5:
            return 50.0
        else:
            return 25.0
    
    def _identify_critical_issues(self, batch_analysis: Dict[str, Any]) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        critical_issues = []
        all_patterns = batch_analysis.get("all_patterns", [])
        
        # Find critical severity patterns
        critical_patterns = [p for p in all_patterns if hasattr(p, 'severity') and p.severity == "critical"]
        
        for pattern in critical_patterns[:3]:  # Top 3 critical issues
            if hasattr(pattern, 'subtype') and hasattr(pattern, 'business_impact'):
                critical_issues.append(f"{pattern.subtype}: {pattern.business_impact}")
        
        # Add high-frequency issues
        top_patterns = batch_analysis.get("top_patterns", [])
        for pattern_key, count in top_patterns[:2]:
            if count > 3:  # Frequent issue
                critical_issues.append(f"Frequent issue: {pattern_key} (occurred {count} times)")
        
        return critical_issues
    
    def _identify_improvement_opportunities(self, batch_analysis: Dict[str, Any]) -> List[str]:
        """Identify improvement opportunities."""
        opportunities = []
        
        # Framework-specific opportunities
        framework_stats = batch_analysis.get("framework_stats", {})
        if len(framework_stats) > 1:
            # Find best performing framework
            best_framework = min(framework_stats.items(), key=lambda x: x[1].get("avg_severity", 0))[0]
            opportunities.append(f"Adopt best practices from {best_framework} framework")
        
        # Pattern-specific opportunities
        recommendations = batch_analysis.get("recommendations", [])
        opportunities.extend(recommendations[:3])  # Top 3 recommendations
        
        return opportunities

    def _assess_business_impact(
        self,
        batch_analysis: Dict[str, Any],
        evaluation_results: List[Dict[str, Any]]
    ) -> str:
        """Assess overall business impact."""
        failure_rate = batch_analysis.get("summary", {}).get("failure_rate", 0)
        total_evaluations = len(evaluation_results)

        if failure_rate > 0.3:
            return f"High business risk: {failure_rate:.1%} failure rate across {total_evaluations} evaluations"
        elif failure_rate > 0.1:
            return f"Moderate business risk: {failure_rate:.1%} failure rate requires attention"
        else:
            return f"Low business risk: {failure_rate:.1%} failure rate within acceptable range"

    def _generate_recommended_actions(self, batch_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommended actions for executives."""
        actions = []

        # Critical issues first
        critical_patterns = [
            p for p in batch_analysis.get("all_patterns", [])
            if hasattr(p, 'severity') and p.severity == "critical"
        ]

        if critical_patterns:
            actions.append("Immediately address critical failure patterns")

        # Framework recommendations
        framework_stats = batch_analysis.get("framework_stats", {})
        if len(framework_stats) > 1:
            actions.append("Standardize on best-performing framework patterns")

        # General recommendations
        recommendations = batch_analysis.get("recommendations", [])
        actions.extend(recommendations[:2])  # Top 2 recommendations

        return actions

    def _calculate_roi_projection(self, batch_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ROI projection for improvements."""
        all_patterns = batch_analysis.get("all_patterns", [])

        if not all_patterns:
            return {"projected_savings": 0, "investment_required": 0, "roi_percentage": 0}

        # Estimate costs based on pattern severity
        severity_costs = {"critical": 10000, "high": 5000, "medium": 2000, "low": 500}  # Annual cost per pattern

        total_current_cost = sum(
            severity_costs.get(getattr(p, 'severity', 'medium'), 2000) * getattr(p, 'confidence', 0.5)
            for p in all_patterns
        )

        # Estimate investment required (20% of current cost for remediation)
        investment_required = total_current_cost * 0.2

        # Estimate savings (80% of current cost can be saved)
        projected_savings = total_current_cost * 0.8

        # Calculate ROI
        roi_percentage = ((projected_savings - investment_required) / investment_required * 100) if investment_required > 0 else 0

        return {
            "projected_annual_savings": projected_savings,
            "investment_required": investment_required,
            "roi_percentage": roi_percentage,
            "payback_period_months": (investment_required / (projected_savings / 12)) if projected_savings > 0 else 0
        }

    def _calculate_current_costs(self, failure_patterns: List[FailurePattern]) -> float:
        """Calculate current costs from failure patterns."""
        severity_costs = {"critical": 10000, "high": 5000, "medium": 2000, "low": 500}

        total_cost = sum(
            severity_costs.get(pattern.severity, 2000) * pattern.confidence
            for pattern in failure_patterns
        )

        return total_cost

    def _calculate_remediation_costs(self, remediation_suggestions: List[RemediationSuggestion]) -> float:
        """Calculate costs for implementing remediation suggestions."""
        effort_costs = {"low": 5000, "medium": 15000, "high": 40000}  # Implementation costs

        total_cost = sum(
            effort_costs.get(suggestion.estimated_effort, 15000)
            for suggestion in remediation_suggestions
        )

        return total_cost

    def _calculate_potential_savings(
        self,
        failure_patterns: List[FailurePattern],
        remediation_suggestions: List[RemediationSuggestion]
    ) -> float:
        """Calculate potential savings from implementing fixes."""
        # Assume 80% of current failure costs can be saved
        current_costs = self._calculate_current_costs(failure_patterns)
        return current_costs * 0.8

    def _generate_business_impact_summary(
        self,
        current_costs: float,
        potential_savings: float,
        roi: float
    ) -> str:
        """Generate business impact summary text."""
        if roi > 3.0:
            return f"High-impact investment: ${potential_savings:,.0f} annual savings with {roi:.1f}x ROI"
        elif roi > 1.5:
            return f"Moderate-impact investment: ${potential_savings:,.0f} annual savings with {roi:.1f}x ROI"
        elif roi > 0.5:
            return f"Low-impact investment: ${potential_savings:,.0f} annual savings with {roi:.1f}x ROI"
        else:
            return f"Investment may not be cost-effective: {roi:.1f}x ROI"

    def _analyze_metric_trend(self, historical_data: List[Dict[str, Any]], metric: str) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric."""
        if len(historical_data) < 2:
            return None

        # Get current and previous values
        current_data = historical_data[-1]
        previous_data = historical_data[-2]

        current_value = current_data.get(metric, 0)
        previous_value = previous_data.get(metric, 0)

        if previous_value == 0:
            return None

        # Calculate change
        change_percentage = ((current_value - previous_value) / previous_value) * 100

        # Determine trend direction
        if abs(change_percentage) < 5:
            trend_direction = "stable"
        elif change_percentage > 0:
            trend_direction = "improving" if metric in ["health_score", "cost_efficiency"] else "declining"
        else:
            trend_direction = "declining" if metric in ["health_score", "cost_efficiency"] else "improving"

        # Simple projection (linear trend)
        if len(historical_data) >= 3:
            trend_slope = (current_value - historical_data[-3].get(metric, current_value)) / 2
            projection = current_value + trend_slope
        else:
            projection = None

        return TrendAnalysis(
            metric_name=metric,
            current_value=current_value,
            previous_value=previous_value,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            projection=projection
        )

    def _calculate_overall_performance_score(self, evaluation_results: List[Dict[str, Any]]) -> float:
        """Calculate overall performance score for benchmarking."""
        if not evaluation_results:
            return 0.0

        # Simple performance score based on pass rate and efficiency
        total_evaluations = len(evaluation_results)
        passed_evaluations = sum(1 for result in evaluation_results if result.get("passed", False))
        pass_rate = passed_evaluations / total_evaluations

        # Factor in cost efficiency
        total_cost = sum(result.get("cost", 0) for result in evaluation_results)
        avg_cost = total_cost / total_evaluations if total_evaluations > 0 else 0

        # Benchmark: $0.10 per evaluation
        cost_efficiency = min(1.0, 0.10 / avg_cost) if avg_cost > 0 else 1.0

        # Combined score (70% pass rate, 30% cost efficiency)
        performance_score = (pass_rate * 0.7 + cost_efficiency * 0.3) * 100

        return round(performance_score, 1)

    def _load_industry_benchmarks(self) -> Dict[str, float]:
        """Load industry benchmark data."""
        # Default industry benchmarks (would be loaded from external source in production)
        return {
            "overall_performance": 75.0,
            "pass_rate": 0.85,
            "cost_per_evaluation": 0.10,
            "compliance_risk": 25.0,
            "efficiency_score": 70.0
        }

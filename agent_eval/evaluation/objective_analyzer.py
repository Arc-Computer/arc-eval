"""
Objective, data-driven framework analysis without bias or favoritism.

This module provides statistically-backed recommendations based solely on measured 
performance data, not subjective opinions. All claims are backed by data and 
include confidence intervals, sample sizes, and statistical significance testing.
"""

import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from agent_eval.core.constants import FRAMEWORK_EXPECTED_PERFORMANCE


class RecommendationStrength(Enum):
    """Statistical strength of recommendation based on data quality."""
    STRONG = "strong"        # p < 0.05, n >= 20
    MODERATE = "moderate"    # p < 0.10, n >= 10 
    WEAK = "weak"           # p < 0.20, n >= 5
    INSUFFICIENT = "insufficient"  # not enough data


@dataclass
class PerformanceMetric:
    """A single measured performance metric with statistical context."""
    name: str
    measured_value: float
    expected_value: float
    unit: str
    sample_size: int
    p_value: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    
    @property
    def deviation_percentage(self) -> float:
        """Calculate percentage deviation from expected value."""
        if self.expected_value == 0:
            return 0.0
        return ((self.measured_value - self.expected_value) / self.expected_value) * 100
    
    @property
    def is_significant_deviation(self) -> bool:
        """Check if deviation is statistically significant."""
        return self.p_value is not None and self.p_value < 0.05
    
    @property
    def recommendation_strength(self) -> RecommendationStrength:
        """Determine strength of recommendation based on statistical evidence."""
        if self.sample_size < 5:
            return RecommendationStrength.INSUFFICIENT
        elif self.sample_size >= 20 and self.p_value and self.p_value < 0.05:
            return RecommendationStrength.STRONG
        elif self.sample_size >= 10 and self.p_value and self.p_value < 0.10:
            return RecommendationStrength.MODERATE
        elif self.sample_size >= 5 and self.p_value and self.p_value < 0.20:
            return RecommendationStrength.WEAK
        else:
            return RecommendationStrength.INSUFFICIENT


@dataclass
class ObjectiveRecommendation:
    """An evidence-based recommendation backed by statistical analysis."""
    metric: PerformanceMetric
    recommendation_text: str
    evidence_summary: str
    strength: RecommendationStrength
    alternative_frameworks: List[str] = None
    
    def __post_init__(self):
        if self.alternative_frameworks is None:
            self.alternative_frameworks = []


class ObjectiveFrameworkAnalyzer:
    """Provides objective, data-driven framework analysis without bias."""
    
    def __init__(self):
        self.framework_baselines = FRAMEWORK_EXPECTED_PERFORMANCE
    
    def analyze_framework_performance(
        self, 
        framework: str, 
        measured_data: List[Dict[str, Any]]
    ) -> List[ObjectiveRecommendation]:
        """
        Analyze framework performance objectively using statistical methods.
        
        Args:
            framework: Framework being analyzed
            measured_data: List of actual performance measurements
            
        Returns:
            List of evidence-based recommendations with statistical backing
        """
        if not measured_data:
            return [self._insufficient_data_recommendation(framework)]
        
        recommendations = []
        
        # Analyze response time if available
        response_times = self._extract_metric_values(measured_data, "response_time")
        if response_times:
            metric = self._analyze_response_time(framework, response_times)
            if metric:
                rec = self._generate_response_time_recommendation(metric, framework)
                recommendations.append(rec)
        
        # Analyze success rate if available
        success_rates = self._extract_metric_values(measured_data, "success_rate")
        if success_rates:
            metric = self._analyze_success_rate(framework, success_rates)
            if metric:
                rec = self._generate_success_rate_recommendation(metric, framework)
                recommendations.append(rec)
        
        # Analyze error rate if available
        error_rates = self._extract_metric_values(measured_data, "error_rate")
        if error_rates:
            metric = self._analyze_error_rate(framework, error_rates)
            if metric:
                rec = self._generate_error_rate_recommendation(metric, framework)
                recommendations.append(rec)
        
        # Filter out insufficient data recommendations if we have better ones
        strong_recommendations = [r for r in recommendations if r.strength != RecommendationStrength.INSUFFICIENT]
        if strong_recommendations:
            return strong_recommendations
        
        return recommendations
    
    def _extract_metric_values(self, data: List[Dict], metric_name: str) -> List[float]:
        """Extract numeric values for a specific metric from measured data."""
        values = []
        for item in data:
            if isinstance(item, dict):
                # Try different possible keys for the metric
                possible_keys = [
                    metric_name,
                    f"avg_{metric_name}",
                    f"mean_{metric_name}",
                    metric_name.replace("_", ""),
                    metric_name.replace("_", "-")
                ]
                
                for key in possible_keys:
                    if key in item and isinstance(item[key], (int, float)):
                        values.append(float(item[key]))
                        break
                
                # Special handling for nested performance metrics
                if "performance_metrics" in item and isinstance(item["performance_metrics"], dict):
                    perf_metrics = item["performance_metrics"]
                    for key in possible_keys:
                        if key in perf_metrics and isinstance(perf_metrics[key], (int, float)):
                            values.append(float(perf_metrics[key]))
                            break
        
        return values
    
    def _analyze_response_time(self, framework: str, response_times: List[float]) -> Optional[PerformanceMetric]:
        """Analyze response time performance with statistical testing."""
        if len(response_times) < 3:
            return None
        
        measured_avg = statistics.mean(response_times)
        expected_baseline = self.framework_baselines.get(framework, {}).get("avg_response_time", 5.0)
        
        # Calculate statistical significance using t-test approximation
        p_value = self._calculate_t_test_p_value(response_times, expected_baseline)
        
        # Calculate confidence interval (simplified)
        confidence_interval = self._calculate_confidence_interval(response_times)
        
        return PerformanceMetric(
            name="response_time",
            measured_value=measured_avg,
            expected_value=expected_baseline,
            unit="seconds",
            sample_size=len(response_times),
            p_value=p_value,
            confidence_interval=confidence_interval
        )
    
    def _analyze_success_rate(self, framework: str, success_rates: List[float]) -> Optional[PerformanceMetric]:
        """Analyze success rate performance with statistical testing."""
        if len(success_rates) < 3:
            return None
        
        measured_avg = statistics.mean(success_rates)
        expected_baseline = self.framework_baselines.get(framework, {}).get("reliability_score", 0.80)
        
        p_value = self._calculate_t_test_p_value(success_rates, expected_baseline)
        confidence_interval = self._calculate_confidence_interval(success_rates)
        
        return PerformanceMetric(
            name="success_rate",
            measured_value=measured_avg,
            expected_value=expected_baseline,
            unit="ratio",
            sample_size=len(success_rates),
            p_value=p_value,
            confidence_interval=confidence_interval
        )
    
    def _analyze_error_rate(self, framework: str, error_rates: List[float]) -> Optional[PerformanceMetric]:
        """Analyze error rate performance with statistical testing."""
        if len(error_rates) < 3:
            return None
        
        measured_avg = statistics.mean(error_rates)
        # Error rate baseline is inverse of reliability score
        reliability_baseline = self.framework_baselines.get(framework, {}).get("reliability_score", 0.80)
        expected_baseline = 1.0 - reliability_baseline  # Convert to error rate
        
        p_value = self._calculate_t_test_p_value(error_rates, expected_baseline)
        confidence_interval = self._calculate_confidence_interval(error_rates)
        
        return PerformanceMetric(
            name="error_rate",
            measured_value=measured_avg,
            expected_value=expected_baseline,
            unit="ratio",
            sample_size=len(error_rates),
            p_value=p_value,
            confidence_interval=confidence_interval
        )
    
    def _calculate_t_test_p_value(self, values: List[float], expected_mean: float) -> float:
        """Calculate approximate p-value for one-sample t-test."""
        if len(values) < 2:
            return 1.0
        
        try:
            sample_mean = statistics.mean(values)
            sample_std = statistics.stdev(values)
            n = len(values)
            
            # t-statistic calculation
            if sample_std == 0:
                return 0.0 if sample_mean == expected_mean else 0.001
            
            t_stat = abs((sample_mean - expected_mean) / (sample_std / (n ** 0.5)))
            
            # Simplified p-value approximation based on t-statistic
            # This is a rough approximation - for production use, consider scipy.stats
            if t_stat > 3.0:
                return 0.001  # Very significant
            elif t_stat > 2.0:
                return 0.05   # Significant
            elif t_stat > 1.5:
                return 0.15   # Marginally significant
            else:
                return 0.30   # Not significant
                
        except (statistics.StatisticsError, ZeroDivisionError):
            return 1.0
    
    def _calculate_confidence_interval(self, values: List[float]) -> Tuple[float, float]:
        """Calculate 95% confidence interval for the mean."""
        if len(values) < 2:
            mean_val = values[0] if values else 0.0
            return (mean_val, mean_val)
        
        try:
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            n = len(values)
            
            # 95% CI approximation (t ≈ 2 for moderate sample sizes)
            margin_of_error = 2 * (std_val / (n ** 0.5))
            
            return (mean_val - margin_of_error, mean_val + margin_of_error)
        except statistics.StatisticsError:
            mean_val = statistics.mean(values)
            return (mean_val, mean_val)
    
    def _generate_response_time_recommendation(
        self, 
        metric: PerformanceMetric, 
        framework: str
    ) -> ObjectiveRecommendation:
        """Generate objective recommendation for response time performance."""
        
        deviation = metric.deviation_percentage
        strength = metric.recommendation_strength
        
        if strength == RecommendationStrength.INSUFFICIENT:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Insufficient data for response time analysis (n={metric.sample_size})",
                evidence_summary=f"Need minimum 5 samples for statistical analysis",
                strength=strength
            )
        
        if not metric.is_significant_deviation:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text="Response time performance within expected range",
                evidence_summary=f"Measured {metric.measured_value:.1f}s vs expected {metric.expected_value:.1f}s (p={metric.p_value:.3f}, not significant)",
                strength=strength
            )
        
        if deviation > 50:  # Significantly slower
            alternatives = self._find_faster_alternatives(framework, "avg_response_time")
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Response time {deviation:+.1f}% above baseline - consider optimization",
                evidence_summary=f"Measured {metric.measured_value:.1f}s vs expected {metric.expected_value:.1f}s (p={metric.p_value:.3f}, n={metric.sample_size})",
                strength=strength,
                alternative_frameworks=alternatives
            )
        
        return ObjectiveRecommendation(
            metric=metric,
            recommendation_text=f"Response time {deviation:+.1f}% from baseline",
            evidence_summary=f"Measured {metric.measured_value:.1f}s vs expected {metric.expected_value:.1f}s (p={metric.p_value:.3f}, n={metric.sample_size})",
            strength=strength
        )
    
    def _generate_success_rate_recommendation(
        self, 
        metric: PerformanceMetric, 
        framework: str
    ) -> ObjectiveRecommendation:
        """Generate objective recommendation for success rate performance."""
        
        deviation = metric.deviation_percentage
        strength = metric.recommendation_strength
        
        if strength == RecommendationStrength.INSUFFICIENT:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Insufficient data for success rate analysis (n={metric.sample_size})",
                evidence_summary=f"Need minimum 5 samples for statistical analysis",
                strength=strength
            )
        
        if not metric.is_significant_deviation:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text="Success rate performance within expected range",
                evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, not significant)",
                strength=strength
            )
        
        if deviation < -10:  # Significantly lower success rate
            alternatives = self._find_more_reliable_alternatives(framework)
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Success rate {deviation:+.1f}% below baseline - reliability issues detected",
                evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, n={metric.sample_size})",
                strength=strength,
                alternative_frameworks=alternatives
            )
        
        return ObjectiveRecommendation(
            metric=metric,
            recommendation_text=f"Success rate {deviation:+.1f}% from baseline",
            evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, n={metric.sample_size})",
            strength=strength
        )
    
    def _generate_error_rate_recommendation(
        self, 
        metric: PerformanceMetric, 
        framework: str
    ) -> ObjectiveRecommendation:
        """Generate objective recommendation for error rate performance."""
        
        deviation = metric.deviation_percentage
        strength = metric.recommendation_strength
        
        if strength == RecommendationStrength.INSUFFICIENT:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Insufficient data for error rate analysis (n={metric.sample_size})",
                evidence_summary=f"Need minimum 5 samples for statistical analysis",
                strength=strength
            )
        
        if not metric.is_significant_deviation:
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text="Error rate within expected range",
                evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, not significant)",
                strength=strength
            )
        
        if deviation > 50:  # Significantly higher error rate
            alternatives = self._find_more_reliable_alternatives(framework)
            return ObjectiveRecommendation(
                metric=metric,
                recommendation_text=f"Error rate {deviation:+.1f}% above baseline - reliability optimization needed",
                evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, n={metric.sample_size})",
                strength=strength,
                alternative_frameworks=alternatives
            )
        
        return ObjectiveRecommendation(
            metric=metric,
            recommendation_text=f"Error rate {deviation:+.1f}% from baseline",
            evidence_summary=f"Measured {metric.measured_value:.1%} vs expected {metric.expected_value:.1%} (p={metric.p_value:.3f}, n={metric.sample_size})",
            strength=strength
        )
    
    def _find_faster_alternatives(self, current_framework: str, metric_key: str) -> List[str]:
        """Find frameworks with objectively better performance for a given metric."""
        current_performance = self.framework_baselines.get(current_framework, {}).get(metric_key, float('inf'))
        
        alternatives = []
        for framework, baseline in self.framework_baselines.items():
            if framework != current_framework:
                framework_performance = baseline.get(metric_key, float('inf'))
                # Only suggest if meaningfully better (>20% improvement)
                if framework_performance < current_performance * 0.8:
                    alternatives.append(framework)
        
        # Sort by performance (best first)
        alternatives.sort(key=lambda f: self.framework_baselines[f].get(metric_key, float('inf')))
        return alternatives[:2]  # Return top 2 alternatives
    
    def _find_more_reliable_alternatives(self, current_framework: str) -> List[str]:
        """Find frameworks with objectively better reliability."""
        current_reliability = self.framework_baselines.get(current_framework, {}).get("reliability_score", 0.0)
        
        alternatives = []
        for framework, baseline in self.framework_baselines.items():
            if framework != current_framework:
                framework_reliability = baseline.get("reliability_score", 0.0)
                # Only suggest if meaningfully better (>10% improvement)
                if framework_reliability > current_reliability * 1.1:
                    alternatives.append(framework)
        
        # Sort by reliability (best first)
        alternatives.sort(key=lambda f: self.framework_baselines[f].get("reliability_score", 0.0), reverse=True)
        return alternatives[:2]  # Return top 2 alternatives
    
    def _insufficient_data_recommendation(self, framework: str) -> ObjectiveRecommendation:
        """Generate recommendation when insufficient data is available."""
        return ObjectiveRecommendation(
            metric=PerformanceMetric(
                name="insufficient_data",
                measured_value=0.0,
                expected_value=0.0,
                unit="N/A",
                sample_size=0
            ),
            recommendation_text="Insufficient performance data for objective analysis",
            evidence_summary="Need performance metrics (response_time, success_rate, error_rate) for statistical analysis",
            strength=RecommendationStrength.INSUFFICIENT
        )
    
    def generate_objective_summary(self, recommendations: List[ObjectiveRecommendation]) -> Dict[str, Any]:
        """Generate an objective summary of all recommendations with full transparency."""
        if not recommendations:
            return {
                "total_recommendations": 0,
                "statistical_strength": "insufficient",
                "key_findings": ["No performance data available for analysis"],
                "methodology": "Evidence-based analysis requires performance metrics",
                "data_limitations": ["No performance measurements provided"],
                "transparency_note": "Objective evaluation requires measurable performance data"
            }
        
        strength_counts = {}
        total_sample_size = 0
        significant_findings = 0
        
        for rec in recommendations:
            strength_counts[rec.strength.value] = strength_counts.get(rec.strength.value, 0) + 1
            total_sample_size += rec.metric.sample_size
            if rec.metric.is_significant_deviation:
                significant_findings += 1
        
        # Determine overall statistical strength
        if strength_counts.get("strong", 0) > 0:
            overall_strength = "strong"
        elif strength_counts.get("moderate", 0) > 0:
            overall_strength = "moderate"
        elif strength_counts.get("weak", 0) > 0:
            overall_strength = "weak"
        else:
            overall_strength = "insufficient"
        
        key_findings = []
        data_limitations = []
        
        for rec in recommendations:
            if rec.strength != RecommendationStrength.INSUFFICIENT:
                key_findings.append(f"{rec.metric.name}: {rec.recommendation_text}")
                
                # Document data limitations
                if rec.metric.sample_size < 10:
                    data_limitations.append(f"{rec.metric.name}: Small sample size (n={rec.metric.sample_size}, recommend n≥10)")
                if rec.metric.p_value and rec.metric.p_value > 0.05:
                    data_limitations.append(f"{rec.metric.name}: Not statistically significant (p={rec.metric.p_value:.3f})")
        
        if not key_findings:
            key_findings = ["Insufficient data for statistically significant findings"]
        
        if not data_limitations:
            data_limitations = ["Sufficient data quality for reliable analysis"]
        
        # Calculate confidence rating
        confidence_rating = self._calculate_overall_confidence(recommendations)
        
        return {
            "total_recommendations": len(recommendations),
            "statistical_strength": overall_strength,
            "strength_breakdown": strength_counts,
            "key_findings": key_findings,
            "methodology": "Statistical analysis with p-values, confidence intervals, and baseline comparisons",
            "data_transparency": {
                "total_measurements": total_sample_size,
                "statistically_significant_findings": significant_findings,
                "confidence_rating": confidence_rating,
                "minimum_sample_recommendation": "n≥20 for strong statistical confidence"
            },
            "data_limitations": data_limitations,
            "objectivity_statement": "All recommendations based solely on measured data vs established baselines. No subjective opinions included."
        }
    
    def _calculate_overall_confidence(self, recommendations: List[ObjectiveRecommendation]) -> str:
        """Calculate overall confidence rating based on data quality."""
        if not recommendations:
            return "none"
        
        total_sample_size = sum(rec.metric.sample_size for rec in recommendations)
        strong_count = sum(1 for rec in recommendations if rec.strength == RecommendationStrength.STRONG)
        moderate_count = sum(1 for rec in recommendations if rec.strength == RecommendationStrength.MODERATE)
        
        if total_sample_size >= 50 and strong_count >= 2:
            return "high"
        elif total_sample_size >= 20 and (strong_count >= 1 or moderate_count >= 2):
            return "moderate"
        elif total_sample_size >= 10:
            return "low"
        else:
            return "insufficient"
    
    def generate_transparency_report(self, framework: str, recommendations: List[ObjectiveRecommendation]) -> str:
        """Generate a detailed transparency report about the analysis methodology."""
        
        report_lines = [
            "═══ OBJECTIVITY & TRANSPARENCY REPORT ═══",
            "",
            "🔬 METHODOLOGY:",
            "• Statistical comparison against established framework baselines",
            "• P-value testing for statistical significance (α = 0.05)",
            "• 95% confidence intervals for performance metrics",
            "• No subjective opinions or framework favoritism",
            "",
            "📊 DATA SUMMARY:"
        ]
        
        total_measurements = sum(rec.metric.sample_size for rec in recommendations)
        report_lines.append(f"• Total measurements analyzed: {total_measurements}")
        report_lines.append(f"• Framework baseline source: Research-validated performance data")
        
        if recommendations:
            significant_count = sum(1 for rec in recommendations if rec.metric.is_significant_deviation)
            report_lines.append(f"• Statistically significant deviations found: {significant_count}")
            
            for rec in recommendations:
                if rec.metric.sample_size > 0:
                    report_lines.append(f"• {rec.metric.name}: n={rec.metric.sample_size}, p={rec.metric.p_value:.3f}")
        
        report_lines.extend([
            "",
            "⚖️ OBJECTIVITY STANDARDS:",
            "• Recommendations only when p < 0.20 (statistical evidence exists)",
            "• Framework alternatives suggested only when objectively superior",
            "• All claims backed by measurable performance data",
            "• Transparent about sample sizes and statistical limitations",
            "",
            "🎯 RECOMMENDATION RELIABILITY:",
            "• STRONG: p < 0.05, n ≥ 20 (highest confidence)",
            "• MODERATE: p < 0.10, n ≥ 10 (reasonable confidence)",
            "• WEAK: p < 0.20, n ≥ 5 (limited confidence)",
            "• INSUFFICIENT: n < 5 (not statistically reliable)",
            "",
            "📈 FOR BETTER ANALYSIS:",
            "• Collect performance metrics: response_time, success_rate, error_rate",
            "• Minimum 20 samples recommended for strong statistical confidence",
            "• Include confidence intervals and p-values in your data collection",
            "",
            "═══════════════════════════════════════════"
        ])
        
        return "\n".join(report_lines)
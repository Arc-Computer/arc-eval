"""Judge Comparison Mode for A/B testing different judge configurations."""

import time
import statistics
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent_eval.core.types import AgentOutput, EvaluationScenario
from agent_eval.evaluation.judges import AgentJudge, JudgmentResult
import logging

logger = logging.getLogger(__name__)


@dataclass
class JudgeConfig:
    """Configuration for a judge to compare."""
    name: str
    domain: str
    enable_confidence_calibration: bool = False
    enable_verification: bool = False
    description: str = ""


@dataclass
class BiasAnalysis:
    """Analysis of bias patterns in judge decisions."""
    length_bias_correlation: float
    position_bias_detected: bool
    style_preference: Optional[str]
    consistency_score: float
    

@dataclass
class ComparisonMetrics:
    """Metrics for comparing judge performance."""
    agreement_score: float  # How much judges agree with each other
    confidence_correlation: float  # How well confidence correlates with agreement
    avg_evaluation_time: float
    total_cost_estimate: float
    consistency_score: float  # How consistent each judge is with itself


@dataclass
class ComparisonReport:
    """Comprehensive report comparing multiple judges."""
    judge_agreements: Dict[str, float]  # Judge name -> agreement with others
    performance_metrics: Dict[str, ComparisonMetrics]
    bias_analysis: Dict[str, BiasAnalysis]
    recommendations: List[str]
    best_judge_config: str
    execution_time: float


class JudgeComparison:
    """A/B test different judge configurations for optimization."""
    
    def __init__(self, config_file: Optional[str] = None, default_domain: Optional[str] = None):
        self.judges: Dict[str, AgentJudge] = {}
        self.config_file = config_file
        self.default_domain = default_domain
        self.config_data = self._load_config() if config_file else None
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load judge comparison configuration from YAML file."""
        if not self.config_file:
            return None
        
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                logger.error(f"Config file not found: {self.config_file}")
                return None
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            logger.info(f"Loaded judge comparison config from {self.config_file}")
            return config_data
        except Exception as e:
            logger.error(f"Failed to load config file {self.config_file}: {e}")
            return None
    
    def run_comparison(self, agent_outputs: List[AgentOutput]) -> None:
        """Run judge comparison using loaded configuration and agent outputs."""
        if not self.config_data:
            logger.error("No configuration loaded for judge comparison")
            return
        
        # Use default comparison if no specific comparison specified
        comparison_key = "default_comparison"
        if comparison_key not in self.config_data:
            logger.error(f"Default comparison '{comparison_key}' not found in config")
            return
        
        comparison_config = self.config_data[comparison_key]
        judge_configs = []
        
        # Load judge configurations from YAML
        for judge_data in comparison_config.get("judges", []):
            judge_config = JudgeConfig(
                name=judge_data.get("name", "unnamed"),
                domain=judge_data.get("domain", self.default_domain or "security"),
                enable_confidence_calibration=judge_data.get("enable_confidence_calibration", False),
                enable_verification=judge_data.get("enable_verification", False),
                description=judge_data.get("description", "")
            )
            judge_configs.append(judge_config)
        
        if not judge_configs:
            logger.error("No valid judge configurations found in config file")
            return
        
        # Create dummy scenarios for comparison (simplified for demo)
        scenarios = []
        for i, _ in enumerate(agent_outputs):
            scenario = EvaluationScenario(
                id=f"scenario_{i}",
                name=f"Judge Comparison Scenario {i}",
                description=f"Evaluation scenario {i} for judge comparison testing",
                severity="medium",
                test_type="positive",
                category="general",
                input_template="Agent output for evaluation",
                expected_behavior="valid_output",
                remediation="Address any identified issues in agent output",
                failure_indicators=["invalid", "error"]
            )
            scenarios.append(scenario)
        
        # Run comparison
        logger.info(f"Running comparison with {len(judge_configs)} judges on {len(agent_outputs)} outputs")
        report = self.compare_judges(judge_configs, scenarios, agent_outputs)
        
        # Display results
        self._display_comparison_results(report)
    
    def _display_comparison_results(self, report: ComparisonReport) -> None:
        """Display comparison results in a formatted way."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Judge Agreement Table
        table = Table(title="Judge Comparison Results")
        table.add_column("Judge", style="cyan")
        table.add_column("Agreement Score", style="green")
        table.add_column("Avg Time (s)", style="yellow")
        table.add_column("Consistency", style="blue")
        
        for judge_name, agreement in report.judge_agreements.items():
            metrics = report.performance_metrics.get(judge_name)
            if metrics:
                table.add_row(
                    judge_name,
                    f"{agreement:.2f}",
                    f"{metrics.avg_evaluation_time:.1f}",
                    f"{metrics.consistency_score:.2f}"
                )
        
        console.print(table)
        
        # Recommendations Panel
        recommendations_text = "\n".join([f"• {rec}" for rec in report.recommendations])
        recommendations_panel = Panel(
            recommendations_text,
            title="📊 Recommendations",
            border_style="blue"
        )
        console.print(recommendations_panel)
        
        # Best Judge
        console.print(f"\n[bold green]🏆 Best Judge Configuration:[/bold green] {report.best_judge_config}")
        console.print(f"[dim]Execution Time: {report.execution_time:.1f}s[/dim]")
        
    def add_judge_config(self, config: JudgeConfig) -> None:
        """Add a judge configuration to compare."""
        try:
            # Use Claude 4 Sonnet as primary for all judge comparisons
            judge = AgentJudge(
                domain=config.domain,
                enable_confidence_calibration=config.enable_confidence_calibration,
                preferred_model="claude-sonnet-4-20250514"  # Ensure consistent model for fair comparison
            )
            self.judges[config.name] = judge
            logger.info(f"Added judge config: {config.name}")
        except Exception as e:
            logger.error(f"Failed to create judge {config.name}: {e}")
            raise
    
    def compare_judges(
        self, 
        judge_configs: List[JudgeConfig], 
        scenarios: List[EvaluationScenario],
        agent_outputs: List[AgentOutput],
        max_workers: int = 3
    ) -> ComparisonReport:
        """Run same scenarios through different judge setups and compare results."""
        start_time = time.time()
        
        # Initialize judges
        for config in judge_configs:
            self.add_judge_config(config)
        
        # Run evaluations for each judge
        all_results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_judge = {}
            
            for config in judge_configs:
                judge_name = config.name
                if judge_name in self.judges:
                    future = executor.submit(
                        self._evaluate_with_judge,
                        self.judges[judge_name],
                        agent_outputs,
                        scenarios
                    )
                    future_to_judge[future] = judge_name
            
            # Collect results
            for future in as_completed(future_to_judge):
                judge_name = future_to_judge[future]
                try:
                    results = future.result()
                    all_results[judge_name] = results
                    logger.info(f"Completed evaluation for judge: {judge_name}")
                except Exception as e:
                    logger.error(f"Judge {judge_name} evaluation failed: {e}")
                    continue
        
        # Generate comparison analysis
        return self._generate_comparison_report(
            all_results, 
            judge_configs,
            time.time() - start_time,
            agent_outputs
        )
    
    def _evaluate_with_judge(
        self,
        judge: AgentJudge,
        agent_outputs: List[AgentOutput],
        scenarios: List[EvaluationScenario]
    ) -> List[JudgmentResult]:
        """Evaluate scenarios with a specific judge."""
        results = []
        for output, scenario in zip(agent_outputs, scenarios):
            try:
                result = judge.evaluate_scenario(output, scenario)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed evaluation for scenario {scenario.id}: {e}")
                continue
        return results
    
    def measure_agreement(self, results: Dict[str, List[JudgmentResult]]) -> Dict[str, float]:
        """Measure inter-judge agreement for each judge against others."""
        judge_names = list(results.keys())
        agreements = {}
        
        for judge_name in judge_names:
            if judge_name not in results or not results[judge_name]:
                agreements[judge_name] = 0.0
                continue
                
            total_agreements = 0
            total_comparisons = 0
            
            for other_judge in judge_names:
                if other_judge != judge_name and other_judge in results:
                    judge_results = results[judge_name]
                    other_results = results[other_judge]
                    
                    # Compare judgments for matching scenarios
                    for j_result, o_result in zip(judge_results, other_results):
                        if j_result.scenario_id == o_result.scenario_id:
                            if j_result.judgment == o_result.judgment:
                                total_agreements += 1
                            total_comparisons += 1
            
            if total_comparisons > 0:
                agreements[judge_name] = total_agreements / total_comparisons
            else:
                agreements[judge_name] = 0.0
        
        return agreements
    
    def analyze_bias_patterns(
        self, 
        results: Dict[str, List[JudgmentResult]],
        agent_outputs: List[AgentOutput]
    ) -> Dict[str, BiasAnalysis]:
        """Analyze bias patterns across different judges."""
        bias_analysis = {}
        
        for judge_name, judge_results in results.items():
            if not judge_results:
                bias_analysis[judge_name] = BiasAnalysis(
                    length_bias_correlation=0.0,
                    position_bias_detected=False,
                    style_preference=None,
                    consistency_score=0.0
                )
                continue
            
            # Length bias analysis
            output_lengths = [len(output.normalized_output) for output in agent_outputs]
            confidences = [r.confidence for r in judge_results]
            
            length_bias_correlation = 0.0
            if len(output_lengths) > 1 and len(confidences) > 1:
                try:
                    # Simple correlation approximation
                    mean_length = statistics.mean(output_lengths)
                    mean_confidence = statistics.mean(confidences)
                    
                    numerator = sum((l - mean_length) * (c - mean_confidence) 
                                  for l, c in zip(output_lengths, confidences))
                    length_variance = sum((l - mean_length) ** 2 for l in output_lengths)
                    confidence_variance = sum((c - mean_confidence) ** 2 for c in confidences)
                    
                    if length_variance > 0 and confidence_variance > 0:
                        length_bias_correlation = abs(numerator / (length_variance * confidence_variance) ** 0.5)
                except Exception:
                    length_bias_correlation = 0.0
            
            # Position bias detection (simplified)
            position_bias_detected = False
            if len(judge_results) >= 3:
                first_third_avg = statistics.mean([r.confidence for r in judge_results[:len(judge_results)//3]])
                last_third_avg = statistics.mean([r.confidence for r in judge_results[-len(judge_results)//3:]])
                position_bias_detected = abs(first_third_avg - last_third_avg) > 0.1
            
            # Consistency score
            consistency_score = 0.0
            if confidences:
                consistency_score = 1.0 - (statistics.stdev(confidences) if len(confidences) > 1 else 0.0)
                consistency_score = max(0.0, min(1.0, consistency_score))
            
            bias_analysis[judge_name] = BiasAnalysis(
                length_bias_correlation=length_bias_correlation,
                position_bias_detected=position_bias_detected,
                style_preference=None,  # Could be extended
                consistency_score=consistency_score
            )
        
        return bias_analysis
    
    def _calculate_performance_metrics(
        self, 
        results: Dict[str, List[JudgmentResult]],
        agreements: Dict[str, float]
    ) -> Dict[str, ComparisonMetrics]:
        """Calculate performance metrics for each judge."""
        metrics = {}
        
        for judge_name, judge_results in results.items():
            if not judge_results:
                metrics[judge_name] = ComparisonMetrics(
                    agreement_score=0.0,
                    confidence_correlation=0.0,
                    avg_evaluation_time=0.0,
                    total_cost_estimate=0.0,
                    consistency_score=0.0
                )
                continue
            
            # Basic metrics
            agreement_score = agreements.get(judge_name, 0.0)
            avg_evaluation_time = statistics.mean([r.evaluation_time for r in judge_results])
            
            # Confidence correlation with agreement (simplified)
            confidences = [r.confidence for r in judge_results]
            confidence_correlation = agreement_score  # Simplified - could be more sophisticated
            
            # Cost estimation (simplified based on evaluation time)
            total_cost_estimate = len(judge_results) * 0.001  # Rough estimate
            
            # Consistency score
            consistency_score = 1.0 - (statistics.stdev(confidences) if len(confidences) > 1 else 0.0)
            consistency_score = max(0.0, min(1.0, consistency_score))
            
            metrics[judge_name] = ComparisonMetrics(
                agreement_score=agreement_score,
                confidence_correlation=confidence_correlation,
                avg_evaluation_time=avg_evaluation_time,
                total_cost_estimate=total_cost_estimate,
                consistency_score=consistency_score
            )
        
        return metrics
    
    def _generate_recommendations(
        self,
        performance_metrics: Dict[str, ComparisonMetrics],
        bias_analysis: Dict[str, BiasAnalysis]
    ) -> List[str]:
        """Generate actionable recommendations for judge optimization."""
        recommendations = []
        
        if not performance_metrics:
            return ["No valid judge results available for analysis"]
        
        # Find best performing judge
        best_judge = max(performance_metrics.keys(), 
                        key=lambda j: performance_metrics[j].agreement_score)
        best_score = performance_metrics[best_judge].agreement_score
        
        recommendations.append(f"Best performing judge: {best_judge} (agreement: {best_score:.2f})")
        
        # Identify issues
        for judge_name, metrics in performance_metrics.items():
            if metrics.agreement_score < 0.7:
                recommendations.append(f"Consider recalibrating {judge_name} - low agreement ({metrics.agreement_score:.2f})")
            
            if metrics.avg_evaluation_time > 5.0:
                recommendations.append(f"Optimize {judge_name} for speed - avg time {metrics.avg_evaluation_time:.1f}s")
            
            bias = bias_analysis.get(judge_name)
            if bias and bias.length_bias_correlation > 0.3:
                recommendations.append(f"Address length bias in {judge_name} (correlation: {bias.length_bias_correlation:.2f})")
            
            if bias and bias.position_bias_detected:
                recommendations.append(f"Address position bias detected in {judge_name}")
        
        return recommendations
    
    def _generate_comparison_report(
        self,
        all_results: Dict[str, List[JudgmentResult]],
        judge_configs: List[JudgeConfig],
        execution_time: float,
        agent_outputs: Optional[List[AgentOutput]] = None
    ) -> ComparisonReport:
        """Generate comprehensive comparison report."""
        
        # Calculate agreements
        judge_agreements = self.measure_agreement(all_results)
        
        # Perform bias analysis using real agent outputs if available
        if agent_outputs:
            bias_analysis = self.analyze_bias_patterns(all_results, agent_outputs)
        else:
            # Fallback to empty analysis if no outputs provided
            bias_analysis = {judge_name: BiasAnalysis(
                length_bias_correlation=0.0,
                position_bias_detected=False,
                style_preference=None,
                consistency_score=0.0
            ) for judge_name in all_results.keys()}
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(all_results, judge_agreements)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(performance_metrics, bias_analysis)
        
        # Determine best judge
        best_judge_config = "unknown"
        if judge_agreements:
            best_judge_config = max(judge_agreements.keys(), key=lambda j: judge_agreements[j])
        
        return ComparisonReport(
            judge_agreements=judge_agreements,
            performance_metrics=performance_metrics,
            bias_analysis=bias_analysis,
            recommendations=recommendations,
            best_judge_config=best_judge_config,
            execution_time=execution_time
        )
    
    def generate_comparison_report(
        self, 
        results: Dict[str, List[JudgmentResult]]
    ) -> ComparisonReport:
        """Generate comparison report from existing results."""
        return self._generate_comparison_report(results, [], 0.0, None)
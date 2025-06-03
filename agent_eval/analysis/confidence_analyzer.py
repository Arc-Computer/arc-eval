"""
Confidence calibration analyzer for post-launch tuning.
Analyzes collected confidence data to optimize QA routing thresholds.
"""

import json
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class ConfidenceAnalyzer:
    """Analyzes confidence calibration data to optimize thresholds."""

    def __init__(self):
        """Initialize analyzer with centralized configuration."""
        from agent_eval.core.config import load_config
        self.config = load_config()
    
    def analyze_calibration_data(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze confidence calibration from evaluation results."""
        
        calibration_data = []
        for result in evaluation_results:
            reward_signals = result.get('reward_signals', {})
            if 'confidence_calibration' in reward_signals:
                calibration_data.append(reward_signals['confidence_calibration'])
        
        if not calibration_data:
            return {"error": "No calibration data found in results"}
        
        analysis = {
            "total_evaluations": len(calibration_data),
            "qa_routing_stats": self._analyze_qa_routing(calibration_data),
            "confidence_accuracy": self._analyze_confidence_accuracy(calibration_data),
            "threshold_optimization": self._optimize_thresholds(calibration_data),
            "cost_impact": self._analyze_cost_impact(calibration_data),
            "recommendations": self._generate_recommendations(calibration_data)
        }
        
        return analysis
    
    def _analyze_qa_routing(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze QA routing patterns."""
        total = len(data)
        qa_applied = sum(1 for d in data if d.get('qa_applied', False))
        
        # Breakdown by scenario type
        critical_qa = sum(1 for d in data if d.get('scenario_severity') == 'critical' and d.get('qa_applied'))
        failure_qa = sum(1 for d in data if d.get('cerebras_judgment') == 'fail' and d.get('qa_applied'))
        
        return {
            "qa_rate": qa_applied / total if total > 0 else 0,
            "critical_qa_rate": critical_qa / sum(1 for d in data if d.get('scenario_severity') == 'critical') if sum(1 for d in data if d.get('scenario_severity') == 'critical') > 0 else 0,
            "failure_qa_rate": failure_qa / sum(1 for d in data if d.get('cerebras_judgment') == 'fail') if sum(1 for d in data if d.get('cerebras_judgment') == 'fail') > 0 else 0,
            "total_qa_evaluations": qa_applied
        }
    
    def _analyze_confidence_accuracy(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze how well confidence predicts accuracy."""
        
        # Group by confidence ranges
        confidence_buckets = {
            "high": [],      # 0.9+
            "medium": [],    # 0.7-0.9
            "low": []        # <0.7
        }
        
        for d in data:
            conf = d.get('cerebras_confidence', 0.5)
            accuracy = 1.0 if d.get('cerebras_judgment') == d.get('final_judgment') else 0.0
            
            if conf >= 0.9:
                confidence_buckets["high"].append(accuracy)
            elif conf >= 0.7:
                confidence_buckets["medium"].append(accuracy)
            else:
                confidence_buckets["low"].append(accuracy)
        
        return {
            bucket: {
                "count": len(accuracies),
                "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
                "confidence_range": {"high": "0.9+", "medium": "0.7-0.9", "low": "<0.7"}[bucket]
            }
            for bucket, accuracies in confidence_buckets.items()
        }
    
    def _optimize_thresholds(self, data: List[Dict]) -> Dict[str, Any]:
        """Suggest optimal confidence thresholds."""
        
        # Calculate accuracy improvement from QA
        qa_improvements = []
        for d in data:
            if d.get('qa_applied'):
                cerebras_correct = d.get('cerebras_judgment') == 'pass'  # Simplified
                final_correct = d.get('final_judgment') == 'pass'
                if final_correct and not cerebras_correct:
                    qa_improvements.append(1)
                else:
                    qa_improvements.append(0)
        
        qa_improvement_rate = sum(qa_improvements) / len(qa_improvements) if qa_improvements else 0
        
        # Suggest threshold adjustments
        current_threshold = self.config.confidence.base_threshold
        
        if qa_improvement_rate > 0.2:  # High improvement rate
            suggested_threshold = min(current_threshold + 0.05, 0.95)
            recommendation = "Increase threshold - QA is very effective"
        elif qa_improvement_rate < 0.05:  # Low improvement rate
            suggested_threshold = max(current_threshold - 0.05, 0.7)
            recommendation = "Decrease threshold - QA not adding much value"
        else:
            suggested_threshold = current_threshold
            recommendation = "Current threshold appears optimal"
        
        return {
            "current_threshold": current_threshold,
            "suggested_threshold": suggested_threshold,
            "qa_improvement_rate": qa_improvement_rate,
            "recommendation": recommendation
        }
    
    def _analyze_cost_impact(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze cost impact of hybrid architecture."""
        total_evaluations = len(data)
        qa_evaluations = sum(1 for d in data if d.get('qa_applied', False))
        
        # Rough cost estimates (will be replaced with actual cost data)
        cerebras_cost_per_eval = 0.001  # $0.001 per evaluation
        gemini_cost_per_eval = 0.002    # $0.002 per evaluation
        
        baseline_cost = total_evaluations * cerebras_cost_per_eval
        hybrid_cost = baseline_cost + (qa_evaluations * gemini_cost_per_eval)
        cost_multiplier = hybrid_cost / baseline_cost if baseline_cost > 0 else 1.0
        
        return {
            "baseline_cost": baseline_cost,
            "hybrid_cost": hybrid_cost,
            "cost_multiplier": cost_multiplier,
            "qa_cost_percentage": (qa_evaluations * gemini_cost_per_eval) / hybrid_cost if hybrid_cost > 0 else 0
        }
    
    def _generate_recommendations(self, data: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        qa_rate = sum(1 for d in data if d.get('qa_applied', False)) / len(data)
        
        if qa_rate > 0.5:
            recommendations.append("QA rate is high (>50%) - consider raising confidence thresholds")
        elif qa_rate < 0.2:
            recommendations.append("QA rate is low (<20%) - consider lowering confidence thresholds")
        
        # Check for confidence-accuracy correlation
        high_conf_data = [d for d in data if d.get('cerebras_confidence', 0) > 0.9]
        if high_conf_data:
            high_conf_accuracy = sum(1 for d in high_conf_data 
                                   if d.get('cerebras_judgment') == d.get('final_judgment')) / len(high_conf_data)
            if high_conf_accuracy < 0.8:
                recommendations.append("High confidence predictions are often wrong - confidence calibration needed")
        
        return recommendations
    

    
    def export_analysis_report(self, analysis: Dict[str, Any], output_path: str = "confidence_analysis_report.json"):
        """Export analysis report for review."""
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Confidence analysis report exported to {output_path}")

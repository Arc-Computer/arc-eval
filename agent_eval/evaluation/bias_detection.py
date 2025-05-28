"""Basic Bias Detection Metrics for Judge Transparency and Quality Assurance."""

import statistics
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from agent_eval.evaluation.judges import JudgmentResult
from agent_eval.core.types import BiasMetrics
import logging

logger = logging.getLogger(__name__)


@dataclass
class BiasScore:
    """Quantified bias score with context."""
    score: float  # 0.0 to 1.0, where 1.0 = high bias detected
    confidence: float  # Confidence in the bias detection
    description: str
    severity: str  # "low", "medium", "high"
    



class BasicBiasDetection:
    """Track common bias patterns in judge decisions for transparency."""
    
    def __init__(self):
        self.bias_history: List[BiasMetrics] = []
        
    def detect_length_bias(
        self, 
        judgments: List[JudgmentResult], 
        outputs: List[str]
    ) -> BiasScore:
        """Check if judgment quality correlates with response length."""
        if len(judgments) < 3 or len(outputs) < 3:
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Insufficient data for length bias analysis",
                severity="low"
            )
        
        try:
            # Calculate correlation between output length and confidence/judgment
            output_lengths = [len(output) for output in outputs[:len(judgments)]]
            confidences = [j.confidence for j in judgments]
            
            # Simple correlation calculation
            if len(output_lengths) != len(confidences):
                output_lengths = output_lengths[:len(confidences)]
            
            correlation = self._calculate_correlation(output_lengths, confidences)
            bias_score = abs(correlation)  # High correlation indicates potential bias
            
            # Determine severity
            if bias_score > 0.7:
                severity = "high"
                description = f"Strong correlation ({correlation:.3f}) between output length and judgment confidence"
            elif bias_score > 0.4:
                severity = "medium"
                description = f"Moderate correlation ({correlation:.3f}) between output length and judgment confidence"
            else:
                severity = "low"
                description = f"Low correlation ({correlation:.3f}) between output length and judgment confidence"
            
            confidence = min(1.0, len(judgments) / 10.0)  # More data = higher confidence
            
            return BiasScore(
                score=bias_score,
                confidence=confidence,
                description=description,
                severity=severity
            )
            
        except Exception as e:
            logger.warning(f"Length bias detection failed: {e}")
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Length bias analysis failed",
                severity="low"
            )
    
    def detect_position_bias(self, judgments: List[JudgmentResult]) -> BiasScore:
        """Check if first/last options are favored (position bias)."""
        if len(judgments) < 5:
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Insufficient data for position bias analysis",
                severity="low"
            )
        
        try:
            # Split judgments into thirds and compare confidence levels
            n = len(judgments)
            first_third = judgments[:n//3]
            middle_third = judgments[n//3:2*n//3]
            last_third = judgments[2*n//3:]
            
            if not first_third or not middle_third or not last_third:
                return BiasScore(
                    score=0.0,
                    confidence=0.0,
                    description="Insufficient data for position analysis",
                    severity="low"
                )
            
            first_avg = statistics.mean([j.confidence for j in first_third])
            middle_avg = statistics.mean([j.confidence for j in middle_third])
            last_avg = statistics.mean([j.confidence for j in last_third])
            
            # Calculate position bias as max deviation from middle
            max_deviation = max(abs(first_avg - middle_avg), abs(last_avg - middle_avg))
            bias_score = min(1.0, max_deviation * 2)  # Scale to 0-1
            
            # Determine severity
            if bias_score > 0.3:
                severity = "high"
                description = f"Significant position bias detected (deviation: {max_deviation:.3f})"
            elif bias_score > 0.15:
                severity = "medium"
                description = f"Moderate position bias detected (deviation: {max_deviation:.3f})"
            else:
                severity = "low"
                description = f"Low position bias (deviation: {max_deviation:.3f})"
            
            confidence = min(1.0, len(judgments) / 15.0)
            
            return BiasScore(
                score=bias_score,
                confidence=confidence,
                description=description,
                severity=severity
            )
            
        except Exception as e:
            logger.warning(f"Position bias detection failed: {e}")
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Position bias analysis failed",
                severity="low"
            )
    
    def detect_style_bias(
        self, 
        judgments: List[JudgmentResult], 
        outputs: List[str]
    ) -> BiasScore:
        """Check preference for formal vs informal language styles."""
        if len(judgments) < 3 or len(outputs) < 3:
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Insufficient data for style bias analysis",
                severity="low"
            )
        
        try:
            # Simple style analysis based on formality indicators
            formal_scores = []
            confidences = [j.confidence for j in judgments]
            
            for output in outputs[:len(judgments)]:
                formal_score = self._calculate_formality_score(output)
                formal_scores.append(formal_score)
            
            # Calculate correlation between formality and confidence
            correlation = self._calculate_correlation(formal_scores, confidences)
            bias_score = abs(correlation)
            
            # Determine severity
            if bias_score > 0.6:
                severity = "high"
                preference = "formal" if correlation > 0 else "informal"
                description = f"Strong {preference} style preference detected (correlation: {correlation:.3f})"
            elif bias_score > 0.3:
                severity = "medium"
                preference = "formal" if correlation > 0 else "informal"
                description = f"Moderate {preference} style preference (correlation: {correlation:.3f})"
            else:
                severity = "low"
                description = f"Low style bias detected (correlation: {correlation:.3f})"
            
            confidence = min(1.0, len(judgments) / 10.0)
            
            return BiasScore(
                score=bias_score,
                confidence=confidence,
                description=description,
                severity=severity
            )
            
        except Exception as e:
            logger.warning(f"Style bias detection failed: {e}")
            return BiasScore(
                score=0.0,
                confidence=0.0,
                description="Style bias analysis failed",
                severity="low"
            )
    
    def generate_bias_report(
        self, 
        judgments: List[JudgmentResult], 
        outputs: List[str]
    ) -> BiasMetrics:
        """Generate comprehensive bias report for transparency."""
        
        if not judgments:
            return BiasMetrics(
                length_bias_score=0.0,
                position_bias_score=0.0,
                style_bias_score=0.0,
                overall_bias_risk="low",
                recommendations=["No judgments available for bias analysis"]
            )
        
        # Detect different types of bias
        length_bias = self.detect_length_bias(judgments, outputs)
        position_bias = self.detect_position_bias(judgments)
        style_bias = self.detect_style_bias(judgments, outputs)
        
        # Create bias summary
        bias_summary = {
            "length_bias": length_bias,
            "position_bias": position_bias,
            "style_bias": style_bias
        }
        
        # Calculate overall risk
        max_bias_score = max(length_bias.score, position_bias.score, style_bias.score)
        
        if max_bias_score > 0.7:
            overall_risk = "high"
        elif max_bias_score > 0.4:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        # Generate recommendations
        recommendations = self._generate_bias_recommendations(bias_summary)
        
        bias_metrics = BiasMetrics(
            length_bias_score=length_bias.score,
            position_bias_score=position_bias.score,
            style_bias_score=style_bias.score,
            overall_bias_risk=overall_risk,
            recommendations=recommendations
        )
        
        # Store in history for trend analysis
        self.bias_history.append(bias_metrics)
        
        return bias_metrics
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            sum_y2 = sum(y[i] ** 2 for i in range(n))
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]
            
        except Exception:
            return 0.0
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calculate formality score based on linguistic indicators."""
        text_lower = text.lower()
        
        # Formal indicators
        formal_patterns = [
            r'\b(therefore|consequently|furthermore|moreover|however|nevertheless)\b',
            r'\b(utilize|implement|facilitate|demonstrate|establish)\b',
            r'\b(pursuant to|in accordance with|notwithstanding)\b',
            r'\b(shall|must|required|mandatory|compliance)\b'
        ]
        
        # Informal indicators
        informal_patterns = [
            r'\b(gonna|wanna|kinda|sorta|yeah|ok|okay)\b',
            r'\b(really|pretty|super|totally|awesome)\b',
            r'\b(stuff|things|guys|folks)\b',
            r'[!]{2,}|[?]{2,}'  # Multiple punctuation
        ]
        
        formal_count = sum(len(re.findall(pattern, text_lower)) for pattern in formal_patterns)
        informal_count = sum(len(re.findall(pattern, text_lower)) for pattern in informal_patterns)
        
        # Calculate formality score (0.0 = informal, 1.0 = formal)
        total_indicators = formal_count + informal_count
        if total_indicators == 0:
            return 0.5  # Neutral
        
        return formal_count / total_indicators
    
    def _generate_bias_recommendations(self, bias_summary: Dict[str, BiasScore]) -> List[str]:
        """Generate actionable bias mitigation recommendations."""
        recommendations = []
        
        for bias_type, bias_score in bias_summary.items():
            if bias_score.severity == "high":
                if bias_type == "length_bias":
                    recommendations.append(
                        "Implement length normalization: truncate/pad outputs to standard length before evaluation"
                    )
                elif bias_type == "position_bias":
                    recommendations.append(
                        "Randomize evaluation order: shuffle scenarios to eliminate position effects"
                    )
                elif bias_type == "style_bias":
                    recommendations.append(
                        "Add style-neutral evaluation: focus on content over linguistic style"
                    )
            elif bias_score.severity == "medium":
                if bias_type == "length_bias":
                    recommendations.append(
                        "Monitor length correlation: track relationship between output length and scores"
                    )
                elif bias_type == "position_bias":
                    recommendations.append(
                        "Consider position rotation: vary presentation order in evaluation batches"
                    )
                elif bias_type == "style_bias":
                    recommendations.append(
                        "Review style sensitivity: ensure evaluation criteria focus on substance"
                    )
        
        # General recommendations
        if not recommendations:
            recommendations.append("Bias levels are within acceptable ranges - continue monitoring")
        
        recommendations.append("Increase evaluation dataset size for more robust bias detection")
        recommendations.append("Consider multi-judge consensus to reduce individual bias effects")
        
        return recommendations[:5]  # Limit to top 5 recommendations
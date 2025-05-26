"""
Confidence Calibration with Logprobs for ARC-Eval.

Uses logprobs for better confidence estimation and uncertainty quantification.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceCalibration:
    """Confidence calibration result with uncertainty metrics."""
    calibrated_confidence: float
    raw_confidence: float
    uncertainty: float
    decision_logprobs: Dict[str, float]
    calibration_method: str
    quality_score: float


class ConfidenceCalibrator:
    """Enhanced confidence calibration using logprobs for uncertainty estimation."""
    
    def __init__(self):
        """Initialize confidence calibrator with decision token mappings."""
        # Key decision tokens for different judgment types
        self.decision_tokens = {
            "pass": ["pass", "passed", "acceptable", "compliant", "safe"],
            "fail": ["fail", "failed", "unacceptable", "violation", "unsafe"],  
            "warning": ["warning", "caution", "concern", "partial", "unclear"]
        }
        
        # Confidence threshold mappings
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def calibrate_confidence(self, response_text: str, logprobs: Optional[Dict[str, float]] = None) -> ConfidenceCalibration:
        """Calibrate confidence using logprobs and text analysis.
        
        Args:
            response_text: Response text from the model
            logprobs: Token logprobs from API response
            
        Returns:
            ConfidenceCalibration with calibrated metrics
        """
        # Extract basic confidence from text
        raw_confidence = self._extract_text_confidence(response_text)
        
        if logprobs is None:
            # Fallback to text-based calibration
            return ConfidenceCalibration(
                calibrated_confidence=raw_confidence,
                raw_confidence=raw_confidence,
                uncertainty=0.3,  # Default uncertainty when no logprobs
                decision_logprobs={},
                calibration_method="text_only",
                quality_score=0.6
            )
        
        # Extract decision token logprobs
        decision_logprobs = self.extract_decision_logprobs(logprobs)
        
        # Calculate uncertainty from logprobs
        uncertainty = self.calculate_uncertainty(decision_logprobs)
        
        # Calibrate confidence using logprobs
        calibrated_confidence = self._calibrate_with_logprobs(raw_confidence, decision_logprobs, uncertainty)
        
        # Calculate calibration quality score
        quality_score = self._calculate_quality_score(decision_logprobs, uncertainty)
        
        return ConfidenceCalibration(
            calibrated_confidence=calibrated_confidence,
            raw_confidence=raw_confidence,
            uncertainty=uncertainty,
            decision_logprobs=decision_logprobs,
            calibration_method="logprobs_enhanced",
            quality_score=quality_score
        )
    
    def extract_decision_logprobs(self, logprobs: Dict[str, float]) -> Dict[str, float]:
        """Extract logprobs for key decision tokens.
        
        Args:
            logprobs: Full token logprobs from API
            
        Returns:
            Dictionary of decision token logprobs
        """
        decision_logprobs = {}
        
        # Convert logprobs keys to lowercase for matching
        logprobs_lower = {k.lower(): v for k, v in logprobs.items()}
        
        # Extract logprobs for decision categories
        for decision, tokens in self.decision_tokens.items():
            max_logprob = float('-inf')
            best_token = None
            
            for token in tokens:
                if token in logprobs_lower:
                    if logprobs_lower[token] > max_logprob:
                        max_logprob = logprobs_lower[token]
                        best_token = token
            
            if best_token is not None:
                decision_logprobs[decision] = max_logprob
        
        return decision_logprobs
    
    def calculate_uncertainty(self, decision_logprobs: Dict[str, float]) -> float:
        """Calculate uncertainty from decision token logprobs.
        
        Args:
            decision_logprobs: Decision token logprobs
            
        Returns:
            Uncertainty score (0.0 = certain, 1.0 = uncertain)
        """
        if not decision_logprobs:
            return 0.5  # Default uncertainty
        
        # Convert logprobs to probabilities
        probs = {k: math.exp(v) for k, v in decision_logprobs.items()}
        
        # Normalize probabilities
        total_prob = sum(probs.values())
        if total_prob > 0:
            probs = {k: v / total_prob for k, v in probs.items()}
        
        # Calculate entropy (uncertainty measure)
        entropy = 0.0
        for prob in probs.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Normalize entropy to [0, 1]
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1.0
        normalized_uncertainty = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return min(1.0, max(0.0, normalized_uncertainty))
    
    def _extract_text_confidence(self, response_text: str) -> float:
        """Extract confidence from response text using heuristics.
        
        Args:
            response_text: Model response text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        text_lower = response_text.lower()
        
        # Look for explicit confidence indicators
        confidence_patterns = {
            "very confident": 0.9,
            "highly confident": 0.9,
            "confident": 0.8,
            "quite sure": 0.8,
            "sure": 0.75,
            "likely": 0.7,
            "probably": 0.65,
            "possibly": 0.5,
            "uncertain": 0.3,
            "unsure": 0.3,
            "unclear": 0.2
        }
        
        for pattern, confidence in confidence_patterns.items():
            if pattern in text_lower:
                return confidence
        
        # Look for uncertainty markers
        uncertainty_markers = [
            "might", "may", "could", "perhaps", "maybe", "seems", "appears",
            "unclear", "ambiguous", "difficult to determine"
        ]
        
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker in text_lower)
        
        # Base confidence adjusted by uncertainty markers
        base_confidence = 0.7
        uncertainty_penalty = uncertainty_count * 0.1
        
        return max(0.1, base_confidence - uncertainty_penalty)
    
    def _calibrate_with_logprobs(self, raw_confidence: float, decision_logprobs: Dict[str, float], uncertainty: float) -> float:
        """Calibrate confidence using logprobs information.
        
        Args:
            raw_confidence: Original confidence from text
            decision_logprobs: Decision token logprobs
            uncertainty: Calculated uncertainty
            
        Returns:
            Calibrated confidence score
        """
        if not decision_logprobs:
            return raw_confidence
        
        # Get the strongest decision logprob
        max_decision_logprob = max(decision_logprobs.values())
        
        # Convert to probability
        max_decision_prob = math.exp(max_decision_logprob)
        
        # Weighted combination of text confidence and logprob confidence
        logprob_weight = 0.6  # Give more weight to logprobs
        text_weight = 0.4
        
        # Adjust for uncertainty
        uncertainty_adjusted_prob = max_decision_prob * (1 - uncertainty * 0.5)
        
        calibrated = (
            text_weight * raw_confidence + 
            logprob_weight * uncertainty_adjusted_prob
        )
        
        return min(1.0, max(0.0, calibrated))
    
    def _calculate_quality_score(self, decision_logprobs: Dict[str, float], uncertainty: float) -> float:
        """Calculate quality score for the calibration.
        
        Args:
            decision_logprobs: Decision token logprobs
            uncertainty: Calculated uncertainty
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not decision_logprobs:
            return 0.5
        
        # Quality based on:
        # 1. Presence of decision tokens
        # 2. Strength of decision signals
        # 3. Low uncertainty
        
        # Token presence score
        token_score = min(1.0, len(decision_logprobs) / 3)
        
        # Signal strength score (higher logprobs = better)
        max_logprob = max(decision_logprobs.values())
        # Normalize typical logprob range [-10, 0] to [0, 1]
        strength_score = max(0.0, (max_logprob + 10) / 10)
        
        # Certainty score (lower uncertainty = better)
        certainty_score = 1.0 - uncertainty
        
        # Combined quality score
        quality = (token_score + strength_score + certainty_score) / 3
        
        return min(1.0, max(0.0, quality))
    
    def batch_calibrate(self, responses: List[Tuple[str, Optional[Dict[str, float]]]]) -> List[ConfidenceCalibration]:
        """Calibrate confidence for multiple responses.
        
        Args:
            responses: List of (response_text, logprobs) tuples
            
        Returns:
            List of ConfidenceCalibration objects
        """
        calibrations = []
        
        for response_text, logprobs in responses:
            try:
                calibration = self.calibrate_confidence(response_text, logprobs)
                calibrations.append(calibration)
            except Exception as e:
                logger.error(f"Failed to calibrate confidence: {e}")
                # Fallback calibration
                calibrations.append(ConfidenceCalibration(
                    calibrated_confidence=0.5,
                    raw_confidence=0.5,
                    uncertainty=0.5,
                    decision_logprobs={},
                    calibration_method="fallback",
                    quality_score=0.3
                ))
        
        return calibrations
    
    def analyze_calibration_trends(self, calibrations: List[ConfidenceCalibration]) -> Dict[str, Any]:
        """Analyze trends across multiple calibrations.
        
        Args:
            calibrations: List of calibration results
            
        Returns:
            Analysis report with trends and insights
        """
        if not calibrations:
            return {"error": "No calibrations to analyze"}
        
        # Calculate statistics
        calibrated_scores = [c.calibrated_confidence for c in calibrations]
        raw_scores = [c.raw_confidence for c in calibrations]
        uncertainties = [c.uncertainty for c in calibrations]
        quality_scores = [c.quality_score for c in calibrations]
        
        avg_calibrated = sum(calibrated_scores) / len(calibrated_scores)
        avg_raw = sum(raw_scores) / len(raw_scores)
        avg_uncertainty = sum(uncertainties) / len(uncertainties)
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Calibration improvement
        improvement = avg_calibrated - avg_raw
        
        # Method distribution
        methods = {}
        for calibration in calibrations:
            method = calibration.calibration_method
            methods[method] = methods.get(method, 0) + 1
        
        return {
            "statistics": {
                "average_calibrated_confidence": avg_calibrated,
                "average_raw_confidence": avg_raw,
                "average_uncertainty": avg_uncertainty,
                "average_quality_score": avg_quality,
                "calibration_improvement": improvement,
                "total_calibrations": len(calibrations)
            },
            "quality_distribution": {
                "high_quality": len([c for c in calibrations if c.quality_score > 0.8]),
                "medium_quality": len([c for c in calibrations if 0.5 <= c.quality_score <= 0.8]),
                "low_quality": len([c for c in calibrations if c.quality_score < 0.5])
            },
            "method_distribution": methods,
            "recommendations": self._generate_calibration_recommendations(
                avg_quality, avg_uncertainty, improvement
            )
        }
    
    def _generate_calibration_recommendations(self, avg_quality: float, avg_uncertainty: float, improvement: float) -> List[str]:
        """Generate recommendations based on calibration analysis."""
        recommendations = []
        
        if avg_quality < 0.6:
            recommendations.append("Consider using higher-quality models for better confidence calibration")
        
        if avg_uncertainty > 0.7:
            recommendations.append("High uncertainty detected - review prompt clarity and decision criteria")
        
        if improvement < 0.05:
            recommendations.append("Limited calibration improvement - verify logprobs are being captured correctly")
        
        if not recommendations:
            recommendations.append("Confidence calibration is performing well - continue current approach")
        
        return recommendations
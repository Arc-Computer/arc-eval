"""
Prediction accuracy analytics for reliability prediction system.

Calculates F1, precision, recall, confusion matrix and trend analysis for:
- Overall prediction accuracy
- Component-specific performance (rules vs LLM)
- Weekly trend analysis
- Framework and domain-specific accuracy
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class PredictionAnalytics:
    """Calculate prediction accuracy metrics and trend analysis."""
    
    def __init__(self, prediction_tracker):
        """Initialize analytics with prediction tracker."""
        self.tracker = prediction_tracker
    
    def calculate_accuracy_metrics(self, days: int = 90) -> Dict[str, Any]:
        """
        Calculate comprehensive accuracy metrics.
        
        Returns F1, precision, recall, confusion matrix for the last N days.
        """
        
        try:
            # Get predictions with outcomes
            predictions = self.tracker.get_predictions_with_outcomes(days)
            
            if len(predictions) < 5:
                logger.warning(f"Insufficient data for accuracy calculation: {len(predictions)} predictions")
                return self._create_empty_metrics(len(predictions))
            
            # Convert to binary classification
            y_true, y_pred, confidence_scores = self._prepare_classification_data(predictions)
            
            # Calculate basic metrics
            confusion_matrix = self._calculate_confusion_matrix(y_true, y_pred)
            precision = self._calculate_precision(confusion_matrix)
            recall = self._calculate_recall(confusion_matrix)
            f1_score = self._calculate_f1(precision, recall)
            accuracy = self._calculate_accuracy(confusion_matrix)
            
            # Calculate confidence-weighted metrics
            weighted_metrics = self._calculate_weighted_metrics(y_true, y_pred, confidence_scores)
            
            # Component analysis
            component_analysis = self._analyze_component_performance(predictions)
            
            # Risk level analysis
            risk_level_analysis = self._analyze_risk_level_performance(predictions)
            
            return {
                'period_days': days,
                'sample_size': len(predictions),
                'data_quality': self._assess_data_quality(predictions),
                
                # Core metrics
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'confusion_matrix': confusion_matrix,
                
                # Weighted metrics
                'weighted_accuracy': weighted_metrics['accuracy'],
                'weighted_f1': weighted_metrics['f1'],
                
                # Component analysis
                'rule_component_accuracy': component_analysis['rule_accuracy'],
                'llm_component_accuracy': component_analysis['llm_accuracy'],
                'hybrid_improvement': component_analysis['hybrid_improvement'],
                
                # Risk level analysis
                'risk_level_performance': risk_level_analysis,
                
                # Metadata
                'calculation_timestamp': datetime.now().isoformat(),
                'falsifiable': True,  # These are objective metrics
                'statistical_significance': self._assess_statistical_significance(len(predictions))
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate accuracy metrics: {e}")
            return self._create_empty_metrics(0, error=str(e))
    
    def calculate_weekly_trends(self, weeks: int = 12) -> Dict[str, Any]:
        """Calculate weekly accuracy trends for the last N weeks."""
        
        try:
            weekly_data = []
            
            for week in range(weeks):
                # Calculate date range for this week
                end_date = datetime.now() - timedelta(weeks=week)
                start_date = end_date - timedelta(weeks=1)
                
                # Get predictions for this week
                week_predictions = self._get_predictions_for_period(start_date, end_date)
                
                if len(week_predictions) >= 3:  # Minimum for meaningful metrics
                    week_metrics = self._calculate_week_metrics(week_predictions)
                    week_metrics['week_start'] = start_date.isoformat()
                    week_metrics['week_end'] = end_date.isoformat()
                    weekly_data.append(week_metrics)
            
            # Calculate trends
            trends = self._calculate_trend_analysis(weekly_data)
            
            return {
                'weeks_analyzed': len(weekly_data),
                'weekly_data': weekly_data,
                'trends': trends,
                'trend_analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate weekly trends: {e}")
            return {'error': str(e), 'weeks_analyzed': 0}
    
    def analyze_prediction_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze patterns in prediction performance."""
        
        try:
            predictions = self.tracker.get_predictions_with_outcomes(days)
            
            if not predictions:
                return {'error': 'No predictions with outcomes found'}
            
            # Framework performance
            framework_performance = defaultdict(list)
            for pred in predictions:
                framework = pred.get('framework', 'unknown')
                is_correct = self._is_prediction_correct(pred)
                framework_performance[framework].append(is_correct)
            
            # Domain performance
            domain_performance = defaultdict(list)
            for pred in predictions:
                domain = pred.get('domain', 'general')
                is_correct = self._is_prediction_correct(pred)
                domain_performance[domain].append(is_correct)
            
            # Risk level accuracy
            risk_accuracy = defaultdict(list)
            for pred in predictions:
                risk_level = pred.get('risk_level', 'UNKNOWN')
                is_correct = self._is_prediction_correct(pred)
                risk_accuracy[risk_level].append(is_correct)
            
            # Confidence calibration
            confidence_calibration = self._analyze_confidence_calibration(predictions)
            
            return {
                'framework_performance': {
                    framework: {
                        'accuracy': np.mean(results),
                        'sample_size': len(results)
                    }
                    for framework, results in framework_performance.items()
                },
                'domain_performance': {
                    domain: {
                        'accuracy': np.mean(results),
                        'sample_size': len(results)
                    }
                    for domain, results in domain_performance.items()
                },
                'risk_level_accuracy': {
                    risk_level: {
                        'accuracy': np.mean(results),
                        'sample_size': len(results)
                    }
                    for risk_level, results in risk_accuracy.items()
                },
                'confidence_calibration': confidence_calibration,
                'analysis_period_days': days,
                'total_predictions': len(predictions)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze prediction patterns: {e}")
            return {'error': str(e)}
    
    def _prepare_classification_data(self, predictions: List[Dict]) -> Tuple[List[int], List[int], List[float]]:
        """Prepare data for binary classification analysis."""
        
        y_true = []
        y_pred = []
        confidence_scores = []
        
        for pred in predictions:
            # True outcome (1 = failure, 0 = success/partial)
            outcome = pred.get('outcome', 'unknown')
            true_label = 1 if outcome == 'failure' else 0
            
            # Predicted outcome (1 = high risk, 0 = low/medium risk)
            risk_level = pred.get('risk_level', 'LOW')
            pred_label = 1 if risk_level == 'HIGH' else 0
            
            # Confidence score
            confidence = pred.get('confidence', 0.5)
            
            y_true.append(true_label)
            y_pred.append(pred_label)
            confidence_scores.append(confidence)
        
        return y_true, y_pred, confidence_scores
    
    def _calculate_confusion_matrix(self, y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
        """Calculate confusion matrix."""
        
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
        tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
        
        return {
            'true_positive': tp,
            'true_negative': tn,
            'false_positive': fp,
            'false_negative': fn
        }
    
    def _calculate_precision(self, cm: Dict[str, int]) -> float:
        """Calculate precision."""
        tp = cm['true_positive']
        fp = cm['false_positive']
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    def _calculate_recall(self, cm: Dict[str, int]) -> float:
        """Calculate recall."""
        tp = cm['true_positive']
        fn = cm['false_negative']
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    def _calculate_f1(self, precision: float, recall: float) -> float:
        """Calculate F1 score."""
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    def _calculate_accuracy(self, cm: Dict[str, int]) -> float:
        """Calculate accuracy."""
        tp = cm['true_positive']
        tn = cm['true_negative']
        total = sum(cm.values())
        return (tp + tn) / total if total > 0 else 0.0
    
    def _calculate_weighted_metrics(self, y_true: List[int], y_pred: List[int], 
                                  confidence_scores: List[float]) -> Dict[str, float]:
        """Calculate confidence-weighted metrics."""
        
        # Weight predictions by confidence
        weighted_correct = 0
        total_weight = 0
        
        for true_val, pred_val, confidence in zip(y_true, y_pred, confidence_scores):
            is_correct = (true_val == pred_val)
            weighted_correct += is_correct * confidence
            total_weight += confidence
        
        weighted_accuracy = weighted_correct / total_weight if total_weight > 0 else 0.0
        
        # For F1, we need to recalculate with weights
        # This is a simplified approach
        weighted_f1 = weighted_accuracy  # Approximation
        
        return {
            'accuracy': weighted_accuracy,
            'f1': weighted_f1
        }
    
    def _analyze_component_performance(self, predictions: List[Dict]) -> Dict[str, float]:
        """Analyze rule vs LLM component performance."""
        
        rule_correct = 0
        llm_correct = 0
        hybrid_correct = 0
        total = len(predictions)
        
        for pred in predictions:
            is_correct = self._is_prediction_correct(pred)
            
            # Simulate component accuracy (in real implementation, we'd track this)
            rule_score = pred.get('rule_component_score', 0.5)
            llm_score = pred.get('llm_component_score', 0.5)
            
            # Simple heuristic: if rule score > 0.7, rule would have predicted high risk
            rule_prediction = rule_score > 0.7
            llm_prediction = llm_score > 0.5
            
            outcome = pred.get('outcome', 'success')
            actual_failure = outcome == 'failure'
            
            if rule_prediction == actual_failure:
                rule_correct += 1
            if llm_prediction == actual_failure:
                llm_correct += 1
            if is_correct:
                hybrid_correct += 1
        
        rule_accuracy = rule_correct / total if total > 0 else 0.0
        llm_accuracy = llm_correct / total if total > 0 else 0.0
        hybrid_accuracy = hybrid_correct / total if total > 0 else 0.0
        
        return {
            'rule_accuracy': rule_accuracy,
            'llm_accuracy': llm_accuracy,
            'hybrid_accuracy': hybrid_accuracy,
            'hybrid_improvement': hybrid_accuracy - max(rule_accuracy, llm_accuracy)
        }
    
    def _analyze_risk_level_performance(self, predictions: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by risk level."""
        
        risk_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for pred in predictions:
            risk_level = pred.get('risk_level', 'UNKNOWN')
            is_correct = self._is_prediction_correct(pred)
            
            risk_performance[risk_level]['total'] += 1
            if is_correct:
                risk_performance[risk_level]['correct'] += 1
        
        return {
            risk_level: {
                'accuracy': data['correct'] / data['total'] if data['total'] > 0 else 0.0,
                'sample_size': data['total']
            }
            for risk_level, data in risk_performance.items()
        }
    
    def _is_prediction_correct(self, prediction: Dict) -> bool:
        """Determine if a prediction was correct."""
        
        risk_level = prediction.get('risk_level', 'LOW')
        outcome = prediction.get('outcome', 'success')
        
        # High risk prediction should correspond to failure outcome
        if risk_level == 'HIGH':
            return outcome == 'failure'
        else:
            return outcome in ['success', 'partial']
    
    def _create_empty_metrics(self, sample_size: int, error: str = None) -> Dict[str, Any]:
        """Create empty metrics structure."""
        
        return {
            'sample_size': sample_size,
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'confusion_matrix': {'true_positive': 0, 'true_negative': 0, 'false_positive': 0, 'false_negative': 0},
            'data_quality': 'insufficient',
            'statistical_significance': 'none',
            'error': error,
            'calculation_timestamp': datetime.now().isoformat()
        }
    
    def _assess_data_quality(self, predictions: List[Dict]) -> str:
        """Assess the quality of prediction data."""
        
        if len(predictions) < 10:
            return 'insufficient'
        elif len(predictions) < 50:
            return 'limited'
        elif len(predictions) < 100:
            return 'good'
        else:
            return 'excellent'
    
    def _assess_statistical_significance(self, sample_size: int) -> str:
        """Assess statistical significance of results."""
        
        if sample_size < 30:
            return 'none'
        elif sample_size < 100:
            return 'limited'
        else:
            return 'significant'

    def _get_predictions_for_period(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get predictions for a specific time period."""

        all_predictions = self.tracker.get_predictions_with_outcomes(days=365)  # Get all

        period_predictions = []
        for pred in all_predictions:
            timestamp_str = pred.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if start_date <= timestamp <= end_date:
                        period_predictions.append(pred)
                except ValueError:
                    continue

        return period_predictions

    def _calculate_week_metrics(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics for a single week."""

        if len(predictions) < 3:
            return {'sample_size': len(predictions), 'accuracy': 0.0}

        y_true, y_pred, confidence_scores = self._prepare_classification_data(predictions)
        cm = self._calculate_confusion_matrix(y_true, y_pred)

        return {
            'sample_size': len(predictions),
            'accuracy': self._calculate_accuracy(cm),
            'precision': self._calculate_precision(cm),
            'recall': self._calculate_recall(cm),
            'f1_score': self._calculate_f1(self._calculate_precision(cm), self._calculate_recall(cm))
        }

    def _calculate_trend_analysis(self, weekly_data: List[Dict]) -> Dict[str, Any]:
        """Calculate trend analysis from weekly data."""

        if len(weekly_data) < 3:
            return {'trend': 'insufficient_data'}

        # Extract accuracy values
        accuracies = [week['accuracy'] for week in weekly_data if 'accuracy' in week]

        if len(accuracies) < 3:
            return {'trend': 'insufficient_data'}

        # Calculate simple trend
        recent_avg = np.mean(accuracies[:3])  # Last 3 weeks
        older_avg = np.mean(accuracies[-3:])  # First 3 weeks

        trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        trend_magnitude = abs(recent_avg - older_avg)

        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'recent_average': recent_avg,
            'baseline_average': older_avg,
            'weeks_analyzed': len(accuracies)
        }

    def _analyze_confidence_calibration(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze how well confidence scores match actual accuracy."""

        # Group predictions by confidence ranges
        confidence_ranges = {
            'low': (0.0, 0.4),
            'medium': (0.4, 0.7),
            'high': (0.7, 1.0)
        }

        calibration_data = {}

        for range_name, (min_conf, max_conf) in confidence_ranges.items():
            range_predictions = [
                pred for pred in predictions
                if min_conf <= pred.get('confidence', 0.5) < max_conf
            ]

            if range_predictions:
                correct_count = sum(1 for pred in range_predictions if self._is_prediction_correct(pred))
                accuracy = correct_count / len(range_predictions)
                avg_confidence = np.mean([pred.get('confidence', 0.5) for pred in range_predictions])

                calibration_data[range_name] = {
                    'sample_size': len(range_predictions),
                    'accuracy': accuracy,
                    'average_confidence': avg_confidence,
                    'calibration_error': abs(accuracy - avg_confidence)
                }

        return calibration_data

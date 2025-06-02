"""
Hybrid reliability predictor combining deterministic rules with LLM heuristics.

Implements the advisor-recommended approach:
- 40% weight: Deterministic compliance rules for regulatory requirements
- 60% weight: LLM pattern recognition for complex reliability assessment
- Unified risk assessment with confidence levels and rationale
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from .compliance_rules import ComplianceRuleEngine
from .llm_predictor import LLMReliabilityPredictor

logger = logging.getLogger(__name__)


class HybridReliabilityPredictor:
    """Combines rule-based + LLM scoring with weighted approach."""
    
    def __init__(self, api_manager=None):
        """Initialize hybrid predictor with both engines."""
        self.compliance_engine = ComplianceRuleEngine()
        self.llm_predictor = LLMReliabilityPredictor(api_manager)
        
        # Weighting as per advisor recommendation
        self.rule_weight = 0.4  # 40% for deterministic compliance
        self.llm_weight = 0.6   # 60% for LLM pattern recognition
    
    def predict_reliability(self, analysis, agent_config: Dict) -> Dict:
        """Generate hybrid prediction combining rules + LLM."""
        
        prediction_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        try:
            # Step 1: Run deterministic compliance rules
            compliance_result = self.compliance_engine.calculate_overall_compliance_risk(agent_config)
            
            # Step 2: Run LLM pattern analysis
            llm_result = self.llm_predictor.predict_failure_probability(analysis)
            
            # Step 3: Combine scores with weighting
            combined_result = self._combine_predictions(compliance_result, llm_result)
            
            # Step 4: Generate unified prediction
            prediction = {
                'prediction_id': prediction_id,
                'timestamp': timestamp,
                'combined_risk_score': combined_result['risk_score'],
                'risk_level': combined_result['risk_level'],
                'confidence': combined_result['confidence'],
                
                # Separate components for transparency
                'rule_based_component': {
                    'risk_score': compliance_result['risk_score'],
                    'weight': self.rule_weight,
                    'violations': compliance_result['all_violations'],
                    'critical_violations': compliance_result['critical_violations'],
                    'compliant': compliance_result['overall_compliant']
                },
                'llm_component': {
                    'risk_score': llm_result['failure_probability'],
                    'weight': self.llm_weight,
                    'confidence': llm_result['confidence'],
                    'risk_factors': llm_result.get('top_3_risk_factors', []),
                    'predicted_failures': llm_result.get('predicted_failure_modes', []),
                    'rationale': llm_result.get('rationale', ''),
                    'fallback_used': llm_result.get('fallback_used', False)
                },
                
                # Unified insights
                'top_risk_factors': self._merge_risk_factors(compliance_result, llm_result),
                'recommendations': self._generate_recommendations(compliance_result, llm_result),
                'business_impact': self._calculate_business_impact(combined_result),
                
                # For feedback loop
                'input_hash': hashlib.md5(str(agent_config).encode()).hexdigest(),
                'analysis_hash': hashlib.md5(str(analysis).encode()).hexdigest() if analysis else None,
                'outcome': None,  # To be filled by feedback
                'feedback_collected': False
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Hybrid prediction failed: {e}")
            return self._create_error_prediction(prediction_id, timestamp, str(e))
    
    def _combine_predictions(self, compliance_result: Dict, llm_result: Dict) -> Dict:
        """Combine rule-based and LLM predictions with weighting."""
        
        # Extract risk scores
        rule_risk = compliance_result['risk_score']
        llm_risk = llm_result['failure_probability']
        llm_confidence = llm_result['confidence']
        
        # Apply weighting: 40% rules, 60% LLM
        combined_risk = (self.rule_weight * rule_risk) + (self.llm_weight * llm_risk)
        
        # Adjust for LLM confidence (lower confidence reduces LLM contribution)
        confidence_adjusted_risk = (
            (self.rule_weight * rule_risk) + 
            (self.llm_weight * llm_risk * llm_confidence)
        )
        
        # Use confidence-adjusted score if LLM confidence is low
        final_risk = confidence_adjusted_risk if llm_confidence < 0.7 else combined_risk
        
        # Determine final risk level
        risk_level = self._determine_risk_level(final_risk, compliance_result)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(compliance_result, llm_result)
        
        return {
            'risk_score': final_risk,
            'risk_level': risk_level,
            'confidence': overall_confidence
        }
    
    def _determine_risk_level(self, combined_risk: float, compliance_result: Dict) -> str:
        """Determine risk level considering both score and compliance violations."""
        
        # Critical compliance violations always result in HIGH risk
        if compliance_result['critical_violations'] > 0:
            return 'HIGH'
        
        # Standard risk level determination
        if combined_risk >= 0.7:
            return 'HIGH'
        elif combined_risk >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_overall_confidence(self, compliance_result: Dict, llm_result: Dict) -> float:
        """Calculate overall prediction confidence."""
        
        # Rule-based component has high confidence (deterministic)
        rule_confidence = 0.95
        
        # LLM confidence from the prediction
        llm_confidence = llm_result['confidence']
        
        # Weighted average
        overall_confidence = (
            (self.rule_weight * rule_confidence) + 
            (self.llm_weight * llm_confidence)
        )
        
        # Reduce confidence if using fallback
        if llm_result.get('fallback_used', False):
            overall_confidence *= 0.6
        
        return round(overall_confidence, 2)
    
    def _merge_risk_factors(self, compliance_result: Dict, llm_result: Dict) -> List[str]:
        """Merge risk factors from both components."""
        
        risk_factors = []
        
        # Add compliance violations as risk factors
        for violation in compliance_result['all_violations']:
            risk_factors.append(f"{violation['regulation']}: {violation['description']}")
        
        # Add LLM-identified risk factors
        llm_factors = llm_result.get('top_3_risk_factors', [])
        risk_factors.extend(llm_factors)
        
        # Return top 5 most critical
        return risk_factors[:5]
    
    def _generate_recommendations(self, compliance_result: Dict, llm_result: Dict) -> List[str]:
        """Generate actionable recommendations from both components."""
        
        recommendations = []
        
        # Add compliance remediation recommendations
        for violation in compliance_result['all_violations']:
            if violation['severity'] in ['CRITICAL', 'HIGH']:
                recommendations.append(violation['remediation'])
        
        # Add LLM recommendations
        llm_recommendations = llm_result.get('recommendations', [])
        recommendations.extend(llm_recommendations)
        
        # Remove duplicates and return top 5
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:5]
    
    def _calculate_business_impact(self, combined_result: Dict) -> Dict:
        """Calculate business impact metrics for the prediction."""
        
        risk_score = combined_result['risk_score']
        risk_level = combined_result['risk_level']
        
        # Estimate failure prevention percentage
        if risk_level == 'HIGH':
            prevention_percentage = 85
            time_saved_hours = 8.0
        elif risk_level == 'MEDIUM':
            prevention_percentage = 65
            time_saved_hours = 4.0
        else:
            prevention_percentage = 30
            time_saved_hours = 1.0
        
        # Calculate cost savings (rough estimates)
        incident_cost = 25000  # Average cost of production incident
        potential_savings = incident_cost * (prevention_percentage / 100) * risk_score
        
        return {
            'failure_prevention_percentage': prevention_percentage,
            'estimated_time_saved_hours': time_saved_hours,
            'potential_cost_savings': round(potential_savings, 2),
            'production_readiness': 'Not Ready' if risk_level == 'HIGH' else 'Review Required' if risk_level == 'MEDIUM' else 'Ready'
        }
    
    def _create_error_prediction(self, prediction_id: str, timestamp: str, error_msg: str) -> Dict:
        """Create error prediction when hybrid prediction fails."""
        
        return {
            'prediction_id': prediction_id,
            'timestamp': timestamp,
            'combined_risk_score': 0.8,  # High risk due to prediction failure
            'risk_level': 'HIGH',
            'confidence': 0.2,  # Low confidence
            
            'rule_based_component': {
                'risk_score': 0.5,
                'weight': self.rule_weight,
                'violations': [],
                'error': 'Compliance check failed'
            },
            'llm_component': {
                'risk_score': 0.8,
                'weight': self.llm_weight,
                'confidence': 0.2,
                'error': error_msg,
                'fallback_used': True
            },
            
            'top_risk_factors': [
                'Prediction system failure - unable to assess reliability',
                'Recommend manual review of agent configuration'
            ],
            'recommendations': [
                'Manually review agent configuration for reliability issues',
                'Check system logs for prediction service errors',
                'Consider running individual compliance checks'
            ],
            'business_impact': {
                'failure_prevention_percentage': 0,
                'estimated_time_saved_hours': 0,
                'potential_cost_savings': 0,
                'production_readiness': 'Manual Review Required'
            },
            
            'error': error_msg,
            'outcome': None,
            'feedback_collected': False
        }

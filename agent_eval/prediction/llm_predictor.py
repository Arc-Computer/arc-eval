"""
LLM-powered pattern recognition for complex reliability assessment.

Uses GPT-4.1 to analyze agent configurations and execution patterns for:
- Complex failure mode detection
- Framework-specific reliability patterns  
- Risk assessment with confidence weighting
- Explainable prediction reasoning
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMReliabilityPredictor:
    """LLM-powered pattern recognition for complex reliability assessment."""
    
    def __init__(self, api_manager=None):
        """Initialize with API manager for LLM calls."""
        self.api_manager = api_manager
        if not api_manager:
            # Import here to avoid circular imports
            from agent_eval.evaluation.judges.api_manager import APIManager
            self.api_manager = APIManager()
    
    def predict_failure_probability(self, analysis) -> Dict:
        """Use GPT-4.1 to analyze patterns and predict failure probability."""
        
        # Prepare structured data for LLM analysis
        analysis_data = self._extract_analysis_features(analysis)
        
        # Create prediction prompt
        prompt = self._create_prediction_prompt(analysis_data)
        
        try:
            # Call GPT-4.1 for prediction using the API manager
            response, _ = self.api_manager.call_with_logprobs(
                prompt=prompt,
                enable_logprobs=False  # We don't need logprobs for prediction
            )
            
            # Parse structured response
            prediction = self._parse_prediction_response(response)
            
            # Add metadata
            prediction['model_used'] = 'gpt-4.1'
            prediction['timestamp'] = datetime.now().isoformat()
            prediction['analysis_features'] = analysis_data
            
            return prediction
            
        except Exception as e:
            logger.error(f"LLM prediction failed: {e}")
            return self._create_fallback_prediction(analysis_data, str(e))
    
    def _extract_analysis_features(self, analysis) -> Dict:
        """Extract key features from ComprehensiveReliabilityAnalysis for LLM."""
        
        # Handle both object and dict formats
        if hasattr(analysis, 'to_dict'):
            analysis_dict = analysis.to_dict()
        elif isinstance(analysis, dict):
            analysis_dict = analysis
        else:
            analysis_dict = {}
        
        # Extract key reliability metrics
        features = {
            'framework': getattr(analysis, 'detected_framework', analysis_dict.get('detected_framework', 'unknown')),
            'framework_confidence': getattr(analysis, 'framework_confidence', analysis_dict.get('framework_confidence', 0)),
            'sample_size': getattr(analysis, 'sample_size', analysis_dict.get('sample_size', 0)),
            'evidence_quality': getattr(analysis, 'evidence_quality', analysis_dict.get('evidence_quality', 0)),
        }
        
        # Extract workflow metrics if available
        workflow_metrics = getattr(analysis, 'workflow_metrics', analysis_dict.get('workflow_metrics', {}))
        if workflow_metrics:
            # Handle both dataclass objects and dictionaries
            if hasattr(workflow_metrics, 'workflow_success_rate'):
                # It's a dataclass object
                features.update({
                    'success_rate': getattr(workflow_metrics, 'workflow_success_rate', 0),
                    'tool_reliability': getattr(workflow_metrics, 'tool_chain_reliability', 0),
                    'error_recovery_rate': getattr(workflow_metrics, 'error_recovery_rate', 0),
                    'timeout_rate': getattr(workflow_metrics, 'timeout_rate', 0),
                    'decision_consistency': getattr(workflow_metrics, 'decision_consistency_score', 0),
                    'schema_mismatch_rate': getattr(workflow_metrics, 'schema_mismatch_rate', 0)
                })
            else:
                # It's a dictionary
                features.update({
                    'success_rate': workflow_metrics.get('workflow_success_rate', 0),
                    'tool_reliability': workflow_metrics.get('tool_chain_reliability', 0),
                    'error_recovery_rate': workflow_metrics.get('error_recovery_rate', 0),
                    'timeout_rate': workflow_metrics.get('timeout_rate', 0),
                    'decision_consistency': workflow_metrics.get('decision_consistency_score', 0),
                    'schema_mismatch_rate': workflow_metrics.get('schema_mismatch_rate', 0)
                })
        
        # Extract framework performance if available
        framework_performance = getattr(analysis, 'framework_performance', analysis_dict.get('framework_performance', {}))
        if framework_performance:
            # Handle both dataclass objects and dictionaries
            if hasattr(framework_performance, 'avg_response_time'):
                # It's a dataclass object
                features.update({
                    'avg_response_time': getattr(framework_performance, 'avg_response_time', 0),
                    'tool_call_failure_rate': getattr(framework_performance, 'tool_call_failure_rate', 0),
                    'abstraction_overhead': getattr(framework_performance, 'abstraction_overhead', 0)
                })
            else:
                # It's a dictionary
                features.update({
                    'avg_response_time': framework_performance.get('avg_response_time', 0),
                    'tool_call_failure_rate': framework_performance.get('tool_call_failure_rate', 0),
                    'abstraction_overhead': framework_performance.get('abstraction_overhead', 0)
                })
        
        return features
    
    def _create_prediction_prompt(self, analysis_data: Dict) -> str:
        """Create structured prompt for GPT-4.1 reliability prediction."""
        
        prompt = f"""You are a senior reliability engineer analyzing agent telemetry data to predict failure probability.

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

TASK: Predict reliability risks and failure probability based on the metrics above.

ANALYSIS GUIDELINES:
1. Focus on patterns that indicate brittleness or failure modes
2. Consider framework-specific reliability characteristics
3. Weight predictions by sample size and evidence quality  
4. Identify specific risk factors with evidence from the metrics
5. Provide confidence level based on data quality

FRAMEWORK-SPECIFIC PATTERNS:
- LangChain: Watch for intermediate_steps complexity, tool chaining issues
- CrewAI: Monitor crew coordination, task delegation failures
- OpenAI: Check for rate limiting, context window issues
- Generic: Focus on basic reliability patterns

RELIABILITY RISK FACTORS:
- High response times (>10s) indicate timeout risk
- Low success rates (<80%) suggest systematic issues
- High tool failure rates (>5%) indicate integration problems
- Low error recovery (<50%) suggests brittle error handling
- High schema mismatches indicate tool compatibility issues

OUTPUT FORMAT (valid JSON only):
{{
    "failure_probability": 0.0-1.0,
    "confidence": 0.0-1.0,
    "risk_level": "LOW|MEDIUM|HIGH",
    "top_3_risk_factors": [
        "specific risk factor with evidence from metrics",
        "another risk factor with supporting data",
        "third risk factor with quantitative evidence"
    ],
    "predicted_failure_modes": [
        {{
            "type": "timeout_cascade|tool_integration|framework_compatibility|performance_degradation|error_propagation",
            "probability": 0.0-1.0,
            "evidence": "specific evidence from the metrics provided"
        }}
    ],
    "rationale": "2-3 sentence explanation of prediction reasoning based on the specific metrics",
    "recommendations": [
        "specific actionable recommendation based on identified risks",
        "another recommendation with implementation guidance"
    ]
}}

IMPORTANT: Return only valid JSON. Do not include any text before or after the JSON."""
        
        return prompt
    
    def _parse_prediction_response(self, response: str) -> Dict:
        """Parse and validate LLM prediction response."""
        
        try:
            # Clean response (remove any non-JSON content)
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            prediction = json.loads(response)
            
            # Validate required fields
            required_fields = ['failure_probability', 'confidence', 'risk_level', 'rationale']
            for field in required_fields:
                if field not in prediction:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate ranges
            if not (0 <= prediction['failure_probability'] <= 1):
                raise ValueError("failure_probability must be between 0 and 1")
            
            if not (0 <= prediction['confidence'] <= 1):
                raise ValueError("confidence must be between 0 and 1")
            
            if prediction['risk_level'] not in ['LOW', 'MEDIUM', 'HIGH']:
                raise ValueError("risk_level must be LOW, MEDIUM, or HIGH")
            
            # Ensure lists exist
            prediction.setdefault('top_3_risk_factors', [])
            prediction.setdefault('predicted_failure_modes', [])
            prediction.setdefault('recommendations', [])
            
            return prediction
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except Exception as e:
            logger.error(f"Failed to validate LLM prediction: {e}")
            raise ValueError(f"Invalid prediction format: {e}")
    
    def _create_fallback_prediction(self, analysis_data: Dict, error_msg: str) -> Dict:
        """Create fallback prediction when LLM call fails."""
        
        # Simple heuristic-based fallback
        success_rate = analysis_data.get('success_rate', 80)
        tool_failure_rate = analysis_data.get('tool_call_failure_rate', 0)
        response_time = analysis_data.get('avg_response_time', 0)
        
        # Calculate basic risk score
        risk_score = 0.0
        risk_factors = []
        
        if success_rate < 70:
            risk_score += 0.4
            risk_factors.append(f"Low success rate: {success_rate}%")
        
        if tool_failure_rate > 0.1:
            risk_score += 0.3
            risk_factors.append(f"High tool failure rate: {tool_failure_rate:.1%}")
        
        if response_time > 15:
            risk_score += 0.3
            risk_factors.append(f"High response time: {response_time}s")
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = 'HIGH'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'failure_probability': min(risk_score, 1.0),
            'confidence': 0.3,  # Low confidence for fallback
            'risk_level': risk_level,
            'top_3_risk_factors': risk_factors[:3],
            'predicted_failure_modes': [],
            'rationale': f"Fallback prediction due to LLM error: {error_msg}",
            'recommendations': ["Review agent configuration for reliability issues"],
            'fallback_used': True,
            'error': error_msg
        }

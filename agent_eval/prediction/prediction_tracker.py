"""
Prediction tracking system for reliability prediction accuracy measurement.

Implements JSONL-based logging for:
- Prediction storage with unique IDs and timestamps
- Automatic outcome detection from trace data
- Data retrieval for analytics and trend analysis
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)


class PredictionTracker:
    """Log predictions with unique IDs and timestamps for accuracy tracking."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize prediction tracker with storage configuration."""
        
        # Set up storage directory
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Default to user's home directory for persistence
            home_dir = Path.home()
            self.storage_dir = home_dir / ".arc-eval" / "predictions"

        # Ensure storage directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.predictions_file = self.storage_dir / "predictions.jsonl"

        # Ensure file exists
        self.predictions_file.touch(exist_ok=True)
        
        logger.info(f"PredictionTracker initialized with storage: {self.storage_dir}")
    
    def log_prediction(self, prediction: Dict[str, Any], agent_config: Dict[str, Any],
                     pipeline_data: Optional[Dict[str, Any]] = None) -> str:
        """Log prediction with metadata for later accuracy tracking."""
        
        try:
            # Extract key information
            prediction_id = prediction.get('prediction_id')
            if not prediction_id:
                logger.error("Prediction missing prediction_id")
                return None
            
            # Create log entry
            log_entry = {
                'prediction_id': prediction_id,
                'timestamp': prediction.get('timestamp', datetime.now().isoformat()),
                'risk_score': prediction.get('combined_risk_score', 0.0),
                'risk_level': prediction.get('risk_level', 'UNKNOWN'),
                'confidence': prediction.get('confidence', 0.0),
                
                # Agent configuration metadata
                'agent_config_hash': prediction.get('input_hash'),
                'framework': self._extract_framework(agent_config),
                'domain': self._detect_domain(agent_config),
                
                # Component scores for analysis
                'rule_component_score': prediction.get('rule_based_component', {}).get('risk_score', 0.0),
                'llm_component_score': prediction.get('llm_component', {}).get('risk_score', 0.0),
                'llm_confidence': prediction.get('llm_component', {}).get('confidence', 0.0),
                'fallback_used': prediction.get('llm_component', {}).get('fallback_used', False),
                
                # Business impact
                'business_impact': prediction.get('business_impact', {}),

                # Pipeline data integration (NEW - unified data capture)
                'pipeline_metadata': self._extract_pipeline_metadata(pipeline_data) if pipeline_data else {},

                # Outcome tracking (to be filled by outcome detection)
                'outcome_detected': False,
                'outcome': None,
                'outcome_timestamp': None,
                'outcome_confidence': 0.0,
                'outcome_evidence': []
            }
            
            # Append to JSONL file
            with open(self.predictions_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.info(f"Logged prediction {prediction_id} with risk level {log_entry['risk_level']}")
            return prediction_id
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
            return None
    
    def update_prediction_outcome(self, prediction_id: str, outcome: str,
                                confidence: float = 1.0, evidence: List[str] = None) -> bool:
        """Update prediction with automatically detected outcome."""
        
        try:
            # Read all predictions
            predictions = self._load_predictions()
            
            # Find and update the prediction
            updated = False
            for prediction in predictions:
                if prediction.get('prediction_id') == prediction_id:
                    prediction['outcome_detected'] = True
                    prediction['outcome'] = outcome
                    prediction['outcome_timestamp'] = datetime.now().isoformat()
                    prediction['outcome_confidence'] = confidence
                    prediction['outcome_evidence'] = evidence or []
                    updated = True
                    break
            
            if not updated:
                logger.warning(f"Prediction {prediction_id} not found for outcome update")
                return False
            
            # Write back all predictions
            self._save_predictions(predictions)

            logger.info(f"Updated prediction {prediction_id} with outcome: {outcome} (confidence: {confidence:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update prediction outcome: {e}")
            return False

    def find_prediction_by_config(self, agent_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find recent prediction for the same agent configuration."""

        try:
            # Generate hash for current config
            config_hash = hashlib.md5(str(agent_config).encode()).hexdigest()

            # Get recent predictions (last 7 days)
            recent_predictions = self.get_predictions_for_analysis(days=7)

            # Find matching config hash
            for prediction in reversed(recent_predictions):  # Most recent first
                if prediction.get('agent_config_hash') == config_hash:
                    return prediction

            return None

        except Exception as e:
            logger.error(f"Failed to find prediction by config: {e}")
            return None

    def get_predictions_for_analysis(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get predictions from the last N days for analysis."""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            predictions = self._load_predictions()
            
            # Filter by date
            recent_predictions = []
            for prediction in predictions:
                timestamp_str = prediction.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if timestamp >= cutoff_date:
                            recent_predictions.append(prediction)
                    except ValueError:
                        # Skip predictions with invalid timestamps
                        continue
            
            logger.info(f"Retrieved {len(recent_predictions)} predictions from last {days} days")
            return recent_predictions
            
        except Exception as e:
            logger.error(f"Failed to get predictions for analysis: {e}")
            return []
    
    def get_predictions_with_outcomes(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get predictions that have detected outcomes for accuracy calculation."""

        predictions = self.get_predictions_for_analysis(days)
        return [p for p in predictions if p.get('outcome_detected') and p.get('outcome')]
    
    def get_prediction_by_id(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prediction by ID."""
        
        predictions = self._load_predictions()
        for prediction in predictions:
            if prediction.get('prediction_id') == prediction_id:
                return prediction
        return None
    
    def _load_predictions(self) -> List[Dict[str, Any]]:
        """Load all predictions from JSONL file."""
        
        predictions = []
        try:
            if self.predictions_file.exists():
                with open(self.predictions_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                predictions.append(json.loads(line))
                            except json.JSONDecodeError:
                                logger.warning(f"Skipping invalid JSON line: {line[:100]}")
        except Exception as e:
            logger.error(f"Failed to load predictions: {e}")
        
        return predictions
    
    def _save_predictions(self, predictions: List[Dict[str, Any]]) -> None:
        """Save all predictions back to JSONL file."""
        
        try:
            with open(self.predictions_file, 'w', encoding='utf-8') as f:
                for prediction in predictions:
                    f.write(json.dumps(prediction) + '\n')
        except Exception as e:
            logger.error(f"Failed to save predictions: {e}")
    
    def _extract_framework(self, agent_config: Dict[str, Any]) -> str:
        """Extract framework from agent configuration using centralized patterns."""

        # Look for explicit framework field first
        framework = agent_config.get('framework', 'unknown')
        if framework != 'unknown':
            return framework.lower()

        # Use centralized framework detection for consistency
        try:
            from agent_eval.core.framework_patterns import framework_patterns
            detected = framework_patterns.detect_framework_from_structure(agent_config)
            if detected:
                return detected
        except ImportError:
            logger.warning("Framework patterns not available, using fallback detection")

        # Fallback: Check for all supported framework patterns
        config_str = str(agent_config).lower()

        # Check all 9 supported frameworks with comprehensive patterns
        framework_keywords = {
            'langchain': ['langchain', 'intermediate_steps'],
            'langgraph': ['langgraph', 'lang_graph', 'graph_state', 'messages.*type.*ai'],
            'crewai': ['crewai', 'crew_ai', 'crew_output', 'task_results'],
            'autogen': ['autogen', 'auto_gen', 'microsoft', 'summary.*messages'],
            'openai': ['openai', 'gpt-', 'chatgpt', 'choices.*message'],
            'anthropic': ['anthropic', 'claude', 'content.*type.*text'],
            'agno': ['agno', 'phidata', 'structured_output', 'tools_used'],
            'google_adk': ['google_adk', 'vertex_ai', 'gemini', 'parts.*text', 'functioncall'],
            'nvidia_aiq': ['nvidia_aiq', 'nvidia', 'workbench', 'workflow_output', 'agent_state']
        }

        for framework_name, keywords in framework_keywords.items():
            if any(keyword in config_str for keyword in keywords):
                return framework_name

        return 'generic'
    
    def _detect_domain(self, agent_config: Dict[str, Any]) -> str:
        """Detect domain from agent configuration."""
        
        config_str = str(agent_config).lower()
        
        if any(term in config_str for term in ['finance', 'trading', 'investment', 'portfolio']):
            return 'finance'
        elif any(term in config_str for term in ['security', 'vulnerability', 'threat', 'compliance']):
            return 'security'
        elif any(term in config_str for term in ['model', 'training', 'ml', 'ai', 'machine learning']):
            return 'ml'
        elif any(term in config_str for term in ['healthcare', 'medical', 'patient', 'diagnosis']):
            return 'healthcare'
        
        return 'general'

    def _extract_pipeline_metadata(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract unified metadata from pipeline components."""

        metadata = {}

        try:
            # Input detection metadata
            if 'input_detection' in pipeline_data:
                input_data = pipeline_data['input_detection']
                metadata['input_detection'] = {
                    'detected_framework': input_data.get('detected_framework'),
                    'confidence': input_data.get('confidence', 0.0),
                    'file_size_mb': input_data.get('file_size_mb', 0.0),
                    'entry_count': input_data.get('entry_count', 0),
                    'validation_issues': input_data.get('validation_issues', [])
                }

            # Parser registry metadata
            if 'parser_registry' in pipeline_data:
                parser_data = pipeline_data['parser_registry']
                metadata['parser_registry'] = {
                    'framework_detected': parser_data.get('framework_detected'),
                    'extraction_method': parser_data.get('extraction_method'),
                    'tool_calls_extracted': parser_data.get('tool_calls_extracted', []),
                    'output_text_length': len(str(parser_data.get('extracted_output', ''))),
                    'parsing_errors': parser_data.get('parsing_errors', [])
                }

            # Input helpers metadata
            if 'input_helpers' in pipeline_data:
                helper_data = pipeline_data['input_helpers']
                metadata['input_helpers'] = {
                    'input_source': helper_data.get('input_source'),  # file, clipboard, scan
                    'file_discovery_method': helper_data.get('discovery_method'),
                    'candidates_found': helper_data.get('candidates_found', 0),
                    'quick_validation_result': helper_data.get('validation_result', {})
                }

            # Raw input metadata
            if 'raw_input' in pipeline_data:
                raw_data = pipeline_data['raw_input']
                metadata['raw_input'] = {
                    'input_type': type(raw_data).__name__,
                    'input_size': len(str(raw_data)) if raw_data else 0,
                    'is_list': isinstance(raw_data, list),
                    'list_length': len(raw_data) if isinstance(raw_data, list) else 0
                }

            # Processing timestamps
            metadata['processing_timestamps'] = {
                'pipeline_start': pipeline_data.get('start_timestamp'),
                'pipeline_end': pipeline_data.get('end_timestamp'),
                'total_processing_time_ms': pipeline_data.get('processing_time_ms', 0)
            }

        except Exception as e:
            logger.warning(f"Failed to extract pipeline metadata: {e}")
            metadata['extraction_error'] = str(e)

        return metadata

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about storage location and statistics."""
        
        try:
            predictions_count = len(self._load_predictions())

            return {
                'storage_dir': str(self.storage_dir),
                'predictions_file': str(self.predictions_file),
                'total_predictions': predictions_count,
                'predictions_with_outcomes': len(self.get_predictions_with_outcomes()),
                'recent_predictions': len(self.get_predictions_for_analysis(days=7))
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {}

"""
Pipeline Data Collector for unified data capture across the ARC-Eval pipeline.

Collects data from:
- input_detector.py: Framework detection and validation
- input_helpers.py: File discovery and input processing  
- parser_registry.py: Framework-specific parsing and extraction
- reliability_validator.py: Analysis and prediction results

Ensures unified data points for prediction tracking and accuracy measurement.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class PipelineDataCollector:
    """Collect unified data points across the entire ARC-Eval pipeline."""
    
    def __init__(self):
        """Initialize pipeline data collector."""
        self.pipeline_data = {
            'start_timestamp': datetime.now().isoformat(),
            'input_detection': {},
            'input_helpers': {},
            'parser_registry': {},
            'reliability_analysis': {},
            'raw_input': None,
            'processing_stages': []
        }
    
    def record_input_detection(self, detected_framework: Optional[str], 
                             confidence: float, file_info: Dict[str, Any]) -> None:
        """Record data from input_detector.py stage."""
        
        try:
            self.pipeline_data['input_detection'] = {
                'detected_framework': detected_framework,
                'confidence': confidence,
                'file_size_mb': file_info.get('size_mb', 0.0),
                'entry_count': file_info.get('entries', 0),
                'validation_issues': file_info.get('issues', []),
                'timestamp': datetime.now().isoformat()
            }
            
            self.pipeline_data['processing_stages'].append('input_detection')
            logger.debug(f"Recorded input detection: {detected_framework} (confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.warning(f"Failed to record input detection data: {e}")
    
    def record_input_helpers(self, input_source: str, discovery_method: Optional[str],
                           candidates_found: int, validation_result: Dict[str, Any]) -> None:
        """Record data from input_helpers.py stage."""
        
        try:
            self.pipeline_data['input_helpers'] = {
                'input_source': input_source,  # 'file', 'clipboard', 'scan'
                'discovery_method': discovery_method,
                'candidates_found': candidates_found,
                'validation_result': validation_result,
                'timestamp': datetime.now().isoformat()
            }
            
            self.pipeline_data['processing_stages'].append('input_helpers')
            logger.debug(f"Recorded input helpers: {input_source} source, {candidates_found} candidates")
            
        except Exception as e:
            logger.warning(f"Failed to record input helpers data: {e}")
    
    def record_parser_registry(self, framework_detected: Optional[str], 
                             extraction_method: str, extracted_output: str,
                             tool_calls_extracted: List[str], parsing_errors: List[str]) -> None:
        """Record data from parser_registry.py stage."""
        
        try:
            self.pipeline_data['parser_registry'] = {
                'framework_detected': framework_detected,
                'extraction_method': extraction_method,
                'extracted_output': extracted_output[:1000],  # Truncate for storage
                'tool_calls_extracted': tool_calls_extracted,
                'output_text_length': len(extracted_output),
                'tool_count': len(tool_calls_extracted),
                'parsing_errors': parsing_errors,
                'timestamp': datetime.now().isoformat()
            }
            
            self.pipeline_data['processing_stages'].append('parser_registry')
            logger.debug(f"Recorded parser registry: {framework_detected}, {len(tool_calls_extracted)} tools")
            
        except Exception as e:
            logger.warning(f"Failed to record parser registry data: {e}")
    
    def record_raw_input(self, raw_input: Any) -> None:
        """Record raw input data for analysis."""
        
        try:
            # Store metadata about raw input without storing the full content
            self.pipeline_data['raw_input'] = {
                'input_type': type(raw_input).__name__,
                'input_size': len(str(raw_input)) if raw_input else 0,
                'is_list': isinstance(raw_input, list),
                'list_length': len(raw_input) if isinstance(raw_input, list) else 0,
                'has_content': bool(raw_input),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f"Recorded raw input: {type(raw_input).__name__}, size: {len(str(raw_input))}")
            
        except Exception as e:
            logger.warning(f"Failed to record raw input data: {e}")
    
    def record_reliability_analysis(self, analysis_result: Any) -> None:
        """Record data from reliability_validator.py stage."""
        
        try:
            # Extract key metrics from analysis result
            if hasattr(analysis_result, 'detected_framework'):
                framework = analysis_result.detected_framework
                confidence = getattr(analysis_result, 'framework_confidence', 0.0)
                sample_size = getattr(analysis_result, 'sample_size', 0)
                
                self.pipeline_data['reliability_analysis'] = {
                    'detected_framework': framework,
                    'framework_confidence': confidence,
                    'sample_size': sample_size,
                    'auto_detection_successful': getattr(analysis_result, 'auto_detection_successful', False),
                    'analysis_confidence': getattr(analysis_result, 'analysis_confidence', 0.0),
                    'evidence_quality': getattr(analysis_result, 'evidence_quality', 'unknown'),
                    'has_prediction': hasattr(analysis_result, 'reliability_prediction') and 
                                    analysis_result.reliability_prediction is not None,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Handle dictionary format
                self.pipeline_data['reliability_analysis'] = {
                    'analysis_type': type(analysis_result).__name__,
                    'has_data': bool(analysis_result),
                    'timestamp': datetime.now().isoformat()
                }
            
            self.pipeline_data['processing_stages'].append('reliability_analysis')
            logger.debug("Recorded reliability analysis data")
            
        except Exception as e:
            logger.warning(f"Failed to record reliability analysis data: {e}")
    
    def finalize_collection(self) -> Dict[str, Any]:
        """Finalize data collection and return complete pipeline data."""
        
        try:
            self.pipeline_data['end_timestamp'] = datetime.now().isoformat()
            
            # Calculate processing time
            start_time = datetime.fromisoformat(self.pipeline_data['start_timestamp'])
            end_time = datetime.fromisoformat(self.pipeline_data['end_timestamp'])
            processing_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            self.pipeline_data['processing_time_ms'] = processing_time
            self.pipeline_data['stages_completed'] = len(self.pipeline_data['processing_stages'])
            
            logger.info(f"Pipeline data collection completed: {len(self.pipeline_data['processing_stages'])} stages, {processing_time:.1f}ms")
            
            return self.pipeline_data.copy()
            
        except Exception as e:
            logger.error(f"Failed to finalize pipeline data collection: {e}")
            return self.pipeline_data.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of collected pipeline data."""
        
        try:
            summary = {
                'stages_completed': len(self.pipeline_data['processing_stages']),
                'processing_stages': self.pipeline_data['processing_stages'],
                'frameworks_detected': [],
                'total_processing_time_ms': self.pipeline_data.get('processing_time_ms', 0),
                'data_quality_indicators': {}
            }
            
            # Collect framework detections
            for stage in ['input_detection', 'parser_registry', 'reliability_analysis']:
                if stage in self.pipeline_data:
                    framework = self.pipeline_data[stage].get('detected_framework') or \
                              self.pipeline_data[stage].get('framework_detected')
                    if framework:
                        summary['frameworks_detected'].append(f"{stage}: {framework}")
            
            # Data quality indicators
            if 'input_detection' in self.pipeline_data:
                input_data = self.pipeline_data['input_detection']
                summary['data_quality_indicators']['input_validation_issues'] = len(input_data.get('validation_issues', []))
                summary['data_quality_indicators']['input_confidence'] = input_data.get('confidence', 0.0)
            
            if 'parser_registry' in self.pipeline_data:
                parser_data = self.pipeline_data['parser_registry']
                summary['data_quality_indicators']['parsing_errors'] = len(parser_data.get('parsing_errors', []))
                summary['data_quality_indicators']['tools_extracted'] = parser_data.get('tool_count', 0)
            
            if 'reliability_analysis' in self.pipeline_data:
                analysis_data = self.pipeline_data['reliability_analysis']
                summary['data_quality_indicators']['analysis_confidence'] = analysis_data.get('analysis_confidence', 0.0)
                summary['data_quality_indicators']['has_prediction'] = analysis_data.get('has_prediction', False)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate pipeline data summary: {e}")
            return {'error': str(e)}


def create_pipeline_collector() -> PipelineDataCollector:
    """Factory function to create a new pipeline data collector."""
    return PipelineDataCollector()


def integrate_with_input_detector(detector_result: Dict[str, Any], 
                                collector: PipelineDataCollector) -> None:
    """Helper to integrate input_detector.py results with pipeline collector."""
    
    try:
        # Extract framework detection results
        framework = detector_result.get('framework')
        confidence = detector_result.get('confidence', 0.0)
        
        # Extract file information
        file_info = {
            'size_mb': detector_result.get('file_size_mb', 0.0),
            'entries': detector_result.get('entry_count', 0),
            'issues': detector_result.get('validation_issues', [])
        }
        
        collector.record_input_detection(framework, confidence, file_info)
        
    except Exception as e:
        logger.warning(f"Failed to integrate input detector results: {e}")


def integrate_with_parser_registry(parser_result: Dict[str, Any],
                                 collector: PipelineDataCollector) -> None:
    """Helper to integrate parser_registry.py results with pipeline collector."""
    
    try:
        framework = parser_result.get('framework')
        extraction_method = parser_result.get('extraction_method', 'unknown')
        extracted_output = parser_result.get('extracted_output', '')
        tool_calls = parser_result.get('tool_calls', [])
        errors = parser_result.get('errors', [])
        
        collector.record_parser_registry(
            framework, extraction_method, extracted_output, tool_calls, errors
        )
        
    except Exception as e:
        logger.warning(f"Failed to integrate parser registry results: {e}")


def integrate_with_input_helpers(helper_result: Dict[str, Any],
                               collector: PipelineDataCollector) -> None:
    """Helper to integrate input_helpers.py results with pipeline collector."""
    
    try:
        input_source = helper_result.get('input_source', 'unknown')
        discovery_method = helper_result.get('discovery_method')
        candidates_found = helper_result.get('candidates_found', 0)
        validation_result = helper_result.get('validation_result', {})
        
        collector.record_input_helpers(
            input_source, discovery_method, candidates_found, validation_result
        )
        
    except Exception as e:
        logger.warning(f"Failed to integrate input helpers results: {e}")

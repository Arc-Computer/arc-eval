"""
Automatic outcome detection from agent trace data.

Analyzes agent outputs to determine success/failure outcomes for prediction accuracy tracking.
Uses pattern matching and heuristics to detect:
- Task completion success/failure
- Error patterns and failure modes
- Performance degradation indicators
"""

import logging
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OutcomeDetector:
    """Automatically detect success/failure outcomes from agent trace data."""
    
    def __init__(self):
        """Initialize outcome detector with pattern matching rules."""
        
        # Success indicators
        self.success_patterns = [
            r'task\s+completed?\s+successfully',
            r'operation\s+successful',
            r'successfully\s+processed',
            r'completed\s+without\s+errors?',
            r'task\s+finished',
            r'execution\s+successful',
            r'result:\s*success',
            r'status:\s*success',
            r'✅',  # Success emoji
            r'done\s*[.!]',
            r'finished\s+successfully'
        ]
        
        # Failure indicators
        self.failure_patterns = [
            r'error\s*:',
            r'exception\s*:',
            r'failed\s+to',
            r'could\s+not',
            r'unable\s+to',
            r'timeout\s+exceeded',
            r'connection\s+failed',
            r'authentication\s+failed',
            r'permission\s+denied',
            r'invalid\s+response',
            r'task\s+failed',
            r'execution\s+failed',
            r'result:\s*fail',
            r'status:\s*fail',
            r'❌',  # Failure emoji
            r'aborted',
            r'cancelled'
        ]
        
        # Warning indicators (potential issues)
        self.warning_patterns = [
            r'warning\s*:',
            r'deprecated',
            r'retry\s+attempt',
            r'fallback\s+to',
            r'partial\s+success',
            r'some\s+errors?',
            r'⚠️',  # Warning emoji
            r'rate\s+limit',
            r'quota\s+exceeded'
        ]
        
        # Tool call failure patterns
        self.tool_failure_patterns = [
            r'tool\s+call\s+failed',
            r'invalid\s+tool\s+parameters?',
            r'tool\s+not\s+found',
            r'schema\s+validation\s+failed',
            r'parameter\s+missing',
            r'tool\s+timeout'
        ]
        
        # Compile patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        
        self.success_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.success_patterns]
        self.failure_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.failure_patterns]
        self.warning_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.warning_patterns]
        self.tool_failure_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.tool_failure_patterns]
    
    def detect_outcome(self, agent_outputs: List[Any]) -> Tuple[str, float, List[str]]:
        """
        Detect outcome from agent outputs.
        
        Returns:
            Tuple of (outcome, confidence, evidence)
            - outcome: 'success', 'failure', or 'partial'
            - confidence: 0.0-1.0 confidence in the detection
            - evidence: List of evidence strings supporting the outcome
        """
        
        try:
            # Combine all outputs into text for analysis
            combined_text = self._extract_text_from_outputs(agent_outputs)
            
            # Count pattern matches
            success_matches = self._count_pattern_matches(combined_text, self.success_regex)
            failure_matches = self._count_pattern_matches(combined_text, self.failure_regex)
            warning_matches = self._count_pattern_matches(combined_text, self.warning_regex)
            tool_failure_matches = self._count_pattern_matches(combined_text, self.tool_failure_regex)
            
            # Collect evidence
            evidence = []
            evidence.extend(success_matches['evidence'])
            evidence.extend(failure_matches['evidence'])
            evidence.extend(warning_matches['evidence'])
            evidence.extend(tool_failure_matches['evidence'])
            
            # Calculate scores
            success_score = success_matches['count']
            failure_score = failure_matches['count'] + tool_failure_matches['count'] * 2  # Tool failures are more serious
            warning_score = warning_matches['count']
            
            # Determine outcome and confidence
            outcome, confidence = self._determine_outcome(
                success_score, failure_score, warning_score, len(agent_outputs)
            )
            
            logger.info(f"Detected outcome: {outcome} (confidence: {confidence:.2f}, evidence: {len(evidence)} items)")
            return outcome, confidence, evidence[:10]  # Limit evidence to top 10
            
        except Exception as e:
            logger.error(f"Failed to detect outcome: {e}")
            return 'unknown', 0.0, [f"Detection error: {str(e)}"]
    
    def detect_outcome_for_prediction(self, prediction_id: str, agent_outputs: List[Any]) -> Dict[str, Any]:
        """
        Detect outcome specifically for a prediction.
        
        Returns detailed outcome information for prediction tracking.
        """
        
        outcome, confidence, evidence = self.detect_outcome(agent_outputs)
        
        return {
            'prediction_id': prediction_id,
            'outcome': outcome,
            'confidence': confidence,
            'evidence': evidence,
            'detection_timestamp': datetime.now().isoformat(),
            'sample_size': len(agent_outputs),
            'detection_method': 'pattern_matching'
        }
    
    def _extract_text_from_outputs(self, agent_outputs: List[Any]) -> str:
        """Extract text content from various agent output formats."""
        
        text_parts = []
        
        for output in agent_outputs:
            try:
                if isinstance(output, str):
                    text_parts.append(output)
                elif isinstance(output, dict):
                    # Extract common text fields
                    for field in ['response', 'output', 'content', 'message', 'result', 'text']:
                        if field in output and output[field]:
                            text_parts.append(str(output[field]))
                    
                    # Extract error information
                    for field in ['error', 'exception', 'error_message']:
                        if field in output and output[field]:
                            text_parts.append(str(output[field]))
                    
                    # Extract tool call information
                    if 'tool_calls' in output:
                        for tool_call in output['tool_calls']:
                            if isinstance(tool_call, dict):
                                text_parts.append(str(tool_call))
                
                else:
                    # Convert other types to string
                    text_parts.append(str(output))
                    
            except Exception as e:
                logger.warning(f"Failed to extract text from output: {e}")
                continue
        
        return ' '.join(text_parts)
    
    def _count_pattern_matches(self, text: str, regex_patterns: List[re.Pattern]) -> Dict[str, Any]:
        """Count matches for a set of regex patterns."""
        
        matches = []
        for pattern in regex_patterns:
            found_matches = pattern.findall(text)
            matches.extend(found_matches)
        
        return {
            'count': len(matches),
            'evidence': matches[:5]  # Keep top 5 matches as evidence
        }
    
    def _determine_outcome(self, success_score: int, failure_score: int, 
                          warning_score: int, sample_size: int) -> Tuple[str, float]:
        """Determine final outcome and confidence based on scores."""
        
        # Calculate total signals
        total_signals = success_score + failure_score + warning_score
        
        # If no clear signals, assume success with low confidence
        if total_signals == 0:
            return 'success', 0.3
        
        # Calculate confidence based on signal strength and sample size
        base_confidence = min(total_signals / max(sample_size, 1), 1.0)
        
        # Determine outcome
        if failure_score > success_score:
            # More failure signals than success
            outcome = 'failure'
            confidence = base_confidence * 0.9  # High confidence in failure detection
        elif success_score > failure_score + warning_score:
            # Clear success signals
            outcome = 'success'
            confidence = base_confidence * 0.8  # Good confidence in success
        elif warning_score > 0 and success_score > 0:
            # Mixed signals with warnings
            outcome = 'partial'
            confidence = base_confidence * 0.6  # Moderate confidence
        else:
            # Unclear signals
            outcome = 'success'  # Default to success
            confidence = base_confidence * 0.4  # Low confidence
        
        # Ensure confidence is in valid range
        confidence = max(0.1, min(confidence, 1.0))
        
        return outcome, confidence
    
    def analyze_failure_patterns(self, agent_outputs: List[Any]) -> Dict[str, Any]:
        """Analyze specific failure patterns for detailed insights."""
        
        combined_text = self._extract_text_from_outputs(agent_outputs)
        
        # Specific failure analysis
        failure_types = {
            'timeout': len(re.findall(r'timeout|timed?\s+out', combined_text, re.IGNORECASE)),
            'authentication': len(re.findall(r'auth|permission|unauthorized', combined_text, re.IGNORECASE)),
            'network': len(re.findall(r'network|connection|connectivity', combined_text, re.IGNORECASE)),
            'tool_error': len(re.findall(r'tool.*error|invalid.*tool', combined_text, re.IGNORECASE)),
            'schema_error': len(re.findall(r'schema|validation|parameter', combined_text, re.IGNORECASE)),
            'rate_limit': len(re.findall(r'rate.*limit|quota|throttle', combined_text, re.IGNORECASE))
        }
        
        # Find dominant failure type
        dominant_failure = max(failure_types.items(), key=lambda x: x[1])
        
        return {
            'failure_types': failure_types,
            'dominant_failure_type': dominant_failure[0] if dominant_failure[1] > 0 else 'unknown',
            'total_failure_signals': sum(failure_types.values())
        }
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get statistics about the detection patterns."""
        
        return {
            'success_patterns': len(self.success_patterns),
            'failure_patterns': len(self.failure_patterns),
            'warning_patterns': len(self.warning_patterns),
            'tool_failure_patterns': len(self.tool_failure_patterns),
            'total_patterns': len(self.success_patterns) + len(self.failure_patterns) + 
                            len(self.warning_patterns) + len(self.tool_failure_patterns)
        }

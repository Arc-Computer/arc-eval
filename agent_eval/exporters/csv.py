"""
CSV exporter for evaluation results - data analysis friendly format.
"""

import csv
from datetime import datetime
from typing import List

from agent_eval.core.types import EvaluationResult


class CSVExporter:
    """Export evaluation results to CSV format for data analysis and automation."""
    
    def export(self, results: List[EvaluationResult], filename: str, domain: str) -> None:
        """
        Export evaluation results to CSV file.
        
        Args:
            results: List of evaluation results
            filename: Output filename
            domain: Domain being evaluated
        """
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'timestamp',
                'domain',
                'scenario_id',
                'scenario_name',
                'description',
                'severity',
                'compliance_frameworks',
                'test_type',
                'status',
                'passed',
                'confidence',
                'failure_reason',
                'remediation',
                'agent_output_preview'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            timestamp = datetime.now().isoformat()
            
            for result in results:
                # Truncate agent output for CSV readability
                agent_output_preview = ""
                if result.agent_output:
                    agent_output_preview = result.agent_output[:100].replace('\n', ' ').replace('\r', ' ')
                    if len(result.agent_output) > 100:
                        agent_output_preview += "..."
                
                writer.writerow({
                    'timestamp': timestamp,
                    'domain': domain,
                    'scenario_id': result.scenario_id,
                    'scenario_name': result.scenario_name,
                    'description': result.description,
                    'severity': result.severity,
                    'compliance_frameworks': '; '.join(result.compliance),
                    'test_type': result.test_type,
                    'status': result.status,
                    'passed': result.passed,
                    'confidence': result.confidence,
                    'failure_reason': result.failure_reason or '',
                    'remediation': result.remediation or '',
                    'agent_output_preview': agent_output_preview
                })
"""
CSV exporter for evaluation results - data analysis friendly format.
"""

import csv
from datetime import datetime
from typing import List

from agent_eval.core.types import EvaluationResult


class CSVExporter:
    """Export evaluation results to CSV format for data analysis and automation."""
    
    def export(self, results: List[EvaluationResult], filename: str, domain: str, format_template: str = None, summary_only: bool = False) -> None:
        """
        Export evaluation results to CSV file.
        
        Args:
            results: List of evaluation results
            filename: Output filename
            domain: Domain being evaluated
            format_template: Template for data formatting (executive, technical, compliance, minimal)
            summary_only: Export summary data only
        """
        # Handle None or invalid results gracefully
        if results is None:
            results = []
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Adjust fieldnames based on template and summary mode
            if summary_only:
                fieldnames = [
                    'timestamp',
                    'domain',
                    'format_template',
                    'total_scenarios',
                    'passed_scenarios',
                    'failed_scenarios',
                    'critical_failures',
                    'high_failures',
                    'pass_rate_percent',
                    'compliance_frameworks_affected'
                ]
            else:
                fieldnames = [
                    'timestamp',
                    'domain',
                    'format_template',
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
            
            if summary_only:
                # Write summary row
                total = len(results)
                passed = sum(1 for r in results if r.passed)
                failed = total - passed
                critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
                high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                compliance_frameworks = set()
                for result in results:
                    compliance_frameworks.update(result.compliance)
                
                writer.writerow({
                    'timestamp': timestamp,
                    'domain': domain,
                    'format_template': format_template or 'standard',
                    'total_scenarios': total,
                    'passed_scenarios': passed,
                    'failed_scenarios': failed,
                    'critical_failures': critical_failures,
                    'high_failures': high_failures,
                    'pass_rate_percent': f"{pass_rate:.1f}",
                    'compliance_frameworks_affected': '; '.join(sorted(compliance_frameworks))
                })
            else:
                # Write detailed rows
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
                        'format_template': format_template or 'standard',
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
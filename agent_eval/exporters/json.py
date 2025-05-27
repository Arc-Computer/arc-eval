"""
JSON exporter for evaluation results - API and integration friendly format.
"""

import json
from datetime import datetime
from typing import List

from agent_eval.core.types import EvaluationResult


class JSONExporter:
    """Export evaluation results to JSON format for APIs and integrations."""
    
    def export(self, results: List[EvaluationResult], filename: str, domain: str, format_template: str = None, summary_only: bool = False) -> None:
        """
        Export evaluation results to JSON file.
        
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
            
        export_data = [r.to_dict() for r in results]
        
        if summary_only:
            # For summary-only, include just key metrics
            timestamp = datetime.now().isoformat()
            summary = {
                "summary": {
                    "total_scenarios": len(results),
                    "passed": sum(1 for r in results if r.passed),
                    "failed": sum(1 for r in results if not r.passed),
                    "critical_failures": sum(1 for r in results if r.severity == "critical" and not r.passed),
                    "compliance_frameworks": list(set().union(*[r.compliance for r in results])),
                    "timestamp": timestamp,
                    "format_template": format_template,
                    "domain": domain
                },
                "detailed_results": export_data
            }
            export_data = summary
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
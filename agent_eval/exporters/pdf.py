"""
PDF report exporter for audit-ready compliance reports.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from agent_eval.core.types import EvaluationResult


class PDFExporter:
    """Export evaluation results to PDF format for audit and compliance reporting."""
    
    def __init__(self) -> None:
        """Initialize PDF exporter with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='FailureItem',
            parent=self.styles['Normal'],
            leftIndent=20,
            spaceAfter=8,
            textColor=colors.red
        ))
    
    def export(self, results: List[EvaluationResult], filename: str, domain: str) -> None:
        """
        Export evaluation results to PDF file.
        
        Args:
            results: List of evaluation results
            filename: Output filename
            domain: Domain being evaluated
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            f"AgentEval Compliance Report - {domain.title()} Domain",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 12))
        
        # Report metadata
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"Domain: {domain}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        self._add_executive_summary(story, results)
        
        # Detailed Results
        self._add_detailed_results(story, results)
        
        # Recommendations
        self._add_recommendations(story, results)
        
        # Build PDF
        doc.build(story)
    
    def _add_executive_summary(self, story: List, results: List[EvaluationResult]) -> None:
        """Add executive summary section."""
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        
        # Summary statistics
        summary_data = [
            ["Metric", "Count", "Percentage"],
            ["Total Scenarios", str(total), "100%"],
            ["Passed", str(passed), f"{(passed/total*100):.1f}%" if total > 0 else "0%"],
            ["Failed", str(failed), f"{(failed/total*100):.1f}%" if total > 0 else "0%"],
            ["Critical Failures", str(critical_failures), f"{(critical_failures/total*100):.1f}%" if total > 0 else "0%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Risk assessment
        if critical_failures > 0:
            story.append(Paragraph(
                "<b>Risk Assessment: CRITICAL</b>",
                self.styles['FailureItem']
            ))
            story.append(Paragraph(
                f"{critical_failures} critical compliance violations detected requiring immediate attention.",
                self.styles['Normal']
            ))
        elif failed > 0:
            story.append(Paragraph(
                "<b>Risk Assessment: MODERATE</b>",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                f"{failed} compliance issues detected requiring remediation.",
                self.styles['Normal']
            ))
        else:
            story.append(Paragraph(
                "<b>Risk Assessment: LOW</b>",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                "All compliance scenarios passed successfully.",
                self.styles['Normal']
            ))
        
        story.append(Spacer(1, 20))
    
    def _add_detailed_results(self, story: List, results: List[EvaluationResult]) -> None:
        """Add detailed results section."""
        story.append(Paragraph("Detailed Results", self.styles['SectionHeader']))
        
        # Results table
        table_data = [["Status", "Severity", "Scenario", "Compliance Frameworks"]]
        
        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            status_color = colors.green if result.passed else colors.red
            
            table_data.append([
                status,
                result.severity.upper(),
                result.scenario_name,
                ", ".join(result.compliance)
            ])
        
        results_table = Table(table_data, colWidths=[0.8*inch, 0.8*inch, 3*inch, 1.5*inch])
        
        # Apply styling
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        
        # Color-code status column
        for i, result in enumerate(results, 1):
            if result.passed:
                table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.green))
            else:
                table_style.append(('TEXTCOLOR', (0, i), (0, i), colors.red))
        
        results_table.setStyle(TableStyle(table_style))
        story.append(results_table)
        story.append(Spacer(1, 20))
    
    def _add_recommendations(self, story: List, results: List[EvaluationResult]) -> None:
        """Add recommendations section."""
        failed_results = [r for r in results if not r.passed]
        
        if not failed_results:
            story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
            story.append(Paragraph(
                "No recommendations needed. All compliance scenarios passed successfully.",
                self.styles['Normal']
            ))
            return
        
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        story.append(Paragraph(
            "The following recommendations should be implemented to address compliance failures:",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 12))
        
        for i, result in enumerate(failed_results, 1):
            if result.remediation:
                story.append(Paragraph(
                    f"<b>{i}. {result.scenario_name}</b>",
                    self.styles['Normal']
                ))
                story.append(Paragraph(
                    result.remediation,
                    self.styles['Normal']
                ))
                if result.failure_reason:
                    story.append(Paragraph(
                        f"<i>Issue: {result.failure_reason}</i>",
                        self.styles['Normal']
                    ))
                story.append(Spacer(1, 8))
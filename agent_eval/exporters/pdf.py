"""
PDF report exporter for audit-ready compliance reports.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF

from agent_eval.core.types import EvaluationResult


class PDFExporter:
    """Export evaluation results to PDF format for audit and compliance reporting."""
    
    def __init__(self) -> None:
        """Initialize PDF exporter with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the report."""
        # Main title style with ARC-Eval branding
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#FF6B35'),  # ARC orange
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E3440'),  # Professional dark
            fontName='Helvetica'
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            spaceBefore=10,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#2E3440'),
            leading=14
        ))
        
        # Section headers with professional styling
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#FF6B35'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#FF6B35'),
            borderPadding=8,
            backColor=colors.HexColor('#FFF8F5')
        ))
        
        # Risk indicators
        self.styles.add(ParagraphStyle(
            name='CriticalRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#DC2626'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#FEF2F2'),
            borderWidth=1,
            borderColor=colors.HexColor('#DC2626'),
            borderPadding=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='ModerateRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#D97706'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#FFFBEB'),
            borderWidth=1,
            borderColor=colors.HexColor('#D97706'),
            borderPadding=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#F0FDF4'),
            borderWidth=1,
            borderColor=colors.HexColor('#059669'),
            borderPadding=8
        ))
        
        # Recommendation items
        self.styles.add(ParagraphStyle(
            name='RecommendationTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=5,
            textColor=colors.HexColor('#1F2937'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RecommendationText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            textColor=colors.HexColor('#374151'),
            leading=13
        ))
    
    def export(self, results: List[EvaluationResult], filename: str, domain: str, format_template: str = None, summary_only: bool = False) -> None:
        """
        Export evaluation results to PDF file.
        
        Args:
            results: List of evaluation results
            filename: Output filename
            domain: Domain being evaluated
            format_template: Template for report formatting (executive, technical, compliance, minimal)
            summary_only: Generate executive summary only
        """
        # Handle None or invalid results gracefully
        if results is None:
            results = []
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Header with branding
        self._add_header(story, domain, format_template)
        
        # Report metadata in professional format
        report_type = self._get_report_type(format_template, summary_only)
        metadata_table = Table([
            ["Report Generated:", datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ["Evaluation Domain:", f"{domain.title()} Compliance Framework"],
            ["Report Type:", report_type],
            ["Format Template:", format_template or "Standard"],
            ["ARC-Eval Version:", "v2.0.0"]
        ], colWidths=[2*inch, 4*inch])
        
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#6B7280')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 30))
        
        # Executive Summary
        self._add_executive_summary(story, results, format_template)
        
        # Only add detailed sections if not summary-only
        if not summary_only:
            # Detailed Results
            self._add_detailed_results(story, results, format_template)
            
            # Recommendations
            self._add_recommendations(story, results, format_template)
        else:
            # Add note about summary-only mode
            story.append(Paragraph(
                "📋 Executive Summary Report - Detailed scenarios available in full report format.",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
    
    def _get_report_type(self, format_template: str, summary_only: bool) -> str:
        """Get report type based on template and summary mode."""
        if summary_only:
            return "Executive Summary"
        
        template_types = {
            "executive": "Executive Compliance Assessment", 
            "technical": "Technical Compliance Analysis",
            "compliance": "Regulatory Compliance Report",
            "minimal": "Compliance Summary"
        }
        return template_types.get(format_template, "Standard Compliance Assessment")
    
    def _add_header(self, story: List, domain: str, format_template: str = None) -> None:
        """Add professional header with ARC-Eval branding."""
        # Main title with ARC-Eval branding
        story.append(Paragraph(
            "ARC-EVAL",
            self.styles['CustomTitle']
        ))
        
        # Subtitle
        domain_titles = {
            "finance": "Financial Services Compliance Assessment",
            "security": "Cybersecurity & AI Agent Security Assessment", 
            "ml": "ML Infrastructure & Safety Assessment"
        }
        subtitle = domain_titles.get(domain, f"{domain.title()} Compliance Assessment")
        
        story.append(Paragraph(
            subtitle,
            self.styles['Subtitle']
        ))
        
        # Professional separator line
        separator_table = Table([["" for _ in range(10)]], colWidths=[0.6*inch]*10)
        separator_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#FF6B35')),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ]))
        story.append(separator_table)
        story.append(Spacer(1, 20))
    
    def _add_executive_summary(self, story: List, results: List[EvaluationResult], format_template: str = None) -> None:
        """Add executive summary section."""
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical_failures = sum(1 for r in results if r.severity == "critical" and not r.passed)
        high_failures = sum(1 for r in results if r.severity == "high" and not r.passed)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Professional summary metrics in dashboard format
        summary_data = [
            ["📊 COMPLIANCE METRICS", "COUNT", "PERCENTAGE", "STATUS"],
            ["Total Scenarios Evaluated", str(total), "100%", "✓ Complete"],
            ["Scenarios Passed", str(passed), f"{pass_rate:.1f}%", "✓ Compliant" if pass_rate >= 95 else "⚠ Review"],
            ["Scenarios Failed", str(failed), f"{(failed/total*100):.1f}%" if total > 0 else "0%", "❌ Non-Compliant" if failed > 0 else "✓ Compliant"],
            ["Critical Risk Scenarios", str(critical_failures), f"{(critical_failures/total*100):.1f}%" if total > 0 else "0%", "🔴 Immediate Action" if critical_failures > 0 else "✓ Acceptable"],
            ["High Risk Scenarios", str(high_failures), f"{(high_failures/total*100):.1f}%" if total > 0 else "0%", "🟡 Plan Remediation" if high_failures > 0 else "✓ Acceptable"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 1.7*inch])
        summary_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FAFAFA')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 25))
        
        # Enhanced risk assessment with visual indicators
        
        if critical_failures > 0:
            story.append(Paragraph(
                f"🔴 CRITICAL RISK ASSESSMENT: {critical_failures} critical compliance violations detected requiring immediate executive attention and remediation.",
                self.styles['CriticalRisk']
            ))
            story.append(Paragraph(
                "RECOMMENDED ACTION: Immediate risk mitigation required. Escalate to compliance team and suspend affected operations until remediation is complete.",
                self.styles['ExecutiveSummary']
            ))
        elif failed > 0:
            story.append(Paragraph(
                f"🟡 MODERATE RISK ASSESSMENT: {failed} compliance issues identified requiring planned remediation within defined timeframes.",
                self.styles['ModerateRisk']
            ))
            story.append(Paragraph(
                "RECOMMENDED ACTION: Develop remediation plan with timeline. Monitor affected operations and implement corrective measures.",
                self.styles['ExecutiveSummary']
            ))
        else:
            story.append(Paragraph(
                f"🟢 LOW RISK ASSESSMENT: All {total} compliance scenarios passed successfully. System demonstrates adherence to regulatory requirements.",
                self.styles['LowRisk']
            ))
            story.append(Paragraph(
                "RECOMMENDED ACTION: Maintain current compliance posture. Continue regular monitoring and assessment cycles.",
                self.styles['ExecutiveSummary']
            ))
        
        # Compliance frameworks affected
        if failed > 0:
            affected_frameworks = set()
            for result in results:
                if not result.passed:
                    affected_frameworks.update(result.compliance)
            
            if affected_frameworks:
                story.append(Spacer(1, 15))
                story.append(Paragraph(
                    f"<b>Regulatory Frameworks Affected:</b> {', '.join(sorted(affected_frameworks))}",
                    self.styles['ExecutiveSummary']
                ))
        
        story.append(Spacer(1, 25))
    
    def _add_detailed_results(self, story: List, results: List[EvaluationResult], format_template: str = None) -> None:
        """Add detailed results section."""
        story.append(Paragraph("Detailed Results", self.styles['SectionHeader']))
        
        # Results table
        table_data = [["Status", "Severity", "Scenario", "Compliance Frameworks"]]
        
        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            
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
    
    def _add_recommendations(self, story: List, results: List[EvaluationResult], format_template: str = None) -> None:
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
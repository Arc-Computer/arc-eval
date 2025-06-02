"""
Specialized rendering for reliability prediction results.

Provides high-impact, high-signal visualization of prediction data with:
- Color-coded risk level displays
- Business impact metrics
- Compliance violation highlights
- Actionable recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree
from rich import box

logger = logging.getLogger(__name__)


class PredictionRenderer:
    """Specialized rendering for prediction results with high-impact visualization."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize prediction renderer."""
        self.console = console or Console()
    
    def render_prediction_summary(self, prediction: Dict[str, Any]) -> None:
        """Render prominent prediction summary with risk level banner."""
        
        if not prediction:
            return
        
        risk_level = prediction.get('risk_level', 'UNKNOWN')
        risk_score = prediction.get('combined_risk_score', 0.0)
        confidence = prediction.get('confidence', 0.0)
        prediction_id = prediction.get('prediction_id', 'unknown')
        
        # Create risk level banner with color coding
        banner_text = Text()
        banner_text.append("🎯 RELIABILITY PREDICTION\n\n", style="bold white")
        
        # Risk level with prominent color coding
        risk_color, risk_emoji = self._get_risk_styling(risk_level)
        banner_text.append(f"{risk_emoji} RISK LEVEL: ", style="bold white")
        banner_text.append(f"{risk_level}", style=f"bold {risk_color}")
        banner_text.append(f" ({risk_score:.2f})\n", style="white")
        
        # Confidence indicator
        conf_color = "green" if confidence > 0.8 else "yellow" if confidence > 0.6 else "red"
        banner_text.append(f"🎯 Confidence: ", style="bold white")
        banner_text.append(f"{confidence:.1%}", style=f"bold {conf_color}")
        banner_text.append(f" • ID: {prediction_id[:8]}...\n", style="dim")
        
        # Business impact preview
        business_impact = prediction.get('business_impact', {})
        if business_impact:
            prevention_pct = business_impact.get('failure_prevention_percentage', 0)
            banner_text.append(f"💼 Impact: ", style="bold white")
            banner_text.append(f"Prevents {prevention_pct}% of production failures", style="bold cyan")
        
        # Create prominent banner
        banner_panel = Panel(
            banner_text,
            title=f"[bold {risk_color}]🚨 RELIABILITY ASSESSMENT 🚨[/bold {risk_color}]",
            border_style=risk_color,
            padding=(1, 2)
        )
        
        self.console.print(banner_panel)
    
    def render_risk_factors(self, prediction: Dict[str, Any]) -> None:
        """Render top risk factors with clear prioritization."""
        
        risk_factors = prediction.get('top_risk_factors', [])
        if not risk_factors:
            return
        
        # Create risk factors table
        risk_table = Table(title="🔍 Top Risk Factors", box=box.ROUNDED)
        risk_table.add_column("Priority", justify="center", width=8)
        risk_table.add_column("Risk Factor", style="white", width=50)
        risk_table.add_column("Impact", style="yellow", width=20)
        
        # Add top 5 risk factors
        for i, factor in enumerate(risk_factors[:5], 1):
            priority_icon = "🔴" if i <= 2 else "🟡" if i <= 4 else "🟢"
            impact_level = "Critical" if i <= 2 else "High" if i <= 4 else "Medium"
            
            risk_table.add_row(
                f"{priority_icon} #{i}",
                str(factor),
                impact_level
            )
        
        self.console.print(risk_table)
    
    def render_compliance_violations(self, prediction: Dict[str, Any]) -> None:
        """Render compliance violations with regulatory context."""
        
        rule_component = prediction.get('rule_based_component', {})
        violations = rule_component.get('violations', [])
        
        if not violations:
            # Show compliance success
            success_text = Text()
            success_text.append("✅ No Critical Compliance Violations Detected\n", style="bold green")
            success_text.append("All major regulatory frameworks appear compliant", style="green")
            
            compliance_panel = Panel(
                success_text,
                title="[bold green]🛡️ Compliance Status[/bold green]",
                border_style="green"
            )
            self.console.print(compliance_panel)
            return
        
        # Create violations table
        violations_table = Table(title="🚨 Compliance Violations", box=box.ROUNDED)
        violations_table.add_column("Severity", justify="center", width=10)
        violations_table.add_column("Framework", style="cyan", width=15)
        violations_table.add_column("Violation", style="red", width=40)
        violations_table.add_column("Citation", style="dim", width=15)
        
        # Sort violations by severity
        sorted_violations = sorted(violations, key=lambda x: x.get('severity', 'medium'), reverse=True)
        
        for violation in sorted_violations[:10]:  # Show top 10
            severity = violation.get('severity', 'medium')
            severity_icon = "🔴" if severity == 'critical' else "🟡" if severity == 'high' else "🟠"
            
            violations_table.add_row(
                f"{severity_icon} {severity.upper()}",
                violation.get('framework', 'Unknown'),
                violation.get('description', 'No description'),
                violation.get('rule_id', 'N/A')
            )
        
        self.console.print(violations_table)
        
        # Show regulatory context
        self._render_regulatory_context(violations)
    
    def render_business_impact(self, prediction: Dict[str, Any]) -> None:
        """Render business impact metrics with clear value proposition."""
        
        business_impact = prediction.get('business_impact', {})
        if not business_impact:
            return
        
        # Create business impact metrics
        impact_table = Table(title="💼 Business Impact Analysis", box=box.ROUNDED)
        impact_table.add_column("Metric", style="cyan", width=30)
        impact_table.add_column("Value", justify="center", width=20)
        impact_table.add_column("Significance", style="green", width=30)
        
        # Failure prevention
        prevention_pct = business_impact.get('failure_prevention_percentage', 0)
        if prevention_pct > 0:
            impact_table.add_row(
                "Failure Prevention",
                f"{prevention_pct}%",
                "Reduces production incidents"
            )
        
        # Time savings
        time_saved = business_impact.get('estimated_time_saved_hours', 0)
        if time_saved > 0:
            impact_table.add_row(
                "Time Savings",
                f"{time_saved:.1f} hours",
                "Per incident resolution"
            )
        
        # Cost impact
        cost_savings = business_impact.get('estimated_cost_savings', 0)
        if cost_savings > 0:
            impact_table.add_row(
                "Cost Savings",
                f"${cost_savings:,.0f}",
                "Annual estimated savings"
            )
        
        # Compliance risk reduction
        compliance_risk = business_impact.get('compliance_risk_reduction', 0)
        if compliance_risk > 0:
            impact_table.add_row(
                "Compliance Risk Reduction",
                f"{compliance_risk}%",
                "Regulatory violation prevention"
            )
        
        self.console.print(impact_table)
    
    def render_recommendations(self, prediction: Dict[str, Any]) -> None:
        """Render actionable recommendations based on prediction."""
        
        recommendations = prediction.get('recommendations', [])
        if not recommendations:
            # Generate basic recommendations based on risk level
            risk_level = prediction.get('risk_level', 'UNKNOWN')
            recommendations = self._generate_default_recommendations(risk_level)
        
        if not recommendations:
            return
        
        # Split recommendations by category
        immediate_actions = []
        preventive_measures = []
        monitoring_steps = []
        
        for rec in recommendations:
            rec_str = str(rec)
            if any(word in rec_str.lower() for word in ['immediate', 'urgent', 'critical', 'fix']):
                immediate_actions.append(rec_str)
            elif any(word in rec_str.lower() for word in ['monitor', 'track', 'observe', 'watch']):
                monitoring_steps.append(rec_str)
            else:
                preventive_measures.append(rec_str)
        
        # Create recommendation panels
        panels = []
        
        if immediate_actions:
            immediate_text = "\n".join([f"• {action}" for action in immediate_actions[:3]])
            immediate_panel = Panel(
                immediate_text,
                title="[bold red]🚨 Immediate Actions[/bold red]",
                border_style="red"
            )
            panels.append(immediate_panel)
        
        if preventive_measures:
            preventive_text = "\n".join([f"• {measure}" for measure in preventive_measures[:3]])
            preventive_panel = Panel(
                preventive_text,
                title="[bold yellow]🛡️ Preventive Measures[/bold yellow]",
                border_style="yellow"
            )
            panels.append(preventive_panel)
        
        if monitoring_steps:
            monitoring_text = "\n".join([f"• {step}" for step in monitoring_steps[:3]])
            monitoring_panel = Panel(
                monitoring_text,
                title="[bold blue]📊 Monitoring[/bold blue]",
                border_style="blue"
            )
            panels.append(monitoring_panel)
        
        if panels:
            if len(panels) == 1:
                self.console.print(panels[0])
            else:
                columns = Columns(panels, equal=True)
                self.console.print(columns)
    
    def render_llm_rationale(self, prediction: Dict[str, Any], expandable: bool = True) -> None:
        """Render LLM rationale in expandable format."""
        
        llm_component = prediction.get('llm_component', {})
        rationale = llm_component.get('rationale', '')
        
        if not rationale:
            return
        
        # Truncate rationale for overview
        if expandable and len(rationale) > 200:
            preview = rationale[:200] + "..."
            rationale_text = Text()
            rationale_text.append(f"{preview}\n\n", style="white")
            rationale_text.append("💡 Full rationale available in detailed view", style="dim italic")
        else:
            rationale_text = Text(rationale, style="white")
        
        # Add LLM metadata
        llm_confidence = llm_component.get('confidence', 0.0)
        fallback_used = llm_component.get('fallback_used', False)
        
        if fallback_used:
            rationale_text.append("\n\n⚠️ Note: Fallback prediction used (LLM unavailable)", style="yellow")
        else:
            rationale_text.append(f"\n\n🤖 LLM Confidence: {llm_confidence:.1%}", style="dim")
        
        rationale_panel = Panel(
            rationale_text,
            title="[bold magenta]🧠 AI Analysis Rationale[/bold magenta]",
            border_style="magenta"
        )
        
        self.console.print(rationale_panel)
    
    def _get_risk_styling(self, risk_level: str) -> tuple:
        """Get color and emoji for risk level."""
        
        risk_styling = {
            'LOW': ('green', '🟢'),
            'MEDIUM': ('yellow', '🟡'),
            'HIGH': ('red', '🔴'),
            'UNKNOWN': ('dim', '⚪')
        }
        
        return risk_styling.get(risk_level.upper(), ('dim', '⚪'))
    
    def _render_regulatory_context(self, violations: List[Dict]) -> None:
        """Render regulatory context for violations."""
        
        # Group violations by framework
        frameworks = {}
        for violation in violations:
            framework = violation.get('framework', 'Unknown')
            if framework not in frameworks:
                frameworks[framework] = []
            frameworks[framework].append(violation)
        
        if not frameworks:
            return
        
        context_text = Text()
        context_text.append("📋 Regulatory Context:\n\n", style="bold cyan")
        
        framework_info = {
            'GDPR': 'EU General Data Protection Regulation - Privacy and data protection',
            'SOX': 'Sarbanes-Oxley Act - Financial reporting and audit requirements',
            'PCI_DSS': 'Payment Card Industry Data Security Standard - Payment data protection',
            'OWASP': 'Open Web Application Security Project - Security best practices'
        }
        
        for framework in frameworks.keys():
            info = framework_info.get(framework, 'Regulatory compliance framework')
            context_text.append(f"• {framework}: {info}\n", style="white")
        
        context_panel = Panel(
            context_text,
            title="[bold blue]📚 Compliance Frameworks[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(context_panel)
    
    def _generate_default_recommendations(self, risk_level: str) -> List[str]:
        """Generate default recommendations based on risk level."""
        
        recommendations = {
            'HIGH': [
                "Immediate review of agent configuration required",
                "Implement additional error handling and validation",
                "Consider framework migration for better reliability",
                "Add comprehensive monitoring and alerting"
            ],
            'MEDIUM': [
                "Review and optimize current implementation",
                "Add preventive monitoring for early detection",
                "Consider performance optimizations",
                "Implement gradual reliability improvements"
            ],
            'LOW': [
                "Continue current practices with regular monitoring",
                "Consider minor optimizations for efficiency",
                "Maintain current reliability standards"
            ]
        }
        
        return recommendations.get(risk_level.upper(), [])

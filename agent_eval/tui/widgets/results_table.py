"""
Results Table Widget.

Displays evaluation results in a filterable, sortable table
with compliance summary and export functionality.
"""

from typing import Dict, List, Set

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Static, Select

from ...core.types import EvaluationResult


class ResultsTable(Container):
    """Interactive results table with filtering and analysis."""
    
    class ExportRequested(Message):
        """Message sent when export is requested."""
        def __init__(self, format: str):
            self.format = format
            super().__init__()
    
    class FilterChanged(Message):
        """Message sent when filter changes."""
        def __init__(self, filter_type: str):
            self.filter_type = filter_type
            super().__init__()
    
    def __init__(self, results: List[EvaluationResult] = None, **kwargs):
        super().__init__(**kwargs)
        self.results = results or []
        self.filtered_results = self.results.copy()
        self.current_filter = "all"
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("📊 Evaluation Results", classes="section-title")
            
            # Filter and export controls
            with Horizontal():
                yield Static("Filter:", classes="filter-label")
                yield Select(
                    [
                        ("All Results", "all"),
                        ("Failed Only", "failed"),
                        ("Critical Only", "critical"),
                        ("Passed Only", "passed")
                    ],
                    value="all",
                    id="results-filter"
                )
                yield Button("📄 Export PDF", id="export-pdf", variant="primary")
                yield Button("📊 Export CSV", id="export-csv", variant="secondary")
                yield Button("📋 Export JSON", id="export-json", variant="secondary")
            
            # Results table
            yield DataTable(id="results-data-table")
            
            # Compliance summary
            with Container():
                yield Static("Compliance Summary:", classes="section-title")
                yield Container(id="compliance-summary")
    
    def on_mount(self):
        """Initialize widget on mount."""
        self.setup_table()
        self.update_table()
        self.update_compliance_summary()
    
    def setup_table(self):
        """Set up the results table structure."""
        table = self.query_one("#results-data-table")
        table.add_columns(
            "Status",
            "Severity", 
            "Scenario ID",
            "Scenario Name",
            "Compliance",
            "Details"
        )
        table.zebra_stripes = True
        table.cursor_type = "row"
    
    def set_results(self, results: List[EvaluationResult]):
        """Update results and refresh display."""
        self.results = results
        self.apply_filter(self.current_filter)
        self.update_table()
        self.update_compliance_summary()
    
    @on(Select.Changed, "#results-filter")
    def handle_filter_change(self, event: Select.Changed):
        """Handle filter selection change."""
        if event.value:
            self.apply_filter(event.value)
            self.post_message(self.FilterChanged(event.value))
    
    @on(Button.Pressed, "#export-pdf")
    def handle_export_pdf(self):
        """Handle PDF export request."""
        self.post_message(self.ExportRequested("pdf"))
    
    @on(Button.Pressed, "#export-csv")
    def handle_export_csv(self):
        """Handle CSV export request."""
        self.post_message(self.ExportRequested("csv"))
    
    @on(Button.Pressed, "#export-json")
    def handle_export_json(self):
        """Handle JSON export request."""
        self.post_message(self.ExportRequested("json"))
    
    def apply_filter(self, filter_type: str):
        """Apply filter to results."""
        self.current_filter = filter_type
        
        if filter_type == "all":
            self.filtered_results = self.results.copy()
        elif filter_type == "failed":
            self.filtered_results = [r for r in self.results if not r.passed]
        elif filter_type == "critical":
            self.filtered_results = [r for r in self.results if r.severity == "critical" and not r.passed]
        elif filter_type == "passed":
            self.filtered_results = [r for r in self.results if r.passed]
        
        self.update_table()
    
    def update_table(self):
        """Update the results table with current filtered results."""
        table = self.query_one("#results-data-table")
        table.clear()
        
        if not self.filtered_results:
            table.add_row("No results", "", "", "", "", "")
            return
        
        for result in self.filtered_results:
            # Status with icon
            if result.passed:
                status = "✅ PASS"
                status_style = "status-passed"
            else:
                status = "❌ FAIL"
                status_style = "status-failed"
            
            # Severity with color coding
            severity = result.severity.upper()
            if result.severity == "critical":
                severity_display = f"🔴 {severity}"
            elif result.severity == "high":
                severity_display = f"🟡 {severity}"
            elif result.severity == "medium":
                severity_display = f"🔵 {severity}"
            else:
                severity_display = f"⚪ {severity}"
            
            # Truncate long names
            scenario_name = result.scenario_name
            if len(scenario_name) > 30:
                scenario_name = scenario_name[:27] + "..."
            
            # Compliance frameworks
            compliance = ", ".join(result.compliance)
            if len(compliance) > 20:
                compliance = compliance[:17] + "..."
            
            # Details (failure reason or status)
            details = result.failure_reason if result.failure_reason else "Passed"
            if len(details) > 40:
                details = details[:37] + "..."
            
            table.add_row(
                status,
                severity_display,
                result.scenario_id,
                scenario_name,
                compliance,
                details
            )
    
    def update_compliance_summary(self):
        """Update the compliance framework summary."""
        container = self.query_one("#compliance-summary")
        container.remove_children()
        
        if not self.results:
            container.mount(Static("No results to summarize"))
            return
        
        # Calculate compliance scores by framework
        framework_scores = self.calculate_framework_scores()
        
        # Calculate overall statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        critical = sum(1 for r in self.results if r.severity == "critical" and not r.passed)
        
        # Overall summary
        overall_score = (passed / total) * 100 if total > 0 else 0
        grade = self.calculate_grade(overall_score)
        
        with container:
            with Horizontal(classes="stats-row"):
                Static(f"📊 Total: {total}", classes="stat-item")
                Static(f"✅ Passed: {passed}", classes="stat-item")
                Static(f"❌ Failed: {failed}", classes="stat-item")
                Static(f"🔴 Critical: {critical}", classes="stat-item")
            
            Static(f"Overall Score: {grade} ({overall_score:.1f}%)", classes="overall-score")
            
            # Framework breakdown
            if framework_scores:
                Static("Framework Breakdown:", classes="framework-header")
                for framework, score_data in framework_scores.items():
                    score = score_data['score']
                    grade = self.calculate_grade(score)
                    
                    # Create progress bar representation
                    filled = int(score / 10)
                    empty = 10 - filled
                    progress_bar = "█" * filled + "░" * empty
                    
                    Static(
                        f"{framework}: {progress_bar} {score:.0f}% {grade}",
                        classes="framework-score"
                    )
    
    def calculate_framework_scores(self) -> Dict[str, Dict]:
        """Calculate compliance scores by framework."""
        framework_scores = {}
        
        for result in self.results:
            for framework in result.compliance:
                if framework not in framework_scores:
                    framework_scores[framework] = {'total': 0, 'passed': 0}
                
                framework_scores[framework]['total'] += 1
                if result.passed:
                    framework_scores[framework]['passed'] += 1
        
        # Calculate percentages
        for framework, data in framework_scores.items():
            if data['total'] > 0:
                data['score'] = (data['passed'] / data['total']) * 100
            else:
                data['score'] = 0
        
        # Sort by score (lowest first to highlight problems)
        return dict(sorted(framework_scores.items(), key=lambda x: x[1]['score']))
    
    def calculate_grade(self, score: float) -> str:
        """Convert score to letter grade with emoji."""
        if score >= 95: return "🟢 A+"
        elif score >= 90: return "🟢 A"
        elif score >= 85: return "🟡 B+"
        elif score >= 80: return "🟡 B"
        elif score >= 75: return "🟡 B-"
        elif score >= 70: return "🟡 C+"
        elif score >= 65: return "🟡 C"
        elif score >= 60: return "🟡 C-"
        elif score >= 55: return "🔴 D"
        else: return "🔴 F"
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for the current results."""
        if not self.results:
            return {}
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Count by severity
        severity_counts = {}
        for result in self.results:
            if not result.passed:
                severity = result.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Get affected frameworks
        failed_frameworks: Set[str] = set()
        for result in self.results:
            if not result.passed:
                failed_frameworks.update(result.compliance)
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total) * 100,
            'severity_counts': severity_counts,
            'failed_frameworks': sorted(failed_frameworks),
            'framework_scores': self.calculate_framework_scores()
        }
"""
Main Screen for ARC-Eval TUI.

The primary interface showing file selection, domain choice,
progress monitoring, and results display.
"""

from pathlib import Path
from typing import List, Optional

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Select, Static
from textual.reactive import reactive

from ..widgets.file_selector import FileSelector
from ..widgets.progress_monitor import ProgressMonitor
from ..widgets.results_table import ResultsTable
from ...core.engine import EvaluationEngine
from ...core.types import EvaluationResult


class MainScreen(Screen):
    """Main dashboard screen for ARC-Eval TUI."""
    
    current_domain: reactive[str] = reactive("finance")
    has_files: reactive[bool] = reactive(False)
    is_evaluating: reactive[bool] = reactive(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_files: List[Path] = []
        self.current_results: List[EvaluationResult] = []
        self.engine: Optional[EvaluationEngine] = None
    
    def compose(self):
        """Create the main screen layout."""
        with Vertical():
            # Header section
            yield Static("🛡️ ARC-Eval Interactive: Agent Safety Workbench", classes="onboarding-welcome")
            
            # Main content area
            with Horizontal():
                # Left panel: File selection and domain config
                with Vertical():
                    yield FileSelector(id="file-selector")
                    
                    # Domain selection
                    with Container():
                        yield Static("🎯 Evaluation Domain", classes="section-title")
                        yield Select(
                            [
                                ("🏦 Finance (15 scenarios)", "finance"),
                                ("🔒 Security (15 scenarios)", "security"), 
                                ("🤖 ML Infrastructure (15 scenarios)", "ml")
                            ],
                            value="finance",
                            id="domain-select"
                        )
                    
                    # Action buttons
                    with Container(classes="action-buttons"):
                        yield Button("🎯 Run Evaluation", id="run-btn", variant="primary", disabled=True)
                        yield Button("⏹️ Stop", id="stop-btn", variant="secondary", disabled=True)
                        yield Button("🔄 Clear", id="clear-btn", variant="secondary")
                
                # Right panel: Progress and results
                with Vertical():
                    yield ProgressMonitor(id="progress-monitor")
                    yield ResultsTable(id="results-table")
    
    def on_mount(self):
        """Initialize screen on mount."""
        self.update_ui_state()
        
        # Initialize engine with default domain
        self.initialize_engine(self.current_domain)
    
    @on(FileSelector.FilesChanged)
    def handle_files_changed(self, event: FileSelector.FilesChanged):
        """Handle file selection changes."""
        self.current_files = event.files
        self.has_files = len(self.current_files) > 0
        self.update_ui_state()
        
        # Notify user
        if self.current_files:
            count = len(self.current_files)
            self.notify(f"Selected {count} file{'s' if count != 1 else ''}", severity="information")
        else:
            self.notify("No files selected", severity="information")
    
    @on(Select.Changed, "#domain-select")
    def handle_domain_change(self, event: Select.Changed):
        """Handle domain selection change."""
        if event.value:
            self.current_domain = event.value
            self.initialize_engine(self.current_domain)
            
            domain_names = {
                "finance": "Finance", 
                "security": "Security",
                "ml": "ML Infrastructure"
            }
            domain_name = domain_names.get(self.current_domain, self.current_domain)
            self.notify(f"Switched to {domain_name} domain", severity="information")
    
    @on(Button.Pressed, "#run-btn")
    async def handle_run_evaluation(self):
        """Handle run evaluation button press."""
        if not self.current_files or not self.engine:
            return
        
        self.is_evaluating = True
        self.update_ui_state()
        
        # Start evaluation
        progress_monitor = self.query_one("#progress-monitor", ProgressMonitor)
        await progress_monitor.start_evaluation(self.engine, self.current_files)
    
    @on(Button.Pressed, "#stop-btn")
    def handle_stop_evaluation(self):
        """Handle stop evaluation button press."""
        self.is_evaluating = False
        self.update_ui_state()
        
        # Stop evaluation
        progress_monitor = self.query_one("#progress-monitor", ProgressMonitor)
        progress_monitor.stop_evaluation()
        
        self.notify("Evaluation stopped", severity="warning")
    
    @on(Button.Pressed, "#clear-btn")
    def handle_clear(self):
        """Handle clear button press."""
        # Clear files
        file_selector = self.query_one("#file-selector", FileSelector)
        file_selector.current_files = []
        file_selector.update_files_display()
        
        # Clear results
        results_table = self.query_one("#results-table", ResultsTable)
        results_table.set_results([])
        
        # Reset state
        self.current_files = []
        self.current_results = []
        self.has_files = False
        self.is_evaluating = False
        self.update_ui_state()
        
        self.notify("Cleared all data", severity="information")
    
    @on(ProgressMonitor.EvaluationComplete)
    def handle_evaluation_complete(self, event: ProgressMonitor.EvaluationComplete):
        """Handle evaluation completion."""
        self.is_evaluating = False
        self.current_results = event.results
        self.update_ui_state()
        
        # Update results table
        results_table = self.query_one("#results-table", ResultsTable)
        results_table.set_results(self.current_results)
        
        # Show completion notification
        total = len(self.current_results)
        passed = sum(1 for r in self.current_results if r.passed)
        failed = total - passed
        critical = sum(1 for r in self.current_results if r.severity == "critical" and not r.passed)
        
        if critical > 0:
            self.notify(f"⚠️ Evaluation complete: {critical} critical failures found!", severity="error")
        elif failed > 0:
            self.notify(f"✅ Evaluation complete: {failed} failures, {passed} passed", severity="warning")
        else:
            self.notify(f"🎉 Evaluation complete: All {passed} scenarios passed!", severity="success")
        
        # Track metrics
        if hasattr(self.app, 'track_evaluation_run'):
            self.app.track_evaluation_run()
    
    @on(ProgressMonitor.EvaluationError)
    def handle_evaluation_error(self, event: ProgressMonitor.EvaluationError):
        """Handle evaluation error."""
        self.is_evaluating = False
        self.update_ui_state()
        
        self.notify(f"Evaluation failed: {event.error}", severity="error")
    
    @on(ResultsTable.ExportRequested)
    async def handle_export_request(self, event: ResultsTable.ExportRequested):
        """Handle export request from results table."""
        if not self.current_results:
            self.notify("No results to export", severity="warning")
            return
        
        try:
            # Use existing exporters from core
            timestamp = "2024-01-15_14-30"  # TODO: Use actual timestamp
            filename = f"arc_eval_{self.current_domain}_{timestamp}.{event.format}"
            
            if event.format == "pdf":
                from ...exporters.pdf import PDFExporter
                exporter = PDFExporter()
                exporter.export(self.current_results, filename, self.current_domain)
            elif event.format == "csv":
                from ...exporters.csv import CSVExporter
                exporter = CSVExporter()
                exporter.export(self.current_results, filename, self.current_domain)
            elif event.format == "json":
                import json
                with open(filename, 'w') as f:
                    json.dump([r.to_dict() for r in self.current_results], f, indent=2)
            
            self.notify(f"📄 Exported to {filename}", severity="success")
            
            # Track metrics
            if hasattr(self.app, 'track_export'):
                self.app.track_export()
                
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")
    
    def initialize_engine(self, domain: str):
        """Initialize evaluation engine for specified domain."""
        try:
            self.engine = EvaluationEngine(domain=domain)
            scenarios_count = len(self.engine.eval_pack.scenarios)
            self.notify(f"Loaded {scenarios_count} scenarios for {domain} domain", severity="information")
        except Exception as e:
            self.notify(f"Failed to load {domain} domain: {e}", severity="error")
            self.engine = None
    
    def update_ui_state(self):
        """Update UI button states based on current state."""
        run_btn = self.query_one("#run-btn", Button)
        stop_btn = self.query_one("#stop-btn", Button)
        
        # Run button: enabled if we have files and not evaluating
        run_btn.disabled = not (self.has_files and not self.is_evaluating and self.engine)
        
        # Stop button: enabled only when evaluating
        stop_btn.disabled = not self.is_evaluating
        
        # Update button text based on state
        if self.is_evaluating:
            run_btn.label = "🔄 Running..."
        else:
            run_btn.label = "🎯 Run Evaluation"
    
    def focus_file_selector(self):
        """Focus the file selector input."""
        file_selector = self.query_one("#file-selector", FileSelector)
        file_selector.focus_input()
    
    def run_evaluation(self):
        """Trigger evaluation run (called from app shortcuts)."""
        if self.has_files and not self.is_evaluating and self.engine:
            run_btn = self.query_one("#run-btn", Button)
            run_btn.press()
    
    def refresh(self):
        """Refresh the screen."""
        self.update_ui_state()
        self.notify("Screen refreshed", severity="information")
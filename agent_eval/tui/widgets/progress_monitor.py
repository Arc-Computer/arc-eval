"""
Progress Monitor Widget.

Provides real-time progress monitoring during evaluation
with live statistics, progress bars, and results feed.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from textual import work
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import DataTable, ProgressBar, Static
from textual.reactive import reactive

from ...core.engine import EvaluationEngine
from ...core.types import EvaluationResult


class ProgressMonitor(Container):
    """Real-time evaluation progress and results monitor."""
    
    is_running: reactive[bool] = reactive(False)
    current_progress: reactive[float] = reactive(0.0)
    
    class EvaluationStarted(Message):
        """Message sent when evaluation starts."""
        pass
    
    class EvaluationProgress(Message):
        """Message sent with progress updates."""
        def __init__(self, progress: float, current_scenario: str):
            self.progress = progress
            self.current_scenario = current_scenario
            super().__init__()
    
    class EvaluationComplete(Message):
        """Message sent when evaluation completes."""
        def __init__(self, results: List[EvaluationResult]):
            self.results = results
            super().__init__()
    
    class EvaluationError(Message):
        """Message sent when evaluation encounters an error."""
        def __init__(self, error: str):
            self.error = error
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine: Optional[EvaluationEngine] = None
        self.results: List[EvaluationResult] = []
        self.stats = {
            'total_scenarios': 0,
            'completed_scenarios': 0,
            'total_outputs': 0,
            'processed_outputs': 0,
            'critical_failures': 0,
            'high_warnings': 0,
            'medium_warnings': 0,
            'passes': 0,
            'start_time': None,
            'current_scenario': 'Not started'
        }
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("📈 Evaluation Progress", classes="section-title")
            
            # Overall progress
            with Container():
                yield Static("Overall Progress:", id="progress-label")
                yield ProgressBar(total=100, id="overall-progress")
                yield Static("Ready to start evaluation", id="progress-status")
            
            # Current scenario info
            with Container():
                yield Static("Current Scenario:", id="scenario-label")
                yield Static("No scenario running", id="current-scenario")
            
            # Live statistics
            with Container():
                yield Static("Live Statistics:", id="stats-label")
                with Horizontal(classes="stats-row"):
                    yield Static("✅ Passed: 0", id="stat-passed")
                    yield Static("❌ Critical: 0", id="stat-critical")
                    yield Static("⚠️ High: 0", id="stat-high")
                    yield Static("🔶 Medium: 0", id="stat-medium")
            
            # Performance metrics
            with Container():
                yield Static("Performance:", id="perf-label")
                with Horizontal(classes="stats-row"):
                    yield Static("⏱️ Time: 0s", id="stat-time")
                    yield Static("🚀 Speed: 0/s", id="stat-speed")
                    yield Static("📊 Score: --", id="stat-score")
                    yield Static("📈 ETA: --", id="stat-eta")
            
            # Live results feed
            with Container():
                yield Static("Live Results Feed:", id="feed-label")
                yield DataTable(id="results-feed")
    
    def on_mount(self):
        """Initialize widget on mount."""
        # Set up results feed table
        table = self.query_one("#results-feed")
        table.add_columns("Time", "Status", "ID", "Scenario", "Details")
        table.zebra_stripes = True
        
        self.update_display()
    
    async def start_evaluation(self, engine: EvaluationEngine, files: List[Path]):
        """Start evaluation process."""
        if self.is_running:
            return
        
        self.engine = engine
        self.is_running = True
        self.results = []
        self.reset_stats()
        
        self.post_message(self.EvaluationStarted())
        
        try:
            await self.run_evaluation(files)
        except Exception as e:
            self.post_message(self.EvaluationError(str(e)))
        finally:
            self.is_running = False
    
    def reset_stats(self):
        """Reset statistics for new evaluation."""
        self.stats = {
            'total_scenarios': 0,
            'completed_scenarios': 0,
            'total_outputs': 0,
            'processed_outputs': 0,
            'critical_failures': 0,
            'high_warnings': 0,
            'medium_warnings': 0,
            'passes': 0,
            'start_time': datetime.now(),
            'current_scenario': 'Loading...'
        }
        self.current_progress = 0.0
        
        # Clear results feed
        table = self.query_one("#results-feed")
        table.clear()
        
        self.update_display()
    
    @work(exclusive=True)
    async def run_evaluation(self, files: List[Path]):
        """Execute evaluation with real-time updates."""
        if not self.engine:
            return
        
        try:
            # Count total work
            total_outputs = 0
            for file_path in files:
                outputs = await self.load_file(file_path)
                total_outputs += len(outputs)
            
            self.stats['total_outputs'] = total_outputs
            self.stats['total_scenarios'] = len(self.engine.eval_pack.scenarios)
            
            # Process each file
            processed_outputs = 0
            for file_path in files:
                outputs = await self.load_file(file_path)
                
                # Run evaluation on this file's outputs
                file_results = self.engine.evaluate(outputs)
                self.results.extend(file_results)
                
                # Update statistics
                for result in file_results:
                    if result.passed:
                        self.stats['passes'] += 1
                    elif result.severity == 'critical':
                        self.stats['critical_failures'] += 1
                    elif result.severity == 'high':
                        self.stats['high_warnings'] += 1
                    elif result.severity == 'medium':
                        self.stats['medium_warnings'] += 1
                    
                    # Add to live feed
                    await self.add_to_feed(result)
                    
                    # Small delay to show progress
                    await asyncio.sleep(0.01)
                
                processed_outputs += len(outputs)
                self.stats['processed_outputs'] = processed_outputs
                
                # Update progress
                progress = (processed_outputs / total_outputs) * 100
                self.current_progress = progress
                self.post_message(self.EvaluationProgress(progress, "Processing..."))
                
                await self.update_display()
            
            # Evaluation complete
            self.post_message(self.EvaluationComplete(self.results))
            
        except Exception as e:
            self.post_message(self.EvaluationError(str(e)))
            raise
    
    async def load_file(self, file_path: Path) -> List[Any]:
        """Load and parse file contents."""
        import json
        
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix == '.json':
                    data = json.load(f)
                elif file_path.suffix == '.jsonl':
                    data = [json.loads(line) for line in f]
                else:
                    # For CSV, create simple dict structure
                    import csv
                    reader = csv.DictReader(f)
                    data = list(reader)
            
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]
            
            return data
            
        except Exception as e:
            self.notify(f"Error loading {file_path}: {e}", severity="error")
            return []
    
    async def add_to_feed(self, result: EvaluationResult):
        """Add result to live feed."""
        table = self.query_one("#results-feed")
        
        # Status icon and styling
        if result.passed:
            status = "✅ PASS"
            status_style = "status-passed"
        elif result.severity == "critical":
            status = "❌ CRIT"
            status_style = "status-failed"
        elif result.severity == "high":
            status = "⚠️ HIGH"
            status_style = "status-warning"
        elif result.severity == "medium":
            status = "🔶 MED"
            status_style = "status-warning"
        else:
            status = "🔵 LOW"
            status_style = "status-passed"
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Truncate long text
        scenario_name = result.scenario_name
        if len(scenario_name) > 25:
            scenario_name = scenario_name[:22] + "..."
        
        details = result.failure_reason or "Passed"
        if len(details) > 30:
            details = details[:27] + "..."
        
        # Add row
        table.add_row(
            timestamp,
            status,
            result.scenario_id,
            scenario_name,
            details
        )
        
        # Keep only last 20 results visible
        if table.row_count > 20:
            table.remove_row(0)
        
        # Scroll to bottom
        table.cursor_coordinate = (table.row_count - 1, 0)
    
    async def update_display(self):
        """Update all display elements."""
        # Progress bar
        progress_bar = self.query_one("#overall-progress")
        progress_bar.update(progress=self.current_progress)
        
        # Progress status
        if self.is_running:
            status_text = f"Processing... {self.current_progress:.1f}% complete"
        elif self.current_progress == 100:
            status_text = "✅ Evaluation complete"
        else:
            status_text = "Ready to start evaluation"
        
        self.query_one("#progress-status").update(status_text)
        
        # Current scenario
        scenario_text = self.stats.get('current_scenario', 'No scenario running')
        self.query_one("#current-scenario").update(scenario_text)
        
        # Statistics
        self.query_one("#stat-passed").update(f"✅ Passed: {self.stats['passes']}")
        self.query_one("#stat-critical").update(f"❌ Critical: {self.stats['critical_failures']}")
        self.query_one("#stat-high").update(f"⚠️ High: {self.stats['high_warnings']}")
        self.query_one("#stat-medium").update(f"🔶 Medium: {self.stats['medium_warnings']}")
        
        # Performance metrics
        if self.stats['start_time']:
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
            self.query_one("#stat-time").update(f"⏱️ Time: {elapsed:.1f}s")
            
            if elapsed > 0 and self.stats['processed_outputs'] > 0:
                speed = self.stats['processed_outputs'] / elapsed
                self.query_one("#stat-speed").update(f"🚀 Speed: {speed:.1f}/s")
                
                # ETA calculation
                if self.stats['total_outputs'] > 0 and self.current_progress > 0:
                    remaining = self.stats['total_outputs'] - self.stats['processed_outputs']
                    eta = remaining / speed if speed > 0 else 0
                    self.query_one("#stat-eta").update(f"📈 ETA: {eta:.0f}s")
        
        # Overall score
        total_results = len(self.results)
        if total_results > 0:
            score = (self.stats['passes'] / total_results) * 100
            grade = self.calculate_grade(score)
            self.query_one("#stat-score").update(f"📊 Score: {grade} ({score:.0f}%)")
    
    def calculate_grade(self, score: float) -> str:
        """Convert score to letter grade."""
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
    
    def stop_evaluation(self):
        """Stop the current evaluation."""
        self.is_running = False
        self.query_one("#progress-status").update("⏹️ Evaluation stopped")
    
    def get_results(self) -> List[EvaluationResult]:
        """Get current evaluation results."""
        return self.results.copy()
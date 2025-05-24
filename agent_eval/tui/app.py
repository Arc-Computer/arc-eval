"""
Main ARC-Eval TUI Application.

This module contains the main Textual application for the interactive
terminal user interface, providing keyboard shortcuts, navigation,
and core app functionality.
"""

from pathlib import Path
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from .screens.main import MainScreen
from .screens.onboarding import LandingScreen
from .utils.state_manager import StateManager, TUIState
from ..core.engine import EvaluationEngine


class ARCEvalApp(App):
    """ARC-Eval Interactive TUI Application."""
    
    CSS_PATH = str(Path(__file__).parent / "styles/main.tcss")
    TITLE = "ARC-Eval Interactive: Agent Safety Workbench"
    SUB_TITLE = "Domain-specific compliance evaluation for LLMs and AI agents"
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command Palette"),
        Binding("ctrl+o", "open_files", "Open Files"),
        Binding("ctrl+r", "run_evaluation", "Run Evaluation"),
        Binding("ctrl+s", "save_session", "Save Session"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
    ]
    
    def __init__(self, initial_config: Optional[dict] = None):
        super().__init__()
        self.engine: Optional[EvaluationEngine] = None
        self.current_files: List[Path] = []
        self.current_domain: str = "finance"
        self.evaluation_state = {}
        self.session_history = []
        
        # Apply initial configuration from CLI if provided
        if initial_config:
            if 'domain' in initial_config:
                self.current_domain = initial_config['domain']
            if 'files' in initial_config:
                self.current_files = [Path(f) for f in initial_config['files']]
        
        # Initialize state manager
        config_dir = Path.home() / ".arc-eval"
        self.state_manager = StateManager(config_dir)
        self.app_state: Optional[TUIState] = None
        
        # Track usage metrics for validation
        self.usage_metrics = {
            "session_start": None,
            "files_processed": 0,
            "evaluations_run": 0,
            "exports_generated": 0,
        }
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
    
    async def on_mount(self):
        """Initialize app on startup."""
        from datetime import datetime
        
        # Load application state
        self.app_state = await self.state_manager.load_state()
        
        # Track session start for metrics
        self.usage_metrics["session_start"] = datetime.now()
        
        # Always start with landing screen for simplified experience
        # The landing screen now replaces the old complex onboarding
        self.push_screen(LandingScreen())
    
    def action_open_files(self):
        """Open file manager."""
        if hasattr(self, 'current_screen') and hasattr(self.current_screen, 'focus_file_selector'):
            self.current_screen.focus_file_selector()
    
    def action_run_evaluation(self):
        """Start evaluation process."""
        if hasattr(self, 'current_screen') and hasattr(self.current_screen, 'run_evaluation'):
            self.current_screen.run_evaluation()
    
    def action_save_session(self):
        """Save current session."""
        if self.app_state:
            # Update current session data
            session_data = {
                "files": [str(f) for f in self.current_files],
                "domain": self.current_domain,
                "metrics": self.usage_metrics.copy()
            }
            
            # This will be async in real implementation
            # For now, just update the state
            self.app_state.current_files = [str(f) for f in self.current_files]
            self.app_state.selected_domain = self.current_domain
    
    def action_help(self):
        """Show help information."""
        help_text = """
ARC-Eval Interactive Help

Keyboard Shortcuts:
  Ctrl+Q    - Quit application
  Ctrl+O    - Focus file selector
  Ctrl+R    - Run evaluation
  Ctrl+S    - Save session
  F1        - Show this help
  F5        - Refresh current screen

Getting Started:
1. Select input files containing agent outputs
2. Choose evaluation domain (Finance, Security, ML)
3. Run evaluation to see real-time progress
4. Review results and export reports

Supported file formats: .json, .csv, .jsonl
Auto-detected frameworks: OpenAI, Anthropic, LangChain, LangGraph
        """
        
        from textual.screen import ModalScreen
        from textual.widgets import Static
        from textual.containers import Vertical, Horizontal
        from textual.widgets import Button
        
        class HelpScreen(ModalScreen):
            def compose(self) -> ComposeResult:
                with Vertical():
                    yield Static(help_text, id="help-text")
                    with Horizontal():
                        yield Button("Close", variant="primary", id="close-help")
            
            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "close-help":
                    self.dismiss()
        
        self.push_screen(HelpScreen())
    
    def action_refresh(self):
        """Refresh current screen."""
        if hasattr(self, 'current_screen') and hasattr(self.current_screen, 'refresh'):
            self.current_screen.refresh()
    
    def set_current_files(self, files: List[Path]):
        """Update current files and track metrics."""
        self.current_files = files
        self.usage_metrics["files_processed"] = len(files)
        
        # Update state for persistence
        if self.app_state:
            self.app_state.current_files = [str(f) for f in files]
    
    def set_current_domain(self, domain: str):
        """Update current domain."""
        self.current_domain = domain
        
        # Update state for persistence
        if self.app_state:
            self.app_state.selected_domain = domain
    
    def initialize_engine(self, domain: str):
        """Initialize evaluation engine for specified domain."""
        try:
            self.engine = EvaluationEngine(domain=domain)
            return True
        except Exception as e:
            self.notify(f"Failed to initialize engine: {e}", severity="error")
            return False
    
    def track_evaluation_run(self):
        """Track evaluation run for metrics."""
        self.usage_metrics["evaluations_run"] += 1
    
    def track_export(self):
        """Track export for metrics."""
        self.usage_metrics["exports_generated"] += 1
    
    async def on_unmount(self):
        """Save state when app closes."""
        if self.app_state:
            await self.state_manager.save_state(self.app_state)
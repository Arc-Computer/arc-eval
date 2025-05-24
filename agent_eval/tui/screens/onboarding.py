"""
Landing Screen for ARC-Eval TUI.

Simplified developer-focused interface for immediate value delivery.
"""

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, Select, Input
from pathlib import Path


class LandingScreen(Screen):
    """Simplified landing screen focusing on core workflow."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_files = []
        self.selected_domain = "finance"  # Smart default
        self.file_validated = False
    
    def compose(self):
        """Create minimal landing screen layout."""
        with Vertical(id="landing-main"):
            # Simple header only
            yield Static("ARC-Eval", classes="app-title")
            
            # Core workflow - centered and minimal
            with Container(id="workflow-container"):
                # File selection - primary focus
                with Container(classes="workflow-step"):
                    yield Static("Agent Output Files", classes="step-label")
                    with Horizontal(classes="file-input-group"):
                        yield Input(
                            placeholder="Select files (.json, .csv, .jsonl)...",
                            id="file-input",
                            classes="file-path-input"
                        )
                        yield Button("Browse", id="browse-btn", variant="default")
                
                # Domain selection - becomes active after file selection
                with Container(classes="workflow-step"):
                    yield Static("Evaluation Domain", classes="step-label")
                    yield Select(
                        [
                            ("Finance - Compliance & risk assessment", "finance"),
                            ("Security - Vulnerability & threat detection", "security"),
                            ("ML - Model safety & bias analysis", "ml")
                        ],
                        value="finance",
                        id="domain-select",
                        disabled=True
                    )
                
                # Run button - becomes active after domain selection
                with Container(classes="workflow-step"):
                    yield Button(
                        "Run Evaluation",
                        id="run-btn",
                        variant="primary",
                        disabled=True,
                        classes="run-button"
                    )
    
    async def on_mount(self):
        """Auto-focus file input on startup."""
        # Auto-focus file input for immediate workflow start
        file_input = self.query_one("#file-input", Input)
        file_input.focus()
    
    @on(Input.Changed, "#file-input")
    def handle_file_input_change(self, event: Input.Changed):
        """Handle file path input changes."""
        if event.value.strip():
            # Basic validation - check if files exist
            self.validate_file_input(event.value)
    
    def validate_file_input(self, file_paths_str: str):
        """Validate file input and enable next step."""
        try:
            # Simple comma-separated or space-separated file paths
            paths = [p.strip() for p in file_paths_str.replace(',', ' ').split() if p.strip()]
            valid_files = []
            
            for path_str in paths:
                path = Path(path_str)
                if path.exists() and path.suffix.lower() in ['.json', '.csv', '.jsonl']:
                    valid_files.append(path)
            
            if valid_files:
                self.selected_files = valid_files
                self.file_validated = True
                
                # Enable domain selector
                domain_select = self.query_one("#domain-select", Select)
                domain_select.disabled = False
                
                # Show validation success
                file_input = self.query_one("#file-input", Input)
                file_input.add_class("valid")
                
                # Auto-enable run button if domain already selected
                if self.selected_domain:
                    run_btn = self.query_one("#run-btn", Button)
                    run_btn.disabled = False
            else:
                self.file_validated = False
                # Disable subsequent steps
                domain_select = self.query_one("#domain-select", Select)
                domain_select.disabled = True
                run_btn = self.query_one("#run-btn", Button)
                run_btn.disabled = True
                
        except Exception:
            # Invalid input - disable subsequent steps
            self.file_validated = False
            domain_select = self.query_one("#domain-select", Select)
            domain_select.disabled = True
            run_btn = self.query_one("#run-btn", Button)
            run_btn.disabled = True
    
    @on(Button.Pressed, "#browse-btn")
    def handle_browse_button(self):
        """Open file browser dialog."""
        import tkinter as tk
        from tkinter import filedialog
        
        def open_dialog():
            root = tk.Tk()
            try:
                root.withdraw()
                file_paths = filedialog.askopenfilenames(
                    title="Select Agent Output Files",
                    filetypes=[
                        ("JSON files", "*.json"),
                        ("CSV files", "*.csv"),
                        ("JSONL files", "*.jsonl"),
                        ("All supported", "*.json;*.csv;*.jsonl")
                    ]
                )
                return file_paths
            finally:
                root.destroy()
        
        file_paths = open_dialog()
        if file_paths:
            # Update input field with selected files
            file_input = self.query_one("#file-input", Input)
            file_input.value = " ".join(file_paths)
            self.validate_file_input(file_input.value)
    
    @on(Select.Changed, "#domain-select")
    def handle_domain_change(self, event: Select.Changed):
        """Handle domain selection change."""
        if event.value:
            self.selected_domain = event.value
            
            # Enable run button if files are validated
            if self.file_validated:
                run_btn = self.query_one("#run-btn", Button)
                run_btn.disabled = False
    
    @on(Button.Pressed, "#run-btn")
    def handle_run_button(self):
        """Handle run evaluation button press."""
        if not self.selected_files or not self.selected_domain:
            self.app.notify("Please select files and domain first.", severity="warning")
            return
        
        # Pass configuration to app
        self.app.set_current_files(self.selected_files)
        self.app.set_current_domain(self.selected_domain)
        
        # Mark first launch as completed
        if hasattr(self.app, 'app_state') and self.app.app_state:
            self.app.app_state.user_preferences["first_launch"] = False
        
        # Navigate directly to main screen with configuration
        from .main import MainScreen
        main_screen = MainScreen()
        self.app.push_screen(main_screen)
        
        # Auto-start evaluation for immediate value
        # This will be handled by the main screen on mount
    

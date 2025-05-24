"""
Landing Screen for ARC-Eval TUI.

Simplified developer-focused interface for immediate value delivery.
"""

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, Select, Input
from textual.binding import Binding
from pathlib import Path


class LandingScreen(Screen):
    """Simplified landing screen focusing on core workflow."""
    
    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("ctrl+o", "focus_files", "Focus Files"),
        Binding("ctrl+r", "run_if_ready", "Run"),
        Binding("escape", "app.quit", "Quit"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_files = []
        self.selected_domain = "finance"  # Smart default
        self.file_validated = False
        self.current_step = 1  # Track current step for visual feedback
    
    def compose(self):
        """Create minimal landing screen layout."""
        with Vertical(id="landing-main"):
            # Header with value proposition
            yield Static("ARC-Eval", classes="app-title")
            yield Static("Agent Reliability & Compliance evaluation for LLMs and AI agents", classes="app-subtitle")
            
            # Core workflow - centered and minimal
            with Container(id="workflow-container"):
                # File selection - Step 1
                with Container(classes="workflow-step"):
                    with Horizontal(classes="step-header"):
                        yield Static("Step 1 of 3", classes="step-indicator current", id="step1-indicator")
                        yield Static("Agent Output Files", classes="step-label")
                    with Horizontal(classes="file-input-group"):
                        yield Input(
                            placeholder="Select files (.json, .csv, .jsonl) or click Browse...",
                            id="file-input",
                            classes="file-path-input"
                        )
                        yield Button("Browse", id="browse-btn", variant="default")
                
                # Domain selection - Step 2
                with Container(classes="workflow-step"):
                    with Horizontal(classes="step-header"):
                        yield Static("Step 2 of 3", classes="step-indicator pending", id="step2-indicator")
                        yield Static("Evaluation Domain", classes="step-label")
                    yield Select(
                        [
                            ("Finance - SOX, KYC, AML, PCI-DSS compliance", "finance"),
                            ("Security - OWASP, prompt injection, data leakage", "security"),
                            ("ML - Model bias, safety, performance analysis", "ml")
                        ],
                        value="finance",
                        id="domain-select",
                        classes="domain-select",
                        disabled=True
                    )
                
                # Run button - Step 3
                with Container(classes="workflow-step"):
                    with Horizontal(classes="step-header"):
                        yield Static("Step 3 of 3", classes="step-indicator pending", id="step3-indicator")
                        yield Static("Start Evaluation", classes="step-label")
                    yield Button(
                        "🚀 Run Evaluation",
                        id="run-btn",
                        variant="primary",
                        disabled=True,
                        classes="run-button"
                    )
            
            # Footer with version and keyboard shortcuts
            try:
                import importlib.metadata
                version = importlib.metadata.version('arc-eval')
            except:
                version = "1.0.0"
            yield Static(f"v{version} | F1: Help | Ctrl+O: Files | Ctrl+R: Run | Tab: Navigate", classes="app-footer", id="app-footer")
    
    async def on_mount(self):
        """Auto-focus file input on startup."""
        # Auto-focus file input for immediate workflow start
        file_input = self.query_one("#file-input", Input)
        file_input.focus()
        
        # Set up tab order for keyboard navigation
        self.set_focus_order([
            "#file-input",
            "#browse-btn", 
            "#domain-select",
            "#run-btn"
        ])
    
    def set_focus_order(self, widget_ids: list):
        """Set up proper tab order for keyboard navigation."""
        # This ensures proper tab navigation through the workflow
        for i, widget_id in enumerate(widget_ids):
            try:
                widget = self.query_one(widget_id)
                widget.tab_index = i
            except:
                pass  # Widget might not exist yet
    
    @on(Input.Changed, "#file-input")
    def handle_file_input_change(self, event: Input.Changed):
        """Handle file path input changes."""
        if event.value.strip():
            # Basic validation - check if files exist
            self.validate_file_input(event.value)
    
    def validate_file_input(self, file_paths_str: str):
        """Validate file input and enable next step."""
        file_input = self.query_one("#file-input", Input)
        domain_select = self.query_one("#domain-select", Select)
        run_btn = self.query_one("#run-btn", Button)
        
        # Remove previous validation classes
        file_input.remove_class("valid")
        file_input.remove_class("invalid")
        
        try:
            if not file_paths_str.strip():
                # Empty input - reset to initial state
                self.selected_files = []
                self.file_validated = False
                domain_select.disabled = True
                run_btn.disabled = True
                return
            
            # Parse comma-separated or space-separated file paths
            # Handle quoted paths for paths with spaces
            import shlex
            try:
                paths = shlex.split(file_paths_str)
            except ValueError:
                # Fallback to simple split if shlex fails
                paths = [p.strip() for p in file_paths_str.replace(',', ' ').split() if p.strip()]
            
            valid_files = []
            invalid_files = []
            
            for path_str in paths:
                path = Path(path_str.strip('"\'')).expanduser()  # Handle ~ and quotes
                if path.exists():
                    if path.is_file() and path.suffix.lower() in ['.json', '.csv', '.jsonl']:
                        valid_files.append(path)
                    else:
                        invalid_files.append(f"{path} (unsupported format)")
                else:
                    invalid_files.append(f"{path} (not found)")
            
            if valid_files and not invalid_files:
                # All files valid
                self.selected_files = valid_files
                self.file_validated = True
                file_input.add_class("valid")
                domain_select.disabled = False
                
                # Auto-enable run button if domain already selected
                if self.selected_domain:
                    run_btn.disabled = False
                    
                # Show success feedback
                file_count = len(valid_files)
                self.app.notify(f"✅ {file_count} valid file{'s' if file_count != 1 else ''} selected", severity="information")
                
            elif valid_files and invalid_files:
                # Some files valid, some invalid
                self.selected_files = valid_files
                self.file_validated = True
                file_input.add_class("valid")
                domain_select.disabled = False
                
                if self.selected_domain:
                    run_btn.disabled = False
                    
                # Show warning about invalid files
                self.app.notify(f"⚠️ {len(valid_files)} valid files selected, {len(invalid_files)} skipped", severity="warning")
                
            else:
                # No valid files
                self.selected_files = []
                self.file_validated = False
                file_input.add_class("invalid")
                domain_select.disabled = True
                run_btn.disabled = True
                
                if invalid_files:
                    self.app.notify(f"❌ No valid files found. Check file paths and formats.", severity="error")
                
        except Exception as e:
            # Unexpected error
            self.selected_files = []
            self.file_validated = False
            file_input.add_class("invalid")
            domain_select.disabled = True
            run_btn.disabled = True
            self.app.notify(f"Error validating files: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#browse-btn")
    def handle_browse_button(self):
        """Open file browser dialog."""
        import threading
        
        def open_dialog():
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                root.lift()  # Bring to front
                root.attributes('-topmost', True)  # Keep on top
                
                file_paths = filedialog.askopenfilenames(
                    title="Select Agent Output Files",
                    filetypes=[
                        ("JSON files", "*.json"),
                        ("CSV files", "*.csv"),
                        ("JSONL files", "*.jsonl"),
                        ("All supported", "*.json *.csv *.jsonl")
                    ]
                )
                root.destroy()
                return file_paths
            except ImportError:
                # Fallback if tkinter not available
                self.app.notify("File browser not available. Please enter file paths manually.", severity="warning")
                return None
            except Exception as e:
                self.app.notify(f"Error opening file browser: {str(e)}", severity="error")
                return None
        
        # Run in thread to avoid blocking the TUI
        def handle_selection():
            file_paths = open_dialog()
            if file_paths:
                # Schedule UI update on main thread
                self.call_from_thread(self.update_selected_files, list(file_paths))
        
        thread = threading.Thread(target=handle_selection, daemon=True)
        thread.start()
    
    def update_selected_files(self, file_paths: list):
        """Update UI with selected files (called from main thread)."""
        if file_paths:
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
    
    def update_step_indicators(self, step: int, state: str):
        """Update step indicator visual state."""
        try:
            indicator = self.query_one(f"#step{step}-indicator", Static)
            indicator.remove_class("current")
            indicator.remove_class("pending")
            indicator.remove_class("active")
            indicator.add_class(state)
        except:
            pass
    
    def reset_step_indicators(self):
        """Reset all step indicators to initial state."""
        self.update_step_indicators(1, "current")
        self.update_step_indicators(2, "pending")
        self.update_step_indicators(3, "pending")
        self.current_step = 1
    
    def action_help(self):
        """Show help information."""
        self.app.action_help()
    
    def action_focus_files(self):
        """Focus the file input field."""
        try:
            file_input = self.query_one("#file-input", Input)
            file_input.focus()
        except:
            pass
    
    def action_run_if_ready(self):
        """Run evaluation if ready."""
        if self.file_validated and self.selected_domain:
            self.handle_run_button()
        else:
            self.app.notify("Please complete file selection and domain choice first", severity="warning")
    

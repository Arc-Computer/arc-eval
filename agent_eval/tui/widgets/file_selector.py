"""
File Selector Widget.

Provides file selection functionality including path input,
browse button, validation, and framework detection display.
"""

import asyncio
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import List, Optional

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Static, Select
from textual.reactive import reactive

from ..utils.file_utils import validate_file, get_framework_info


class FileSelector(Container):
    """File selection widget with validation and framework detection."""
    
    current_files: reactive[List[Path]] = reactive(list)
    
    class FileAdded(Message):
        """Message sent when a file is added."""
        def __init__(self, file_path: Path):
            self.file_path = file_path
            super().__init__()
    
    class FileRemoved(Message):
        """Message sent when a file is removed."""
        def __init__(self, file_path: Path):
            self.file_path = file_path
            super().__init__()
    
    class FilesChanged(Message):
        """Message sent when file list changes."""
        def __init__(self, files: List[Path]):
            self.files = files
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recent_files: List[Path] = []
    
    def compose(self):
        """Create child widgets."""
        with Vertical():
            yield Static("📁 File Selection", classes="section-title")
            
            # File input section
            with Container(classes="file-drop-zone"):
                yield Static("📁 Select Files for Evaluation", id="drop-header")
                yield Static("Supported: .json, .csv, .jsonl (max 100MB per file)", id="drop-subtext")
                
                with Horizontal():
                    yield Input(
                        placeholder="Enter file path or paste here",
                        id="file-path-input"
                    )
                    yield Button("📂 Browse", id="browse-btn", variant="primary")
                    yield Button("🗑️ Clear", id="clear-btn", variant="secondary")
            
            # Current files display
            yield Static("Current Files:", id="current-files-label")
            yield Container(id="current-files-container")
            
            # Recent files (if any)
            yield Static("Recent Files:", id="recent-files-label")
            yield Container(id="recent-files-container", classes="recent-files")
    
    def on_mount(self):
        """Initialize widget on mount."""
        self.update_files_display()
        self.update_recent_files_display()
    
    @on(Input.Submitted, "#file-path-input")
    async def handle_file_path_input(self, event: Input.Submitted):
        """Handle file path input submission."""
        file_path = Path(event.value.strip())
        if file_path.exists():
            await self.add_file(file_path)
            event.input.value = ""
        else:
            self.notify(f"File not found: {file_path}", severity="error")
    
    @on(Button.Pressed, "#browse-btn")
    def handle_browse_button(self):
        """Handle browse button press."""
        asyncio.create_task(self.open_file_browser())
    
    @on(Button.Pressed, "#clear-btn")
    def handle_clear_button(self):
        """Handle clear button press."""
        self.current_files = []
        self.update_files_display()
        self.post_message(self.FilesChanged(self.current_files))
    
    async def open_file_browser(self):
        """Open system file browser."""
        try:
            # Use tkinter file dialog in a separate thread to avoid blocking
            def open_dialog():
                root = tk.Tk()
                try:
                    root.withdraw()  # Hide the root window
                    
                    file_paths = filedialog.askopenfilenames(
                        title="Select Agent Output Files",
                        filetypes=[
                            ("JSON files", "*.json"),
                            ("CSV files", "*.csv"),
                            ("JSONL files", "*.jsonl"),
                            ("All supported", "*.json *.csv *.jsonl"),
                            ("All files", "*.*")
                        ]
                    )
                    return file_paths
                finally:
                    root.destroy()
            
            # Run in thread pool to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                file_paths = await asyncio.get_event_loop().run_in_executor(
                    executor, open_dialog
                )
            
            # Add selected files
            for path_str in file_paths:
                await self.add_file(Path(path_str))
                
        except Exception as e:
            self.notify(f"Error opening file browser: {e}", severity="error")
    
    async def add_file(self, file_path: Path):
        """Add a file to the current files list."""
        # Validate file
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            self.notify(f"Invalid file: {error_msg}", severity="error")
            return
        
        # Check if already added
        if file_path in self.current_files:
            self.notify(f"File already added: {file_path.name}", severity="warning")
            return
        
        # Add to current files
        self.current_files = self.current_files + [file_path]
        self.update_files_display()
        
        # Send messages
        self.post_message(self.FileAdded(file_path))
        self.post_message(self.FilesChanged(self.current_files))
        
        self.notify(f"Added file: {file_path.name}", severity="information")
    
    def remove_file(self, file_path: Path):
        """Remove a file from the current files list."""
        if file_path in self.current_files:
            self.current_files = [f for f in self.current_files if f != file_path]
            self.update_files_display()
            
            # Send messages
            self.post_message(self.FileRemoved(file_path))
            self.post_message(self.FilesChanged(self.current_files))
            
            self.notify(f"Removed file: {file_path.name}", severity="information")
    
    def update_files_display(self):
        """Update the current files display."""
        container = self.query_one("#current-files-container")
        container.remove_children()
        
        if not self.current_files:
            container.mount(Static("No files selected", classes="file-info"))
            return
        
        for file_path in self.current_files:
            file_info = get_framework_info(file_path)
            
            with container:
                with Horizontal(classes="file-item"):
                    Static(f"📄 {file_path.name}", classes="file-item-name")
                    Static(f"{file_info['framework']} | {file_info['size']}", classes="file-item-info")
                    Button("🗑️", id=f"remove-{file_path.name}", classes="file-item-remove")
    
    def update_recent_files_display(self):
        """Update the recent files display."""
        container = self.query_one("#recent-files-container")
        container.remove_children()
        
        if not self.recent_files:
            container.mount(Static("No recent files", classes="file-info"))
            return
        
        # Show up to 5 recent files
        for file_path in self.recent_files[:5]:
            if file_path.exists():
                file_info = get_framework_info(file_path)
                
                with container:
                    with Horizontal(classes="file-item"):
                        Static(f"📄 {file_path.name}", classes="file-item-name")
                        Static(f"{file_info['framework']} | {file_info['size']}", classes="file-item-info")
                        Button("➕", id=f"add-recent-{file_path.name}", classes="file-item-add")
    
    @on(Button.Pressed)
    def handle_file_action_buttons(self, event: Button.Pressed):
        """Handle file action buttons (remove, add from recent)."""
        button_id = event.button.id
        
        if button_id and button_id.startswith("remove-"):
            file_name = button_id[7:]  # Remove "remove-" prefix
            for file_path in self.current_files:
                if file_path.name == file_name:
                    self.remove_file(file_path)
                    break
        
        elif button_id and button_id.startswith("add-recent-"):
            file_name = button_id[11:]  # Remove "add-recent-" prefix
            for file_path in self.recent_files:
                if file_path.name == file_name:
                    asyncio.create_task(self.add_file(file_path))
                    break
    
    def set_recent_files(self, recent_files: List[Path]):
        """Set the recent files list."""
        self.recent_files = recent_files
        self.update_recent_files_display()
    
    def focus_input(self):
        """Focus the file path input."""
        input_widget = self.query_one("#file-path-input")
        input_widget.focus()
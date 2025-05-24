"""
TUI State Management.

Handles persistence of application state, user preferences,
and session history for the ARC-Eval TUI.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles


@dataclass
class TUIState:
    """TUI application state."""
    current_files: List[str]
    recent_files: List[str]
    selected_domain: str
    export_formats: List[str]
    last_template: Optional[str]
    window_layout: Dict[str, Any]
    user_preferences: Dict[str, Any]
    session_history: List[Dict[str, Any]]


class StateManager:
    """Manage TUI application state and persistence."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.state_file = config_dir / "tui_state.json"
        self.templates_dir = config_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
    
    async def load_state(self) -> TUIState:
        """Load application state from disk."""
        if not self.state_file.exists():
            return self.get_default_state()
        
        try:
            async with aiofiles.open(self.state_file, 'r') as f:
                content = await f.read()
                state_data = json.loads(content)
                return TUIState(**state_data)
        except Exception:
            # If state is corrupted, return default
            return self.get_default_state()
    
    async def save_state(self, state: TUIState):
        """Save application state to disk."""
        try:
            async with aiofiles.open(self.state_file, 'w') as f:
                content = json.dumps(asdict(state), indent=2)
                await f.write(content)
        except Exception as e:
            # Log error but don't crash app
            print(f"Failed to save state: {e}")
    
    def get_default_state(self) -> TUIState:
        """Get default application state."""
        return TUIState(
            current_files=[],
            recent_files=[],
            selected_domain="finance",
            export_formats=["pdf"],
            last_template=None,
            window_layout={},
            user_preferences={
                "theme": "dark",
                "auto_save": True,
                "show_tooltips": True,
                "default_export_format": "pdf",
                "first_launch": True
            },
            session_history=[]
        )
    
    async def add_recent_file(self, file_path: str, state: TUIState):
        """Add file to recent files list."""
        if file_path in state.recent_files:
            state.recent_files.remove(file_path)
        
        state.recent_files.insert(0, file_path)
        
        # Keep only last 20 files
        state.recent_files = state.recent_files[:20]
        
        await self.save_state(state)
    
    async def save_session(self, session_data: Dict[str, Any], state: TUIState):
        """Save evaluation session to history."""
        session_data['timestamp'] = datetime.now().isoformat()
        state.session_history.insert(0, session_data)
        
        # Keep only last 50 sessions
        state.session_history = state.session_history[:50]
        
        await self.save_state(state)
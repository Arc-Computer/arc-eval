"""Workflow state management for ARC-Eval CLI.

This module handles persistent workflow state tracking across CLI sessions,
enabling the Arc Loop functionality where users progress through:
debug → compliance → improve → re-evaluate cycles.

The workflow state system:
- Tracks completion of each workflow step
- Maintains history of evaluation cycles
- Supports workflow continuity across CLI sessions
- Enables progress recommendations and guided user experience
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorkflowStateManager:
    """Manages persistent workflow state for ARC-Eval CLI sessions.
    
    Provides thread-safe persistence and retrieval of workflow progress
    to enable the Arc Loop user experience. Tracks individual workflow
    completions and full cycle progression.
    
    Attributes:
        state_file: Path to the workflow state file (.arc-eval-workflow-state.json)
    """
    
    def __init__(self, state_file: Optional[Path] = None) -> None:
        """Initialize the workflow state manager.
        
        Args:
            state_file: Optional custom path for state file. 
                       Defaults to .arc-eval-workflow-state.json in current directory.
        """
        self.state_file = state_file or Path(".arc-eval-workflow-state.json")
    
    def load_state(self) -> Dict[str, Any]:
        """Load workflow state from disk.
        
        Returns:
            Dictionary containing current workflow state, or empty dict if no state exists.
            
        Structure:
            {
                "current_cycle": {
                    "started_at": "2024-01-01T12:00:00",
                    "debug": {...} | None,
                    "compliance": {...} | None, 
                    "improve": {...} | None
                },
                "history": [
                    {"started_at": "...", "debug": {...}, "compliance": {...}, "improve": {...}},
                    ...
                ]
            }
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Return empty state if file is corrupted
                return {}
        return {}
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save workflow state to disk.
        
        Args:
            state: Complete workflow state dictionary to persist.
            
        Raises:
            IOError: If unable to write to state file.
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            # Non-fatal error - workflow can continue without state persistence
            print(f"Warning: Could not save workflow state: {e}")
    
    def update_workflow_progress(self, workflow: str, **kwargs) -> None:
        """Update workflow progress tracking.
        
        Records completion of a workflow step and manages cycle progression.
        When all three workflows (debug, compliance, improve) are completed,
        the cycle is archived to history and a new cycle begins.
        
        Args:
            workflow: Workflow name ('debug', 'compliance', or 'improve')
            **kwargs: Additional metadata to store with the workflow completion
                     (e.g., pass_rate=85.0, domain='finance', issues_found=3)
        """
        state = self.load_state()
        
        # Initialize current cycle if needed
        if 'current_cycle' not in state:
            state['current_cycle'] = {
                'started_at': datetime.now().isoformat(),
                'debug': None,
                'compliance': None,
                'improve': None
            }
        
        # Record workflow completion with metadata
        state['current_cycle'][workflow] = {
            'completed_at': datetime.now().isoformat(),
            **kwargs
        }
        
        # Initialize history if needed
        if 'history' not in state:
            state['history'] = []
        
        # Check if cycle is complete (all three workflows done)
        cycle = state['current_cycle']
        if all(cycle.get(w) for w in ['debug', 'compliance', 'improve']):
            # Archive completed cycle
            state['history'].append(cycle.copy())
            
            # Start new cycle
            state['current_cycle'] = {
                'started_at': datetime.now().isoformat(),
                'debug': None,
                'compliance': None,
                'improve': None
            }
        
        self.save_state(state)
    
    def get_current_cycle(self) -> Dict[str, Any]:
        """Get the current workflow cycle state.
        
        Returns:
            Dictionary containing current cycle progress with workflow completion status.
        """
        state = self.load_state()
        return state.get('current_cycle', {
            'started_at': datetime.now().isoformat(),
            'debug': None,
            'compliance': None,
            'improve': None
        })
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get completed workflow cycle history.
        
        Returns:
            List of completed workflow cycles, ordered chronologically.
        """
        state = self.load_state()
        return state.get('history', [])
    
    def get_next_recommended_workflow(self) -> Optional[str]:
        """Get the next recommended workflow based on current state.
        
        Implements the Arc Loop guidance:
        - If no workflows completed: recommend 'debug'
        - If debug completed: recommend 'compliance' 
        - If debug + compliance completed: recommend 'improve'
        - If all completed: recommend 'debug' (start new cycle)
        
        Returns:
            Recommended workflow name, or None if state is unclear.
        """
        cycle = self.get_current_cycle()
        
        # Check completion status
        debug_done = cycle.get('debug') is not None
        compliance_done = cycle.get('compliance') is not None
        improve_done = cycle.get('improve') is not None
        
        # Arc Loop progression logic
        if not debug_done:
            return 'debug'
        elif not compliance_done:
            return 'compliance'
        elif not improve_done:
            return 'improve'
        else:
            # Cycle complete - suggest starting new cycle with debug
            return 'debug'
    
    def get_cycle_statistics(self) -> Dict[str, Any]:
        """Get statistics about workflow cycle progression.
        
        Returns:
            Dictionary containing:
            - total_cycles: Number of completed cycles
            - current_cycle_progress: Percentage of current cycle completed
            - average_cycle_duration: Average time to complete a full cycle
            - most_recent_improvements: Performance deltas from recent cycles
        """
        history = self.get_workflow_history()
        current = self.get_current_cycle()
        
        # Calculate current cycle progress
        workflows_completed = sum(1 for w in ['debug', 'compliance', 'improve'] 
                                 if current.get(w) is not None)
        current_progress = (workflows_completed / 3) * 100
        
        # Calculate average cycle duration for completed cycles
        avg_duration = None
        if history:
            durations = []
            for cycle in history:
                if all(cycle.get(w) for w in ['debug', 'compliance', 'improve']):
                    try:
                        start = datetime.fromisoformat(cycle['started_at'])
                        # Use improve completion as cycle end time
                        end = datetime.fromisoformat(cycle['improve']['completed_at'])
                        durations.append((end - start).total_seconds() / 3600)  # hours
                    except (ValueError, KeyError):
                        continue
            
            if durations:
                avg_duration = sum(durations) / len(durations)
        
        # Extract recent performance improvements
        recent_improvements = []
        for cycle in history[-5:]:  # Last 5 cycles
            compliance = cycle.get('compliance', {})
            improve = cycle.get('improve', {})
            
            if isinstance(compliance, dict) and isinstance(improve, dict):
                baseline_rate = compliance.get('pass_rate')
                improved_rate = improve.get('pass_rate')
                
                if baseline_rate is not None and improved_rate is not None:
                    delta = improved_rate - baseline_rate
                    recent_improvements.append({
                        'cycle_start': cycle['started_at'],
                        'baseline_pass_rate': baseline_rate,
                        'improved_pass_rate': improved_rate,
                        'improvement_delta': delta
                    })
        
        return {
            'total_cycles': len(history),
            'current_cycle_progress': current_progress,
            'average_cycle_duration_hours': avg_duration,
            'recent_improvements': recent_improvements
        }
    
    def clear_state(self) -> None:
        """Clear all workflow state (useful for testing or reset).
        
        Removes the state file to start fresh. Use with caution as this
        will lose all workflow history and progress tracking.
        """
        if self.state_file.exists():
            self.state_file.unlink()


# Global instance for backward compatibility with existing CLI code
_default_manager = WorkflowStateManager()

# Backward compatibility functions
def load_workflow_state() -> Dict[str, Any]:
    """Load workflow state from disk (backward compatibility function)."""
    return _default_manager.load_state()

def save_workflow_state(state: Dict[str, Any]) -> None:
    """Save workflow state to disk (backward compatibility function)."""
    _default_manager.save_state(state)

def update_workflow_progress(workflow: str, **kwargs) -> None:
    """Update workflow progress tracking (backward compatibility function)."""
    _default_manager.update_workflow_progress(workflow, **kwargs)
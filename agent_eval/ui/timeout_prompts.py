"""
Timeout-aware interactive prompts for automation-friendly CLI.
"""

import os
import signal
from typing import Optional, List, Union
from rich.prompt import Prompt, Confirm
from rich.console import Console

console = Console()


class TimeoutError(Exception):
    """Raised when a prompt times out."""
    pass


class TimeoutPrompt:
    """Timeout-aware prompt utilities for automation environments."""
    
    @staticmethod
    def get_timeout() -> int:
        """Get timeout value from environment or default."""
        # Check for automation environment variables
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS') or os.getenv('AUTOMATION_MODE'):
            return 5  # 5 seconds in CI/automation
        
        # Check for explicit timeout setting
        timeout_env = os.getenv('ARC_EVAL_TIMEOUT', '30')
        try:
            return int(timeout_env)
        except ValueError:
            return 30  # Default 30 seconds
    
    @staticmethod
    def ask(
        prompt: str,
        *,
        choices: Optional[List[str]] = None,
        default: Optional[str] = None,
        timeout: Optional[int] = None,
        automation_default: Optional[str] = None
    ) -> str:
        """
        Timeout-aware prompt that automatically uses defaults in automation.
        
        Args:
            prompt: The prompt message
            choices: Valid choices (if any)
            default: Default value for interactive use
            timeout: Timeout in seconds (uses environment default if None)
            automation_default: Default to use in automation (uses default if None)
        
        Returns:
            User input or default value
        """
        # Check if we're in automation mode
        if TimeoutPrompt._is_automation_mode():
            result = automation_default or default
            if result is None:
                if choices:
                    result = choices[0]
                else:
                    result = ""
            console.print(f"[dim]Automation mode: Using default '{result}' for: {prompt}[/dim]")
            return result
        
        # Use timeout if specified
        if timeout is None:
            timeout = TimeoutPrompt.get_timeout()
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Prompt timed out after {timeout} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            # Use Rich's Prompt with timeout protection
            result = Prompt.ask(prompt, choices=choices, default=default)
            signal.alarm(0)  # Cancel timeout
            return result
            
        except (TimeoutError, KeyboardInterrupt):
            signal.alarm(0)  # Cancel timeout
            # Use default or first choice on timeout
            result = default
            if result is None and choices:
                result = choices[0]
            if result is None:
                result = ""
            
            console.print(f"\n[yellow]⏰ Timeout: Using default '{result}'[/yellow]")
            return result
            
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    @staticmethod
    def confirm(
        prompt: str,
        *,
        default: bool = True,
        timeout: Optional[int] = None,
        automation_default: Optional[bool] = None
    ) -> bool:
        """
        Timeout-aware confirmation prompt.
        
        Args:
            prompt: The confirmation message
            default: Default value for interactive use
            timeout: Timeout in seconds (uses environment default if None)
            automation_default: Default to use in automation (uses default if None)
        
        Returns:
            User confirmation or default value
        """
        # Check if we're in automation mode
        if TimeoutPrompt._is_automation_mode():
            result = automation_default if automation_default is not None else default
            console.print(f"[dim]Automation mode: Using default '{result}' for: {prompt}[/dim]")
            return result
        
        # Use timeout if specified
        if timeout is None:
            timeout = TimeoutPrompt.get_timeout()
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Confirmation timed out after {timeout} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            # Use Rich's Confirm with timeout protection
            result = Confirm.ask(prompt, default=default)
            signal.alarm(0)  # Cancel timeout
            return result
            
        except (TimeoutError, KeyboardInterrupt):
            signal.alarm(0)  # Cancel timeout
            console.print(f"\n[yellow]⏰ Timeout: Using default '{default}'[/yellow]")
            return default
            
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    @staticmethod
    def _is_automation_mode() -> bool:
        """Check if we're running in an automation environment."""
        automation_indicators = [
            'CI',
            'GITHUB_ACTIONS', 
            'GITLAB_CI',
            'JENKINS_URL',
            'AUTOMATION_MODE',
            'ARC_EVAL_NO_INTERACTIVE'
        ]
        
        return any(os.getenv(var) for var in automation_indicators)


# Convenience functions for backward compatibility
def timeout_ask(*args, **kwargs) -> str:
    """Convenience function for timeout-aware ask."""
    return TimeoutPrompt.ask(*args, **kwargs)


def timeout_confirm(*args, **kwargs) -> bool:
    """Convenience function for timeout-aware confirm."""
    return TimeoutPrompt.confirm(*args, **kwargs)

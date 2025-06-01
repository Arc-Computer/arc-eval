"""
Base command handler for ARC-Eval CLI commands.

Provides common interface and utilities for all command handlers with
standardized error handling, logging, and validation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import logging
import json
import sys
from pathlib import Path

from agent_eval.core.types import AgentOutput

logger = logging.getLogger(__name__)


class CommandError(Exception):
    """Base exception for command execution errors."""
    pass


class ValidationError(CommandError):
    """Exception raised for validation errors."""
    pass


class InputError(CommandError):
    """Exception raised for input file or data errors."""
    pass


class BaseCommandHandler(ABC):
    """Base class for all command handlers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, **kwargs) -> int:
        """Execute the command with given parameters.
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        pass
    
    def _load_raw_data(self, input_file: Optional[Path], stdin: bool = False) -> Any:
        """Load raw JSON data from file or stdin without conversion.

        Args:
            input_file: Path to input file
            stdin: Whether to read from stdin

        Returns:
            Parsed JSON data

        Raises:
            InputError: If file not found or JSON parsing fails
            ValidationError: If no input source provided
        """
        # Validate input sources
        if not input_file and not stdin:
            raise ValidationError("No input source provided. Specify --input file or --stdin")

        # Warn if both input sources are provided
        if input_file and stdin:
            self.logger.warning("Both --input and --stdin provided. Using file input, ignoring stdin.")

        try:
            if stdin and not input_file:
                data = json.load(sys.stdin)
                self.logger.debug("Successfully loaded data from stdin")
            else:
                if not input_file or not input_file.exists():
                    raise InputError(f"Input file not found: {input_file}")

                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.debug(f"Successfully loaded data from {input_file}")

        except json.JSONDecodeError as e:
            source = "stdin" if stdin and not input_file else str(input_file)
            raise InputError(f"Invalid JSON from {source}: {e}") from e
        except OSError as e:
            raise InputError(f"Failed to read file {input_file}: {e}") from e

        return data
    
    def _load_agent_outputs(self, input_file: Optional[Path], stdin: bool = False) -> List[AgentOutput]:
        """Load agent outputs from file or stdin and convert to AgentOutput objects.

        Args:
            input_file: Path to input file
            stdin: Whether to read from stdin

        Returns:
            List of AgentOutput objects

        Raises:
            ValidationError: If data format is invalid
            InputError: If file loading fails
        """
        data = self._load_raw_data(input_file, stdin)

        # Convert to AgentOutput objects
        agent_outputs = []
        try:
            if isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        agent_outputs.append(AgentOutput.from_dict(item))
                    else:
                        self.logger.warning(f"Skipping non-dict item at index {i}: {type(item)}")
            elif isinstance(data, dict):
                agent_outputs.append(AgentOutput.from_dict(data))
            else:
                raise ValidationError(f"Invalid data format: expected list or dict, got {type(data)}")
        except Exception as e:
            raise ValidationError(f"Failed to parse agent outputs: {e}") from e

        if not agent_outputs:
            raise ValidationError("No valid agent outputs found in input data")

        self.logger.info(f"Successfully loaded {len(agent_outputs)} agent outputs")
        return agent_outputs
    
    def _setup_logging(self, verbose: bool, dev: bool) -> None:
        """Setup logging configuration."""
        level = logging.DEBUG if (verbose or dev) else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _validate_required_params(self, required_params: List[str], **kwargs) -> None:
        """Validate that required parameters are provided.

        Args:
            required_params: List of parameter names that must be provided
            **kwargs: Parameters to validate

        Raises:
            ValidationError: If any required parameters are missing
        """
        missing = [param for param in required_params if not kwargs.get(param)]
        if missing:
            raise ValidationError(f"Missing required parameters: {', '.join(missing)}")

    def _handle_command_error(self, error: Exception, verbose: bool = False) -> int:
        """Handle command errors with consistent logging and exit codes.

        Args:
            error: Exception that occurred
            verbose: Whether to show full traceback

        Returns:
            Appropriate exit code based on error type
        """
        if isinstance(error, ValidationError):
            self.logger.error(f"Validation Error: {error}")
            return 2  # Invalid arguments
        elif isinstance(error, InputError):
            self.logger.error(f"Input Error: {error}")
            return 3  # Input file/data error
        elif isinstance(error, CommandError):
            self.logger.error(f"Command Error: {error}")
            return 1  # General command failure
        else:
            self.logger.error(f"Unexpected error: {error}")
            if verbose:
                self.logger.exception("Full traceback:")
            return 1  # General failure

"""
Base command handler for ARC-Eval CLI commands.

Provides common interface and utilities for all command handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

from agent_eval.core.types import AgentOutput

logger = logging.getLogger(__name__)


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
    
    def _load_raw_data(self, input_file: Optional[Path], stdin: bool) -> Any:
        """Load raw JSON data from file or stdin without conversion."""
        import sys
        import json
        
        # Warn if both input sources are provided
        if input_file and stdin:
            self.logger.warning("Both --input and --stdin provided. Using file input, ignoring stdin.")
        
        if stdin and not input_file:
            try:
                data = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON from stdin: {e}")
                raise
        else:
            if not input_file or not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in file {input_file}: {e}")
                raise
        
        return data
    
    def _load_agent_outputs(self, input_file: Optional[Path], stdin: bool) -> List[AgentOutput]:
        """Load agent outputs from file or stdin and convert to AgentOutput objects."""
        data = self._load_raw_data(input_file, stdin)
        
        # Convert to AgentOutput objects
        agent_outputs = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    agent_outputs.append(AgentOutput.from_dict(item))
                else:
                    self.logger.warning(f"Skipping non-dict item: {item}")
        elif isinstance(data, dict):
            agent_outputs.append(AgentOutput.from_dict(data))
        else:
            raise ValueError(f"Invalid data format: expected list or dict, got {type(data)}")
        
        return agent_outputs
    
    def _setup_logging(self, verbose: bool, dev: bool) -> None:
        """Setup logging configuration."""
        level = logging.DEBUG if (verbose or dev) else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _validate_required_params(self, required_params: List[str], **kwargs) -> None:
        """Validate that required parameters are provided."""
        missing = [param for param in required_params if not kwargs.get(param)]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
"""
Configuration management system for ARC-Eval.
Provides centralized loading, saving, and validation of configuration files.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceConfig:
    """Confidence calibration configuration."""
    base_threshold: float = 0.85
    critical_domain_threshold: float = 0.95
    failure_threshold: float = 0.75
    cerebras_adjustment: float = 0.0
    gemini_adjustment: float = 0.0


@dataclass
class CostProtectionConfig:
    """Cost protection settings."""
    qa_skip_threshold: float = 0.8
    emergency_fallback_threshold: float = 0.95


@dataclass
class PerformanceProtectionConfig:
    """Performance protection settings."""
    max_cerebras_time: float = 10.0
    max_total_time: float = 30.0


@dataclass
class DataCollectionConfig:
    """Calibration data collection settings."""
    enabled: bool = True
    sample_rate: float = 1.0
    export_interval: int = 100


@dataclass
class APIConfig:
    """API provider configuration."""
    anthropic_model: str = "claude-3-5-haiku-20241022"
    openai_model: str = "gpt-4.1-mini-2025-04-14"
    gemini_model: str = "gemini-2.5-flash-preview-05-20"
    cerebras_model: str = "llama-4-scout-17b-16e-instruct"
    cost_threshold: float = 10.0


@dataclass
class ArcEvalConfig:
    """Main ARC-Eval configuration."""
    default_domain: str = "finance"
    interactive_mode: bool = True
    confidence: ConfidenceConfig = None
    cost_protection: CostProtectionConfig = None
    performance_protection: PerformanceProtectionConfig = None
    data_collection: DataCollectionConfig = None
    api: APIConfig = None
    
    def __post_init__(self):
        """Initialize nested configs with defaults if not provided."""
        if self.confidence is None:
            self.confidence = ConfidenceConfig()
        if self.cost_protection is None:
            self.cost_protection = CostProtectionConfig()
        if self.performance_protection is None:
            self.performance_protection = PerformanceProtectionConfig()
        if self.data_collection is None:
            self.data_collection = DataCollectionConfig()
        if self.api is None:
            self.api = APIConfig()


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_paths = [
            Path.home() / ".arc-eval" / "config.yaml",  # User config
            Path("agent_eval/config/confidence_thresholds.yaml"),  # Confidence config
            Path(".arc-eval-config.yaml"),  # Project config
        ]
        self._config_cache: Optional[ArcEvalConfig] = None
    
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> ArcEvalConfig:
        """Load configuration from file or defaults.
        
        Args:
            config_path: Optional specific config file path
            
        Returns:
            ArcEvalConfig object with loaded or default settings
        """
        if self._config_cache is not None:
            return self._config_cache
        
        config_data = {}
        
        # Load from specific path if provided
        if config_path:
            config_data = self._load_yaml_file(Path(config_path))
        else:
            # Load from standard paths in order of precedence
            for path in self.config_paths:
                if path.exists():
                    file_data = self._load_yaml_file(path)
                    if file_data:
                        # Merge configs (later files override earlier ones)
                        config_data = self._merge_configs(config_data, file_data)
        
        # Convert to structured config
        config = self._dict_to_config(config_data)
        self._config_cache = config
        return config
    
    def save_config(self, config: ArcEvalConfig, config_path: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: ArcEvalConfig object to save
            config_path: Optional specific path to save to (defaults to user config)
        """
        if config_path is None:
            config_path = self.config_paths[0]  # User config path
        else:
            config_path = Path(config_path)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert config to dict and save
        config_dict = asdict(config)
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {config_path}")
            
            # Clear cache to force reload
            self._config_cache = None
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise
    
    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        """Load YAML file safely."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded config from {path}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ArcEvalConfig:
        """Convert dictionary to ArcEvalConfig object."""
        # Handle legacy confidence_thresholds format
        if "confidence_thresholds" in data:
            confidence_data = data["confidence_thresholds"]
            data["confidence"] = confidence_data
        
        # Extract nested configs
        confidence_config = ConfidenceConfig(**data.get("confidence", {}))
        cost_protection_config = CostProtectionConfig(**data.get("cost_protection", {}))
        performance_protection_config = PerformanceProtectionConfig(**data.get("performance_protection", {}))
        data_collection_config = DataCollectionConfig(**data.get("data_collection", {}))
        api_config = APIConfig(**data.get("api", {}))
        
        return ArcEvalConfig(
            default_domain=data.get("default_domain", "finance"),
            interactive_mode=data.get("interactive_mode", True),
            confidence=confidence_config,
            cost_protection=cost_protection_config,
            performance_protection=performance_protection_config,
            data_collection=data_collection_config,
            api=api_config
        )


# Global configuration manager instance
_config_manager = ConfigManager()


def load_config(config_path: Optional[Union[str, Path]] = None) -> ArcEvalConfig:
    """Load configuration (convenience function).
    
    Args:
        config_path: Optional specific config file path
        
    Returns:
        ArcEvalConfig object
    """
    return _config_manager.load_config(config_path)


def save_config(config: ArcEvalConfig, config_path: Optional[Union[str, Path]] = None) -> None:
    """Save configuration (convenience function).
    
    Args:
        config: ArcEvalConfig object to save
        config_path: Optional specific path to save to
    """
    _config_manager.save_config(config, config_path)


def get_confidence_thresholds() -> ConfidenceConfig:
    """Get confidence threshold configuration."""
    config = load_config()
    return config.confidence


def get_cost_protection() -> CostProtectionConfig:
    """Get cost protection configuration."""
    config = load_config()
    return config.cost_protection


def get_performance_protection() -> PerformanceProtectionConfig:
    """Get performance protection configuration."""
    config = load_config()
    return config.performance_protection

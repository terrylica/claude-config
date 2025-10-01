"""
Configuration management for MQL5 extraction system.

Handles loading, validation, and merging of YAML configuration with CLI overrides.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ExtractionConfig:
    """Extraction-specific configuration."""
    output_dir: str = "simple_extraction_results"
    headless: bool = True
    timeout_ms: int = 30000


@dataclass
class RetryConfig:
    """Retry policy configuration."""
    max_attempts: int = 3
    initial_backoff_seconds: float = 5.0
    max_backoff_seconds: float = 60.0
    exponential_base: float = 2.0


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    rate_limit_seconds: float = 2.0
    checkpoint_file: str = ".extraction_checkpoint.json"
    resume_on_restart: bool = True
    continue_on_error: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: str = "extraction.log"
    console: bool = True


@dataclass
class ValidationConfig:
    """Quality validation configuration."""
    min_word_count: int = 500
    min_code_blocks: int = 1
    reject_login_popup: bool = True


@dataclass
class DiscoveryConfig:
    """URL discovery configuration."""
    default_user_id: str = "29210372"


@dataclass
class Config:
    """Main configuration container."""
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)


class ConfigManager:
    """
    Manages configuration loading, validation, and CLI override merging.

    Example:
        >>> config_mgr = ConfigManager("config.yaml")
        >>> config = config_mgr.load()
        >>> config.extraction.output_dir
        'simple_extraction_results'
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML config file (optional)
        """
        self.config_path = Path(config_path) if config_path else None
        self._config: Optional[Config] = None

    def load(self) -> Config:
        """
        Load configuration from file and merge with defaults.

        Returns:
            Loaded configuration object

        Raises:
            FileNotFoundError: If config file specified but not found
            yaml.YAMLError: If config file has invalid YAML syntax
        """
        # Start with defaults
        config_dict = self._get_defaults()

        # Merge with file config if provided
        if self.config_path and self.config_path.exists():
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
                config_dict = self._deep_merge(config_dict, file_config)
        elif self.config_path:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        # Convert to dataclass objects
        self._config = self._dict_to_config(config_dict)
        return self._config

    def apply_overrides(self, overrides: Dict[str, Any]) -> Config:
        """
        Apply CLI overrides to loaded configuration.

        Args:
            overrides: Dictionary of override values (dot notation keys)
                      Example: {"extraction.output_dir": "my_output"}

        Returns:
            Updated configuration

        Example:
            >>> config = config_mgr.load()
            >>> config = config_mgr.apply_overrides({"extraction.headless": False})
        """
        if not self._config:
            self._config = self.load()

        for key, value in overrides.items():
            self._set_nested(self._config, key, value)

        return self._config

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration as dictionary."""
        return {
            "extraction": {
                "output_dir": "simple_extraction_results",
                "headless": True,
                "timeout_ms": 30000
            },
            "retry": {
                "max_attempts": 3,
                "initial_backoff_seconds": 5.0,
                "max_backoff_seconds": 60.0,
                "exponential_base": 2.0
            },
            "batch": {
                "rate_limit_seconds": 2.0,
                "checkpoint_file": ".extraction_checkpoint.json",
                "resume_on_restart": True,
                "continue_on_error": True
            },
            "logging": {
                "level": "INFO",
                "file": "extraction.log",
                "console": True
            },
            "validation": {
                "min_word_count": 500,
                "min_code_blocks": 1,
                "reject_login_popup": True
            },
            "discovery": {
                "default_user_id": "29210372"
            }
        }

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _dict_to_config(self, config_dict: Dict) -> Config:
        """Convert dictionary to Config dataclass."""
        return Config(
            extraction=ExtractionConfig(**config_dict.get("extraction", {})),
            retry=RetryConfig(**config_dict.get("retry", {})),
            batch=BatchConfig(**config_dict.get("batch", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
            validation=ValidationConfig(**config_dict.get("validation", {})),
            discovery=DiscoveryConfig(**config_dict.get("discovery", {}))
        )

    def _set_nested(self, obj: Any, path: str, value: Any):
        """Set nested attribute using dot notation."""
        parts = path.split('.')
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    def save(self, path: Optional[str] = None):
        """
        Save current configuration to YAML file.

        Args:
            path: Output path (defaults to original config_path)
        """
        if not self._config:
            raise RuntimeError("No configuration loaded to save")

        save_path = Path(path) if path else self.config_path
        if not save_path:
            raise ValueError("No save path specified")

        config_dict = self._config_to_dict(self._config)
        with open(save_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def _config_to_dict(self, config: Config) -> Dict:
        """Convert Config dataclass to dictionary."""
        return {
            "extraction": {
                "output_dir": config.extraction.output_dir,
                "headless": config.extraction.headless,
                "timeout_ms": config.extraction.timeout_ms
            },
            "retry": {
                "max_attempts": config.retry.max_attempts,
                "initial_backoff_seconds": config.retry.initial_backoff_seconds,
                "max_backoff_seconds": config.retry.max_backoff_seconds,
                "exponential_base": config.retry.exponential_base
            },
            "batch": {
                "rate_limit_seconds": config.batch.rate_limit_seconds,
                "checkpoint_file": config.batch.checkpoint_file,
                "resume_on_restart": config.batch.resume_on_restart,
                "continue_on_error": config.batch.continue_on_error
            },
            "logging": {
                "level": config.logging.level,
                "file": config.logging.file,
                "console": config.logging.console
            },
            "validation": {
                "min_word_count": config.validation.min_word_count,
                "min_code_blocks": config.validation.min_code_blocks,
                "reject_login_popup": config.validation.reject_login_popup
            },
            "discovery": {
                "default_user_id": config.discovery.default_user_id
            }
        }

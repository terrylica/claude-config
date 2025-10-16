"""
Logging configuration for MQL5 extraction system.

Provides structured logging to both console and file with configurable levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO",
    console: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logger with file and console handlers.

    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Path to log file (optional)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        console: Whether to output to console
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__, log_file="extraction.log", level="DEBUG")
        >>> logger.info("Starting extraction", extra={"article_id": "19625"})
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Default format with timestamp and level
    if format_string is None:
        format_string = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

    formatter = logging.Formatter(
        format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Only show INFO and above on console by default
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for temporary log level changes.

    Example:
        >>> logger = setup_logger(__name__)
        >>> with LogContext(logger, "DEBUG"):
        ...     logger.debug("This will be logged")
    """

    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
        return False

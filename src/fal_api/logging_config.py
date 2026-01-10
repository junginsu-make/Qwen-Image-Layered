"""
Centralized logging configuration for Qwen-Image-Layered.

Provides consistent logging across all modules with:
- Configurable log levels
- File and console handlers
- Structured log formatting
- Cost tracking integration
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# Log level mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class LoggerFactory:
    """Factory for creating and managing loggers."""

    _initialized: bool = False
    _log_dir: Optional[Path] = None
    _file_handler: Optional[logging.FileHandler] = None
    _console_handler: Optional[logging.StreamHandler] = None
    _log_level: int = logging.INFO

    @classmethod
    def initialize(
        cls,
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        log_to_file: bool = False,
        log_to_console: bool = True,
        detailed_format: bool = False,
    ) -> None:
        """
        Initialize the logging system.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (default: ./logs)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            detailed_format: Use detailed format with file/line info
        """
        if cls._initialized:
            return

        cls._log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)

        # Set up log directory
        if log_to_file:
            if log_dir:
                cls._log_dir = Path(log_dir)
            else:
                cls._log_dir = Path.cwd() / "logs"
            cls._log_dir.mkdir(parents=True, exist_ok=True)

        # Choose format
        log_format = DETAILED_FORMAT if detailed_format else DEFAULT_FORMAT
        formatter = logging.Formatter(log_format)

        # Set up root logger for the package
        root_logger = logging.getLogger("fal_api")
        root_logger.setLevel(cls._log_level)

        # Clear existing handlers
        root_logger.handlers = []

        # Console handler
        if log_to_console:
            cls._console_handler = logging.StreamHandler(sys.stdout)
            cls._console_handler.setLevel(cls._log_level)
            cls._console_handler.setFormatter(formatter)
            root_logger.addHandler(cls._console_handler)

        # File handler
        if log_to_file and cls._log_dir:
            log_file = cls._log_dir / f"fal_api_{datetime.now().strftime('%Y%m%d')}.log"
            cls._file_handler = logging.FileHandler(log_file, encoding="utf-8")
            cls._file_handler.setLevel(cls._log_level)
            cls._file_handler.setFormatter(formatter)
            root_logger.addHandler(cls._file_handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Logger name (usually module name)

        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()

        # Create child logger under fal_api namespace
        if name.startswith("fal_api."):
            logger_name = name
        else:
            logger_name = f"fal_api.{name}"

        return logging.getLogger(logger_name)

    @classmethod
    def set_level(cls, level: str) -> None:
        """Change log level for all loggers."""
        cls._log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        root_logger = logging.getLogger("fal_api")
        root_logger.setLevel(cls._log_level)

        if cls._console_handler:
            cls._console_handler.setLevel(cls._log_level)
        if cls._file_handler:
            cls._file_handler.setLevel(cls._log_level)

    @classmethod
    def reset(cls) -> None:
        """Reset logging configuration."""
        root_logger = logging.getLogger("fal_api")
        root_logger.handlers = []
        cls._initialized = False
        cls._file_handler = None
        cls._console_handler = None


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return LoggerFactory.get_logger(name)


def configure_logging(
    level: str = "INFO",
    log_dir: Optional[str] = None,
    log_to_file: bool = False,
    detailed: bool = False,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_to_file: Enable file logging
        detailed: Use detailed format
    """
    LoggerFactory.initialize(
        log_level=level,
        log_dir=log_dir,
        log_to_file=log_to_file,
        log_to_console=True,
        detailed_format=detailed,
    )


# Environment-based initialization
def _auto_configure():
    """Auto-configure from environment variables."""
    level = os.environ.get("FAL_LOG_LEVEL", "INFO")
    log_dir = os.environ.get("FAL_LOG_DIR")
    log_to_file = os.environ.get("FAL_LOG_TO_FILE", "").lower() == "true"
    detailed = os.environ.get("FAL_LOG_DETAILED", "").lower() == "true"

    LoggerFactory.initialize(
        log_level=level,
        log_dir=log_dir,
        log_to_file=log_to_file,
        log_to_console=True,
        detailed_format=detailed,
    )


# Auto-configure on import if environment variable is set
if os.environ.get("FAL_AUTO_LOG", "").lower() == "true":
    _auto_configure()

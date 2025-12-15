"""Logging utilities for the Audio Transcription App."""

import logging
import os
import sys

# Default log level
DEFAULT_LOG_LEVEL = "INFO"


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages."""

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[91m\033[1m",  # Bold Red
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        """Format the log message with colors based on the log level."""
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{self.COLORS['RESET']}"


def setup_logger(name: str = "audio_transcription", level: int = None) -> logging.Logger:
    """Configure and return a logger with colored output.

    Args:
        name: Logger name
        level: Logging level (int). If None, reads from LOG_LEVEL env var or defaults to INFO

    Returns:
        Configured logger instance

    """
    # Determine log level: use provided level, or read from env var, or use constant default
    if level is None:
        # Priority: env var > constant default
        log_level_str = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
        level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)

    # Prevent propagation to the root logger
    logger.propagate = False

    return logger


# Create and export default logger instance
logger = setup_logger()


def set_log_level(level: str) -> None:
    """Set the logging level for the default logger.

    Args:
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logger.setLevel(numeric_level)
    for handler in logger.handlers:
        handler.setLevel(numeric_level)

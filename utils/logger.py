"""
Logging configuration.

Provides a centralized logger setup for the application.
Full implementation enhanced in Phase 15 (file logging, rotation, etc.).
"""

import logging
import sys


def setup_logger(
    name: str = "ai_db_assistant",
    level: int = logging.INFO,
) -> logging.Logger:
    """Set up and return a configured logger.

    Creates a logger with a stdout handler and consistent formatting.
    Avoids adding duplicate handlers on repeated calls.

    Args:
        name: The logger name (used as a namespace).
        level: The logging level (default: INFO).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger

"""
Module for robust logging with file rotation and unit tests.
"""

import logging
import os
import unittest
from typing import Optional

from loguru import logger


def configure_logging(
    log_file: str, log_level: str = "INFO", rotation: str = "10MB"
) -> None:
    """
    Configures logging to a file with rotation.

    Args:
        log_file: The path to the log file.
        log_level: The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
        rotation:  The rotation size (e.g., "10MB", "1 week").
    """
    try:
        logger.remove()  # Remove default handlers
        logger.add(
            log_file,
            rotation=rotation,
            level=log_level,
            format="{time} - {level} - {message}",
            enqueue=True,
            # Prevent race conditions with the test and make it easier to
            # clean up files.  This might affect performance slightly,
            # but is acceptable for a test.
            # delay=True,
        )
        logger.info(f"Logging configured to {log_file} with rotation {rotation}")
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")


def log_something(message: str) -> None:
    """Logs a message.

    Args:
        message: The message to log.
    """
    try:
        logger.debug(message)
    except Exception as e:
        logger.error(f"Failed to log message: {e}")
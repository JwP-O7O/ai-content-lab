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


class TestRobustLogger(unittest.TestCase):
    """
    Unit tests for the robust logger.
    """

    LOG_FILE = "test.log"
    LOG_LEVEL = "DEBUG"
    ROTATION = "100B"  # Small rotation for testing
    TEST_MESSAGE = "This is a test message."

    def setUp(self) -> None:
        """
        Set up for each test.
        """
        configure_logging(self.LOG_FILE, self.LOG_LEVEL, self.ROTATION)
        # Ensure log file exists if rotation is triggered immediately.
        with open(self.LOG_FILE, "w") as f:
            pass

    def tearDown(self) -> None:
        """
        Clean up after each test.
        """
        try:
            os.remove(self.LOG_FILE)
        except FileNotFoundError:
            pass  # Ignore if file doesn't exist.
        except Exception as e:
            logger.error(f"Failed to clean up test file: {e}")

    def test_log_message(self) -> None:
        """
        Test that a message is logged.
        """
        try:
            log_something(self.TEST_MESSAGE)
            with open(self.LOG_FILE, "r") as f:
                log_content = f.read()
                self.assertIn(self.TEST_MESSAGE, log_content)
        except Exception as e:
            self.fail(f"Logging failed: {e}")

    def test_log_rotation(self) -> None:
        """
        Test that log rotation occurs (basic check - no guarantees about the exact behavior).
        """
        try:
            # Write a few messages to trigger rotation.  This depends on the OS,
            # so the exact number may vary.
            for _ in range(10):  # increased to cover the log size
                log_something("A" * 100)  # write a message larger than rotation
            # Check if there are multiple files (or at least one rotated file,
            # meaning it was rotated).
            rotated_files = [
                f
                for f in os.listdir(".")
                if f.startswith(self.LOG_FILE) and f != self.LOG_FILE
            ]
            self.assertTrue(len(rotated_files) >= 1, "Log rotation did not occur.")

        except Exception as e:
            self.fail(f"Log rotation test failed: {e}")

    def test_log_level(self) -> None:
        """
        Test that log level filtering works.
        """
        try:
            configure_logging(self.LOG_FILE, "WARNING")  # Configure for WARNING
            log_something("This should not be logged")
            logger.debug("Debug message")  # this will not be logged.
            logger.warning("Warning message")  # this will be logged.
            with open(self.LOG_FILE, "r") as f:
                log_content = f.read()
                self.assertNotIn("This should not be logged", log_content)
                self.assertIn("Warning message", log_content)

        except Exception as e:
            self.fail(f"Log level test failed: {e}")


if __name__ == "__main__":
    configure_logging("app.log")
    log_something("Application started.")
    try:
        unittest.main()
    except Exception as e:
        logger.error(f"Unit tests failed: {e}")
    log_something("Application finished.")
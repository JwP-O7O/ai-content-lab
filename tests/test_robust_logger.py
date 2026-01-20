import pytest
import unittest
import os
import sys

from unittest.mock import patch, mock_open, MagicMock

# Add the current directory to the Python path
sys.path.append(os.getcwd())

from src.playground.robust_logger import configure_logging, log_something, logger


class TestRobustLogger:
    """
    Pytest tests for the robust logger.
    """

    LOG_FILE = "test.log"
    LOG_LEVEL = "DEBUG"
    ROTATION = "100B"  # Small rotation for testing
    TEST_MESSAGE = "This is a test message."

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """
        Pytest fixture to set up and tear down for each test.
        """
        # Setup
        configure_logging(self.LOG_FILE, self.LOG_LEVEL, self.ROTATION)
        with open(self.LOG_FILE, "w") as f:
            pass
        yield  # This is where the test runs
        # Teardown
        try:
            os.remove(self.LOG_FILE)
            rotated_files = [
                f
                for f in os.listdir(".")
                if f.startswith(self.LOG_FILE) and f != self.LOG_FILE
            ]
            for file in rotated_files:
                os.remove(file)
        except FileNotFoundError:
            pass  # Ignore if file doesn't exist.
        except Exception as e:
            print(f"Failed to clean up test file: {e}")

    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_log_message(self, mock_open):
        """
        Test that a message is logged.
        """
        log_something(self.TEST_MESSAGE)
        mock_open.assert_called_with(self.LOG_FILE, "r")
        mock_open().read.assert_called()
        log_content = mock_open().read()
        assert self.TEST_MESSAGE in log_content

    @patch('builtins.open', new_callable=mock_open)
    def test_log_rotation(self, mock_open):
        """
        Test that log rotation occurs (basic check - no guarantees about the exact behavior).
        """
        for _ in range(10):  # increased to cover the log size
            log_something("A" * 100)  # write a message larger than rotation
        mock_open.assert_called() # Check that open was called at least once
        rotated_files = [
            f
            for f in os.listdir(".")
            if f.startswith(self.LOG_FILE) and f != self.LOG_FILE
        ]
        assert len(rotated_files) >= 1, "Log rotation did not occur."


    @patch('builtins.open', new_callable=mock_open, read_data="")
    def test_log_level(self, mock_open):
        """
        Test that log level filtering works.
        """
        configure_logging(self.LOG_FILE, "WARNING")  # Configure for WARNING
        log_something("This should not be logged")
        logger.debug("Debug message")  # this will not be logged.
        logger.warning("Warning message")  # this will be logged.
        mock_open.assert_called_with(self.LOG_FILE, "r")
        mock_open().read.assert_called()
        log_content = mock_open().read()
        assert "This should not be logged" not in log_content
        assert "Warning message" in log_content
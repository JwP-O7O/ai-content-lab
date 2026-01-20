import os
import sys
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.robust_logger import configure_logging, log_something


class TestRobustLogger:
    @patch("src.playground.robust_logger.logger.add")
    @patch("src.playground.robust_logger.logger.remove")
    def test_configure_logging_success(self, mock_remove, mock_add):
        """Test configure_logging with success."""
        log_file = "test.log"
        log_level = "DEBUG"
        rotation = "100MB"

        configure_logging(log_file, log_level, rotation)

        mock_remove.assert_called_once()
        mock_add.assert_called_once_with(
            log_file,
            rotation=rotation,
            level=log_level,
            format="{time} - {level} - {message}",
            enqueue=True,
        )

    @patch("src.playground.robust_logger.logger.add")
    @patch("src.playground.robust_logger.logger.remove")
    def test_configure_logging_exception(self, mock_remove, mock_add):
        """Test configure_logging with exception."""
        mock_add.side_effect = Exception("Simulated error")
        log_file = "test.log"
        log_level = "DEBUG"
        rotation = "100MB"

        configure_logging(log_file, log_level, rotation)

        mock_remove.assert_called_once()
        mock_add.assert_called_once_with(
            log_file,
            rotation=rotation,
            level=log_level,
            format="{time} - {level} - {message}",
            enqueue=True,
        )

    @patch("src.playground.robust_logger.logger.debug")
    def test_log_something_success(self, mock_debug):
        """Test log_something with success."""
        message = "Test message"

        log_something(message)

        mock_debug.assert_called_once_with(message)

    @patch("src.playground.robust_logger.logger.debug")
    def test_log_something_exception(self, mock_debug):
        """Test log_something with exception."""
        mock_debug.side_effect = Exception("Simulated error")
        message = "Test message"

        log_something(message)

        mock_debug.assert_called_once_with(message)
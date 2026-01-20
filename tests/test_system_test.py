import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

sys.path.append(os.getcwd())
from src.playground.system_test import create_system_test_file

class TestCreateSystemTestFile:
    @patch('builtins.open', new_callable=mock_open)
    @patch('loguru.logger.info')
    def test_create_system_test_file_success(self, mock_info, mock_open_instance):
        filepath = "test.txt"
        content = "test content"
        mock_open_instance.return_value.__enter__.return_value.write.return_value = None  # Simulate successful write
        
        result = create_system_test_file(filepath, content)
        
        assert result is True
        mock_open_instance.assert_called_once_with(filepath, "w")
        mock_open_instance().write.assert_called_once_with(content)
        mock_info.assert_called_once_with(f"File '{filepath}' created successfully.")

    @patch('builtins.open', new_callable=mock_open)
    @patch('loguru.logger.error')
    def test_create_system_test_file_failure(self, mock_error, mock_open_instance):
        filepath = "test.txt"
        content = "test content"
        mock_open_instance.side_effect = IOError("Simulated error")
        
        result = create_system_test_file(filepath, content)
        
        assert result is False
        mock_open_instance.assert_called_once_with(filepath, "w")
        mock_error.assert_called_once()
        assert "Error creating file" in str(mock_error.call_args)
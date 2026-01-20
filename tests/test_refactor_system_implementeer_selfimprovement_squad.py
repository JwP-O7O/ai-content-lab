import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.refactor_system_implementeer_selfimprovement_squad import SystemRefactor
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.getcwd())


class TestSystemRefactor:
    @pytest.fixture
    def refactor_instance(self):
        return SystemRefactor(file_path="test_file.py")

    @pytest.fixture
    def mock_logger(self):
        with patch.object(logger, "info") as mock_info, \
             patch.object(logger, "error") as mock_error, \
             patch.object(logger, "warning") as mock_warning, \
             patch.object(logger, "success") as mock_success, \
             patch.object(logger, "critical") as mock_critical:
            yield mock_info, mock_error, mock_warning, mock_success, mock_critical

    def test_init(self):
        instance = SystemRefactor(file_path="my_file.py")
        assert instance.file_path == "my_file.py"
        assert instance.backup_path == "my_file.py.bak"

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_create_backup_success(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = False
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._create_backup() is True
        mock_copy2.assert_called_once_with("test_file.py", "test_file.py.bak")
        mock_info.assert_called_with("Backup created at: test_file.py.bak")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_create_backup_overwrite(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove") as mock_remove:
            assert instance._create_backup() is True
            mock_remove.assert_called_once_with("test_file.py.bak")
            mock_copy2.assert_called_once_with("test_file.py", "test_file.py.bak")
            mock_warning.assert_called_with(
                "Backup file already exists: test_file.py.bak. Overwriting."
            )
        mock_info.assert_called_with("Backup created at: test_file.py.bak")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_create_backup_failure(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = False
        mock_copy2.side_effect = OSError("Permission denied")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._create_backup() is False
        mock_error.assert_called_with(
            "Error creating backup: Permission denied"
        )

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_restore_backup_success(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._restore_backup() is True
        mock_copy2.assert_called_once_with("test_file.py.bak", "test_file.py")
        mock_info.assert_called_with("Restored from backup: test_file.py.bak")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_restore_backup_not_found(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = False
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._restore_backup() is False
        mock_error.assert_called_with("Backup file not found: test_file.py.bak")
        mock_copy2.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    def test_restore_backup_failure(self, mock_exists, mock_copy2, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = True
        mock_copy2.side_effect = OSError("Permission denied")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._restore_backup() is False
        mock_error.assert_called_with("Error restoring from backup: Permission denied")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info")
    def test_check_python_version_compatible(self, mock_version_info, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_version_info = MagicMock()
        mock_version_info.major = 3
        mock_version_info.minor = 8  # Compatible version
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._check_python_version() is True
        mock_info.assert_called_with("Python version check passed.")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info")
    def test_check_python_version_incompatible(self, mock_version_info, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_version_info = MagicMock()
        mock_version_info.major = 3
        mock_version_info.minor = 6  # Incompatible version
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._check_python_version() is False
        mock_error.assert_called_with(
            "Incompatible Python version.  Requires Python 3.7 or higher."
        )

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info")
    def test_check_python_version_exception(self, mock_version_info, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_version_info.side_effect = Exception("Simulated error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._check_python_version() is False
        mock_error.assert_called_with("Error checking Python version: Simulated error")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_format_code_success(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Formatted code"
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._format_code() is True
        mock_run.assert_called_once_with(["black", "test_file.py"], check=True, capture_output=True)
        mock_info.assert_called_with("Code formatted with black.")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_format_code_failure(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = subprocess.CalledProcessError(1, ["black", "test_file.py"], stderr=b"Formatting error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._format_code() is False
        mock_error.assert_called_with("Error formatting code with black: Command '['black', 'test_file.py']' returned non-zero exit status 1\nFormatting error")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_format_code_not_found(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = FileNotFoundError
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._format_code() is False
        mock_error.assert_called_with("Black not found. Please install it (pip install black).")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_format_code_unexpected_error(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = Exception("Unexpected error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._format_code() is False
        mock_error.assert_called_with("An unexpected error occurred during formatting: Unexpected error")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_success(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.return_value.stdout = "Test result: OK"
        mock_run.return_value.returncode = 0
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is True
        mock_info.assert_called_with("Test Results:\nTest result: OK")
        mock_info.assert_called_with("Tests passed.")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_failure(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.return_value.stdout = "FAILED"
        mock_run.return_value.returncode = 1
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is False
        mock_info.assert_called_with("Test Results:\nFAILED")
        mock_error.assert_called_with("Tests failed.")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_error_in_output(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.return_value.stdout = "ERROR"
        mock_run.return_value.returncode = 1
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is False
        mock_info.assert_called_with("Test Results:\nERROR")
        mock_error.assert_called_with("Tests failed.")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_subprocess_error(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = subprocess.CalledProcessError(1, ["pytest", "."], stderr="Test error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is False
        mock_error.assert_called_with("Error running tests:\nTest error")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_not_found(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = FileNotFoundError
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is False
        mock_error.assert_called_with("Pytest not found. Please install it (pip install pytest).")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
    def test_run_tests_unexpected_error(self, mock_run, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_run.side_effect = Exception("Unexpected error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance._run_tests() is False
        mock_error.assert_called_with("An unexpected error occurred during testing: Unexpected error")

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_success(self, mock_open, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = True
        mock_create_backup.return_value = True
        mock_format_code.return_value = True
        mock_run_tests.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is True
        mock_info.assert_called_with("Refactoring in progress (Extract Method)...")
        mock_success.assert_called_with("Refactoring completed successfully.")
        mock_error.assert_not_called()
        assert "Refactored using Extract Method (placeholder)" in mock_open.mock_calls[0][2]["mode"]
        
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_tests_fail(self, mock_open, mock_restore_backup, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = True
        mock_create_backup.return_value = True
        mock_format_code.return_value = True
        mock_run_tests.return_value = False
        mock_restore_backup.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is False
        mock_error.assert_called_with("Tests failed after refactoring. Restoring backup.")
        mock_restore_backup.assert_called_once()
        mock_success.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_format_fails(self, mock_open, mock_restore_backup, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = True
        mock_create_backup.return_value = True
        mock_format_code.return_value = False
        mock_run_tests.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is True
        mock_warning.assert_called_with("Code formatting failed, but continuing with refactoring.")
        mock_success.assert_called_with("Refactoring completed successfully.")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_python_version_fails(self, mock_open, mock_restore_backup, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = False
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is False
        mock_restore_backup.assert_not_called()
        mock_success.assert_not_called()
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_create_backup_fails(self, mock_open, mock_restore_backup, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = True
        mock_create_backup.return_value = False
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is False
        mock_restore_backup.assert_not_called()
        mock_success.assert_not_called()
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_refactor_unexpected_error(self, mock_open, mock_restore_backup, mock_run_tests, mock_format_code, mock_create_backup, mock_check_python_version, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_check_python_version.return_value = True
        mock_create_backup.return_value = True
        mock_format_code.return_value = True
        mock_run_tests.return_value = True
        mock_open.side_effect = OSError("File access error")
        instance = SystemRefactor(file_path="test_file.py")
        assert instance.refactor() is False
        mock_restore_backup.assert_called_once()
        mock_error.assert_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
    def test_cleanup_success(self, mock_remove, mock_exists, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = True
        instance = SystemRefactor(file_path="test_file.py")
        instance.cleanup()
        mock_remove.assert_called_once_with("test_file.py.bak")
        mock_info.assert_called_with("Backup file deleted: test_file.py.bak")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
    def test_cleanup_not_found(self, mock_remove, mock_exists, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = False
        instance = SystemRefactor(file_path="test_file.py")
        instance.cleanup()
        mock_remove.assert_not_called()
        mock_info.assert_called_with("No backup file to delete.")
        mock_error.assert_not_called()

    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
    @patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
    def test_cleanup_failure(self, mock_remove, mock_exists, mock_logger):
        mock_info, mock_error, mock_warning, mock_success, mock_critical = mock_logger
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        instance = SystemRefactor(file_path="test_file.py")
        instance.cleanup()
        mock_error.assert_called_with("Error deleting backup file: Permission denied")
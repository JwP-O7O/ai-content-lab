import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.refactor_system_implementeer_selfimprovement_squad import SystemRefactor
from loguru import logger


# Add the current directory to sys.path for relative imports
sys.path.append(os.getcwd())


@pytest.fixture
def system_refactor_instance():
    """Provides a SystemRefactor instance for testing."""
    return SystemRefactor(file_path="test_file.py")


@pytest.fixture
def mock_logger():
    """Provides a mocked logger for testing."""
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger") as mock_logger:
        yield mock_logger


def test_system_refactor_init(system_refactor_instance):
    """Tests the initialization of the SystemRefactor class."""
    assert system_refactor_instance.file_path == "test_file.py"
    assert system_refactor_instance.backup_path == "test_file.py.bak"


@pytest.mark.parametrize("backup_exists, remove_success, expected_return", [
    (False, True, True),
    (True, True, True),
    (True, False, False),
])
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
def test_create_backup(mock_remove, mock_copy2, mock_exists, system_refactor_instance, backup_exists, remove_success, expected_return, mock_logger):
    """Tests the _create_backup method."""
    mock_exists.return_value = backup_exists
    mock_remove.return_value = remove_success
    mock_copy2.return_value = None

    if not remove_success and backup_exists:
        mock_remove.side_effect = OSError("Simulated error")

    assert system_refactor_instance._create_backup() == expected_return

    if backup_exists and remove_success:
        mock_remove.assert_called_once_with(system_refactor_instance.backup_path)
    if expected_return:
        mock_copy2.assert_called_once_with(system_refactor_instance.file_path, system_refactor_instance.backup_path)
    if not expected_return and not remove_success and backup_exists:
        mock_logger.error.assert_called()


@pytest.mark.parametrize("backup_exists, copy2_success, expected_return", [
    (True, True, True),
    (False, True, False),
    (True, False, False),
])
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
def test_restore_backup(mock_copy2, mock_exists, system_refactor_instance, backup_exists, copy2_success, expected_return, mock_logger):
    """Tests the _restore_backup method."""
    mock_exists.return_value = backup_exists
    mock_copy2.return_value = None
    if not copy2_success:
        mock_copy2.side_effect = OSError("Simulated error")

    assert system_refactor_instance._restore_backup() == expected_return

    mock_exists.assert_called_once_with(system_refactor_instance.backup_path)
    if expected_return:
        mock_copy2.assert_called_once_with(system_refactor_instance.backup_path, system_refactor_instance.file_path)
    if not expected_return:
        mock_logger.error.assert_called()


@pytest.mark.parametrize("python_version, expected_return", [
    ((3, 7), True),
    ((3, 6), False),
    ((3, 8), True)
])
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info")
def test_check_python_version(mock_version_info, system_refactor_instance, python_version, expected_return, mock_logger):
    """Tests the _check_python_version method."""
    mock_version_info = MagicMock()
    mock_version_info.__ge__.return_value = python_version >= (3,7)
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info", new=mock_version_info):
        assert system_refactor_instance._check_python_version() == expected_return
        if not expected_return:
            mock_logger.error.assert_called()


@pytest.mark.parametrize("black_found, black_success, expected_return", [
    (True, True, True),
    (True, False, False),
    (False, False, False),
])
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
def test_format_code(mock_run, system_refactor_instance, black_found, black_success, expected_return, mock_logger):
    """Tests the _format_code method."""
    if black_found:
        if black_success:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Formatted"
            mock_run.return_value.stderr = ""
        else:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Error formatting"
    else:
        mock_run.side_effect = FileNotFoundError

    assert system_refactor_instance._format_code() == expected_return

    if black_found:
        mock_run.assert_called_once_with(["black", system_refactor_instance.file_path], check=True, capture_output=True)
        if not black_success:
             mock_logger.error.assert_called()

    else:
        mock_logger.error.assert_called()
        mock_run.assert_not_called()


@pytest.mark.parametrize("test_success, expected_return", [
    (True, True),
    (False, False),
])
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
def test_run_tests(mock_run, system_refactor_instance, test_success, expected_return, mock_logger):
    """Tests the _run_tests method."""
    if test_success:
        mock_run.return_value.stdout = "PASSED"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0
    else:
        mock_run.return_value.stdout = "FAILED"
        mock_run.return_value.stderr = "Test failed"
        mock_run.return_value.returncode = 1

    assert system_refactor_instance._run_tests() == expected_return

    mock_run.assert_called_once_with(["pytest", os.path.dirname(system_refactor_instance.file_path)], capture_output=True, text=True, check=True)
    if not test_success:
        mock_logger.error.assert_called()


@pytest.mark.parametrize(
    "python_version_compatible, backup_created, format_success, test_success, restore_needed, expected_return",
    [
        (True, True, True, True, False, True),  # Success
        (True, True, True, False, True, False), # Tests Fail
        (True, True, False, True, False, False),  # Formatting fails
        (True, False, True, True, False, False),  # Backup fails
        (False, True, True, True, False, False),  # Python version fails
        (True, True, False, False, True, False),  # Formatting and tests fail
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._check_python_version")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._create_backup")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._format_code")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._run_tests")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.SystemRefactor._restore_backup")
@patch("builtins.open", new_callable=mock_open)
def test_refactor(
    mock_open_file,
    mock_restore_backup,
    mock_run_tests,
    mock_format_code,
    mock_create_backup,
    mock_check_python_version,
    system_refactor_instance,
    python_version_compatible,
    backup_created,
    format_success,
    test_success,
    restore_needed,
    expected_return,
    mock_logger,
):
    """Tests the refactor method."""
    mock_check_python_version.return_value = python_version_compatible
    mock_create_backup.return_value = backup_created
    mock_format_code.return_value = format_success
    mock_run_tests.return_value = test_success
    mock_restore_backup.return_value = True # Default to True unless explicitly tested for failure
    mock_open_file.return_value.write.return_value = None


    result = system_refactor_instance.refactor()
    assert result == expected_return

    mock_check_python_version.assert_called_once()
    mock_create_backup.assert_called_once()


    if python_version_compatible and backup_created:
        mock_format_code.assert_called_once()
        if format_success:
            mock_open_file.assert_called_once_with(system_refactor_instance.file_path, "w")
            mock_run_tests.assert_called_once()
            if not test_success:
                mock_restore_backup.assert_called_once()
        else:
            mock_run_tests.assert_not_called()
    if not python_version_compatible or not backup_created:
        mock_format_code.assert_not_called()
        mock_open_file.assert_not_called()
        mock_run_tests.assert_not_called()


@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
def test_cleanup(mock_remove, mock_exists, system_refactor_instance, mock_logger):
    """Tests the cleanup method."""
    mock_exists.return_value = True
    mock_remove.return_value = None

    system_refactor_instance.cleanup()
    mock_exists.assert_called_once_with(system_refactor_instance.backup_path)
    mock_remove.assert_called_once_with(system_refactor_instance.backup_path)

    mock_exists.return_value = False
    system_refactor_instance.cleanup()
    mock_exists.assert_called()
    mock_remove.assert_called()
    mock_logger.info.assert_called_with("No backup file to delete.")
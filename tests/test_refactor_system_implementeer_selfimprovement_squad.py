import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.refactor_system_implementeer_selfimprovement_squad import SystemRefactor
from loguru import logger

# Add the current directory to the Python path for importing the module
sys.path.append(os.getcwd())


@pytest.fixture
def system_refactor():
    return SystemRefactor(file_path="test_file.py")


def test_system_refactor_init(system_refactor):
    assert system_refactor.file_path == "test_file.py"
    assert system_refactor.backup_path == "test_file.py.bak"


@pytest.mark.parametrize(
    "backup_exists, remove_success, expected_log_level, expected_return",
    [
        (False, True, "info", True),
        (True, True, "warning", True),
        (True, False, "error", False),
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
def test_create_backup(
    mock_remove,
    mock_copy2,
    mock_exists,
    system_refactor,
    backup_exists,
    remove_success,
    expected_log_level,
    expected_return,
):
    mock_exists.return_value = backup_exists
    mock_remove.return_value = remove_success
    mock_copy2.return_value = None

    if not remove_success and backup_exists:
        mock_remove.side_effect = OSError("Mocked error")
    
    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor._create_backup()
        assert result == expected_return
        mock_log.assert_called()

    mock_exists.assert_called_once_with("test_file.py.bak")
    if backup_exists:
        mock_remove.assert_called_once_with("test_file.py.bak")
    if expected_return:
         mock_copy2.assert_called_once_with("test_file.py", "test_file.py.bak")


@pytest.mark.parametrize(
    "backup_exists, copy_success, expected_log_level, expected_return",
    [
        (True, True, "info", True),
        (False, True, "error", False),
        (True, False, "error", False),
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.shutil.copy2")
def test_restore_backup(
    mock_copy2,
    mock_exists,
    system_refactor,
    backup_exists,
    copy_success,
    expected_log_level,
    expected_return,
):
    mock_exists.return_value = backup_exists
    mock_copy2.return_value = None
    if not copy_success:
        mock_copy2.side_effect = OSError("Mocked error")

    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor._restore_backup()
        assert result == expected_return
        mock_log.assert_called()

    mock_exists.assert_called_once_with("test_file.py.bak")
    if backup_exists and copy_success:
        mock_copy2.assert_called_once_with("test_file.py.bak", "test_file.py")


@pytest.mark.parametrize(
    "python_version, expected_log_level, expected_return",
    [
        ((3, 7), "info", True),
        ((3, 6), "error", False),
        ((3, 0), "error", False),
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.sys.version_info")
def test_check_python_version(
    mock_version_info, system_refactor, python_version, expected_log_level, expected_return
):
    mock_version_info.return_value = python_version
    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor._check_python_version()
        assert result == expected_return
        if expected_log_level != "info":
            mock_log.assert_called()
        else:
            mock_log.assert_not_called()


@pytest.mark.parametrize(
    "black_exists, subprocess_result, expected_log_level, expected_return",
    [
        (True,  {"returncode": 0, "stdout": b"formatted", "stderr": b""}, "info", True),
        (True, {"returncode": 1, "stdout": b"", "stderr": b"error"}, "error", False),
        (False, {"returncode": 0, "stdout": b"", "stderr": b""}, "error", False),
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
def test_format_code(
    mock_exists,
    mock_subprocess_run,
    system_refactor,
    black_exists,
    subprocess_result,
    expected_log_level,
    expected_return,
):
    mock_exists.return_value = black_exists
    if black_exists:
        mock_subprocess_run.return_value = MagicMock(returncode=subprocess_result["returncode"], stdout=subprocess_result["stdout"], stderr=subprocess_result["stderr"])
        
    else:
        mock_subprocess_run.side_effect = FileNotFoundError
        
    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor._format_code()
        assert result == expected_return
        mock_log.assert_called()

    if black_exists:
        mock_subprocess_run.assert_called_once_with(["black", "test_file.py"], check=True, capture_output=True)
    else:
        mock_subprocess_run.assert_not_called()


@pytest.mark.parametrize(
    "pytest_result, expected_log_level, expected_return",
    [
        ({"stdout": "PASSED"}, "info", True),
        ({"stdout": "FAILED"}, "error", False),
        ({"stdout": "ERROR"}, "error", False),
    ],
)
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.subprocess.run")
def test_run_tests(
    mock_subprocess_run, system_refactor, pytest_result, expected_log_level, expected_return
):
    mock_subprocess_run.return_value = MagicMock(stdout=pytest_result["stdout"], stderr="")
    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor._run_tests()
        assert result == expected_return
        mock_log.assert_called()
    mock_subprocess_run.assert_called_once_with(
        ["pytest", os.path.dirname("test_file.py")], capture_output=True, text=True, check=True
    )

@pytest.mark.parametrize(
    "python_version_result, create_backup_result, format_code_result, run_tests_result, restore_backup_result, expected_log_level, expected_return",
    [
        (True, True, True, True, True, "success", True), # Happy path
        (False, True, True, True, True, "critical", False), # Python Version fails
        (True, False, True, True, True, "critical", False), # Backup fails
        (True, True, False, True, False, "warning", True), # Format fails but doesn't prevent refactor and tests pass
        (True, True, True, False, True, "error", False), # Tests fail
        (True, True, True, False, False, "critical", False), # Tests fail and restore fails
        (True, True, False, False, True, "error", False), # Format fails, tests fails, backup is not restored because it was not created
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
    system_refactor,
    python_version_result,
    create_backup_result,
    format_code_result,
    run_tests_result,
    restore_backup_result,
    expected_log_level,
    expected_return,
):
    mock_check_python_version.return_value = python_version_result
    mock_create_backup.return_value = create_backup_result
    mock_format_code.return_value = format_code_result
    mock_run_tests.return_value = run_tests_result
    mock_restore_backup.return_value = restore_backup_result

    with patch.object(logger, expected_log_level) as mock_log:
        result = system_refactor.refactor()
        assert result == expected_return
        mock_log.assert_called()

    mock_check_python_version.assert_called_once()
    if python_version_result:
        mock_create_backup.assert_called_once()
        if create_backup_result:
            mock_format_code.assert_called_once()
            if format_code_result or not format_code_result:
                mock_run_tests.assert_called_once()
            if not run_tests_result:
                mock_restore_backup.assert_called()
    if not create_backup_result or not run_tests_result:
        mock_restore_backup.assert_called()
        


@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.path.exists")
@patch("src.playground.refactor_system_implementeer_selfimprovement_squad.os.remove")
def test_cleanup(mock_remove, mock_exists, system_refactor):
    mock_exists.return_value = True
    mock_remove.return_value = True
    system_refactor.cleanup()
    mock_exists.assert_called_once_with("test_file.py.bak")
    mock_remove.assert_called_once_with("test_file.py.bak")

    mock_exists.return_value = False
    mock_remove.reset_mock()
    system_refactor.cleanup()
    mock_exists.assert_called_with("test_file.py.bak")
    mock_remove.assert_not_called()

    mock_exists.return_value = True
    mock_remove.side_effect = OSError("Mocked error")
    with patch.object(logger, "error") as mock_log:
        system_refactor.cleanup()
        mock_log.assert_called()
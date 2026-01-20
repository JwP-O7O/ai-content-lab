import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.extract_methods_for_system_implementation import (
    _execute_command,
    _retry_command,
    _write_update_script,
    _run_update_script,
    _reboot_system,
    perform_system_update,
    is_process_running,
    kill_process,
    safely_remove_file,
    execute_commands_in_parallel,
    get_system_information,
    UPDATE_SCRIPT_PATH,
    REBOOT_COMMAND,
    MAX_RETRIES,
    RETRY_DELAY,
)

sys.path.append(os.getcwd())  # Add current directory to sys.path for import


@pytest.fixture
def mock_subprocess_run():
    with patch('subprocess.Popen') as mock_popen:
        yield mock_popen


@pytest.fixture
def mock_open_func():
    with patch('builtins.open', new_callable=mock_open) as mock_open_func:
        yield mock_open_func


def test__execute_command_success(mock_subprocess_run):
    mock_process = MagicMock()
    mock_process.communicate.return_value = (b"stdout", b"stderr")
    mock_process.returncode = 0
    mock_subprocess_run.return_value = mock_process

    return_code, stdout, stderr, execution_time = _execute_command("some command")

    assert return_code == 0
    assert stdout == "stdout"
    assert stderr == "stderr"
    mock_subprocess_run.assert_called_once_with(
        "some command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash'
    )
    assert execution_time >= 0


def test__execute_command_failure_timeout(mock_subprocess_run):
    mock_process = MagicMock()
    mock_process.communicate.side_effect = subprocess.TimeoutExpired("cmd", 1)
    mock_subprocess_run.return_value = mock_process

    return_code, stdout, stderr, execution_time = _execute_command("some command", timeout=1)

    assert return_code == -1
    assert stdout == ""
    assert stderr == ""
    mock_process.kill.assert_called_once()
    mock_subprocess_run.assert_called_once_with(
        "some command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash'
    )
    assert execution_time == 1


def test__execute_command_failure_filenotfound(mock_subprocess_run):
    mock_process = MagicMock()
    mock_process.communicate.side_effect = FileNotFoundError
    mock_subprocess_run.return_value = mock_process

    return_code, stdout, stderr, execution_time = _execute_command("nonexistent_command")

    assert return_code == -1
    assert stdout == ""
    assert "Command not found" in stderr
    mock_subprocess_run.assert_called_once_with(
        "nonexistent_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash'
    )
    assert execution_time == 0


def test__execute_command_failure_general_exception(mock_subprocess_run):
    mock_process = MagicMock()
    mock_process.communicate.side_effect = Exception("Generic error")
    mock_subprocess_run.return_value = mock_process

    return_code, stdout, stderr, execution_time = _execute_command("some command")

    assert return_code == -1
    assert stdout == ""
    assert "An unexpected error occurred" in stderr
    mock_subprocess_run.assert_called_once_with(
        "some command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash'
    )
    assert execution_time == 0


def test__retry_command_success(mock_subprocess_run):
    mock_command = MagicMock(return_value=(0, "stdout", "stderr", 0.1))
    return_code, stdout, stderr, execution_time = _retry_command(mock_command, retries=2, delay=0.1)
    assert return_code == 0
    assert stdout == "stdout"
    assert stderr == "stderr"
    assert execution_time == 0.1
    mock_command.assert_called_once()


def test__retry_command_failure_then_success(mock_subprocess_run):
    mock_command = MagicMock()
    mock_command.side_effect = [
        (1, "stdout1", "stderr1", 0.1),
        (0, "stdout2", "stderr2", 0.2),
    ]
    return_code, stdout, stderr, execution_time = _retry_command(mock_command, retries=2, delay=0.01)
    assert return_code == 0
    assert stdout == "stdout2"
    assert stderr == "stderr2"
    assert execution_time == 0.2
    assert mock_command.call_count == 2


def test__retry_command_failure_all_attempts(mock_subprocess_run):
    mock_command = MagicMock(return_value=(1, "stdout", "stderr", 0.1))

    with pytest.raises(Exception):
        _retry_command(mock_command, retries=2, delay=0.01)

    assert mock_command.call_count == 3  # retries + initial attempt


def test__write_update_script_success(mock_open_func):
    result = _write_update_script("script content")
    assert result is True
    mock_open_func.return_value.__enter__.return_value.write.assert_called_once_with("script content")
    mock_open_func.return_value.__enter__.return_value.close.assert_called_once()
    assert os.chmod.called
    assert os.path.dirname(UPDATE_SCRIPT_PATH) in os.makedirs.call_args_list[0][0]
    assert os.makedirs.call_count == 1

@patch('os.makedirs')
def test__write_update_script_failure_makedirs(mock_makedirs, mock_open_func):
    mock_makedirs.side_effect = OSError("Failed to create directory")
    result = _write_update_script("script content")
    assert result is False
    assert mock_open_func.call_count == 0  # open should not be called
    mock_makedirs.assert_called_once()

@patch('os.chmod')
def test__write_update_script_failure_chmod(mock_chmod, mock_open_func):
    mock_chmod.side_effect = OSError("Failed to chmod")
    result = _write_update_script("script content")
    assert result is True
    mock_chmod.assert_called_once()


def test__run_update_script_success(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")
    return_code, stdout, stderr, execution_time = _run_update_script()
    assert return_code == 0
    assert stdout == "stdout"
    assert stderr == "stderr"
    mock_subprocess_run.assert_called_once_with(f"sudo {UPDATE_SCRIPT_PATH}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    assert execution_time >= 0


def test__run_update_script_failure(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")
    return_code, stdout, stderr, execution_time = _run_update_script()
    assert return_code == 1
    assert stdout == "stdout"
    assert stderr == "stderr"
    mock_subprocess_run.assert_called_once_with(f"sudo {UPDATE_SCRIPT_PATH}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    assert execution_time >= 0


def test__reboot_system_success(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")

    return_code, stdout, stderr, execution_time = _reboot_system()

    assert return_code == 0
    assert stdout == "stdout"
    assert stderr == "stderr"
    mock_subprocess_run.assert_called_once_with(REBOOT_COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    assert execution_time >= 0


def test__reboot_system_failure(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")

    return_code, stdout, stderr, execution_time = _reboot_system()

    assert return_code == 1
    assert stdout == "stdout"
    assert stderr == "stderr"
    mock_subprocess_run.assert_called_once_with(REBOOT_COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    assert execution_time >= 0

@patch('_reboot_system')
@patch('_run_update_script')
@patch('_write_update_script')
def test_perform_system_update_success_reboot(mock_write_script, mock_run_script, mock_reboot, mock_subprocess_run):
    mock_write_script.return_value = True
    mock_run_script.return_value = (0, "stdout", "stderr", 0.1)
    mock_reboot.return_value = (0, "reboot_stdout", "reboot_stderr", 0.2)
    result = perform_system_update("script content", reboot_after_update=True)
    assert result is True
    mock_write_script.assert_called_once_with("script content")
    mock_run_script.assert_called_once()
    mock_reboot.assert_called_once()

@patch('_reboot_system')
@patch('_run_update_script')
@patch('_write_update_script')
def test_perform_system_update_success_no_reboot(mock_write_script, mock_run_script, mock_reboot, mock_subprocess_run):
    mock_write_script.return_value = True
    mock_run_script.return_value = (0, "stdout", "stderr", 0.1)
    result = perform_system_update("script content", reboot_after_update=False)
    assert result is True
    mock_write_script.assert_called_once_with("script content")
    mock_run_script.assert_called_once()
    mock_reboot.assert_not_called()

@patch('_reboot_system')
@patch('_run_update_script')
@patch('_write_update_script')
def test_perform_system_update_failure_write_script(mock_write_script, mock_run_script, mock_reboot, mock_subprocess_run):
    mock_write_script.return_value = False
    result = perform_system_update("script content", reboot_after_update=True)
    assert result is False
    mock_write_script.assert_called_once_with("script content")
    mock_run_script.assert_not_called()
    mock_reboot.assert_not_called()


@patch('_reboot_system')
@patch('_run_update_script')
@patch('_write_update_script')
def test_perform_system_update_failure_run_script(mock_write_script, mock_run_script, mock_reboot, mock_subprocess_run):
    mock_write_script.return_value = True
    mock_run_script.return_value = (1, "stdout", "stderr", 0.1)
    result = perform_system_update("script content", reboot_after_update=True)
    assert result is False
    mock_write_script.assert_called_once_with("script content")
    mock_run_script.assert_called_once()
    mock_reboot.assert_not_called()


@patch('_reboot_system')
@patch('_run_update_script')
@patch('_write_update_script')
def test_perform_system_update_failure_reboot(mock_write_script, mock_run_script, mock_reboot, mock_subprocess_run):
    mock_write_script.return_value = True
    mock_run_script.return_value = (0, "stdout", "stderr", 0.1)
    mock_reboot.return_value = (1, "reboot_stdout", "reboot_stderr", 0.2)
    result = perform_system_update("script content", reboot_after_update=True)
    assert result is False
    mock_write_script.assert_called_once_with("script content")
    mock_run_script.assert_called_once()
    mock_reboot.assert_called_once()

def test_is_process_running_running(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.communicate.return_value = (b"1234", b"")
    result = is_process_running("process_name")
    assert result is True
    mock_subprocess_run.assert_called_once_with("pgrep process_name", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_is_process_running_not_running(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.communicate.return_value = (b"", b"")
    result = is_process_running("process_name")
    assert result is False
    mock_subprocess_run.assert_called_once_with("pgrep process_name", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_is_process_running_exception(mock_subprocess_run):
    mock_subprocess_run.side_effect = Exception("Some error")
    result = is_process_running("process_name")
    assert result is False


def test_kill_process_success(mock_subprocess_run):
    with patch('src.playground.extract_methods_for_system_implementation.is_process_running', return_value=True):
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.communicate.return_value = (b"", b"")
        result = kill_process("process_name")
        assert result is True
        mock_subprocess_run.assert_called_once_with("pkill process_name", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_kill_process_not_running(mock_subprocess_run):
    with patch('src.playground.extract_methods_for_system_implementation.is_process_running', return_value=False):
        result = kill_process("process_name")
        assert result is True
        mock_subprocess_run.assert_not_called()


def test_kill_process_failure(mock_subprocess_run):
    with patch('src.playground.extract_methods_for_system_implementation.is_process_running', return_value=True):
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.communicate.return_value = (b"", b"stderr")
        result = kill_process("process_name")
        assert result is False
        mock_subprocess_run.assert_called_once_with("pkill process_name", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_kill_process_exception(mock_subprocess_run):
    with patch('src.playground.extract_methods_for_system_implementation.is_process_running', return_value=True):
        mock_subprocess_run.side_effect = Exception("Some error")
        result = kill_process("process_name")
        assert result is False


def test_safely_remove_file_success(mock_open_func):
    with patch('os.path.exists', return_value=True), patch('os.remove') as mock_remove:
        result = safely_remove_file("file_path")
        assert result is True
        mock_remove.assert_called_once_with("file_path")

def test_safely_remove_file_does_not_exist():
    with patch('os.path.exists', return_value=False), patch('os.remove') as mock_remove:
        result = safely_remove_file("file_path")
        assert result is True
        mock_remove.assert_not_called()

def test_safely_remove_file_exception():
    with patch('os.path.exists', return_value=True), patch('os.remove', side_effect=Exception("Error")):
        result = safely_remove_file("file_path")
        assert result is False

def test_execute_commands_in_parallel_success(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")
    commands = [("command1", False, 1), ("command2", True, 2)]
    results = execute_commands_in_parallel(commands)
    assert len(results) == 2
    assert results[0] == (0, "stdout", "stderr")
    assert results[1] == (0, "stdout", "stderr")
    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_any_call("command1", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("command2", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_execute_commands_in_parallel_failure(mock_subprocess_run):
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.communicate.return_value = (b"stdout", b"stderr")

    commands = [("command1", False, 1), ("command2", True, 2)]
    results = execute_commands_in_parallel(commands)

    assert len(results) == 2
    assert results[0] == (1, "stdout", "stderr")
    assert results[1] == (1, "stdout", "stderr")
    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_any_call("command1", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("command2", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')

def test_execute_commands_in_parallel_exception(mock_subprocess_run):
    mock_subprocess_run.side_effect = Exception("Test exception")
    commands = [("command1", False, 1), ("command2", True, 2)]
    results = execute_commands_in_parallel(commands)
    assert len(results) == 2
    assert results[0] == (-1, "", "Test exception")
    assert results[1] == (-1, "", "Test exception")
    assert mock_subprocess_run.call_count == 2


def test_get_system_information_success(mock_subprocess_run):
    mock_subprocess_run.side_effect = [
        MagicMock(returncode=0, communicate=lambda timeout: (b"kernel_version", b"")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"hostname", b"")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"uptime", b""))
    ]

    system_info = get_system_information()

    assert "kernel_version" in system_info
    assert "hostname" in system_info
    assert "uptime" in system_info
    assert system_info["kernel_version"] == "kernel_version"
    assert system_info["hostname"] == "hostname"
    assert system_info["uptime"] == "uptime"
    assert mock_subprocess_run.call_count == 3
    mock_subprocess_run.assert_any_call("uname -r", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("hostname", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("uptime -p", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')



def test_get_system_information_failure_kernel(mock_subprocess_run):
    mock_subprocess_run.side_effect = [
        MagicMock(returncode=1, communicate=lambda timeout: (b"", b"error")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"hostname", b"")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"uptime", b"")),
    ]
    system_info = get_system_information()
    assert system_info["kernel_version"] == ""
    assert "hostname" in system_info
    assert "uptime" in system_info
    assert mock_subprocess_run.call_count == 3
    mock_subprocess_run.assert_any_call("uname -r", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("hostname", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("uptime -p", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')



def test_get_system_information_failure_hostname(mock_subprocess_run):
    mock_subprocess_run.side_effect = [
        MagicMock(returncode=0, communicate=lambda timeout: (b"kernel_version", b"")),
        MagicMock(returncode=1, communicate=lambda timeout: (b"", b"error")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"uptime", b"")),
    ]
    system_info = get_system_information()
    assert "kernel_version" in system_info
    assert system_info["hostname"] == ""
    assert "uptime" in system_info
    assert mock_subprocess_run.call_count == 3
    mock_subprocess_run.assert_any_call("uname -r", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("hostname", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("uptime -p", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')



def test_get_system_information_failure_uptime(mock_subprocess_run):
    mock_subprocess_run.side_effect = [
        MagicMock(returncode=0, communicate=lambda timeout: (b"kernel_version", b"")),
        MagicMock(returncode=0, communicate=lambda timeout: (b"hostname", b"")),
        MagicMock(returncode=1, communicate=lambda timeout: (b"", b"error")),
    ]
    system_info = get_system_information()
    assert "kernel_version" in system_info
    assert "hostname" in system_info
    assert system_info["uptime"] == ""
    assert mock_subprocess_run.call_count == 3
    mock_subprocess_run.assert_any_call("uname -r", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("hostname", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    mock_subprocess_run.assert_any_call("uptime -p", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')


def test_get_system_information_major_failure(mock_subprocess_run):
    mock_subprocess_run.side_effect = Exception("Generic error")
    system_info = get_system_information()
    assert system_info == {}
    assert mock_subprocess_run.call_count == 1  # Only tries uname -r because of exception
    mock_subprocess_run.assert_any_call("uname -r", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
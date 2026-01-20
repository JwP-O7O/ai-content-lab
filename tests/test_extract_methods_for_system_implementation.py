import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.extract_methods_for_system_implementation import (
    perform_system_update,
    is_process_running,
    kill_process,
    safely_remove_file,
    execute_commands_in_parallel,
    get_system_information,
    _execute_command,
    _retry_command,
    _write_update_script,
    _run_update_script,
    _reboot_system,
)
import subprocess
import time

sys.path.append(os.getcwd())

UPDATE_SCRIPT_PATH = "/tmp/update_script.sh"


class TestSystemUpdate:
    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_success(self, mock_reboot, mock_run_script, mock_write_script):
        mock_write_script.return_value = True
        mock_run_script.return_value = (0, "stdout", "stderr", 1.0)
        mock_reboot.return_value = (0, "stdout", "stderr", 0.5)
        update_script_content = "#!/bin/bash\necho 'hello'"
        result = perform_system_update(update_script_content, True)
        assert result is True
        mock_write_script.assert_called_once_with(update_script_content)
        mock_run_script.assert_called_once()
        mock_reboot.assert_called_once()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_no_reboot(self, mock_reboot, mock_run_script, mock_write_script):
        mock_write_script.return_value = True
        mock_run_script.return_value = (0, "stdout", "stderr", 1.0)
        update_script_content = "#!/bin/bash\necho 'hello'"
        result = perform_system_update(update_script_content, False)
        assert result is True
        mock_write_script.assert_called_once_with(update_script_content)
        mock_run_script.assert_called_once()
        mock_reboot.assert_not_called()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_write_script_fail(self, mock_reboot, mock_run_script, mock_write_script):
        mock_write_script.return_value = False
        update_script_content = "#!/bin/bash\necho 'hello'"
        result = perform_system_update(update_script_content, True)
        assert result is False
        mock_write_script.assert_called_once_with(update_script_content)
        mock_run_script.assert_not_called()
        mock_reboot.assert_not_called()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_script_fail(self, mock_reboot, mock_run_script, mock_write_script):
        mock_write_script.return_value = True
        mock_run_script.return_value = (1, "stdout", "stderr", 1.0)
        update_script_content = "#!/bin/bash\necho 'hello'"
        result = perform_system_update(update_script_content, True)
        assert result is False
        mock_write_script.assert_called_once_with(update_script_content)
        mock_run_script.assert_called_once()
        mock_reboot.assert_not_called()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_reboot_fail(self, mock_reboot, mock_run_script, mock_write_script):
        mock_write_script.return_value = True
        mock_run_script.return_value = (0, "stdout", "stderr", 1.0)
        mock_reboot.return_value = (1, "stdout", "stderr", 0.5)
        update_script_content = "#!/bin/bash\necho 'hello'"
        result = perform_system_update(update_script_content, True)
        assert result is False
        mock_write_script.assert_called_once_with(update_script_content)
        mock_run_script.assert_called_once()
        mock_reboot.assert_called_once()


class TestProcessManagement:
    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_running(self, mock_execute_command):
        mock_execute_command.return_value = (0, "1234", "", 0.1)
        assert is_process_running("test_process") is True
        mock_execute_command.assert_called_once_with("pgrep test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_not_running(self, mock_execute_command):
        mock_execute_command.return_value = (1, "", "", 0.1)
        assert is_process_running("test_process") is False
        mock_execute_command.assert_called_once_with("pgrep test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_error(self, mock_execute_command):
        mock_execute_command.side_effect = Exception("Some error")
        assert is_process_running("test_process") is False
        mock_execute_command.assert_called_once_with("pgrep test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_success(self, mock_execute_command):
        mock_execute_command.side_effect = [(0, "1234", "", 0.1), (0, "", "", 0.1)]
        assert kill_process("test_process") is True
        assert mock_execute_command.call_count == 2
        mock_execute_command.assert_any_call("pgrep test_process", shell=True)
        mock_execute_command.assert_any_call("pkill test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_not_running(self, mock_execute_command):
        mock_execute_command.side_effect = [(1, "", "", 0.1)]
        assert kill_process("test_process") is True
        assert mock_execute_command.call_count == 1
        mock_execute_command.assert_called_once_with("pgrep test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_fail(self, mock_execute_command):
        mock_execute_command.side_effect = [(0, "1234", "", 0.1), (1, "", "error", 0.1)]
        assert kill_process("test_process") is False
        assert mock_execute_command.call_count == 2
        mock_execute_command.assert_any_call("pgrep test_process", shell=True)
        mock_execute_command.assert_any_call("pkill test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_error_getting_pid(self, mock_execute_command):
        mock_execute_command.side_effect = Exception("Some error")
        assert kill_process("test_process") is False
        mock_execute_command.assert_called_once_with("pgrep test_process", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_error_killing(self, mock_execute_command):
        mock_execute_command.side_effect = [(0, "1234", "", 0.1), Exception("Some error")]
        assert kill_process("test_process") is False
        assert mock_execute_command.call_count == 2
        mock_execute_command.assert_any_call("pgrep test_process", shell=True)
        mock_execute_command.assert_any_call("pkill test_process", shell=True)


class TestFileManagement:
    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_success(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        assert safely_remove_file("/tmp/test_file.txt") is True
        mock_exists.assert_called_once_with("/tmp/test_file.txt")
        mock_remove.assert_called_once_with("/tmp/test_file.txt")

    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_does_not_exist(self, mock_remove, mock_exists):
        mock_exists.return_value = False
        assert safely_remove_file("/tmp/test_file.txt") is True
        mock_exists.assert_called_once_with("/tmp/test_file.txt")
        mock_remove.assert_not_called()

    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_error(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        mock_remove.side_effect = Exception("Some error")
        assert safely_remove_file("/tmp/test_file.txt") is False
        mock_exists.assert_called_once_with("/tmp/test_file.txt")
        mock_remove.assert_called_once_with("/tmp/test_file.txt")


class TestParallelExecution:
    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_execute_commands_in_parallel(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (0, "stdout1", "stderr1", 0.1),
            (1, "stdout2", "stderr2", 0.2),
            (2, "stdout3", "stderr3", 0.3),
        ]
        commands = [
            ("command1", False, 1),
            ("command2", True, 2),
            ("command3", False, 1),
        ]
        results = execute_commands_in_parallel(commands)
        assert len(results) == 3
        assert results[0] == (0, "stdout1", "stderr1")
        assert results[1] == (1, "stdout2", "stderr2")
        assert results[2] == (2, "stdout3", "stderr3")
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("command1", False, 1)
        mock_execute_command.assert_any_call("command2", True, 2)
        mock_execute_command.assert_any_call("command3", False, 1)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_execute_commands_in_parallel_error(self, mock_execute_command):
        mock_execute_command.side_effect = [
            Exception("Command 1 failed"),
            (1, "stdout2", "stderr2", 0.2),
        ]
        commands = [
            ("command1", False, 1),
            ("command2", True, 2),
        ]
        results = execute_commands_in_parallel(commands)
        assert len(results) == 2
        assert results[0] == (-1, "", "Command 1 failed")
        assert results[1] == (1, "stdout2", "stderr2")
        assert mock_execute_command.call_count == 2
        mock_execute_command.assert_any_call("command1", False, 1)
        mock_execute_command.assert_any_call("command2", True, 2)


class TestSystemInformation:
    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_get_system_information_success(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (0, "5.4.0-58-generic", "", 0.1),
            (0, "myhostname", "", 0.1),
            (0, "10:20:30 up", "", 0.1),
        ]
        info = get_system_information()
        assert "kernel_version" in info
        assert "hostname" in info
        assert "uptime" in info
        assert info["kernel_version"] == "5.4.0-58-generic"
        assert info["hostname"] == "myhostname"
        assert info["uptime"] == "10:20:30 up"
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("uname -r")
        mock_execute_command.assert_any_call("hostname")
        mock_execute_command.assert_any_call("uptime -p")

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_get_system_information_failure(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (1, "", "error", 0.1),
            (0, "myhostname", "", 0.1),
            (0, "10:20:30 up", "", 0.1),
        ]
        info = get_system_information()
        assert "kernel_version" not in info
        assert "hostname" in info
        assert "uptime" in info
        assert info["hostname"] == "myhostname"
        assert info["uptime"] == "10:20:30 up"
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("uname -r")
        mock_execute_command.assert_any_call("hostname")
        mock_execute_command.assert_any_call("uptime -p")

class TestExecuteCommand:
    @patch('subprocess.Popen')
    def test_execute_command_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        return_code, stdout, stderr, execution_time = _execute_command("some_command", shell=False)
        assert return_code == 0
        assert stdout == "stdout"
        assert stderr == "stderr"
        mock_popen.assert_called_once_with("some_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        mock_process.communicate.assert_called_once_with(timeout=60)
        assert execution_time >= 0

    @patch('subprocess.Popen')
    def test_execute_command_timeout(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("cmd", 10)
        mock_process.kill.return_value = None
        mock_popen.return_value = mock_process
        return_code, stdout, stderr, execution_time = _execute_command("some_command", shell=False, timeout=10)
        assert return_code == -1
        assert stdout == ""
        assert stderr == ""
        assert execution_time == 10
        mock_popen.assert_called_once_with("some_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        mock_process.communicate.assert_called_once_with(timeout=10)
        mock_process.kill.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_execute_command_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"", b"stderr")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        return_code, stdout, stderr, execution_time = _execute_command("some_command", shell=False)
        assert return_code == 1
        assert stdout == ""
        assert stderr == "stderr"
        mock_popen.assert_called_once_with("some_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
        mock_process.communicate.assert_called_once_with(timeout=60)
        assert execution_time >= 0

    @patch('subprocess.Popen')
    def test_execute_command_file_not_found(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError
        return_code, stdout, stderr, execution_time = _execute_command("nonexistent_command", shell=False)
        assert return_code == -1
        assert stdout == ""
        assert "Command not found" in stderr
        assert execution_time == 0
        mock_popen.assert_called_once_with("nonexistent_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    
    @patch('subprocess.Popen')
    def test_execute_command_exception(self, mock_popen):
        mock_popen.side_effect = Exception("Some error")
        return_code, stdout, stderr, execution_time = _execute_command("some_command", shell=False)
        assert return_code == -1
        assert stdout == ""
        assert "An unexpected error occurred" in stderr
        assert execution_time == 0
        mock_popen.assert_called_once_with("some_command", shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')

class TestRetryCommand:
    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_success_first_attempt(self, mock_execute_command):
        mock_execute_command.return_value = (0, "stdout", "stderr", 1.0)
        result = _retry_command(lambda: mock_execute_command("cmd", False, 10), retries=2, delay=0)
        assert result == (0, "stdout", "stderr", 1.0)
        mock_execute_command.assert_called_once_with("cmd", False, 10)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_success_after_retry(self, mock_execute_command):
        mock_execute_command.side_effect = [
            Exception("error"),
            (0, "stdout", "stderr", 1.0),
        ]
        result = _retry_command(lambda: mock_execute_command("cmd", False, 10), retries=2, delay=0)
        assert result == (0, "stdout", "stderr", 1.0)
        assert mock_execute_command.call_count == 2
        mock_execute_command.assert_any_call("cmd", False, 10)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_failure_after_all_retries(self, mock_execute_command):
        mock_execute_command.side_effect = [Exception("error")] * 3
        with pytest.raises(Exception):
            _retry_command(lambda: mock_execute_command("cmd", False, 10), retries=2, delay=0)
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("cmd", False, 10)

class TestWriteUpdateScript:
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.chmod')
    def test_write_update_script_success(self, mock_chmod, mock_makedirs, mock_open):
        script_content = "#!/bin/bash\necho 'hello'"
        result = _write_update_script(script_content)
        assert result is True
        mock_makedirs.assert_called_once_with(os.path.dirname(UPDATE_SCRIPT_PATH), exist_ok=True)
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(script_content)
        mock_chmod.assert_called_once_with(UPDATE_SCRIPT_PATH, 0o755)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.chmod')
    def test_write_update_script_failure_makedirs(self, mock_chmod, mock_makedirs, mock_open):
        mock_makedirs.side_effect = Exception("Some error")
        script_content = "#!/bin/bash\necho 'hello'"
        result = _write_update_script(script_content)
        assert result is False
        mock_makedirs.assert_called_once_with(os.path.dirname(UPDATE_SCRIPT_PATH), exist_ok=True)
        mock_open.assert_not_called()
        mock_chmod.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.chmod')
    def test_write_update_script_failure_open(self, mock_chmod, mock_makedirs, mock_open):
        mock_open.side_effect = Exception("Some error")
        script_content = "#!/bin/bash\necho 'hello'"
        result = _write_update_script(script_content)
        assert result is False
        mock_makedirs.assert_called_once_with(os.path.dirname(UPDATE_SCRIPT_PATH), exist_ok=True)
        mock_open.assert_called_once_with(UPDATE_SCRIPT_PATH, "w")
        mock_chmod.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.chmod')
    def test_write_update_script_failure_chmod(self, mock_chmod, mock_makedirs, mock_open):
        mock_chmod.side_effect = Exception("Some error")
        script_content = "#!/bin/bash\necho 'hello'"
        result = _write_update_script(script_content)
        assert result is False
        mock_makedirs.assert_called_once_with(os.path.dirname(UPDATE_SCRIPT_PATH), exist_ok=True)
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(script_content)
        mock_chmod.assert_called_once_with(UPDATE_SCRIPT_PATH, 0o755)
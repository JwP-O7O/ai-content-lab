import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
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
    DEFAULT_SHELL,
)

sys.path.append(os.getcwd())


class TestExtractMethods:
    @patch('subprocess.Popen')
    def test_execute_command_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        return_code, stdout, stderr, execution_time = _execute_command("some_command")
        assert return_code == 0
        assert stdout == "stdout"
        assert stderr == "stderr"
        assert execution_time >= 0
        mock_popen.assert_called_once_with(
            "some_command",
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable=DEFAULT_SHELL,
        )

    @patch('subprocess.Popen')
    def test_execute_command_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        return_code, stdout, stderr, execution_time = _execute_command("some_command")
        assert return_code == 1
        assert stdout == "stdout"
        assert stderr == "stderr"
        assert execution_time >= 0

    @patch('subprocess.Popen')
    def test_execute_command_timeout(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("cmd", 1)
        mock_popen.return_value = mock_process
        return_code, stdout, stderr, execution_time = _execute_command("some_command", timeout=1)
        assert return_code == -1
        assert execution_time == 1

    @patch('subprocess.Popen')
    def test_execute_command_file_not_found(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError
        return_code, stdout, stderr, execution_time = _execute_command("nonexistent_command")
        assert return_code == -1
        assert "Command not found" in stderr
        assert execution_time == 0

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_success(self, mock_execute_command):
        mock_execute_command.return_value = (0, "stdout", "stderr", 0.1)
        result = _retry_command(lambda: mock_execute_command("cmd"))
        assert result == (0, "stdout", "stderr", 0.1)
        mock_execute_command.assert_called_once()

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_retry(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (1, "stdout", "stderr", 0.1),
            (0, "stdout", "stderr", 0.1),
        ]
        result = _retry_command(lambda: mock_execute_command("cmd"), retries=1, delay=0)
        assert result == (0, "stdout", "stderr", 0.1)
        assert mock_execute_command.call_count == 2

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_retry_command_failure_after_retries(self, mock_execute_command):
        mock_execute_command.side_effect = [(1, "stdout", "stderr", 0.1)] * (MAX_RETRIES + 1)
        with pytest.raises(Exception):
            _retry_command(lambda: mock_execute_command("cmd"), retries=MAX_RETRIES, delay=0)
        assert mock_execute_command.call_count == MAX_RETRIES + 1

    @patch('builtins.open', new_callable=mock_open)
    def test_write_update_script_success(self, mock_open):
        script_content = "some script content"
        result = _write_update_script(script_content)
        assert result is True
        mock_open.assert_called_once_with(UPDATE_SCRIPT_PATH, "w")
        mock_open().write.assert_called_once_with(script_content)
        assert os.chmod.called
        assert os.chmod.call_args[0][0] == UPDATE_SCRIPT_PATH

    @patch('builtins.open', new_callable=mock_open)
    def test_write_update_script_failure(self, mock_open):
        mock_open.side_effect = OSError("Permission denied")
        result = _write_update_script("content")
        assert result is False

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_run_update_script(self, mock_execute_command):
        mock_execute_command.return_value = (0, "stdout", "stderr", 0.1)
        return_code, stdout, stderr, execution_time = _run_update_script()
        assert return_code == 0
        assert stdout == "stdout"
        assert stderr == "stderr"
        mock_execute_command.assert_called_once_with(f"sudo {UPDATE_SCRIPT_PATH}", shell=True)
        assert execution_time >= 0

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_reboot_system(self, mock_execute_command):
        mock_execute_command.return_value = (0, "stdout", "stderr", 0.1)
        return_code, stdout, stderr, execution_time = _reboot_system()
        assert return_code == 0
        assert stdout == "stdout"
        assert stderr == "stderr"
        mock_execute_command.assert_called_once_with(REBOOT_COMMAND, shell=True)
        assert execution_time >= 0

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_success(
        self, mock_reboot_system, mock_run_update_script, mock_write_update_script
    ):
        mock_write_update_script.return_value = True
        mock_run_update_script.return_value = (0, "stdout", "stderr", 0.1)
        mock_reboot_system.return_value = (0, "stdout", "stderr", 0.1)
        assert perform_system_update("script_content", reboot_after_update=True) is True
        mock_write_update_script.assert_called_once_with("script_content")
        mock_run_update_script.assert_called_once()
        mock_reboot_system.assert_called_once()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_failure_write_script(
        self, mock_reboot_system, mock_run_update_script, mock_write_update_script
    ):
        mock_write_update_script.return_value = False
        assert perform_system_update("script_content") is False
        mock_write_update_script.assert_called_once_with("script_content")
        mock_run_update_script.assert_not_called()
        mock_reboot_system.assert_not_called()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_failure_script_execution(
        self, mock_reboot_system, mock_run_update_script, mock_write_update_script
    ):
        mock_write_update_script.return_value = True
        mock_run_update_script.return_value = (1, "stdout", "stderr", 0.1)
        assert perform_system_update("script_content") is False
        mock_run_update_script.assert_called_once()
        mock_reboot_system.assert_not_called()

    @patch('src.playground.extract_methods_for_system_implementation._write_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._run_update_script')
    @patch('src.playground.extract_methods_for_system_implementation._reboot_system')
    def test_perform_system_update_failure_reboot_execution(
        self, mock_reboot_system, mock_run_update_script, mock_write_update_script
    ):
        mock_write_update_script.return_value = True
        mock_run_update_script.return_value = (0, "stdout", "stderr", 0.1)
        mock_reboot_system.return_value = (1, "stdout", "stderr", 0.1)
        assert perform_system_update("script_content") is False
        mock_run_update_script.assert_called_once()
        mock_reboot_system.assert_called_once()

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_running(self, mock_execute_command):
        mock_execute_command.return_value = (0, "pid", "stderr", 0.1)
        assert is_process_running("process_name") is True
        mock_execute_command.assert_called_once_with("pgrep process_name", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_not_running(self, mock_execute_command):
        mock_execute_command.return_value = (1, "", "stderr", 0.1)
        assert is_process_running("process_name") is False
        mock_execute_command.assert_called_once_with("pgrep process_name", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_is_process_running_error(self, mock_execute_command):
        mock_execute_command.side_effect = Exception("error")
        assert is_process_running("process_name") is False
        mock_execute_command.assert_called_once_with("pgrep process_name", shell=True)

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_success(self, mock_execute_command):
        mock_execute_command.return_value = (0, "stdout", "stderr", 0.1)
        with patch(
            'src.playground.extract_methods_for_system_implementation.is_process_running'
        ) as mock_is_running:
            mock_is_running.return_value = True
            assert kill_process("process_name") is True
            mock_execute_command.assert_called_once_with("pkill process_name", shell=True)
            mock_is_running.assert_called_once_with("process_name")

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_not_running(self, mock_execute_command):
        with patch(
            'src.playground.extract_methods_for_system_implementation.is_process_running'
        ) as mock_is_running:
            mock_is_running.return_value = False
            assert kill_process("process_name") is True
            mock_execute_command.assert_not_called()
            mock_is_running.assert_called_once_with("process_name")

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_failure(self, mock_execute_command):
        mock_execute_command.return_value = (1, "stdout", "stderr", 0.1)
        with patch(
            'src.playground.extract_methods_for_system_implementation.is_process_running'
        ) as mock_is_running:
            mock_is_running.return_value = True
            assert kill_process("process_name") is False
            mock_execute_command.assert_called_once_with("pkill process_name", shell=True)
            mock_is_running.assert_called_once_with("process_name")

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_kill_process_error(self, mock_execute_command):
        with patch(
            'src.playground.extract_methods_for_system_implementation.is_process_running'
        ) as mock_is_running:
            mock_is_running.return_value = True
            mock_execute_command.side_effect = Exception("error")
            assert kill_process("process_name") is False
            mock_is_running.assert_called_once_with("process_name")

    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_exists_success(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        assert safely_remove_file("file_path") is True
        mock_exists.assert_called_once_with("file_path")
        mock_remove.assert_called_once_with("file_path")

    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_not_exists(self, mock_remove, mock_exists):
        mock_exists.return_value = False
        assert safely_remove_file("file_path") is True
        mock_exists.assert_called_once_with("file_path")
        mock_remove.assert_not_called()

    @patch('os.path.exists')
    @patch('os.remove')
    def test_safely_remove_file_failure(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        assert safely_remove_file("file_path") is False
        mock_exists.assert_called_once_with("file_path")
        mock_remove.assert_called_once_with("file_path")

    @patch(
        'src.playground.extract_methods_for_system_implementation._execute_command'
    )
    def test_execute_commands_in_parallel_success(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (0, "stdout1", "stderr1", 0.1),
            (1, "stdout2", "stderr2", 0.2),
            (0, "stdout3", "stderr3", 0.3),
        ]
        commands = [
            ("cmd1", False, 1),
            ("cmd2", False, 1),
            ("cmd3", False, 1),
        ]
        results = execute_commands_in_parallel(commands)
        assert results == [
            (0, "stdout1", "stderr1"),
            (1, "stdout2", "stderr2"),
            (0, "stdout3", "stderr3"),
        ]
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("cmd1", False, 1)
        mock_execute_command.assert_any_call("cmd2", False, 1)
        mock_execute_command.assert_any_call("cmd3", False, 1)

    @patch(
        'src.playground.extract_methods_for_system_implementation._execute_command'
    )
    def test_execute_commands_in_parallel_error(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (0, "stdout1", "stderr1", 0.1),
            Exception("error"),
            (0, "stdout3", "stderr3", 0.3),
        ]
        commands = [
            ("cmd1", False, 1),
            ("cmd2", False, 1),
            ("cmd3", False, 1),
        ]
        results = execute_commands_in_parallel(commands)
        assert results[0] == (0, "stdout1", "stderr1")
        assert results[1][0] == -1
        assert "error" in results[1][2]
        assert results[2] == (0, "stdout3", "stderr3")
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("cmd1", False, 1)
        mock_execute_command.assert_any_call("cmd2", False, 1)
        mock_execute_command.assert_any_call("cmd3", False, 1)


    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_get_system_information_success(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (0, "5.4.0-58-generic", "", 0.1),
            (0, "hostname", "", 0.1),
            (0, "up 1 day, 2 hours", "", 0.1),
        ]
        result = get_system_information()
        assert result == {
            "kernel_version": "5.4.0-58-generic",
            "hostname": "hostname",
            "uptime": "up 1 day, 2 hours",
        }
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("uname -r")
        mock_execute_command.assert_any_call("hostname")
        mock_execute_command.assert_any_call("uptime -p")

    @patch('src.playground.extract_methods_for_system_implementation._execute_command')
    def test_get_system_information_failure(self, mock_execute_command):
        mock_execute_command.side_effect = [
            (1, "", "error", 0.1),
            (0, "hostname", "", 0.1),
            (0, "up 1 day, 2 hours", "", 0.1),
        ]
        result = get_system_information()
        assert "kernel_version" not in result
        assert "hostname" in result
        assert "uptime" in result
        assert mock_execute_command.call_count == 3
        mock_execute_command.assert_any_call("uname -r")
        mock_execute_command.assert_any_call("hostname")
        mock_execute_command.assert_any_call("uptime -p")
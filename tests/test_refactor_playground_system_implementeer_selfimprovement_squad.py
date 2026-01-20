import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
import json

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.refactor_playground_system_implementeer_selfimprovement_squad import SystemRefactor


class TestSystemRefactor:
    @pytest.fixture
    def system_refactor(self):
        return SystemRefactor(config_file="test_config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='{"test_key": "test_value"}')
    def test_load_config_success(self, mock_open_file, system_refactor):
        config = system_refactor._load_config()
        assert config == {"test_key": "test_value"}
        mock_open_file.assert_called_once_with("test_config.json", "r")

    @patch('builtins.open', new_callable=mock_open, side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_open_file, system_refactor):
        config = system_refactor._load_config()
        assert config == {}
        mock_open_file.assert_called_once_with("test_config.json", "r")

    @patch('builtins.open', new_callable=mock_open, read_data='invalid_json')
    def test_load_config_json_decode_error(self, mock_open_file, system_refactor):
        config = system_refactor._load_config()
        assert config == {}
        mock_open_file.assert_called_once_with("test_config.json", "r")

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_subprocess_run, system_refactor):
        mock_subprocess_run.return_value.stdout = "test_output"
        output = system_refactor._execute_command("test_command")
        assert output == "test_output"
        mock_subprocess_run.assert_called_once_with(
            "test_command", shell=True, capture_output=True, text=True, check=True
        )

    @patch('subprocess.run')
    def test_execute_command_called_process_error(self, mock_subprocess_run, system_refactor):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="test_error")
        output = system_refactor._execute_command("test_command")
        assert output == ""
        mock_subprocess_run.assert_called_once_with(
            "test_command", shell=True, capture_output=True, text=True, check=True
        )

    @patch('subprocess.run')
    def test_execute_command_file_not_found(self, mock_subprocess_run, system_refactor):
        mock_subprocess_run.side_effect = FileNotFoundError
        output = system_refactor._execute_command("test_command")
        assert output == ""
        mock_subprocess_run.assert_called_once_with(
            "test_command", shell=True, capture_output=True, text=True, check=True
        )

    @patch('subprocess.run')
    def test_execute_command_other_exception(self, mock_subprocess_run, system_refactor):
        mock_subprocess_run.side_effect = Exception("generic error")
        output = system_refactor._execute_command("test_command")
        assert output == ""
        mock_subprocess_run.assert_called_once_with(
            "test_command", shell=True, capture_output=True, text=True, check=True
        )

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._execute_command')
    def test_run_command_success(self, mock_execute_command, system_refactor):
        mock_execute_command.return_value = "test_output"
        output = system_refactor._run_command("test_command")
        assert output == "test_output"
        mock_execute_command.assert_called_once_with("test_command")

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    def test_get_system_info(self, mock_run_command, system_refactor):
        mock_run_command.side_effect = ["os_name", "kernel_version", "hostname", "cpu_info", "memory_info"]
        info = system_refactor.get_system_info()
        assert info == {
            "os_name": "os_name",
            "kernel_version": "kernel_version",
            "hostname": "hostname",
            "cpu_info": "cpu_info",
            "memory_info": "memory_info",
        }
        assert mock_run_command.call_count == 5

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    def test_get_system_info_exception(self, mock_run_command, system_refactor):
        mock_run_command.side_effect = Exception("test error")
        info = system_refactor.get_system_info()
        assert info == {}
        assert mock_run_command.call_count == 1

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    def test_get_disk_usage_success(self, mock_run_command, system_refactor):
        mock_run_command.return_value = "Filesystem  Size  Used Avail Use% Mounted on\n/dev/sda1   100G  20G   70G   22%   /"
        disk_usage = system_refactor.get_disk_usage()
        assert len(disk_usage) == 1
        assert disk_usage[0] == {
            "filesystem": "/dev/sda1",
            "size": "100G",
            "used": "20G",
            "available": "70G",
            "use_percentage": "22%",
            "mounted_on": "/",
        }
        mock_run_command.assert_called_once_with("df -h")

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    def test_get_disk_usage_df_fails(self, mock_run_command, system_refactor):
        mock_run_command.return_value = ""
        disk_usage = system_refactor.get_disk_usage()
        assert disk_usage == []
        mock_run_command.assert_called_once_with("df -h")

    def test_parse_disk_info(self, system_refactor):
        fields = ["/dev/sda1", "100G", "20G", "70G", "22%", "/"]
        disk_info = system_refactor._parse_disk_info(fields)
        assert disk_info == {
            "filesystem": "/dev/sda1",
            "size": "100G",
            "used": "20G",
            "available": "70G",
            "use_percentage": "22%",
            "mounted_on": "/",
        }

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    @patch('time.sleep')
    def test_monitor_cpu_usage_success(self, mock_sleep, mock_run_command, system_refactor):
        mock_run_command.side_effect = ["10.0%", "20.0%", "30.0%"]
        cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
        assert cpu_usage == [10.0, 20.0]
        assert mock_run_command.call_count == 2
        mock_sleep.assert_called()

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor._run_command')
    @patch('time.sleep')
    def test_monitor_cpu_usage_command_fails(self, mock_sleep, mock_run_command, system_refactor):
        mock_run_command.return_value = ""
        cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
        assert cpu_usage == []
        mock_run_command.assert_called()
        mock_sleep.assert_called()

    def test_parse_cpu_usage_success(self, system_refactor):
        cpu_output = "10.5%"
        cpu_percent = system_refactor._parse_cpu_usage(cpu_output)
        assert cpu_percent == 10.5

    def test_parse_cpu_usage_invalid_value(self, system_refactor):
        cpu_output = "invalid_value"
        cpu_percent = system_refactor._parse_cpu_usage(cpu_output)
        assert cpu_percent is None

    def test_parse_cpu_usage_empty_string(self, system_refactor):
        cpu_output = ""
        cpu_percent = system_refactor._parse_cpu_usage(cpu_output)
        assert cpu_percent is None

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.get_system_info')
    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.get_disk_usage')
    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.monitor_cpu_usage')
    def test_perform_system_check_success(self, mock_monitor_cpu, mock_get_disk, mock_get_system, system_refactor):
        mock_get_system.return_value = {"os_name": "test_os"}
        mock_get_disk.return_value = [{"filesystem": "/"}]
        mock_monitor_cpu.return_value = [10.0]
        results = system_refactor.perform_system_check()
        assert results == {
            "system_info": {"os_name": "test_os"},
            "disk_usage": [{"filesystem": "/"}],
            "cpu_usage": [10.0],
        }
        mock_get_system.assert_called_once()
        mock_get_disk.assert_called_once()
        mock_monitor_cpu.assert_called_once()

    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.get_system_info')
    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.get_disk_usage')
    @patch('src.playground.refactor_playground_system_implementeer_selfimprovement_squad.SystemRefactor.monitor_cpu_usage')
    def test_perform_system_check_exception(self, mock_monitor_cpu, mock_get_disk, mock_get_system, system_refactor):
        mock_get_system.side_effect = Exception("test error")
        results = system_refactor.perform_system_check()
        assert results == {}
        mock_get_system.assert_called_once()
        mock_get_disk.assert_not_called()
        mock_monitor_cpu.assert_not_called()

    @patch('loguru.logger.info')
    @patch('loguru.logger.warning')
    def test_process_system_check_results_success(self, mock_warning, mock_info, system_refactor):
        results = {
            "system_info": {"os_name": "test_os"},
            "disk_usage": [{"filesystem": "/"}],
            "cpu_usage": [10.0],
        }
        system_refactor.process_system_check_results(results)
        assert mock_info.call_count == 4
        mock_warning.assert_not_called()

    @patch('loguru.logger.info')
    @patch('loguru.logger.warning')
    def test_process_system_check_results_no_cpu(self, mock_warning, mock_info, system_refactor):
        results = {
            "system_info": {"os_name": "test_os"},
            "disk_usage": [{"filesystem": "/"}],
        }
        system_refactor.process_system_check_results(results)
        assert mock_info.call_count == 3
        mock_warning.assert_called_once()

    @patch('loguru.logger.info')
    @patch('loguru.logger.warning')
    def test_process_system_check_results_exception(self, mock_warning, mock_info, system_refactor):
        with patch.object(system_refactor, 'get_system_info', side_effect=Exception("test error")):
            results = {
                "system_info": {"os_name": "test_os"},
                "disk_usage": [{"filesystem": "/"}],
                "cpu_usage": [10.0],
            }
            system_refactor.process_system_check_results(results)
            assert mock_info.call_count == 1
            mock_warning.assert_not_called()
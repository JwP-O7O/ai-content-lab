import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from src.playground.refactor_playground_system_implementeer_selfimprovement_squad import SystemRefactor
from loguru import logger
import json

sys.path.append(os.getcwd())


class TestSystemRefactor:
    @pytest.fixture
    def system_refactor(self):
        return SystemRefactor(config_file="test_config.json")

    @pytest.fixture
    def mock_config(self):
        return {"test_key": "test_value"}

    def test_init_with_valid_config_file(self, system_refactor, mock_config):
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))) as mock_file:
            system = SystemRefactor(config_file="test_config.json")
            mock_file.assert_called_once_with("test_config.json", "r")
            assert system.config == mock_config

    def test_init_with_config_file_not_found(self, system_refactor):
        with patch('builtins.open', side_effect=FileNotFoundError):
            system = SystemRefactor()
            assert system.config == {}

    def test_init_with_invalid_json(self, system_refactor):
        with patch('builtins.open', mock_open(read_data="invalid json")) as mock_file:
            system = SystemRefactor()
            assert system.config == {}

    def test_load_config_successful(self, system_refactor, mock_config):
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))) as mock_file:
            config = system_refactor._load_config()
            mock_file.assert_called_once_with("test_config.json", "r")
            assert config == mock_config

    def test_load_config_file_not_found(self, system_refactor):
        with patch('builtins.open', side_effect=FileNotFoundError):
            config = system_refactor._load_config()
            assert config == {}

    def test_load_config_invalid_json(self, system_refactor):
        with patch('builtins.open', mock_open(read_data="invalid json")):
            config = system_refactor._load_config()
            assert config == {}

    def test_execute_command_success(self, system_refactor):
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = "test_output"
            output = system_refactor._execute_command("test_command")
            mock_subprocess.assert_called_once_with(
                "test_command", shell=True, capture_output=True, text=True, check=True
            )
            assert output == "test_output"

    def test_execute_command_called_process_error(self, system_refactor):
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="test_error")
            output = system_refactor._execute_command("test_command")
            assert output == ""

    def test_execute_command_file_not_found_error(self, system_refactor):
        with patch('subprocess.run', side_effect=FileNotFoundError):
            output = system_refactor._execute_command("test_command")
            assert output == ""

    def test_execute_command_general_exception(self, system_refactor):
        with patch('subprocess.run', side_effect=Exception("generic error")):
            output = system_refactor._execute_command("test_command")
            assert output == ""

    def test_run_command_success(self, system_refactor):
        with patch.object(system_refactor, '_execute_command') as mock_execute_command:
            mock_execute_command.return_value = "test_output"
            output = system_refactor._run_command("test_command")
            mock_execute_command.assert_called_once_with("test_command")
            assert output == "test_output"

    def test_run_command_no_output(self, system_refactor):
        with patch.object(system_refactor, '_execute_command') as mock_execute_command:
            mock_execute_command.return_value = ""
            output = system_refactor._run_command("test_command")
            mock_execute_command.assert_called_once_with("test_command")
            assert output == ""

    def test_get_system_info_success(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command:
            mock_run_command.side_effect = ["os_name", "kernel_version", "hostname", "cpu_info", "memory_info"]
            system_info = system_refactor.get_system_info()
            assert system_info == {
                "os_name": "os_name",
                "kernel_version": "kernel_version",
                "hostname": "hostname",
                "cpu_info": "cpu_info",
                "memory_info": "memory_info",
            }
            assert mock_run_command.call_count == 5

    def test_get_system_info_failure(self, system_refactor):
        with patch.object(system_refactor, '_run_command', side_effect=Exception("error")):
            system_info = system_refactor.get_system_info()
            assert system_info == {}

    def test_get_disk_usage_success(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command:
            mock_run_command.return_value = "Filesystem  Size  Used Avail Use% Mounted on\n/dev/sda1   100G   20G   70G   20%   /\n/dev/sdb1   50G    10G   30G   20%   /mnt"
            disk_usage = system_refactor.get_disk_usage()
            assert len(disk_usage) == 2
            assert disk_usage[0]["filesystem"] == "/dev/sda1"
            assert disk_usage[1]["mounted_on"] == "/mnt"
            mock_run_command.assert_called_once_with("df -h")

    def test_get_disk_usage_no_output(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command:
            mock_run_command.return_value = ""
            disk_usage = system_refactor.get_disk_usage()
            assert disk_usage == []
            mock_run_command.assert_called_once_with("df -h")


    def test_get_disk_usage_failure(self, system_refactor):
        with patch.object(system_refactor, '_run_command', side_effect=Exception("error")):
            disk_usage = system_refactor.get_disk_usage()
            assert disk_usage == []

    def test_monitor_cpu_usage_success(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command, patch('time.sleep') as mock_sleep:
            mock_run_command.return_value = "20.0%"
            cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
            assert len(cpu_usage) == 2
            assert mock_run_command.call_count == 2
            mock_sleep.assert_called()

    def test_monitor_cpu_usage_command_failure(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command, patch('time.sleep') as mock_sleep:
            mock_run_command.return_value = ""
            cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
            assert cpu_usage == []
            assert mock_run_command.call_count == 2

    def test_monitor_cpu_usage_parsing_error(self, system_refactor):
        with patch.object(system_refactor, '_run_command') as mock_run_command, patch('time.sleep') as mock_sleep:
            mock_run_command.return_value = "invalid_cpu_usage"
            cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
            assert cpu_usage == []
            assert mock_run_command.call_count == 2

    def test_monitor_cpu_usage_general_exception(self, system_refactor):
        with patch.object(system_refactor, '_run_command', side_effect=Exception("error")), patch('time.sleep'):
            cpu_usage = system_refactor.monitor_cpu_usage(interval=1, duration=2)
            assert cpu_usage == []

    def test_perform_system_check_success(self, system_refactor):
        with patch.object(system_refactor, 'get_system_info') as mock_get_system_info, \
                patch.object(system_refactor, 'get_disk_usage') as mock_get_disk_usage, \
                patch.object(system_refactor, 'monitor_cpu_usage') as mock_monitor_cpu_usage:
            mock_get_system_info.return_value = {"os_name": "test_os"}
            mock_get_disk_usage.return_value = [{"filesystem": "/dev/sda1"}]
            mock_monitor_cpu_usage.return_value = [20.0, 21.0]
            results = system_refactor.perform_system_check()
            assert results["system_info"] == {"os_name": "test_os"}
            assert results["disk_usage"] == [{"filesystem": "/dev/sda1"}]
            assert results["cpu_usage"] == [20.0, 21.0]

    def test_perform_system_check_failure(self, system_refactor):
        with patch.object(system_refactor, 'get_system_info', side_effect=Exception("error")):
            results = system_refactor.perform_system_check()
            assert results == {}

    def test_process_system_check_results_success(self, system_refactor):
        with patch('loguru.logger.info') as mock_logger_info:
            results = {
                "system_info": {"os_name": "test_os"},
                "disk_usage": [{"filesystem": "/dev/sda1"}],
                "cpu_usage": [20.0, 21.0],
            }
            system_refactor.process_system_check_results(results)
            assert mock_logger_info.call_count == 5

    def test_process_system_check_results_no_cpu_usage(self, system_refactor):
        with patch('loguru.logger.info') as mock_logger_info, patch('loguru.logger.warning') as mock_logger_warning:
            results = {
                "system_info": {"os_name": "test_os"},
                "disk_usage": [{"filesystem": "/dev/sda1"}],
            }
            system_refactor.process_system_check_results(results)
            assert mock_logger_info.call_count == 3
            mock_logger_warning.assert_called_once()


    def test_process_system_check_results_failure(self, system_refactor):
        with patch('loguru.logger.error') as mock_logger_error:
            with pytest.raises(Exception):
                system_refactor.process_system_check_results({"results": 123})
            mock_logger_error.assert_called_once()
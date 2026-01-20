import pytest
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
import json

sys.path.append(os.getcwd())  # Add current directory to sys.path
from src.playground.refactor_playground_system_implementeer_selfimprovement_squad import SystemRefactor


@pytest.fixture
def system_refactor_instance():
    return SystemRefactor(config_file="test_config.json")


class TestSystemRefactor:
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_config_success(self, mock_open, system_refactor_instance):
        config = system_refactor_instance._load_config()
        assert config == {"key": "value"}
        mock_open.assert_called_once_with("test_config.json", "r")

    @patch("builtins.open", new_callable=mock_open, side_effect=FileNotFoundError)
    def test_load_config_file_not_found(self, mock_open, system_refactor_instance):
        config = system_refactor_instance._load_config()
        assert config == {}
        mock_open.assert_called_once_with("test_config.json", "r")

    @patch("builtins.open", new_callable=mock_open, read_data="invalid_json")
    def test_load_config_json_decode_error(self, mock_open, system_refactor_instance):
        config = system_refactor_instance._load_config()
        assert config == {}
        mock_open.assert_called_once_with("test_config.json", "r")

    @patch("subprocess.run")
    def test_run_command_success(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.return_value.stdout = "test_output"
        output = system_refactor_instance._run_command("test_command")
        assert output == "test_output"
        mock_subprocess_run.assert_called_once_with(
            "test_command", shell=True, capture_output=True, text=True, check=True
        )

    @patch("subprocess.run")
    def test_run_command_called_process_error(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="test_error")
        output = system_refactor_instance._run_command("test_command")
        assert output == ""
        mock_subprocess_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_file_not_found(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = FileNotFoundError
        output = system_refactor_instance._run_command("test_command")
        assert output == ""
        mock_subprocess_run.assert_called_once()
        
    @patch("subprocess.run")
    def test_get_system_info_success(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = [
            MagicMock(stdout="OS"),
            MagicMock(stdout="Kernel"),
            MagicMock(stdout="Hostname"),
            MagicMock(stdout="CPU"),
            MagicMock(stdout="Memory")
        ]
        info = system_refactor_instance.get_system_info()
        assert info == {
            "os_name": "OS",
            "kernel_version": "Kernel",
            "hostname": "Hostname",
            "cpu_info": "CPU",
            "memory_info": "Memory",
        }
        assert mock_subprocess_run.call_count == 5

    @patch("subprocess.run")
    def test_get_system_info_error(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = Exception("Test error")
        info = system_refactor_instance.get_system_info()
        assert info == {}
        assert mock_subprocess_run.call_count == 1

    @patch("subprocess.run")
    def test_get_disk_usage_success(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.return_value.stdout = "Filesystem  Size  Used  Avail Use% Mounted on\n/dev/sda1   100G   20G   80G   20%   /\n/dev/sdb1   50G    10G   40G   20%   /mnt"
        usage = system_refactor_instance.get_disk_usage()
        assert len(usage) == 2
        assert usage[0]["filesystem"] == "/dev/sda1"
        assert usage[1]["mounted_on"] == "/mnt"
        mock_subprocess_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_disk_usage_error(self, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = Exception("Test error")
        usage = system_refactor_instance.get_disk_usage()
        assert usage == []
        mock_subprocess_run.assert_called_once()

    @patch("subprocess.run")
    @patch("time.sleep")
    def test_monitor_cpu_usage_success(self, mock_sleep, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = [
            MagicMock(stdout="Cpu(s):  0.0%us,  0.0%sy,  0.0%ni, 100.0%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st"),
            MagicMock(stdout="Cpu(s):  1.0%us,  1.0%sy,  1.0%ni, 97.0%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st")
        ]
        percentages = system_refactor_instance.monitor_cpu_usage(interval=1, duration=2)
        assert len(percentages) == 2
        assert abs(percentages[0] - 100.0) < 0.001
        assert abs(percentages[1] - 97.0) < 0.001
        assert mock_subprocess_run.call_count == 2
        mock_sleep.assert_called_with(1)

    @patch("subprocess.run")
    @patch("time.sleep")
    def test_monitor_cpu_usage_error(self, mock_sleep, mock_subprocess_run, system_refactor_instance):
        mock_subprocess_run.side_effect = Exception("Test error")
        percentages = system_refactor_instance.monitor_cpu_usage(interval=1, duration=2)
        assert percentages == []
        mock_subprocess_run.assert_called_once()
        mock_sleep.assert_not_called()

    @patch.object(SystemRefactor, 'get_system_info')
    @patch.object(SystemRefactor, 'get_disk_usage')
    @patch.object(SystemRefactor, 'monitor_cpu_usage')
    def test_perform_system_check_success(self, mock_monitor_cpu, mock_get_disk, mock_get_system, system_refactor_instance):
        mock_get_system.return_value = {"os_name": "TestOS"}
        mock_get_disk.return_value = [{"filesystem": "/"}]
        mock_monitor_cpu.return_value = [50.0]

        results = system_refactor_instance.perform_system_check()
        assert results["system_info"] == {"os_name": "TestOS"}
        assert results["disk_usage"] == [{"filesystem": "/"}]
        assert results["cpu_usage"] == [50.0]

        mock_get_system.assert_called_once()
        mock_get_disk.assert_called_once()
        mock_monitor_cpu.assert_called_once()

    @patch.object(SystemRefactor, 'get_system_info', side_effect=Exception("Test Error"))
    @patch.object(SystemRefactor, 'get_disk_usage')
    @patch.object(SystemRefactor, 'monitor_cpu_usage')
    def test_perform_system_check_error(self, mock_monitor_cpu, mock_get_disk, mock_get_system, system_refactor_instance):
        results = system_refactor_instance.perform_system_check()
        assert results == {}
        mock_get_system.assert_called_once()
        mock_get_disk.assert_not_called()
        mock_monitor_cpu.assert_not_called()

    def test_process_system_check_results_success(self, system_refactor_instance):
        results = {
            "system_info": {"os_name": "TestOS"},
            "disk_usage": [{"filesystem": "/"}],
            "cpu_usage": [50.0],
        }
        with patch('loguru.logger.info') as mock_info:
            system_refactor_instance.process_system_check_results(results)
            assert mock_info.call_count == 4
            mock_info.assert_any_call("Resultaten van systeemcheck:")
            mock_info.assert_any_call("Systeem informatie: {'os_name': 'TestOS'}")
            mock_info.assert_any_call("Disk Usage: [{'filesystem': '/'}]")
            mock_info.assert_any_call("CPU Usage: [50.0]")
            mock_info.assert_any_call("Verwerking van resultaten voltooid.")
    
    def test_process_system_check_results_no_cpu(self, system_refactor_instance):
        results = {
            "system_info": {"os_name": "TestOS"},
            "disk_usage": [{"filesystem": "/"}],
        }
        with patch('loguru.logger.info') as mock_info, patch('loguru.logger.warning') as mock_warn:
            system_refactor_instance.process_system_check_results(results)
            assert mock_info.call_count == 3
            mock_warn.assert_called_once_with("Geen CPU usage data beschikbaar.")
            mock_info.assert_any_call("Resultaten van systeemcheck:")

    def test_process_system_check_results_error(self, system_refactor_instance):
        with patch('loguru.logger.error') as mock_error:
            with pytest.raises(Exception):
                system_refactor_instance.process_system_check_results("invalid_results")
            mock_error.assert_called_once()
import pytest
from unittest.mock import patch, MagicMock
from src.mission_control import MissionControl
import os
import sys

# Add the project root to the Python path
sys.path.append(os.getcwd())


class TestMissionControl:
    @pytest.fixture
    def mission_control(self):
        return MissionControl()

    def test_launch_sequence_success(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ) as mock_validate:
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=True
            ) as mock_prepare:
                with patch.object(
                    mission_control, "_initiate_launch", return_value=True
                ) as mock_initiate:
                    result = mission_control.launch_sequence()
                    assert result is True
                    mock_validate.assert_called_once()
                    mock_prepare.assert_called_once()
                    mock_initiate.assert_called_once()


    def test_launch_sequence_validation_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=False
        ) as mock_validate:
            result = mission_control.launch_sequence()
            assert result is False
            mock_validate.assert_called_once()


    def test_launch_sequence_prepare_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ) as mock_validate:
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=False
            ) as mock_prepare:
                result = mission_control.launch_sequence()
                assert result is False
                mock_validate.assert_called_once()
                mock_prepare.assert_called_once()


    def test_launch_sequence_initiate_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ) as mock_validate:
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=True
            ) as mock_prepare:
                with patch.object(
                    mission_control, "_initiate_launch", return_value=False
                ) as mock_initiate:
                    result = mission_control.launch_sequence()
                    assert result is False
                    mock_validate.assert_called_once()
                    mock_prepare.assert_called_once()
                    mock_initiate.assert_called_once()


    def test_validate_launch_parameters_success(self, mission_control):
        with patch.object(
            mission_control,
            "get_rocket_status",
            return_value={"fuel": 100, "engine": "ok", "navigation": "ok"},
        ) as mock_get_status:
            result = mission_control._validate_launch_parameters()
            assert result is True
            mock_get_status.assert_called_once()


    def test_validate_launch_parameters_failure(self, mission_control):
        with patch.object(
            mission_control,
            "get_rocket_status",
            return_value={"fuel": 10, "engine": "ok", "navigation": "ok"},
        ) as mock_get_status:
            result = mission_control._validate_launch_parameters()
            assert result is False
            mock_get_status.assert_called_once()


    def test_prepare_for_launch_success(self, mission_control):
        with patch.object(
            mission_control, "perform_pre_launch_checks", return_value=True
        ) as mock_perform_checks:
            result = mission_control._prepare_for_launch()
            assert result is True
            mock_perform_checks.assert_called_once()


    def test_prepare_for_launch_failure(self, mission_control):
        with patch.object(
            mission_control, "perform_pre_launch_checks", return_value=False
        ) as mock_perform_checks:
            result = mission_control._prepare_for_launch()
            assert result is False
            mock_perform_checks.assert_called_once()


    def test_initiate_launch_success(self, mission_control):
        with patch.object(mission_control, "trigger_ignition", return_value=True) as mock_trigger_ignition:
            result = mission_control._initiate_launch()
            assert result is True
            mock_trigger_ignition.assert_called_once()


    def test_initiate_launch_failure(self, mission_control):
        with patch.object(mission_control, "trigger_ignition", return_value=False) as mock_trigger_ignition:
            result = mission_control._initiate_launch()
            assert result is False
            mock_trigger_ignition.assert_called_once()


    def test_get_rocket_status_success(self, mission_control):
        with patch("src.mission_control.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "fuel": 80,
                "engine": "ok",
                "navigation": "ok",
            }
            status = mission_control.get_rocket_status()
            assert isinstance(status, dict)
            assert status["fuel"] == 80
            mock_get.assert_called_once()
            mock_get.return_value.json.assert_called_once()


    def test_get_rocket_status_failure(self, mission_control):
        with patch("src.mission_control.requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            status = mission_control.get_rocket_status()
            assert status is None
            mock_get.assert_called_once()
import pytest
from unittest.mock import patch, MagicMock
from src.playground.test_mission_control import MissionControl
import requests
import logging  # Import logging for logger.warning and logger.error
from loguru import logger
import os
import sys

sys.path.append(os.getcwd())


class TestMissionControl:
    @patch("src.playground.test_mission_control.MissionControl.get_rocket_status")
    @patch("src.playground.test_mission_control.MissionControl.perform_pre_launch_checks")
    @patch("src.playground.test_mission_control.MissionControl.trigger_ignition")
    def test_launch_sequence_successful(
        self, mock_trigger_ignition, mock_perform_pre_launch_checks, mock_get_rocket_status
    ):
        mock_get_rocket_status.return_value = {"fuel": 50, "status": "ok"}
        mock_perform_pre_launch_checks.return_value = True
        mock_trigger_ignition.return_value = True

        mission_control = MissionControl()
        result = mission_control.launch_sequence()

        assert result is True
        mock_get_rocket_status.assert_called_once()
        mock_perform_pre_launch_checks.assert_called_once()
        mock_trigger_ignition.assert_called_once()

    @patch("src.playground.test_mission_control.MissionControl.get_rocket_status")
    @patch("src.playground.test_mission_control.MissionControl.perform_pre_launch_checks")
    @patch("src.playground.test_mission_control.MissionControl.trigger_ignition")
    def test_launch_sequence_fuel_low(
        self, mock_trigger_ignition, mock_perform_pre_launch_checks, mock_get_rocket_status
    ):
        mock_get_rocket_status.return_value = {"fuel": 10, "status": "ok"}
        mock_perform_pre_launch_checks.return_value = True
        mock_trigger_ignition.return_value = True

        mission_control = MissionControl()
        result = mission_control.launch_sequence()

        assert result is False
        mock_get_rocket_status.assert_called_once()
        mock_perform_pre_launch_checks.assert_not_called()
        mock_trigger_ignition.assert_not_called()

    @patch("src.playground.test_mission_control.MissionControl.get_rocket_status")
    @patch("src.playground.test_mission_control.MissionControl.perform_pre_launch_checks")
    @patch("src.playground.test_mission_control.MissionControl.trigger_ignition")
    def test_launch_sequence_prelaunch_checks_fail(
        self, mock_trigger_ignition, mock_perform_pre_launch_checks, mock_get_rocket_status
    ):
        mock_get_rocket_status.return_value = {"fuel": 50, "status": "ok"}
        mock_perform_pre_launch_checks.return_value = False
        mock_trigger_ignition.return_value = True

        mission_control = MissionControl()
        result = mission_control.launch_sequence()

        assert result is False
        mock_get_rocket_status.assert_called_once()
        mock_perform_pre_launch_checks.assert_called_once()
        mock_trigger_ignition.assert_not_called()

    @patch("src.playground.test_mission_control.MissionControl.get_rocket_status")
    @patch("src.playground.test_mission_control.MissionControl.perform_pre_launch_checks")
    @patch("src.playground.test_mission_control.MissionControl.trigger_ignition")
    def test_launch_sequence_ignition_fails(
        self, mock_trigger_ignition, mock_perform_pre_launch_checks, mock_get_rocket_status
    ):
        mock_get_rocket_status.return_value = {"fuel": 50, "status": "ok"}
        mock_perform_pre_launch_checks.return_value = True
        mock_trigger_ignition.return_value = False

        mission_control = MissionControl()
        result = mission_control.launch_sequence()

        assert result is False
        mock_get_rocket_status.assert_called_once()
        mock_perform_pre_launch_checks.assert_called_once()
        mock_trigger_ignition.assert_called_once()

    @patch("requests.get")
    def test_get_rocket_status_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"fuel": 50, "status": "ok"}
        mock_get.return_value = mock_response

        mission_control = MissionControl()
        status = mission_control.get_rocket_status()

        assert status == {"fuel": 50, "status": "ok"}
        mock_get.assert_called_once_with("http://example.com/rocket_status")
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    @patch("requests.get")
    def test_get_rocket_status_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Simulated error")

        mission_control = MissionControl()
        status = mission_control.get_rocket_status()

        assert status is None
        mock_get.assert_called_once_with("http://example.com/rocket_status")

    @patch("requests.get")
    def test_get_rocket_status_json_decode_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        mission_control = MissionControl()
        status = mission_control.get_rocket_status()

        assert status is None
        mock_get.assert_called_once_with("http://example.com/rocket_status")
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
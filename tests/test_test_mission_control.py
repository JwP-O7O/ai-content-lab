import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

sys.path.append(os.getcwd())
from src.playground.test_mission_control import MissionControl
from loguru import logger

class TestMissionControl:

    def test_mission_control_initial_status(self):
        mission_control = MissionControl()
        assert mission_control.get_mission_status() == "stopped"

    @patch.object(logger, 'info')
    def test_start_mission(self, mock_logger_info):
        mission_control = MissionControl()
        mission_control.start_mission()
        mock_logger_info.assert_called_once_with("Mission started.")
        assert mission_control.get_mission_status() == "running"

    @patch.object(logger, 'info')
    def test_end_mission(self, mock_logger_info):
        mission_control = MissionControl()
        mission_control.start_mission()  # Ensure mission is running before ending
        mission_control.end_mission()
        mock_logger_info.assert_called_with("Mission ended.")
        assert mission_control.get_mission_status() == "stopped"

    def test_get_mission_status(self):
        mission_control = MissionControl()
        status = mission_control.get_mission_status()
        assert status == "stopped"

        mission_control.start_mission()
        status = mission_control.get_mission_status()
        assert status == "running"
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from src.playground.test_mission_control import TestMissionControl
from src.mission_control import MissionControl

sys.path.append(os.getcwd())


class TestTestMissionControl:
    @pytest.fixture
    def test_mission_control(self):
        return TestMissionControl()

    @pytest.fixture
    def mission_control(self):
        """Fixture to create a MissionControl instance."""
        return MissionControl()

    def test_init(self, test_mission_control: TestMissionControl):
        """Test the initialization of TestMissionControl."""
        assert isinstance(test_mission_control, TestMissionControl)

    def test_mission_control_fixture(self, mission_control: MissionControl):
        """Test if mission_control fixture is working correctly"""
        assert isinstance(mission_control, MissionControl)

    @patch("src.mission_control.logger.info")
    def test_start_mission(self, mock_logger_info, test_mission_control: TestMissionControl, mission_control: MissionControl):
        """Test the start_mission method."""
        test_mission_control.mission_control = mission_control  # Assign mission_control to instance attribute
        test_mission_control.test_start_mission(mock_logger_info, mission_control)
        mock_logger_info.assert_called_with("Mission started.")

    @patch("src.mission_control.logger.info")
    def test_end_mission(self, mock_logger_info, test_mission_control: TestMissionControl, mission_control: MissionControl):
        """Test the end_mission method."""
        test_mission_control.mission_control = mission_control
        test_mission_control.test_end_mission(mock_logger_info, mission_control)
        mock_logger_info.assert_called_with("Mission ended.")

    @patch("src.mission_control.logger.info")
    def test_get_mission_status_running(
        self, mock_logger_info, test_mission_control: TestMissionControl, mission_control: MissionControl
    ):
        """Test get_mission_status method when mission is running."""
        test_mission_control.mission_control = mission_control
        test_mission_control.test_get_mission_status_running(mock_logger_info, mission_control)
        mock_logger_info.assert_called()  # Check if logger.info was called in start_mission

    @patch("src.mission_control.logger.info")
    def test_get_mission_status_stopped(
        self, mock_logger_info, test_mission_control: TestMissionControl, mission_control: MissionControl
    ):
        """Test get_mission_status method when mission is stopped."""
        test_mission_control.mission_control = mission_control
        test_mission_control.test_get_mission_status_stopped(mock_logger_info, mission_control)
        mock_logger_info.assert_called()  # Check if logger.info was called in end_mission
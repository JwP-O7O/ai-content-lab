# test_mission_control.py
import pytest
from unittest.mock import patch
from src.mission_control import MissionControl
from loguru import logger  # Correct import for logging


class TestMissionControl:
    @pytest.fixture
    def mission_control(self):
        """Fixture to create a MissionControl instance."""
        try:
            return MissionControl()
        except Exception as e:
            logger.error(f"Failed to initialize MissionControl: {e}")
            pytest.fail(f"Failed to initialize MissionControl: {e}")

    def test_init(self, mission_control: MissionControl):
        """Test the initialization of MissionControl."""
        assert isinstance(mission_control, MissionControl)

    @patch("src.mission_control.logger.info")
    def test_start_mission(self, mock_logger_info, mission_control: MissionControl):
        """Test the start_mission method."""
        try:
            mission_control.start_mission()
            mock_logger_info.assert_called_with("Mission started.")
        except Exception as e:
            logger.error(f"Error in test_start_mission: {e}")
            pytest.fail(f"test_start_mission failed: {e}")

    @patch("src.mission_control.logger.info")
    def test_end_mission(self, mock_logger_info, mission_control: MissionControl):
        """Test the end_mission method."""
        try:
            mission_control.end_mission()
            mock_logger_info.assert_called_with("Mission ended.")
        except Exception as e:
            logger.error(f"Error in test_end_mission: {e}")
            pytest.fail(f"test_end_mission failed: {e}")

    @patch("src.mission_control.logger.info")
    def test_get_mission_status_running(
        self, mock_logger_info, mission_control: MissionControl
    ):
        """Test get_mission_status method when mission is running."""
        try:
            mission_control.start_mission()
            status = mission_control.get_mission_status()
            assert status == "running"
            mock_logger_info.assert_called()  # Check if logger.info was called in start_mission
        except Exception as e:
            logger.error(f"Error in test_get_mission_status_running: {e}")
            pytest.fail(f"test_get_mission_status_running failed: {e}")

    @patch("src.mission_control.logger.info")
    def test_get_mission_status_stopped(
        self, mock_logger_info, mission_control: MissionControl
    ):
        """Test get_mission_status method when mission is stopped."""
        try:
            mission_control.end_mission()
            status = mission_control.get_mission_status()
            assert status == "stopped"
            mock_logger_info.assert_called()  # Check if logger.info was called in end_mission
        except Exception as e:
            logger.error(f"Error in test_get_mission_status_stopped: {e}")
            pytest.fail(f"test_get_mission_status_stopped failed: {e}")
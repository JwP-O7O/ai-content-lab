# test_mission_control.py
import pytest
from unittest.mock import patch
from src.mission_control import MissionControl
from loguru import logger  # Importeer de logger

# Assume MissionControl is in a module named src/mission_control.py


@pytest.fixture
def mission_control():
    """Fixture to create a MissionControl instance."""
    try:
        return MissionControl()
    except Exception as e:
        logger.error(f"Failed to initialize MissionControl for testing: {e}")
        pytest.fail(f"Failed to initialize MissionControl: {e}")


def test_mission_control_initialization(mission_control):
    """Test that MissionControl initializes without errors."""
    assert isinstance(mission_control, MissionControl)
    logger.info("MissionControl initialized successfully.")


@patch("src.mission_control.logger.info")
def test_mission_control_start_mission(mock_logger_info, mission_control):
    """Test the start_mission method."""
    try:
        mission_control.start_mission("Test Mission")
        mock_logger_info.assert_called_with(
            "Starting mission: Test Mission"
        )  # Check logging
        logger.info("start_mission test passed.")
    except Exception as e:
        logger.error(f"Error in start_mission test: {e}")
        pytest.fail(f"start_mission test failed: {e}")


@patch("src.mission_control.logger.info")
def test_mission_control_end_mission(mock_logger_info, mission_control):
    """Test the end_mission method."""
    try:
        mission_control.end_mission("Test Mission")
        mock_logger_info.assert_called_with(
            "Ending mission: Test Mission"
        )  # Check logging
        logger.info("end_mission test passed.")
    except Exception as e:
        logger.error(f"Error in end_mission test: {e}")
        pytest.fail(f"end_mission test failed: {e}")


def test_mission_control_mission_status(mission_control):
    """Test the mission_status method."""
    try:
        mission_control.start_mission("Status Mission")
        status = mission_control.mission_status("Status Mission")
        assert (
            status == "Mission Status: Status Mission - Active"
        )  # Adjust expected output if mission_status does more.
        logger.info("mission_status test passed (Active).")

        mission_control.end_mission("Status Mission")
        status = mission_control.mission_status("Status Mission")
        assert (
            status == "Mission Status: Status Mission - Inactive"
        )  # Adjust expected output
        logger.info("mission_status test passed (Inactive).")
    except Exception as e:
        logger.error(f"Error in mission_status test: {e}")
        pytest.fail(f"mission_status test failed: {e}")
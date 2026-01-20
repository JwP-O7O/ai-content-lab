import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.getcwd())

from src.playground.test_mission_control import (
    test_mission_control_initialization,
    test_mission_control_start_mission,
    test_mission_control_end_mission,
    test_mission_control_mission_status,
)
from src.mission_control import MissionControl
from loguru import logger

# Mock the logger to avoid real logging during tests
@pytest.fixture
def mock_logger():
    with patch("src.mission_control.logger.info") as mock_info, \
         patch("src.mission_control.logger.error") as mock_error:
        yield mock_info, mock_error


@pytest.fixture
def mission_control():
    """Fixture to create a MissionControl instance."""
    try:
        return MissionControl()
    except Exception as e:
        logger.error(f"Failed to initialize MissionControl for testing: {e}")
        pytest.fail(f"Failed to initialize MissionControl: {e}")


def test_mission_control_initialization_wrapper(mission_control):
    """Wrapper for test_mission_control_initialization."""
    test_mission_control_initialization(mission_control)


def test_mission_control_start_mission_wrapper(mission_control, mock_logger):
    """Wrapper for test_mission_control_start_mission."""
    mock_info, mock_error = mock_logger
    test_mission_control_start_mission(mock_info, mission_control)


def test_mission_control_end_mission_wrapper(mission_control, mock_logger):
    """Wrapper for test_mission_control_end_mission."""
    mock_info, mock_error = mock_logger
    test_mission_control_end_mission(mock_info, mission_control)


def test_mission_control_mission_status_wrapper(mission_control, mock_logger):
    """Wrapper for test_mission_control_mission_status."""
    mock_info, mock_error = mock_logger
    test_mission_control_mission_status(mission_control)
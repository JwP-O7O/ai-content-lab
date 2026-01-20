import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the current directory to sys.path for importing the code under test
sys.path.append(os.getcwd())
from src.playground.test_mission_control import MissionControl


class TestMissionControl:
    @pytest.fixture
    def mission_control(self):
        return MissionControl()

    def test_start_mission(self, mission_control, caplog):
        mission_name = "TestMission"
        mission_control.start_mission(mission_name)
        assert mission_control.missions[mission_name] == "Active"
        assert f"Starting mission: {mission_name}" in caplog.text

    def test_end_mission(self, mission_control, caplog):
        mission_name = "TestMission"
        mission_control.start_mission(mission_name)  # Ensure mission is active
        mission_control.end_mission(mission_name)
        assert mission_control.missions[mission_name] == "Inactive"
        assert f"Ending mission: {mission_name}" in caplog.text

    def test_mission_status_active(self, mission_control):
        mission_name = "TestMission"
        mission_control.start_mission(mission_name)
        status = mission_control.mission_status(mission_name)
        assert status == "Mission Status: TestMission - Active"

    def test_mission_status_inactive(self, mission_control):
        mission_name = "TestMission"
        status = mission_control.mission_status(mission_name)
        assert status == "Mission Status: TestMission - Inactive"
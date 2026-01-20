import pytest
from unittest.mock import patch, MagicMock
from src.playground.test_mission_control import MissionControl
import logging

@pytest.fixture
def mission_control():
    return MissionControl()

def test_start_mission(mission_control, caplog):
    caplog.set_level(logging.INFO)
    mission_name = "TestMission"
    mission_control.start_mission(mission_name)
    assert mission_name in mission_control.missions
    assert mission_control.missions[mission_name] == "Active"
    assert any(record.levelname == "INFO" and record.message == f"Starting mission: {mission_name}" for record in caplog.records)


def test_end_mission(mission_control, caplog):
    caplog.set_level(logging.INFO)
    mission_name = "TestMission"
    mission_control.start_mission(mission_name)
    mission_control.end_mission(mission_name)
    assert mission_name in mission_control.missions
    assert mission_control.missions[mission_name] == "Inactive"
    assert any(record.levelname == "INFO" and record.message == f"Ending mission: {mission_name}" for record in caplog.records)


def test_mission_status_active(mission_control):
    mission_name = "TestMission"
    mission_control.start_mission(mission_name)
    status = mission_control.mission_status(mission_name)
    assert status == f"Mission Status: {mission_name} - Active"


def test_mission_status_inactive(mission_control):
    mission_name = "TestMission"
    status = mission_control.mission_status(mission_name)
    assert status == f"Mission Status: {mission_name} - Inactive"


def test_mission_status_does_not_exist(mission_control):
    mission_name = "NonExistentMission"
    status = mission_control.mission_status(mission_name)
    assert status == f"Mission Status: {mission_name} - Inactive"
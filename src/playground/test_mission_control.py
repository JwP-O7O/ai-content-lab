# test_mission_control.py
import pytest
from unittest.mock import patch
from src.mission_control import MissionControl
from loguru import logger  # Corrected import location


class TestMissionControl:
    @pytest.fixture
    def mission_control(self):
        return MissionControl()

    def test_launch_sequence_success(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ):
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=True
            ):
                with patch.object(
                    mission_control, "_initiate_launch", return_value=True
                ):
                    result = mission_control.launch_sequence()
                    assert result is True
                    logger.info("Launch sequence successful test passed.")

    def test_launch_sequence_validation_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=False
        ):
            result = mission_control.launch_sequence()
            assert result is False
            logger.info("Launch sequence validation failure test passed.")

    def test_launch_sequence_prepare_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ):
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=False
            ):
                result = mission_control.launch_sequence()
                assert result is False
                logger.info("Launch sequence prepare failure test passed.")

    def test_launch_sequence_initiate_failure(self, mission_control):
        with patch.object(
            mission_control, "_validate_launch_parameters", return_value=True
        ):
            with patch.object(
                mission_control, "_prepare_for_launch", return_value=True
            ):
                with patch.object(
                    mission_control, "_initiate_launch", return_value=False
                ):
                    result = mission_control.launch_sequence()
                    assert result is False
                    logger.info("Launch sequence initiate failure test passed.")

    def test_validate_launch_parameters_success(self, mission_control):
        try:
            with patch.object(
                mission_control,
                "get_rocket_status",
                return_value={"fuel": 100, "engine": "ok", "navigation": "ok"},
            ):
                result = mission_control._validate_launch_parameters()
                assert result is True
                logger.info("Validate launch parameters success test passed.")
        except Exception as e:
            logger.error(f"Error in validate launch parameters success test: {e}")
            pytest.fail(f"Test failed: {e}")

    def test_validate_launch_parameters_failure(self, mission_control):
        try:
            with patch.object(
                mission_control,
                "get_rocket_status",
                return_value={"fuel": 10, "engine": "ok", "navigation": "ok"},
            ):
                result = mission_control._validate_launch_parameters()
                assert result is False
                logger.info("Validate launch parameters failure test passed.")
        except Exception as e:
            logger.error(f"Error in validate launch parameters failure test: {e}")
            pytest.fail(f"Test failed: {e}")

    def test_prepare_for_launch_success(self, mission_control):
        with patch.object(
            mission_control, "perform_pre_launch_checks", return_value=True
        ):
            result = mission_control._prepare_for_launch()
            assert result is True
            logger.info("Prepare for launch success test passed.")

    def test_prepare_for_launch_failure(self, mission_control):
        with patch.object(
            mission_control, "perform_pre_launch_checks", return_value=False
        ):
            result = mission_control._prepare_for_launch()
            assert result is False
            logger.info("Prepare for launch failure test passed.")

    def test_initiate_launch_success(self, mission_control):
        with patch.object(mission_control, "trigger_ignition", return_value=True):
            result = mission_control._initiate_launch()
            assert result is True
            logger.info("Initiate launch success test passed.")

    def test_initiate_launch_failure(self, mission_control):
        with patch.object(mission_control, "trigger_ignition", return_value=False):
            result = mission_control._initiate_launch()
            assert result is False
            logger.info("Initiate launch failure test passed.")

    def test_get_rocket_status_success(self, mission_control):
        try:
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
                logger.info("Get rocket status success test passed.")
        except Exception as e:
            logger.error(f"Error in get rocket status success test: {e}")
            pytest.fail(f"Test failed: {e}")

    def test_get_rocket_status_failure(self, mission_control):
        try:
            with patch("src.mission_control.requests.get") as mock_get:
                mock_get.return_value.status_code = 500
                status = mission_control.get_rocket_status()
                assert status is None
                logger.info("Get rocket status failure test passed.")
        except Exception as e:
            logger.error(f"Error in get rocket status failure test: {e}")
            pytest.fail(f"Test failed: {e}")
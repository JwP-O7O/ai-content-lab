import requests
from loguru import logger


class MissionControl:
    def launch_sequence(self):
        if not self._validate_launch_parameters():
            return False
        if not self._prepare_for_launch():
            return False
        if not self._initiate_launch():
            return False
        return True

    def _validate_launch_parameters(self):
        rocket_status = self.get_rocket_status()
        if rocket_status is None:
            return False
        if rocket_status.get("fuel", 0) < 20:  # Assuming fuel check is important
            logger.warning("Fuel level is too low.")
            return False
        return True

    def _prepare_for_launch(self):
        return self.perform_pre_launch_checks()

    def _initiate_launch(self):
        return self.trigger_ignition()

    def get_rocket_status(self):
        try:
            response = requests.get(
                "http://example.com/rocket_status"
            )  # Replace with actual endpoint
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting rocket status: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None

    def perform_pre_launch_checks(self):
        # Simulate pre-launch checks
        return True  # Or return False if checks fail

    def trigger_ignition(self):
        # Simulate ignition sequence
        return True  # Or return False if ignition fails
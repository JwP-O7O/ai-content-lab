from loguru import logger


class MissionControl:
    def __init__(self):
        self.mission_status = "stopped"

    def start_mission(self):
        logger.info("Mission started.")
        self.mission_status = "running"

    def end_mission(self):
        logger.info("Mission ended.")
        self.mission_status = "stopped"

    def get_mission_status(self):
        return self.mission_status
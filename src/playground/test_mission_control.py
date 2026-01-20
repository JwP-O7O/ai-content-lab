from loguru import logger


class MissionControl:
    def __init__(self):
        self.missions = {}

    def start_mission(self, mission_name):
        logger.info(f"Starting mission: {mission_name}")
        self.missions[mission_name] = "Active"

    def end_mission(self, mission_name):
        logger.info(f"Ending mission: {mission_name}")
        self.missions[mission_name] = "Inactive"

    def mission_status(self, mission_name):
        status = self.missions.get(mission_name, "Inactive")
        return f"Mission Status: {mission_name} - {status}"
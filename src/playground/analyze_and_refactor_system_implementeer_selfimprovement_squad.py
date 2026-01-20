from loguru import logger
import random
import time
from typing import List, Dict, Tuple


class SelfImprovementSquad:
    """
    Simuleert een team dat zich bezighoudt met zelfverbetering.
    """

    def __init__(self, squad_name: str, members: int):
        """
        Initialiseert de SelfImprovementSquad.

        Args:
            squad_name: De naam van het team.
            members: Het aantal leden in het team.
        """
        self.squad_name = squad_name
        self.members = members
        self.member_skills: Dict[str, Dict[str, int]] = {}  # skill: {task: skill_level}
        self._initialize_members()

    def _initialize_members(self) -> None:
        """
        Initialiseert de vaardigheden van de teamleden.
        """
        try:
            for i in range(1, self.members + 1):
                member_name = f"Member_{i}"
                self.member_skills[member_name] = {
                    "coding": random.randint(1, 5),
                    "debugging": random.randint(1, 5),
                    "testing": random.randint(1, 5),
                }
            logger.info(
                f"Initialized squad '{self.squad_name}' with {self.members} members."
            )
        except Exception as e:
            logger.error(f"Error initializing members: {e}")

    def display_member_skills(self) -> None:
        """
        Toont de vaardigheden van elk teamlid.
        """
        try:
            logger.info(f"Skills for squad '{self.squad_name}':")
            for member, skills in self.member_skills.items():
                logger.info(f"  {member}: {skills}")
        except Exception as e:
            logger.error(f"Error displaying member skills: {e}")

    def perform_task(self, task_name: str, task_complexity: int) -> None:
        """
        Simuleert het uitvoeren van een taak door het team.

        Args:
            task_name: De naam van de taak.
            task_complexity: De complexiteit van de taak (1-10).
        """
        try:
            logger.info(f"Performing task: {task_name}, Complexity: {task_complexity}")
            self._simulate_task_performance(task_name, task_complexity)
            logger.info(f"Task '{task_name}' completed successfully.")
        except Exception as e:
            logger.error(f"Error performing task: {e}")

    def _simulate_task_performance(self, task_name: str, task_complexity: int) -> None:
        """
        Simuleert de uitvoering van een taak door het team.
        """
        try:
            for member, skills in self.member_skills.items():
                skill_to_use = self._determine_skill_for_task(task_name)
                skill_level = skills.get(skill_to_use, 1)
                success_chance = self._calculate_success_chance(
                    skill_level, task_complexity
                )
                if random.random() < success_chance:
                    logger.info(
                        f"{member} successfully contributed to {task_name} (Skill: {skill_to_use}, Level: {skill_level})"
                    )
                    self._improve_skill(member, skill_to_use)
                else:
                    logger.warning(
                        f"{member} struggled with {task_name} (Skill: {skill_to_use}, Level: {skill_level})"
                    )
                    self._degrade_skill(member, skill_to_use)
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error during task simulation: {e}")

    def _determine_skill_for_task(self, task_name: str) -> str:
        """
        Bepaalt de relevante skill voor de taak.
        """
        try:
            if "code" in task_name.lower():
                return "coding"
            elif "debug" in task_name.lower():
                return "debugging"
            elif "test" in task_name.lower():
                return "testing"
            else:
                return random.choice(["coding", "debugging", "testing"])
        except Exception as e:
            logger.error(f"Error determining skill for task: {e}")
            return "coding"  # Default skill

    def _calculate_success_chance(
        self, skill_level: int, task_complexity: int
    ) -> float:
        """
        Berekent de kans op succes gebaseerd op de skill level en task complexity.
        """
        try:
            return min(0.9, skill_level * 0.1) - (task_complexity * 0.05)
        except Exception as e:
            logger.error(f"Error calculating success chance: {e}")
            return 0.1

    def _improve_skill(self, member_name: str, skill: str) -> None:
        """
        Verbetert de vaardigheid van een teamlid.
        """
        try:
            if skill in self.member_skills[member_name]:
                self.member_skills[member_name][skill] = min(
                    5, self.member_skills[member_name][skill] + 1
                )
                logger.info(
                    f"{member_name} improved {skill} to level {self.member_skills[member_name][skill]}"
                )
        except Exception as e:
            logger.error(f"Error improving skill: {e}")

    def _degrade_skill(self, member_name: str, skill: str) -> None:
        """
        Verlaagt de vaardigheid van een teamlid.
        """
        try:
            if skill in self.member_skills[member_name]:
                self.member_skills[member_name][skill] = max(
                    1, self.member_skills[member_name][skill] - 1
                )
                logger.info(
                    f"{member_name} degraded {skill} to level {self.member_skills[member_name][skill]}"
                )
        except Exception as e:
            logger.error(f"Error degrading skill: {e}")

    def run_sprint(self, sprint_duration: int, tasks: List[Tuple[str, int]]) -> None:
        """
        Simuleert een sprint waarin taken worden uitgevoerd.

        Args:
            sprint_duration: De duur van de sprint in seconden.
            tasks: Een lijst met taken en hun complexiteit.  (task_name, task_complexity)
        """
        try:
            logger.info(
                f"Starting sprint for {self.squad_name} lasting {sprint_duration} seconds."
            )
            start_time = time.time()
            while time.time() - start_time < sprint_duration:
                task_name, task_complexity = random.choice(tasks)
                self.perform_task(task_name, task_complexity)
                time.sleep(random.uniform(1, 3))  # varying time between tasks
            logger.info(f"Sprint completed for {self.squad_name}.")
        except Exception as e:
            logger.error(f"Error running sprint: {e}")
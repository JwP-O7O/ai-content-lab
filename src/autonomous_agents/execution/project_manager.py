import asyncio
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProjectManager:
    """
    Coördineert de werkzaamheden van alle andere agents.
    """
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialiseert de ProjectManager.

        Args:
            agents: Een dictionary met alle andere agent instanties.
        """
        self.agents = agents
        self.task_queue: asyncio.Queue = asyncio.Queue()  # Gebruikt asyncio.Queue voor thread-safe queuing
        self.task_history: List[Dict] = []
        self.status: str = "idle" # 'idle', 'planning', 'executing', 'reviewing'
        self.max_retries = 3  # Maximum aantal pogingen voor een taak


    async def add_task(self, task_description: str, agent_recommendation: str = None,  task_data: Dict = None) -> None:
        """
        Voegt een taak toe aan de taakwachtrij.

        Args:
            task_description: Beschrijving van de taak.
            agent_recommendation: Suggestie voor welke agent de taak moet uitvoeren.
            task_data: Optionele data die aan de taak gekoppeld is, bijvoorbeeld een query of code.
        """
        task = {
            "description": task_description,
            "status": "pending",
            "agent": agent_recommendation,
            "data": task_data,
            "attempts": 0 # Track attempts for retry logic
        }
        await self.task_queue.put(task)
        logging.info(f"ProjectManager: Taak '{task_description}' toegevoegd aan de wachtrij.")


    async def dispatch_task(self, task: Dict) -> Any:
        """
        Verstuurt een taak naar de juiste agent en ontvangt de resultaten.
        """
        agent_name = task.get("agent")
        if not agent_name or agent_name not in self.agents:
            # Fallback mechanisme: use a 'general' agent or raise an error.  Implement a more robust fallback later.
            logging.warning(f"ProjectManager: Geen specifieke agent gevonden voor taak '{task.get('description')}'.")
            return None

        agent = self.agents[agent_name]
        task["status"] = "in progress"
        logging.info(f"ProjectManager: Taak '{task.get('description')}' naar {agent_name} gestuurd.")

        try:
            # Stuur de taak door naar de agent
            result = await agent.execute_task(task.get("description"), task.get("data"))
            task["status"] = "completed"
            task["result"] = result
            logging.info(f"ProjectManager: Taak '{task.get('description')}' voltooid door {agent_name}.")
            return result
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["attempts"] += 1 # Increment attempt counter
            logging.error(f"ProjectManager: Fout tijdens het uitvoeren van taak '{task.get('description')}' door {agent_name}: {e}. Poging {task['attempts']} van {self.max_retries}")

            if task["attempts"] < self.max_retries:
                logging.info(f"ProjectManager: Opnieuw proberen taak '{task.get('description')}'")
                await self.add_task(task.get("description"), task.get("agent"), task.get("data")) # Retry the task
            else:
                logging.error(f"ProjectManager: Taak '{task.get('description')}' is mislukt na {self.max_retries} pogingen.")
            return None


    async def analyze_results(self, task_results: List[Dict]) -> None:
        """
        Analyseert de resultaten van voltooide taken en identificeert eventuele vervolgacties.
        """
        for task in task_results:
            if task.get("status") == "completed":
                logging.info(f"ProjectManager: Resultaten van taak '{task.get('description')}': {task.get('result')}")
                # Logica om de resultaten te analyseren.  Bijvoorbeeld:
                # - Controleer of er nieuwe taken nodig zijn.
                # - Verander prioriteiten op basis van resultaten.
                # - Roep andere agents aan om de resultaten te verwerken (bijvoorbeeld ContentWriter)
            elif task.get("status") == "failed":
                logging.warning(f"ProjectManager: Taak '{task.get('description')}' is mislukt.  Fout: {task.get('error')}")
                # await self.retry_task(task)  # Retry the failed task.  This is now handled in dispatch_task
                pass # Already handled in dispatch_task
            else:
                logging.warning(f"ProjectManager: Taak '{task.get('description')}' heeft een onbekende status: {task.get('status')}")


    async def run(self):
        """
        De hoofdfunctie die de projectmanagement loop runt.
        """
        self.status = "planning"
        logging.info("ProjectManager: Start planning fase.")

        # Hier de planningsfase implementeren.  Bijvoorbeeld:
        # - Vraag de VisionaryAgent om de overkoepelende doelen te bepalen.
        # - Verdeel de doelen in deel-taken.
        # - Roep add_task() aan om de taken in de queue te zetten.
        # Voorbeeld:
        # await self.add_task("Bepaal de belangrijkste functionaliteiten voor de volgende release", agent_recommendation="VisionaryAgent")

        self.status = "executing"
        logging.info("ProjectManager: Start execution fase.")

        task_results: List[Dict] = []
        while True:
            try:
                task = self.task_queue.get_nowait()
                result = await self.dispatch_task(task)
                if task["status"] == "completed":
                    task_results.append(task)
                self.task_queue.task_done()
            except asyncio.QueueEmpty:
                # Wacht tot er nieuwe taken beschikbaar zijn of stop als er geen taken meer zijn.
                if self.task_queue.empty():
                    if task_results:
                        self.status = "reviewing"
                        logging.info("ProjectManager: Start reviewing fase.")
                        await self.analyze_results(task_results)
                        self.status = "idle"
                        logging.info("ProjectManager: Klaar met alle taken.")
                    else:
                        logging.info("ProjectManager: Geen taken te verwerken.")
                    break # Stop de loop als de queue leeg is en er geen resultaten zijn.
                await asyncio.sleep(1) # wacht 1 seconde als de wachtrij leeg is, om te voorkomen dat de CPU overbelast wordt.
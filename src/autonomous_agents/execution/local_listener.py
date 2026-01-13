import os
import json
from loguru import logger
from src.autonomous_agents.execution.task_queue import TaskQueue


class LocalListener:
    def __init__(self):
        self.name = "LocalListener"
        self.command_file = "data/local_commands.json"
        self.queue = TaskQueue()

    async def check_for_orders(self):
        """
        1. Checks for new commands in JSON file and pushes them to DB.
        2. Retrieves the next pending task from the DB.
        """
        # --- STAP 1: INGESTIE (JSON -> DB) ---
        if os.path.exists(self.command_file):
            try:
                content = ""
                with open(self.command_file, "r") as f:
                    content = f.read().strip()

                if content:
                    data = json.loads(content)
                    command_text = data.get("command")
                    if command_text:
                        logger.info(
                            f"[{self.name}] 📨 Ingesting command: {command_text}"
                        )
                        self.queue.add_task(
                            title=command_text,
                            description="Direct command from Admin Interface",
                            source="chat",
                        )

                # Veilig verwijderen na succesvolle ingestie
                os.remove(self.command_file)

            except Exception as e:
                logger.error(f"Error reading command file: {e}")

        # --- STAP 2: OPHALEN (DB -> Orchestrator) ---
        task = self.queue.get_next_pending_task()

        if task:
            return {
                "status": "new_tasks",
                "tasks": [
                    {
                        "id": task["id"],
                        "title": task["title"],
                        "body": task["description"],
                        "source": task["source"],
                    }
                ],
            }

        return {"status": "no_tasks"}

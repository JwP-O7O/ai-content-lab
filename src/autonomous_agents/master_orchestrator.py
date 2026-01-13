import asyncio
import os
import sys
import time
from loguru import logger

sys.path.append(os.getcwd())

# --- IMPORTS ---
try:
    from src.autonomous_agents.execution.local_listener import LocalListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.learning.memory_system import MemorySystem
except ImportError:
    sys.exit(1)


class TermuxMasterOrchestrator:
    def __init__(self):
        self.last_task_hash = ""  # Loop Preventie

        # DE NIEUWE TEAMS
        self.intelligence = ResearchAgent()  # Team 1: Research
        self.backend_squad = (
            FeatureArchitect()
        )  # Team 2: Backend (wordt later geüpgraded)
        self.frontend_squad = (
            WebArchitect()
        )  # Team 3: Frontend (wordt later geüpgraded)

        self.listener = LocalListener()
        self.publisher = GitPublisher()
        self.memory = MemorySystem()  # 🧠 The Brain

    async def run_cycle(self):
        # 1. Check Commando's
        orders = await self.listener.check_for_orders()

        if orders.get("status") == "new_tasks":
            for task in orders["tasks"]:
                title = task["title"]
                task_id = task.get("id")
                start_time = time.time()

                logger.info(f"🚀 Starting Task {task_id}: {title}")

                try:
                    result = None
                    # ROUTING NAAR SQUADS
                    if "RESEARCH:" in title.upper():
                        topic = title.split(":", 1)[1].strip()
                        result = await self.intelligence.conduct_research(topic)

                    elif "WEB:" in title.upper():
                        result = await self.frontend_squad.build_website(title)
                        await self.publisher.publish_changes()

                    elif "SYSTEM:" in title.upper():
                        result = await self.backend_squad.build_feature(title)
                        await self.publisher.publish_changes()

                    # Bereken duur
                    duration = time.time() - start_time

                    # Markeer als voltooid in DB
                    if task_id:
                        self.listener.queue.complete_task(
                            task_id, result=str(result) # Store string representation of result in DB
                        )

                    # 🧠 LEER VAN DEZE SESSIE
                    await self.memory.update_context_after_task(
                        task_id, title, result, "completed", duration
                    )
                    return result # Return the original result dictionary

                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(f"Task {task_id} Failed: {e}")

                    if task_id:
                        self.listener.queue.fail_task(task_id, error_message=str(e))

                    # 🧠 LEER VAN DEZE FOUT
                    await self.memory.update_context_after_task(
                        task_id, title, str(e), "failed", duration
                    )
                    return None # Return None if task failed
        return None # No tasks processed
        while True:
            try:
                await self.run_cycle()
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Critical System Error: {e}")
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().start())

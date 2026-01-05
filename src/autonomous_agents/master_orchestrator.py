import asyncio
import os
import sys
import json
from loguru import logger

sys.path.append(os.getcwd())

# --- IMPORTS ---
try:
    from src.autonomous_agents.execution.local_listener import LocalListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    from src.autonomous_agents.execution.git_publisher import GitPublisher
except ImportError:
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.last_task_hash = "" # Loop Preventie
        
        # DE NIEUWE TEAMS
        self.intelligence = ResearchAgent()   # Team 1: Research
        self.backend_squad = FeatureArchitect() # Team 2: Backend (wordt later geüpgraded)
        self.frontend_squad = WebArchitect()    # Team 3: Frontend (wordt later geüpgraded)
        
        self.listener = LocalListener()
        self.publisher = GitPublisher()

    async def run_cycle(self):
        # 1. Check Commando's
        orders = await self.listener.check_for_orders()
        
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                title = task['title']
                
                # --- LOOP PROTECTIE ---
                if title == self.last_task_hash:
                    logger.warning(f"🛑 STOP: Poging tot herhaling van taak '{title}'. Genegeerd.")
                    continue
                self.last_task_hash = title
                # ----------------------

                # ROUTING NAAR SQUADS
                if "RESEARCH:" in title.upper():
                    # Stuur naar Intelligence Directorate
                    topic = title.split(":", 1)[1].strip()
                    await self.intelligence.conduct_research(topic)

                elif "WEB:" in title.upper():
                    # Stuur naar Frontend Squad
                    await self.frontend_squad.build_website(title)
                    await self.publisher.publish_changes()

                elif "SYSTEM:" in title.upper():
                    # Stuur naar Backend Squad
                    await self.backend_squad.build_feature(title)
                    await self.publisher.publish_changes()

    async def start(self):
        logger.info("🦅 PHOENIX V17 - SQUAD ARCHITECTURE ONLINE")
        while True:
            try:
                await self.run_cycle()
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Critical System Error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().start())

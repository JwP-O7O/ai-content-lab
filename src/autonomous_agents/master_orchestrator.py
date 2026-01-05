import asyncio
import os
import sys
import json
from loguru import logger
from rich.console import Console

sys.path.append(os.getcwd())

# --- IMPORTS ---
try:
    from src.ui_engine import UIEngine
    from src.dependency_manager import DependencyManager 
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.local_listener import LocalListener # <--- NIEUW
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent
    from src.autonomous_agents.planning.system_optimizer import SystemOptimizer
    from src.autonomous_agents.planning.staffing_agent import StaffingAgent
    from src.autonomous_agents.validation.qa_agent import QualityAssuranceAgent
    from src.autonomous_agents.learning.brain import GlobalBrain
except ImportError as e:
    try:
        from src.dependency_manager import DependencyManager
        if DependencyManager.heal(e): sys.exit(0)
    except: pass
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.state_file = "data/system_state.json"
        self.ui = UIEngine()
        self.cycle_count = self._load_state()
        
        # WORKFORCE
        self.publisher = GitPublisher()
        self.gh_listener = GitHubListener()
        self.local_listener = LocalListener() # <--- NIEUW
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        self.researcher = ResearchAgent()
        
        # MANAGEMENT
        self.evolutionary = EvolutionaryAgent()
        self.optimizer = SystemOptimizer()
        self.staffing = StaffingAgent()
        self.qa = QualityAssuranceAgent()
        self.brain = GlobalBrain()

    def _load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f).get("cycle_count", 0)
        except: pass
        return 0

    def _save_state(self):
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({"cycle_count": self.cycle_count}, f)
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        self._save_state()
        self.ui.log_cycle(self.cycle_count)
        
        needs_restart = False
        
        try:
            # 1. MANAGEMENT (Minder vaak)
            if self.cycle_count % 30 == 0: await self.staffing.evaluate_team_needs()
            if self.cycle_count % 20 == 0: await self.optimizer.optimize_system()
            if self.cycle_count % 10 == 0: await self.evolutionary.propose_improvement()

            # 2. ORDERS CONTROLEREN (EERST LOKAAL, DAN GITHUB)
            orders = await self.local_listener.check_for_orders() # <--- EERST CHAT
            if orders.get("status") == "no_tasks":
                orders = await self.gh_listener.check_for_orders() # DAN PAS GITHUB

            if orders.get("status") == "new_tasks":
                for task in orders['tasks']:
                    title = task['title']
                    res = None
                    
                    # ROUTING LOGICA
                    if "RESEARCH:" in title.upper():
                        self.ui.log_task("RESEARCH", title, "🕵️ Deep Search...")
                        res = await self.researcher.conduct_research(title.split(":")[-1])

                    elif "SYSTEM:" in title.upper() or "CODE:" in title.upper():
                        self.ui.log_task("SYSTEM", title, "⚙️ Coding...")
                        full_prompt = f"{title} {task['body']}"
                        res = await self.architect.build_feature(full_prompt)
                        if res and res['status'] == 'built':
                            qa = self.qa.audit_code(res['file'])
                            if qa['status'] == 'failed':
                                self.ui.log_error(f"QA REJECTED: {qa['msg']}")
                                continue
                            needs_restart = True

                    elif "WEB:" in title.upper():
                        self.ui.log_task("WEB", title, "🌐 Building...")
                        res = await self.web_architect.build_website(f"{title} {task['body']}")

                    # AFHANDELING
                    if res and res.get('status') in ['success', 'built']:
                        await self.publisher.publish_changes()
                        # Als het via GitHub kwam, sluit ticket
                        if task.get('issue_obj'):
                            task['issue_obj'].create_comment("✅ Taak Voltooid")
                            task['issue_obj'].edit(state='closed')

        except Exception as e:
            self.ui.log_error(f"Runtime Fout: {e}")
            if "No module named" in str(e): DependencyManager.heal(e)

        if needs_restart:
            self.ui.log_task("SYSTEM", "HERSTART", "♻️ Nieuwe functionaliteit laden...")
            await asyncio.sleep(3)
            sys.exit(0)

    async def run_autonomous_loop(self):
        self.is_running = True
        self.ui.header("PHOENIX V16 - CHAT ENABLED")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                await asyncio.sleep(5) # Iets sneller reageren voor chat (5s)
            except Exception as e:
                self.ui.log_error(f"CRITICAL: {e}")
                if "No module named" in str(e): DependencyManager.heal(e)
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

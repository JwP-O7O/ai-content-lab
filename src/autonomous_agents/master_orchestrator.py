import asyncio
import os
import sys
from loguru import logger
from src.ui_engine import UIEngine

sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    
    # PLANNING & VALIDATIE
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent
    from src.autonomous_agents.planning.system_optimizer import SystemOptimizer
    from src.autonomous_agents.planning.staffing_agent import StaffingAgent # NIEUW
    from src.autonomous_agents.validation.qa_agent import QualityAssuranceAgent # NIEUW
    from src.autonomous_agents.learning.brain import GlobalBrain
except ImportError as e:
    logger.critical(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        self.ui = UIEngine()
        
        # WORKFORCE
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        self.researcher = ResearchAgent()
        
        # BRAIN & MANAGEMENT
        self.evolutionary = EvolutionaryAgent()
        self.optimizer = SystemOptimizer()
        self.staffing = StaffingAgent()  # HR
        self.qa = QualityAssuranceAgent() # POLITIE
        self.brain = GlobalBrain()

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        self.ui.log_cycle(self.cycle_count)
        
        last_action = "Monitoring..."
        needs_restart = False
        
        # 1. MANAGEMENT TAKEN (HR & Research)
        if self.cycle_count % 15 == 0: await self.staffing.evaluate_team_needs()
        if self.cycle_count % 8 == 0: await self.optimizer.optimize_system()
        if self.cycle_count % 5 == 0: await self.evolutionary.propose_improvement()

        # 2. ORDERS UITVOEREN
        orders = await self.listener.check_for_orders()
        
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                title = task['title']
                res = None
                
                # ROUTING
                if "RESEARCH:" in title.upper():
                    self.ui.log_task("RESEARCH", title, "🕵️ Deep Search...")
                    res = await self.researcher.conduct_research(title.split(":")[-1])
                    
                elif "SYSTEM:" in title.upper():
                    self.ui.log_task("SYSTEM", title, "⚙️ Coding...")
                    res = await self.architect.build_feature(f"{title} {task['body']}")
                    if res and res['status'] == 'built':
                        # QA CHECK VOOR SYSTEEM CODE!
                        qa_check = self.qa.audit_code(res['file'])
                        if qa_check['status'] == 'failed':
                            self.ui.log_error(f"QA REJECTED: {qa_check['msg']}")
                            task['issue_obj'].create_comment(f"❌ **QA FAILED:** {qa_check['msg']}")
                            continue # STOP, niet pushen!
                        needs_restart = True

                elif "WEB:" in title.upper():
                    self.ui.log_task("WEB", title, "🌐 Building...")
                    res = await self.web_architect.build_website(f"{title} {task['body']}")

                # AFHANDELING
                if res and res.get('status') in ['success', 'built']:
                    await self.publisher.publish_changes()
                    task['issue_obj'].create_comment("✅ Taak Voltooid")
                    task['issue_obj'].edit(state='closed')
                    last_action = "✅ Taak Uitgevoerd"

        if needs_restart:
            self.ui.log_task("SYSTEM", "HERSTART", "♻️ Nieuwe agents/code laden...")
            await asyncio.sleep(3)
            sys.exit(0)

    async def run_autonomous_loop(self):
        self.is_running = True
        self.ui.header("ALL IN AI - V17 SELF-REPLICATING")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                await asyncio.sleep(10)
            except Exception as e:
                self.ui.log_error(f"CRITICAL: {e}")
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

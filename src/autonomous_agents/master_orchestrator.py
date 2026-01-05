import asyncio
import os
import sys
from loguru import logger

# Voeg pad toe
sys.path.append(os.getcwd())

# --- VEILIGE IMPORT ZONE ---
try:
    from src.ui_engine import UIEngine
    from src.dependency_manager import DependencyManager # <--- DE DOKTER
    
    # Agents
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    
    # Planning & Validatie
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent
    from src.autonomous_agents.planning.system_optimizer import SystemOptimizer
    from src.autonomous_agents.planning.staffing_agent import StaffingAgent
    from src.autonomous_agents.validation.qa_agent import QualityAssuranceAgent
    from src.autonomous_agents.learning.brain import GlobalBrain
    
except ImportError as e:
    # 🚑 HIER GRIJPT DE DOKTER IN
    # Omdat DependencyManager misschien zelf nog niet geladen is, 
    # proberen we hem lokaal te laden of vallen we terug op simpele logica.
    try:
        from src.dependency_manager import DependencyManager
        if DependencyManager.heal(e):
            sys.exit(0) # Herstart is in gang gezet
    except:
        # Als zelfs de dokter niet geladen kan worden
        print(f"CRITICAL BOOT ERROR: {e}")
        # Probeer de 'ratelimit' fix specifiek als fallback
        if "ratelimit" in str(e):
            os.system("pip install ratelimit")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    sys.exit(1)

# --- EINDE IMPORT ZONE ---

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        self.ui = UIEngine()
        
        # WORKFORCE INIT
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        self.researcher = ResearchAgent()
        
        # MANAGEMENT INIT
        self.evolutionary = EvolutionaryAgent()
        self.optimizer = SystemOptimizer()
        self.staffing = StaffingAgent()
        self.qa = QualityAssuranceAgent()
        self.brain = GlobalBrain()

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        self.ui.log_cycle(self.cycle_count)
        
        last_action = "Monitoring..."
        needs_restart = False
        
        try:
            # 1. MANAGEMENT TAKEN
            if self.cycle_count % 15 == 0: await self.staffing.evaluate_team_needs()
            if self.cycle_count % 8 == 0: await self.optimizer.optimize_system()
            if self.cycle_count % 3 == 0: await self.evolutionary.propose_improvement()

            # 2. ORDERS UITVOEREN
            orders = await self.listener.check_for_orders()
            
            if orders.get("status") == "new_tasks":
                for task in orders['tasks']:
                    title = task['title']
                    res = None
                    
                    # A. RESEARCH
                    if "RESEARCH:" in title.upper():
                        self.ui.log_task("RESEARCH", title, "🕵️ Deep Search...")
                        res = await self.researcher.conduct_research(title.split(":")[-1])

                    # B. SYSTEM & CODE
                    elif "SYSTEM:" in title.upper():
                        self.ui.log_task("SYSTEM", title, "⚙️ Coding...")
                        res = await self.architect.build_feature(f"{title} {task['body']}")
                        if res and res['status'] == 'built':
                            # QA CHECK
                            qa = self.qa.audit_code(res['file'])
                            if qa['status'] == 'failed':
                                self.ui.log_error(f"QA REJECTED: {qa['msg']}")
                                task['issue_obj'].create_comment(f"❌ **QA FAILED:** {qa['msg']}")
                                continue
                            needs_restart = True

                    # C. WEB
                    elif "WEB:" in title.upper():
                        self.ui.log_task("WEB", title, "🌐 Building...")
                        res = await self.web_architect.build_website(f"{title} {task['body']}")

                    # AFHANDELING
                    if res and res.get('status') in ['success', 'built']:
                        await self.publisher.publish_changes()
                        task['issue_obj'].create_comment("✅ Taak Voltooid")
                        task['issue_obj'].edit(state='closed')
                        last_action = "✅ Taak Uitgevoerd"

        except Exception as e:
            # Vang fouten tijdens de runtime ook op!
            self.ui.log_error(f"Runtime Fout: {e}")
            # Is het een import error die tijdens runtime ontstond? (bijv. in een sub-functie)
            if "No module named" in str(e):
                DependencyManager.heal(e)

        if needs_restart:
            self.ui.log_task("SYSTEM", "HERSTART", "♻️ Nieuwe functionaliteit laden...")
            await asyncio.sleep(3)
            sys.exit(0)

    async def run_autonomous_loop(self):
        self.is_running = True
        self.ui.header("ALL IN AI - V18 SELF-HEALING")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                await asyncio.sleep(10)
            except Exception as e:
                self.ui.log_error(f"CRITICAL: {e}")
                # Laatste redmiddel voor imports in de main loop
                if "No module named" in str(e):
                    DependencyManager.heal(e)
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

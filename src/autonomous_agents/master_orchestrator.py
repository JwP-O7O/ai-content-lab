import asyncio
import os
import sys
import json
from loguru import logger

# Zorg dat we modules uit de root kunnen vinden
sys.path.append(os.getcwd())

# --- VEILIGE IMPORT ZONE (SELF-HEALING) ---
try:
    from src.ui_engine import UIEngine
    from src.dependency_manager import DependencyManager 
    
    # De "Handen" (Uitvoerende Agents)
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.research_agent import ResearchAgent
    
    # Het "Brein" (Plannende Agents)
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent
    from src.autonomous_agents.planning.system_optimizer import SystemOptimizer
    from src.autonomous_agents.planning.staffing_agent import StaffingAgent
    from src.autonomous_agents.validation.qa_agent import QualityAssuranceAgent
    from src.autonomous_agents.learning.brain import GlobalBrain
    
except ImportError as e:
    # Als er iets mist, roep de dokter
    try:
        from src.dependency_manager import DependencyManager
        if DependencyManager.heal(e):
            sys.exit(0) # Herstart geactiveerd door medic
    except:
        print(f"CRITICAL BOOT ERROR: {e}")
    sys.exit(1)

# --- EINDE IMPORT ZONE ---

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.state_file = "data/system_state.json"
        self.ui = UIEngine()
        
        # Laad het geheugen (voorkomt reset naar 0)
        self.cycle_count = self._load_state()
        
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

    def _load_state(self):
        """Laadt het cyclus nummer uit een bestand"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return data.get("cycle_count", 0)
        except: pass
        return 0

    def _save_state(self):
        """Slaat het cyclus nummer op"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({"cycle_count": self.cycle_count}, f)
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        self._save_state() # Save progress
        self.ui.log_cycle(self.cycle_count)
        
        last_action = "Monitoring..."
        needs_restart = False
        
        try:
            # 1. MANAGEMENT TAKEN (Gespreid over tijd)
            # HR kijkt elke 30 rondes of er nieuwe agents nodig zijn
            if self.cycle_count % 30 == 0: await self.staffing.evaluate_team_needs()
            # Optimizer schoont code op elke 10 rondes
            if self.cycle_count % 10 == 0: await self.optimizer.optimize_system()
            # Game Designer/Evolutie bedenkt iets nieuws elke 5 rondes
            if self.cycle_count % 5 == 0: await self.evolutionary.propose_improvement()

            # 2. ORDERS UITVOEREN (Van GitHub)
            orders = await self.listener.check_for_orders()
            
            if orders.get("status") == "new_tasks":
                for task in orders['tasks']:
                    title = task['title']
                    res = None
                    
                    # A. RESEARCH TAAK
                    if "RESEARCH:" in title.upper():
                        self.ui.log_task("RESEARCH", title, "🕵️ Deep Search...")
                        topic = title.split(":")[-1].strip()
                        res = await self.researcher.conduct_research(topic)

                    # B. SYSTEM & CODE TAAK
                    elif "SYSTEM:" in title.upper() or "CODE:" in title.upper():
                        self.ui.log_task("SYSTEM", title, "⚙️ Coding...")
                        context = self.brain.get_context()
                        full_prompt = f"{title} {task['body']}\n\nCONTEXT:\n{context}"
                        
                        res = await self.architect.build_feature(full_prompt)
                        
                        if res and res['status'] == 'built':
                            # --- QA CHECK ---
                            # Voordat we herstarten, checken of de code valide is
                            qa = self.qa.audit_code(res['file'])
                            if qa['status'] == 'failed':
                                self.ui.log_error(f"QA REJECTED: {qa['msg']}")
                                task['issue_obj'].create_comment(f"❌ **QA FAILED:** {qa['msg']}\n\n*Fix de code en probeer opnieuw.*")
                                continue # STOP DEZE TAAK
                            
                            # Als QA slaagt:
                            self.brain.add_lesson("successful_patterns", f"Fix voor {title}")
                            needs_restart = True # Vlag voor herstart

                    # C. WEB TAAK
                    elif "WEB:" in title.upper():
                        self.ui.log_task("WEB", title, "🌐 Building...")
                        res = await self.web_architect.build_website(f"{title} {task['body']}")

                    # D. ART TAAK
                    elif "IMG:" in title.upper():
                        self.ui.log_task("ART", title, "🎨 Generating...")
                        res = self.visionary.generate_image(title.replace("IMG:", ""))

                    # AFHANDELING & PUBLICATIE
                    if res and res.get('status') in ['success', 'built']:
                        await self.publisher.publish_changes()
                        
                        # Feedback naar GitHub
                        if "WEB:" in title.upper():
                            url = f"https://JwP-O7O.github.io/ai-content-lab/apps/{res['filename']}"
                            task['issue_obj'].create_comment(f"✅ **Klaar!**\n👉 [OPEN APP]({url})")
                        elif "RESEARCH:" in title.upper():
                            raw_url = f"https://github.com/JwP-O7O/ai-content-lab/blob/main/{res['file']}"
                            task['issue_obj'].create_comment(f"✅ **Rapport:** [Lezen]({raw_url})")
                        else:
                            task['issue_obj'].create_comment("✅ Taak Succesvol Uitgevoerd.")
                            
                        task['issue_obj'].edit(state='closed')

        except Exception as e:
            # Vang fouten tijdens de runtime ook op!
            self.ui.log_error(f"Runtime Fout: {e}")
            if "No module named" in str(e):
                DependencyManager.heal(e)

        # 3. HERSTART LOGICA (Phoenix Protocol)
        if needs_restart:
            self.ui.log_task("SYSTEM", "HERSTART", "♻️ Nieuwe functionaliteit laden...")
            await asyncio.sleep(3)
            sys.exit(0) # keep_alive.sh zal het script opnieuw starten

    async def run_autonomous_loop(self):
        self.is_running = True
        self.ui.header("ALL IN AI - V19 ULTIMATE")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                await asyncio.sleep(10) # Korte pauze
            except Exception as e:
                self.ui.log_error(f"CRITICAL: {e}")
                # Laatste redmiddel voor imports in de main loop
                if "No module named" in str(e):
                    DependencyManager.heal(e)
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

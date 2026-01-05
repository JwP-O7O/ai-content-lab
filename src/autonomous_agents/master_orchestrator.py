import asyncio
import os
import sys
from loguru import logger
from datetime import datetime

sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    
    # NIEUWE MODULES
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent
    from src.autonomous_agents.planning.system_optimizer import SystemOptimizer
    from src.autonomous_agents.learning.brain import GlobalBrain
except ImportError as e:
    logger.critical(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        
        # SLIMME AGENTS
        self.evolutionary = EvolutionaryAgent()
        self.optimizer = SystemOptimizer() # De Monteur
        self.brain = GlobalBrain()         # Het Geheugen

    async def _update_remote_status(self, last_action):
        try:
            with open("data/output/SYSTEM_STATUS.md", "w") as f:
                f.write(f"# 🔵 All In AI - Self-Evolving System\n\n")
                f.write(f"| Metric | Waarde |\n|---|---|\n")
                f.write(f"| **Model** | `Gemini 2.0` |\n")
                f.write(f"| **Cycles** | {self.cycle_count} |\n")
                f.write(f"| **Status** | 🧠 LEARNING & OPTIMIZING |\n")
                f.write(f"| **Laatste Actie** | {last_action} |\n")
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        logger.info(f"--- 🔄 Cycle #{self.cycle_count} ---")
        last_action = "Monitoring..."
        
        # 1. ZELF-OPTIMALISATIE (Elke 4 cycles)
        if self.cycle_count % 4 == 0:
            await self.optimizer.optimize_system()
            
        # 2. EVOLUTIE (Elke 3 cycles)
        if self.cycle_count % 3 == 0:
            await self.evolutionary.propose_improvement()

        # 3. ORDER VERWERKING
        orders = await self.listener.check_for_orders()
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                
                # A. SYSTEM & CODE TAAK (Python)
                if "SYSTEM:" in task['title'].upper() or "CODE:" in task['title'].upper():
                    logger.info(f"⚙️ Systeem Taak: {task['title']}")
                    # Geef het brein context mee!
                    context = self.brain.get_context()
                    full_prompt = f"{task['title']} {task['body']}\n\nCONTEXT:\n{context}"
                    
                    res = await self.architect.build_feature(full_prompt)
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        task['issue_obj'].create_comment(f"✅ **Systeem Update Uitgevoerd**\nBestand: `{res['file']}`")
                        task['issue_obj'].edit(state='closed')
                        
                        # LEERMOMENT
                        self.brain.add_lesson("successful_patterns", f"Python fix voor {task['title']}")
                        last_action = "🛠️ Systeem geüpgraded"

                # B. WEB TAAK
                elif "WEB:" in task['title'].upper():
                    logger.info(f"🌐 Web Taak: {task['title']}")
                    res = await self.web_architect.build_website(f"{task['title']} {task['body']}")
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        url = f"https://JwP-O7O.github.io/ai-content-lab/apps/{res['filename']}"
                        task['issue_obj'].create_comment(f"✅ **App Online**\n\n👉 [**OPEN APP**]({url})")
                        task['issue_obj'].edit(state='closed')
                        last_action = f"🌐 Web App: {res['filename']}"

                # C. ART TAAK
                elif "IMG:" in task['title'].upper():
                    res = self.visionary.generate_image(task['title'].replace("IMG:", ""))
                    if res['status'] == 'success':
                        await self.publisher.publish_changes()
                        img = os.path.basename(res['file'])
                        url = f"https://raw.githubusercontent.com/JwP-O7O/ai-content-lab/main/data/images/{img}"
                        task['issue_obj'].create_comment(f"![Art]({url})")
                        task['issue_obj'].edit(state='closed')
                        last_action = "🎨 Art gemaakt"

        await self._update_remote_status(last_action)
        await self.publisher.publish_changes()
        
        if last_action != "Monitoring...":
            logger.success(f"📡 {last_action}")

    async def run_autonomous_loop(self):
        self.is_running = True
        logger.info("🧠 All In AI - ZELF-LEREND SYSTEEM ONLINE")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                logger.info("💤 Ruststand (20 sec)...")
                await asyncio.sleep(20) 
            except Exception as e:
                logger.error(f"❌ Loop fout: {e}")
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

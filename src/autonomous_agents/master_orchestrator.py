import asyncio
import os
import sys
import random
from loguru import logger
from datetime import datetime

sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.monitoring.code_health_monitor import CodeHealthMonitor
    from src.autonomous_agents.execution.code_refactorer import CodeRefactorer
    from src.autonomous_agents.validation.test_runner import TestRunner
    from src.autonomous_agents.analysis.content_quality_monitor import ContentQualityMonitor
    from src.autonomous_agents.execution.content_editor import ContentEditor
    from src.autonomous_agents.execution.content_writer import ContentWriter
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.deep_debugger import DeepDebugger
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.planning.evolutionary_agent import EvolutionaryAgent # NIEUW
except ImportError as e:
    logger.critical(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        
        # HET TEAM
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        self.evolutionary = EvolutionaryAgent() # NIEUW: Het Brein
        
        # Support
        self.content_monitor = ContentQualityMonitor()
        self.content_editor = ContentEditor()
        self.content_writer = ContentWriter()

    async def _update_remote_status(self, last_action):
        try:
            with open("data/output/SYSTEM_STATUS.md", "w") as f:
                f.write(f"# 🔵 All In AI - System Status\n\n")
                f.write(f"| Metric | Waarde |\n|---|---|\n")
                f.write(f"| **Model** | `Gemini 2.0 Flash Lite` |\n")
                f.write(f"| **Cycles** | {self.cycle_count} |\n")
                f.write(f"| **Laatste Actie** | {last_action} |\n")
                f.write(f"| **Status** | ✅ EVOLVING |\n")
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        logger.info(f"--- 🔄 Cycle #{self.cycle_count} ---")
        last_action = "Monitoring..."
        
        # STAP 1: EVOLUTIE (Zelfbedenken) - Elke 3 rondes
        if self.cycle_count % 3 == 0:
            logger.info("🧬 Tijd voor evolutie...")
            await self.evolutionary.propose_improvement()

        # STAP 2: UITVOEREN (Orders checken)
        orders = await self.listener.check_for_orders()
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                
                # A. WEB
                if "WEB:" in task['title'].upper():
                    logger.info(f"🌐 Web Taak: {task['title']}")
                    # Voeg de body toe voor context
                    full_prompt = f"{task['title']}\nDetails: {task['body']}"
                    res = await self.web_architect.build_website(full_prompt)
                    
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        live_url = f"https://JwP-O7O.github.io/ai-content-lab/apps/{res['filename']}"
                        msg = f"✅ **Update Live!**\n\n👉 [**SPEEL HIER**]({live_url})"
                        task['issue_obj'].create_comment(msg)
                        # Sluit het issue als het klaar is
                        task['issue_obj'].edit(state='closed')
                        last_action = f"🌐 Web App Update: {res['filename']}"

                # B. IMAGE
                elif "IMG:" in task['title'].upper():
                    prompt = task['title'].replace("IMG:", "").strip()
                    res = self.visionary.generate_image(prompt)
                    if res['status'] == 'success':
                        await self.publisher.publish_changes()
                        img = os.path.basename(res['file'])
                        url = f"https://raw.githubusercontent.com/JwP-O7O/ai-content-lab/main/data/images/{img}"
                        task['issue_obj'].create_comment(f"![Art]({url})")
                        task['issue_obj'].edit(state='closed')
                        last_action = "🎨 Art gemaakt"

        # STAP 3: PUBLICEREN
        await self._update_remote_status(last_action)
        await self.publisher.publish_changes()
        
        if last_action != "Monitoring...":
            logger.success(f"📡 {last_action}")

    async def run_autonomous_loop(self):
        self.is_running = True
        logger.info("🧠 All In AI - ONLINE & EVOLVING")
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

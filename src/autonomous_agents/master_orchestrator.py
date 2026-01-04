import asyncio
import os
import sys
import subprocess
from loguru import logger
from datetime import datetime

sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.monitoring.code_health_monitor import CodeHealthMonitor
    from src.autonomous_agents.execution.code_refactorer import CodeRefactorer
    from src.autonomous_agents.validation.test_runner import TestRunner
    from src.autonomous_agents.learning.pattern_learner import PatternLearner
    from src.autonomous_agents.analysis.content_quality_monitor import ContentQualityMonitor
    from src.autonomous_agents.execution.content_editor import ContentEditor
    from src.autonomous_agents.execution.content_writer import ContentWriter
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.deep_debugger import DeepDebugger
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.web_architect import WebArchitect # NIEUW
except ImportError as e:
    logger.critical(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        
        # Het Team
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect() # Python
        self.web_architect = WebArchitect() # HTML/JS (Nieuw)
        self.debugger = DeepDebugger()
        self.visionary = VisionaryAgent()
        
        self.code_monitor = CodeHealthMonitor()
        self.refactorer = CodeRefactorer()
        self.content_monitor = ContentQualityMonitor()
        self.content_editor = ContentEditor()
        self.content_writer = ContentWriter()

    async def _update_remote_status(self, last_action):
        try:
            with open("data/output/SYSTEM_STATUS.md", "w") as f:
                f.write(f"# 🔵 All In AI - System Status\n\n")
                f.write(f"| Metric | Waarde |\n|---|---|\n")
                f.write(f"| **Model** | `Gemini 2.0 Flash Lite` |\n")
                f.write(f"| **Laatste Actie** | {last_action} |\n")
                f.write(f"| **Status** | ✅ OPERATIONAL |\n")
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        logger.info(f"--- 🔄 Cycle #{self.cycle_count} ---")
        last_action = "Monitoring..."
        
        orders = await self.listener.check_for_orders()
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                
                # A. WEBSITE BOUWEN (NIEUW)
                if "WEB:" in task['title'].upper():
                    logger.info(f"🌐 Web Taak: {task['title']}")
                    res = await self.web_architect.build_website(f"{task['title']} {task['body']}")
                    
                    if res['status'] == 'built':
                        # Eerst pushen
                        await self.publisher.publish_changes()
                        
                        # Live link genereren
                        # Jouw GitHub gebruikersnaam is JwP-O7O
                        live_url = f"https://JwP-O7O.github.io/ai-content-lab/apps/{res['filename']}"
                        
                        msg = f"✅ **Website Online!**\n\nJe kunt de app hier bekijken en spelen:\n👉 [**KLIK OM TE OPENEN**]({live_url})\n\n*(Geef GitHub Pages 1-2 minuten om te updaten)*"
                        task['issue_obj'].create_comment(msg)
                        last_action = f"🌐 Web App: {res['filename']}"

                # B. CODE BOUWEN (PYTHON)
                elif task['type'] == 'code':
                    logger.info(f"⚙️ Code taak: {task['title']}")
                    res = await self.architect.build_feature(f"{task['title']} {task['body']}")
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        msg = f"✅ **Python Code Gebouwd!**\nBestand: `{res['file']}`"
                        task['issue_obj'].create_comment(msg)
                        last_action = f"🏗️ Code: {res['file']}"

                # C. AFBEELDING MAKEN
                elif "IMG:" in task['title'].upper():
                    prompt = task['title'].replace("IMG:", "").strip()
                    logger.info(f"🎨 Foto taak: {prompt}")
                    res = self.visionary.generate_image(prompt, "github_order")
                    if res['status'] == 'success':
                        await self.publisher.publish_changes()
                        img_filename = os.path.basename(res['file'])
                        blob_url = f"https://github.com/JwP-O7O/ai-content-lab/blob/main/data/images/{img_filename}"
                        raw_url = f"https://raw.githubusercontent.com/JwP-O7O/ai-content-lab/main/data/images/{img_filename}"
                        msg = f"✅ **Afbeelding Gegenereerd!**\n\n👉 [**KLIK HIER OM TE ZIEN**]({blob_url})\n\n![Preview]({raw_url})"
                        task['issue_obj'].create_comment(msg)
                        last_action = "🎨 Afbeelding gemaakt"

                # D. CONTENT SCHRIJVEN
                elif task['type'] == 'content':
                    with open(f"data/output/task_{datetime.now().strftime('%S')}.md", 'w') as f: f.write(task['title'])
                    last_action = "✍️ Artikel gestart"

        # Content Pipeline & Publish
        content = await self.content_monitor.analyze()
        if content['status'] == 'issues':
            await self.content_editor.fix_content(content['details'])
            await self.content_writer.expand_content()

        await self._update_remote_status(last_action)
        await self.publisher.publish_changes()
        
        if last_action != "Monitoring...":
            logger.success(f"📡 {last_action}")

    async def run_autonomous_loop(self):
        self.is_running = True
        logger.info("🧠 All In AI - ONLINE")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                logger.info("💤 Ruststand (30 sec)...")
                await asyncio.sleep(30) 
            except Exception as e:
                logger.error(f"❌ Loop fout: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

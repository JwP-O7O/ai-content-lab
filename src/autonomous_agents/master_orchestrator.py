import asyncio
import os
import sys
import subprocess
from loguru import logger
from datetime import datetime

sys.path.append(os.getcwd())

# Importeer het hele team
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
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent # NIEUW
except ImportError as e:
    logger.critical(f"IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        
        # Team "All In AI"
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.debugger = DeepDebugger()
        self.visionary = VisionaryAgent() # De Kunstenaar
        
        # Support agents
        self.code_monitor = CodeHealthMonitor()
        self.refactorer = CodeRefactorer()
        self.content_monitor = ContentQualityMonitor()
        self.content_editor = ContentEditor()
        self.content_writer = ContentWriter()

    async def _update_remote_status(self, last_action):
        with open("data/output/SYSTEM_STATUS.md", "w") as f:
            f.write(f"# 🔵 All In AI - System Status\n\n")
            f.write(f"| Metric | Waarde |\n|---|---|\n")
            f.write(f"| **Model** | `Gemini 2.0 Flash Lite` |\n")
            f.write(f"| **Laatste Actie** | {last_action} |\n")
            f.write(f"| **Status** | ✅ OPERATIONAL |\n")

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        logger.info(f"--- 🔄 Cycle #{self.cycle_count} ---")
        last_action = "Monitoring..."
        
        # 1. CHECK ORDERS
        orders = await self.listener.check_for_orders()
        if orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                
                # A. CODE BOUWEN
                if task['type'] == 'code':
                    logger.info(f"⚙️ Code taak: {task['title']}")
                    res = await self.architect.build_feature(f"{task['title']} {task['body']}")
                    if res['status'] == 'built':
                        msg = f"✅ **Code Gebouwd!**\nBestand: `{res['file']}`"
                        task['issue_obj'].create_comment(msg)
                        last_action = f"🏗️ Code: {res['file']}"

                # B. AFBEELDING MAKEN (NIEUW)
                elif "IMG:" in task['title'].upper():
                    prompt = task['title'].replace("IMG:", "").strip()
                    logger.info(f"🎨 Foto taak: {prompt}")
                    res = self.visionary.generate_image(prompt, "github_order")
                    if res['status'] == 'success':
                        # Post de foto in de comments!
                        img_filename = os.path.basename(res['file'])
                        # GitHub raw url hack om hem direct te tonen
                        raw_url = f"https://github.com/JwP-O7O/ai-content-lab/raw/main/data/images/{img_filename}"
                        msg = f"✅ **Afbeelding Gegenereerd!**\n\n![AI Art]({raw_url})"
                        task['issue_obj'].create_comment(msg)
                        last_action = "🎨 Afbeelding gemaakt"

                # C. CONTENT SCHRIJVEN
                elif task['type'] == 'content':
                    logger.info(f"📝 Content taak: {task['title']}")
                    with open(f"data/output/task_{datetime.now().strftime('%S')}.md", 'w') as f: 
                        f.write(task['title'])
                    last_action = "✍️ Artikel gestart"

        # 2. CONTENT PIPELINE
        content = await self.content_monitor.analyze()
        if content['status'] == 'issues':
            await self.content_editor.fix_content(content['details'])
            await self.content_writer.expand_content()

        # 3. PUBLISH
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

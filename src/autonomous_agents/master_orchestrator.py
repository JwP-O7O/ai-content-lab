import asyncio
import os
import sys
import subprocess
from loguru import logger
from datetime import datetime

sys.path.append(os.getcwd())

# Forceer laden van de modules
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
except ImportError as e:
    logger.critical(f"🔥 IMPORT ERROR: {e}")
    sys.exit(1)

class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.cycle_count = 0
        self.start_time = datetime.now()
        
        # We initiëren alles met prints om zeker te zijn
        print("DEBUG: Start init agents...")
        self.code_monitor = CodeHealthMonitor()
        self.refactorer = CodeRefactorer()
        self.validator = TestRunner()
        self.learner = PatternLearner()
        self.content_monitor = ContentQualityMonitor()
        self.content_editor = ContentEditor()
        self.content_writer = ContentWriter()
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.debugger = DeepDebugger()
        print("DEBUG: Init klaar.")

    async def _update_remote_status(self, last_action):
        try:
            with open("data/output/SYSTEM_STATUS.md", "w") as f:
                f.write(f"# 🟢 S21 Ultra AI - DEBUG MODE\n\n| Metric | Waarde |\n|---|---|\n| **Update** | `{datetime.now().strftime('%H:%M:%S')}` |\n| **Actie** | {last_action} |\n")
        except Exception: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        logger.info(f"--- 🔄 Cycle #{self.cycle_count} ---")
        last_action = "Monitoring..."
        
        # 1. CHECK GITHUB ORDERS
        logger.debug("👀 Even kijken op GitHub...")
        orders = await self.listener.check_for_orders()
        
        # DEBUG PRINT: Wat kwam er terug?
        if orders.get("status") == "new_tasks":
            logger.warning(f"🚨 ORDER GEVONDEN! Aantal: {len(orders['tasks'])}")
            
            for task in orders['tasks']:
                logger.warning(f"👉 Taak Type: {task['type']} | Titel: {task['title']}")
                
                if task['type'] == 'code':
                    logger.info("🚀 Start FeatureArchitect...")
                    try:
                        # HIER GAAT HET WAARSCHIJNLIJK MIS
                        prompt = f"{task['title']} {task['body']}"
                        logger.info(f"🧠 Prompt sturen naar Gemini: {prompt[:50]}...")
                        
                        res = await self.architect.build_feature(prompt)
                        logger.warning(f"🔙 Resultaat van Architect: {res}")
                        
                        if res['status'] == 'built':
                            last_action = f"🏗️ Code gebouwd: {res['file']}"
                            # Probeer meteen te reageren
                            task['issue_obj'].create_comment(f"✅ **Code Klaar!**\nBestand: `{res['file']}`")
                        else:
                            logger.error(f"❌ Architect faalde: {res}")
                            
                    except Exception as e:
                        logger.critical(f"🔥 CRASH TIJDENS BOUWEN: {e}")

                elif task['type'] == 'content':
                    logger.info("📝 Content taak starten...")
                    fname = f"data/output/task_{datetime.now().strftime('%S')}.md"
                    with open(fname, 'w') as f: f.write(task['title'])
                    last_action = "✍️ Content taak gestart"

        # 2. CONTENT PIPELINE (Slaan we even over in logs als er niks is)
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
        logger.info("🧠 AIS V13 (DEBUG MODE) ONLINE")
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

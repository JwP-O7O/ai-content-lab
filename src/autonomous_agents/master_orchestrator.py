import asyncio
import os
import sys
from loguru import logger
from src.ui_engine import UIEngine  # <--- NIEUW

sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.execution.git_publisher import GitPublisher
    from src.autonomous_agents.execution.github_listener import GitHubListener
    from src.autonomous_agents.execution.feature_architect import FeatureArchitect
    from src.autonomous_agents.execution.web_architect import WebArchitect
    from src.autonomous_agents.execution.visionary_agent import VisionaryAgent
    from src.autonomous_agents.execution.research_agent import ResearchAgent
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
        self.ui = UIEngine() # <--- UI Starten
        
        self.publisher = GitPublisher()
        self.listener = GitHubListener()
        self.architect = FeatureArchitect()
        self.web_architect = WebArchitect()
        self.visionary = VisionaryAgent()
        self.researcher = ResearchAgent()
        self.evolutionary = EvolutionaryAgent()
        self.optimizer = SystemOptimizer()
        self.brain = GlobalBrain()

    async def _update_remote_status(self, last_action):
        try:
            with open("data/output/SYSTEM_STATUS.md", "w") as f:
                f.write(f"# 🔵 All In AI - Knowledge System\n")
                f.write(f"| Metric | Waarde |\n|---|---|\n")
                f.write(f"| **Model** | `Gemini 2.0` |\n")
                f.write(f"| **Cycles** | {self.cycle_count} |\n")
                f.write(f"| **Status** | 🟢 ONLINE |\n")
                f.write(f"| **Actie** | {last_action} |\n")
        except: pass

    async def run_improvement_cycle(self):
        self.cycle_count += 1
        self.ui.log_cycle(self.cycle_count) # <--- Mooie scheidingslijn
        
        last_action = "Monitoring..."
        needs_restart = False
        
        # ONDERHOUD
        if self.cycle_count % 10 == 0: await self.optimizer.optimize_system()
        if self.cycle_count % 5 == 0: await self.evolutionary.propose_improvement()

        # ORDERS
        orders = await self.listener.check_for_orders()
        
        if orders.get("status") == "no_tasks":
            self.ui.log_info("Geen nieuwe orders. Wachten op GitHub...")

        elif orders.get("status") == "new_tasks":
            for task in orders['tasks']:
                title = task['title']
                
                # A. RESEARCH
                if "RESEARCH:" in title.upper() or "ZOEK:" in title.upper():
                    topic = title.replace("RESEARCH:", "").replace("ZOEK:", "").strip()
                    self.ui.log_task("RESEARCH", topic, "🕵️ Bezig met zoeken op Google...")
                    
                    res = await self.researcher.conduct_research(topic)
                    if res['status'] == 'success':
                        await self.publisher.publish_changes()
                        raw_url = f"https://github.com/JwP-O7O/ai-content-lab/blob/main/{res['file']}"
                        msg = f"✅ **Onderzoek Afgerond!**\n\n📄 [Bekijk Rapport]({raw_url})\n\n---\n{res['summary'][:500]}..."
                        task['issue_obj'].create_comment(msg)
                        task['issue_obj'].edit(state='closed')
                        last_action = f"📚 Onderzoek: {topic}"

                # B. SYSTEM & CODE
                elif "SYSTEM:" in title.upper() or "CODE:" in title.upper():
                    self.ui.log_task("SYSTEM CODE", title, "⚙️ Gemini past Python code aan...")
                    context = self.brain.get_context()
                    full_prompt = f"{title} {task['body']}\n\nCONTEXT:\n{context}"
                    res = await self.architect.build_feature(full_prompt)
                    
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        task['issue_obj'].create_comment(f"✅ **Systeem Update**\nBestand: `{res['file']}`\n\n🔄 *Herstarten...*")
                        task['issue_obj'].edit(state='closed')
                        self.brain.add_lesson("successful_patterns", f"Python fix voor {title}")
                        last_action = "🛠️ Systeem geüpgraded"
                        needs_restart = True

                # C. WEB
                elif "WEB:" in title.upper():
                    self.ui.log_task("WEB APP", title, "🌐 Web Architect bouwt HTML/JS...")
                    res = await self.web_architect.build_website(f"{title} {task['body']}")
                    if res['status'] == 'built':
                        await self.publisher.publish_changes()
                        url = f"https://JwP-O7O.github.io/ai-content-lab/apps/{res['filename']}"
                        task['issue_obj'].create_comment(f"✅ **App Online**\n👉 [OPEN APP]({url})")
                        task['issue_obj'].edit(state='closed')
                        last_action = f"🌐 Web App: {res['filename']}"

                # D. ART
                elif "IMG:" in title.upper():
                    prompt = title.replace("IMG:", "").strip()
                    self.ui.log_task("ART STUDIO", prompt, "🎨 Visionary Agent genereert beeld...")
                    res = self.visionary.generate_image(prompt)
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
            self.ui.log_success(last_action)

        if needs_restart:
            self.ui.log_task("SYSTEM", "HERSTARTEN", "♻️ Nieuwe code gedetecteerd. Tot zo!")
            await asyncio.sleep(3)
            sys.exit(0)

    async def run_autonomous_loop(self):
        self.is_running = True
        self.ui.header("ALL IN AI - V16 ULTIMATE")
        while self.is_running:
            try:
                await self.run_improvement_cycle()
                await asyncio.sleep(10) # Iets sneller
            except Exception as e:
                self.ui.log_error(f"CRITICAL LOOP ERROR: {e}")
                await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(TermuxMasterOrchestrator().run_autonomous_loop())

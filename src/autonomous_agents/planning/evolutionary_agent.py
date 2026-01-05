import os
import random
from github import Github
from loguru import logger
from dotenv import load_dotenv
from src.autonomous_agents.ai_service import AIService

load_dotenv()

class EvolutionaryAgent:
    def __init__(self):
        self.name = "EvolutionaryAgent"
        self.ai = AIService()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = "JwP-O7O/ai-content-lab"
        self.apps_dir = "apps"
        self.src_dir = "src"
        self.research_dir = "data/research"

    def _get_random_file(self, directory, extension):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    file_list.append(os.path.join(root, file))
        return random.choice(file_list) if file_list else None

    async def propose_improvement(self):
        # Check eerst of het niet te druk is op GitHub
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            open_issues = repo.get_issues(state='open')
            
            if open_issues.totalCount >= 3:
                logger.info(f"[{self.name}] ⏸️ Te veel open tickets ({open_issues.totalCount}). Ik wacht.")
                return
                
            # Haal titels op om duplicaten te voorkomen
            existing_titles = [i.title for i in open_issues]
        except Exception as e:
            logger.error(f"GitHub connectie fout: {e}")
            return

        # KIES DOMEIN
        domain = random.choice(["WEB", "SYSTEM", "RESEARCH"])
        
        if domain == "WEB":
            await self._improve_web(existing_titles)
        elif domain == "SYSTEM":
            await self._improve_system(existing_titles)
        # Research doen we even minder vaak om Google te sparen

    async def _improve_web(self, existing_titles):
        target = self._get_random_file(self.apps_dir, ".html")
        if not target: return
        filename = os.path.basename(target)

        # DUPLICAAT CHECK: Als we al bezig zijn met dit bestand, STOP.
        for title in existing_titles:
            if filename in title:
                logger.info(f"[{self.name}] ⏩ Ticket voor {filename} loopt al. Overslaan.")
                return

        logger.info(f"[{self.name}] 🎮 Web Evolutie: {filename}")
        with open(target, 'r') as f: code = f.read()

        prompt = f"""
        Je bent een Game Designer.
        APP: {filename}
        CODE: {code[:2000]}
        
        OPDRACHT: Verzin 1 unieke feature.
        FORMAT: Titel: WEB: Upgrade {filename} met [Feature] \n Body: ...
        """
        await self._create_ticket(prompt, "feature-request")

    async def _improve_system(self, existing_titles):
        target = self._get_random_file(self.src_dir, ".py")
        if not target: return
        filename = os.path.basename(target)
        
        if "master_orchestrator" in filename: return # Even met rust laten
        
        for title in existing_titles:
            if filename in title: return

        logger.info(f"[{self.name}] ⚙️ System Evolutie: {filename}")
        with open(target, 'r') as f: code = f.read()
        
        prompt = f"""
        Je bent een Python Expert.
        FILE: {filename}
        CODE: {code[:2000]}
        
        OPDRACHT: 1 Optimalisatie.
        FORMAT: Titel: SYSTEM: Optimaliseer {filename} \n Body: ...
        """
        await self._create_ticket(prompt, "system-optimization")

    async def _create_ticket(self, prompt, label):
        suggestion = await self.ai.generate_text(prompt)
        if not suggestion: return
        
        lines = suggestion.split('\n')
        title = "UPDATE"
        body = suggestion
        for line in lines:
            if line.startswith("Titel:"): title = line.replace("Titel:", "").strip()
            if line.startswith("Body:"): body = line.replace("Body:", "").strip()
            
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            repo.create_issue(title=title, body=body, labels=[label])
            logger.success(f"[{self.name}] 🚀 Idee gelanceerd: {title}")
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")

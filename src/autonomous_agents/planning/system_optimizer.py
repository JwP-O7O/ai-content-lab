import os
import random
from github import Github
from loguru import logger
from dotenv import load_dotenv
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.learning.brain import GlobalBrain
from src.autonomous_agents.execution.research_agent import ResearchAgent # NIEUW

load_dotenv()

class SystemOptimizer:
    def __init__(self):
        self.name = "SystemOptimizer"
        self.ai = AIService()
        self.brain = GlobalBrain()
        self.researcher = ResearchAgent() # Toegang tot kennis
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = "JwP-O7O/ai-content-lab"
        self.source_dir = "src"

    def _get_random_source_file(self):
        py_files = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return random.choice(py_files) if py_files else None

    async def optimize_system(self):
        target_file = self._get_random_source_file()
        if not target_file: return

        filename = os.path.basename(target_file)
        logger.info(f"[{self.name}] 🔧 Analyseren van: {filename}")

        # 1. EERST ONDERZOEK DOEN
        logger.info(f"[{self.name}] 🌍 Best practices opzoeken voor {filename}...")
        search_q = f"Python best practices optimization for {filename} library"
        research = await self.researcher.conduct_research(search_q)
        
        # 2. DAN OPTIMALISEREN
        with open(target_file, 'r') as f:
            code = f.read()

        prompt = f"""
        Optimaliseer dit bestand: '{filename}'.
        
        GEBRUIK DEZE KENNIS VAN HET WEB:
        {research.get('summary', 'Geen specifieke data')}
        
        HUIDIGE CODE:
        {code[:3000]}
        
        OPDRACHT:
        Vind 1 concrete verbetering op basis van de research.
        """

        advice = await self.ai.generate_text(prompt)
        
        # (Hieronder volgt de standaard issue-aanmaak logica, ingekort voor leesbaarheid)
        if not advice: return
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            repo.create_issue(title=f"SYSTEM: Optimaliseer {filename} (Research Based)", body=advice)
            logger.success(f"[{self.name}] 🛠️ Ticket aangemaakt met externe kennis.")
        except: pass

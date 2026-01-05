import os
import random
import time
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

    def _get_random_file(self):
        """Kiest een willekeurig bestand om te verbeteren"""
        if not os.path.exists(self.apps_dir): return None
        
        files = [f for f in os.listdir(self.apps_dir) if f.endswith('.html')]
        if not files: return None
        
        return os.path.join(self.apps_dir, random.choice(files))

    async def propose_improvement(self):
        """Bedenkt een verbetering en maakt een ticket aan"""
        target_file = self._get_random_file()
        if not target_file:
            logger.warning(f"[{self.name}] Geen bestanden gevonden om te verbeteren.")
            return

        filename = os.path.basename(target_file)
        logger.info(f"[{self.name}] 🧬 Analyseren van {filename} voor evolutie...")

        # 1. Lees de huidige code
        with open(target_file, 'r') as f:
            code_snippet = f.read()[:2000] # Lees eerste 2000 tekens voor context

        # 2. Vraag Gemini om een creatieve upgrade
        prompt = f"""
        Je bent een Product Owner die kijkt naar de code van '{filename}'.
        
        CODE CONTEXT:
        {code_snippet}
        ...
        
        OPDRACHT:
        Verzin 1 concrete, leuke feature of verbetering voor deze app.
        Het moet een duidelijke taak zijn voor een developer.
        
        FORMAT:
        Titel: WEB: [Korte pakkende titel]
        Body: [Beschrijving van wat er moet gebeuren]
        """

        suggestion = await self.ai.generate_text(prompt)
        
        if not suggestion: return

        # 3. Parse het antwoord
        lines = suggestion.split('\n')
        title = "WEB: Verbetering"
        body = "Verbeter de code."
        
        for line in lines:
            if line.startswith("Titel:"):
                title = line.replace("Titel:", "").strip()
            if line.startswith("Body:"):
                body = line.replace("Body:", "").strip()

        # 4. Maak het issue aan op GitHub (zodat de Listener het oppakt)
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            
            # Check of we niet spammen (max 3 open auto-issues)
            open_issues = repo.get_issues(state='open', labels=['evolution'])
            if open_issues.totalCount >= 3:
                logger.info(f"[{self.name}] ⏸️ Al genoeg open verbeteringen. Ik wacht even.")
                return

            new_issue = repo.create_issue(
                title=title,
                body=f"{body}\n\n*(Gegenereerd door EvolutionaryAgent 🧬)*",
                labels=['evolution']
            )
            logger.success(f"[{self.name}] 💡 Nieuw idee gelanceerd: {title}")
            
        except Exception as e:
            logger.error(f"[{self.name}] Kon geen issue maken: {e}")

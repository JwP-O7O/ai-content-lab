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
        self.apps_dir = "apps" # FOCUS OP APPS

    def _get_random_app(self):
        """Kiest een bestaande game/app"""
        if not os.path.exists(self.apps_dir): return None
        files = [f for f in os.listdir(self.apps_dir) if f.endswith('.html')]
        if not files: return None
        return os.path.join(self.apps_dir, random.choice(files))

    async def propose_improvement(self):
        target_file = self._get_random_app()
        if not target_file:
            logger.warning(f"[{self.name}] Geen apps gevonden om te verbeteren.")
            return

        filename = os.path.basename(target_file)
        logger.info(f"[{self.name}] 🎮 Gameplay analyseren van {filename}...")

        with open(target_file, 'r') as f:
            code_snippet = f.read()

        # DE NIEUWE PROMPT: FOCUS OP GAMEPLAY & FEATURES
        prompt = f"""
        Je bent een Creatieve Game Designer en Product Owner.
        Je kijkt naar de broncode van een web-game: '{filename}'.
        
        HUIDIGE CODE (Snippet):
        {code_snippet[:4000]}
        ...
        
        OPDRACHT:
        Bedenk 1 CONCRETE, ZICHTBARE feature om dit spel leuker te maken.
        Niet refactoren, geen 'clean code', maar SPELPLEZIER.
        
        Denk aan:
        - Power-ups (schilden, snelheid, lasers)
        - Visuele effecten (partikels, explosies, achtergronden)
        - Geluidseffecten (indien nog niet aanwezig)
        - UI verbeteringen (Score bord, Start scherm, Game Over scherm)
        - Nieuwe obstakels of vijanden
        
        FORMAT (Belangrijk voor de WebArchitect):
        Titel: WEB: Voeg [Feature Naam] toe aan {filename}
        Body:
        Breid de bestaande '{filename}' uit met [Feature].
        Behoud de bestaande logica, maar voeg deze functionaliteit toe.
        Zorg dat het direct werkt in de browser.
        """

        suggestion = await self.ai.generate_text(prompt)
        if not suggestion: return

        # Parse antwoord
        lines = suggestion.split('\n')
        title = f"WEB: Upgrade {filename}"
        body = suggestion
        
        for line in lines:
            if line.startswith("Titel:"): title = line.replace("Titel:", "").strip()
            if line.startswith("Body:"): body = line.replace("Body:", "").strip()

        # Post naar GitHub
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            
            # Max 2 open feature requests tegelijk om chaos te voorkomen
            issues = repo.get_issues(state='open', labels=['feature-request'])
            if issues.totalCount >= 2: return

            repo.create_issue(
                title=title,
                body=f"{body}\n\n*(Gegenereerd door Game Designer Agent 🎮)*",
                labels=['feature-request']
            )
            logger.success(f"[{self.name}] 💡 Nieuwe game feature bedacht: {title}")
            
        except Exception as e:
            logger.error(f"[{self.name}] Kon feature ticket niet maken: {e}")

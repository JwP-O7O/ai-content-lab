import os
import random
from github import Github
from loguru import logger
from dotenv import load_dotenv
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.learning.brain import GlobalBrain

load_dotenv()

class SystemOptimizer:
    def __init__(self):
        self.name = "SystemOptimizer"
        self.ai = AIService()
        self.brain = GlobalBrain()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = "JwP-O7O/ai-content-lab"
        self.source_dir = "src"

    def _get_random_source_file(self):
        """Kiest een willekeurig Python bestand uit het eigen systeem"""
        py_files = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        
        if not py_files: return None
        return random.choice(py_files)

    async def optimize_system(self):
        """Analyseert eigen broncode en stelt verbeteringen voor"""
        target_file = self._get_random_source_file()
        if not target_file: return

        filename = os.path.basename(target_file)
        logger.info(f"[{self.name}] 🔧 Interne inspectie van: {filename}")

        with open(target_file, 'r') as f:
            code = f.read()

        # Vraag Gemini om optimalisatie
        prompt = f"""
        Je bent een Senior Python Architect.
        Review deze systeem-code: '{filename}'.
        
        CONTEXT (Uit Geheugen):
        {self.brain.get_context()}
        
        HUIDIGE CODE:
        {code[:2500]}
        
        OPDRACHT:
        Vind 1 kritieke verbetering (Performance, Security, of Clean Code).
        Leg uit WAAROM het beter moet.
        
        FORMAT:
        Titel: SYSTEM: [Technische titel]
        Body: [Technische uitleg + Suggestie]
        """

        advice = await self.ai.generate_text(prompt)
        if not advice: return

        # Parse & Post Issue
        lines = advice.split('\n')
        title = f"SYSTEM: Optimaliseer {filename}"
        body = advice
        
        for line in lines:
            if line.startswith("Titel:"): title = line.replace("Titel:", "").strip()
            if line.startswith("Body:"): body = line.replace("Body:", "").strip()

        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            
            # Check duplicaten
            issues = repo.get_issues(state='open', labels=['system-optimization'])
            if issues.totalCount >= 2: return # Niet te veel tegelijk

            repo.create_issue(
                title=title,
                body=f"{body}\n\n*(Gegenereerd door SystemOptimizer)*",
                labels=['system-optimization']
            )
            logger.success(f"[{self.name}] 🛠️ Optimalisatie-ticket aangemaakt: {title}")
            
            # LEERMOMENT: Sla op dat we aan dit bestand werken
            self.brain.add_lesson("lessons_learned", f"Code in {filename} werd als 'needs improvement' gemarkeerd.")

        except Exception as e:
            logger.error(f"SystemOptimizer fout: {e}")

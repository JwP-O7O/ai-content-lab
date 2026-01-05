import os
import random
from github import Github
from loguru import logger
from dotenv import load_dotenv
from src.autonomous_agents.ai_service import AIService
import asyncio  # Importeer asyncio

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
        self.max_open_issues = 3  # Maximum aantal open issues

    def _get_files(self, directory, extension):  # Efficienter ophalen van bestanden
        file_list = [
            os.path.join(root, file)
            for root, _, files in os.walk(directory)
            for file in files
            if file.endswith(extension)
        ]
        return file_list

    async def _is_too_busy(self, repo):
        """Controleert of de GitHub repository te druk is."""
        try:
            open_issues = repo.get_issues(state='open')
            return open_issues.totalCount >= self.max_open_issues
        except Exception as e:
            logger.error(f"GitHub issue count error: {e}")
            return True  # Assume busy on error

    async def _get_existing_titles(self, repo):
        """Haalt de titels van de open issues op."""
        try:
            open_issues = repo.get_issues(state='open')
            return [i.title for i in open_issues]
        except Exception as e:
            logger.error(f"GitHub issue title retrieval error: {e}")
            return []  # Return empty list on error

    async def propose_improvement(self):
        if not self.github_token:
            logger.warning(f"[{self.name}] ⚠️ GITHUB_TOKEN niet geconfigureerd.  Afbreken.")
            return

        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)

            if await self._is_too_busy(repo):
                logger.info(f"[{self.name}] ⏸️ Te veel open tickets. Ik wacht.")
                return

            existing_titles = await self._get_existing_titles(repo)
        except Exception as e:
            logger.error(f"GitHub connectie fout: {e}")
            return

        domain = random.choices(["WEB", "SYSTEM"], weights=[0.6, 0.4], k=1)[0] # Web iets vaker
        #domain = random.choice(["WEB", "SYSTEM"]) # Alternatief: evenveel kans.

        if domain == "WEB":
            await self._improve_web(existing_titles, repo)
        elif domain == "SYSTEM":
            await self._improve_system(existing_titles, repo)


    async def _improve_web(self, existing_titles, repo):
        files = self._get_files(self.apps_dir, ".html")
        if not files:
            logger.info(f"[{self.name}] ⏭️ Geen .html bestanden gevonden in {self.apps_dir}.")
            return

        target = random.choice(files)
        filename = os.path.basename(target)

        if any(filename in title for title in existing_titles):
            logger.info(f"[{self.name}] ⏩ Ticket voor {filename} loopt al. Overslaan.")
            return

        logger.info(f"[{self.name}] 🎮 Web Evolutie: {filename}")
        with open(target, 'r') as f:
            code = f.read()

        prompt = f"""
        Je bent een Web Designer.
        APP: {filename}
        CODE: {code[:2000]}
        
        OPDRACHT: Verzin 1 unieke feature.
        FORMAT: Titel: WEB: Upgrade {filename} met [Feature] \n Body: ...
        """
        await self._create_ticket(prompt, "feature-request", repo, filename)  # Pass repo


    async def _improve_system(self, existing_titles, repo):
        files = self._get_files(self.src_dir, ".py")
        if not files:
            logger.info(f"[{self.name}] ⏭️ Geen .py bestanden gevonden in {self.src_dir}.")
            return

        # Filter out specific files
        system_files = [f for f in files if "master_orchestrator" not in f]

        if not system_files:
            logger.info(f"[{self.name}] ⏭️ Geen geschikte .py bestanden gevonden in {self.src_dir}.")
            return

        target = random.choice(system_files)
        filename = os.path.basename(target)

        if any(filename in title for title in existing_titles):
            logger.info(f"[{self.name}] ⏩ Ticket voor {filename} loopt al. Overslaan.")
            return

        logger.info(f"[{self.name}] ⚙️ System Evolutie: {filename}")
        with open(target, 'r') as f:
            code = f.read()

        prompt = f"""
        Je bent een System Engineer.
        FILE: {filename}
        CODE: {code[:2000]}

        OPDRACHT: Vind 1 concrete verbetering op basis van de research. Geef een duidelijke uitleg en suggestie voor de code aanpassing.
        FORMAT: Titel: SYSTEM: Verbeter {filename} door [Verandering] \n Body: ...
        """
        await self._create_ticket(prompt, "improvement", repo, filename)  # Pass repo

    async def _create_ticket(self, prompt, label, repo, filename):  # Added repo and filename
        try:
            response = await self.ai.generate_content(prompt)
            if response:
                title, body = self._extract_title_and_body(response)
                if title:
                    logger.info(f"[{self.name}] ✅ Ticket aanmaken: {title}")
                    repo.create_issue(title=title, body=body, labels=[label])
                else:
                    logger.warning(f"[{self.name}] ⚠️ Kon geen titel extraheren uit response:\n{response}")
            else:
                logger.warning(f"[{self.name}] ⚠️ Geen response van AI.")
        except Exception as e:
            logger.error(f"Fout bij het aanmaken van ticket: {e}")

    def _extract_title_and_body(self, text):
        """Extracts the title and body from the AI response."""
        try:
            parts = text.split('\n', 1)  # Split only once
            title = parts[0].strip()
            body = parts[1].strip() if len(parts) > 1 else ""
            return title, body
        except Exception as e:
            logger.error(f"Fout bij het extraheren van titel/body: {e}")
            return None, None
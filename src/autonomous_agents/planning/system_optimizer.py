import os
import random
from github import Github
from loguru import logger
from dotenv import load_dotenv
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.learning.brain import GlobalBrain
from src.autonomous_agents.execution.research_agent import ResearchAgent

load_dotenv()


class SystemOptimizer:
    def __init__(self):
        self.name = "SystemOptimizer"
        self.ai = AIService()
        self.brain = GlobalBrain()
        self.researcher = ResearchAgent()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv(
            "GITHUB_REPO_NAME", "JwP-O7O/ai-content-lab"
        )  # Fallback voor flexibiliteit
        self.source_dir = "src"
        self.max_code_snippet_length = 3000  # Configureerbaar

    def _get_random_source_file(self):
        """Selecteert willekeurig een .py bestand uit de source directory."""
        py_files = []
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))
        return random.choice(py_files) if py_files else None

    async def optimize_system(self):
        """Optimaliseert willekeurige Python bestanden met behulp van AI en GitHub Issues."""
        target_file = self._get_random_source_file()
        if not target_file:
            logger.warning(
                f"[{self.name}] ⚠️ Geen Python bestanden gevonden in {self.source_dir}."
            )
            return

        filename = os.path.basename(target_file)
        logger.info(f"[{self.name}] 🔧 Analyseren van: {filename}")

        # 1. ONDERZOEK DOEN
        search_q = f"Python best practices optimization for {filename} library"
        logger.info(f"[{self.name}] 🌍 Best practices opzoeken voor {filename}...")
        research_results = await self.researcher.conduct_research(search_q)
        research_summary = research_results.get("summary", "Geen specifieke data")

        # 2. OPTIMALISEREN
        try:
            with open(target_file, "r") as f:
                code = f.read()
        except FileNotFoundError:
            logger.error(f"[{self.name}] ❗ Bestand niet gevonden: {target_file}")
            return
        except Exception as e:
            logger.error(f"[{self.name}] ❗ Fout bij het lezen van {target_file}: {e}")
            return

        prompt = f"""
        Optimaliseer dit bestand: '{filename}'.

        GEBRUIK DEZE KENNIS VAN HET WEB:
        {research_summary}

        HUIDIGE CODE:
        {code[: self.max_code_snippet_length]}

        OPDRACHT:
        Vind 1 concrete verbetering op basis van de research. Geef een duidelijke uitleg en suggestie voor de code aanpassing.
        """

        advice = await self.ai.generate_text(prompt)

        if not advice:
            logger.warning(
                f"[{self.name}] ⚠️ Geen advies ontvangen van de AI voor {filename}."
            )
            return

        # 3. GITHUB ISSUE AANMAKEN
        await self.create_github_issue(filename, advice)

    async def create_github_issue(self, filename: str, body: str):
        """Maakt een GitHub issue aan met het optimalisatie advies."""
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            issue_title = f"SYSTEM: Optimaliseer {filename} (Research Based)"
            repo.create_issue(title=issue_title, body=body)
            logger.success(f"[{self.name}] 🛠️ Ticket aangemaakt: {issue_title}")
        except Exception as e:
            logger.error(
                f"[{self.name}] ❗ Fout bij het aanmaken van GitHub issue: {e}"
            )

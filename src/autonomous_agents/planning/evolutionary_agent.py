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
        
        # DOMEINEN
        self.apps_dir = "apps"
        self.src_dir = "src"
        self.research_dir = "data/research"

    def _get_random_file(self, directory, extension):
        """Zoekt recursief naar een bestand"""
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    file_list.append(os.path.join(root, file))
        
        if not file_list: return None
        return random.choice(file_list)

    async def propose_improvement(self):
        # 🎲 KIES EEN DOMEIN (Roulette)
        domain = random.choice(["WEB", "SYSTEM", "RESEARCH"])
        
        if domain == "WEB":
            await self._improve_web()
        elif domain == "SYSTEM":
            await self._improve_system()
        elif domain == "RESEARCH":
            await self._improve_research()

    # --- 1. WEB EVOLUTIE ---
    async def _improve_web(self):
        target = self._get_random_file(self.apps_dir, ".html")
        if not target: return

        filename = os.path.basename(target)
        logger.info(f"[{self.name}] 🎮 Web Evolutie: {filename}")
        
        with open(target, 'r') as f: code = f.read()

        prompt = f"""
        Je bent een Game Designer.
        HUIDIGE APP: {filename}
        CODE SNIPPET: {code[:3000]}
        
        OPDRACHT:
        Verzin 1 coole feature om deze app leuker te maken voor de gebruiker.
        Bijvoorbeeld: Geluid, Animaties, Scorebord, Dark Mode, Mobile Support.
        
        FORMAT:
        Titel: WEB: Upgrade {filename} met [Feature]
        Body: Voeg [Feature] toe aan de bestaande code.
        """
        await self._create_ticket(prompt, "feature-request")

    # --- 2. SYSTEM EVOLUTIE ---
    async def _improve_system(self):
        target = self._get_random_file(self.src_dir, ".py")
        if not target: return
        
        filename = os.path.basename(target)
        # Sla dit bestand over om infinite loops te voorkomen
        if "evolutionary" in filename: return 
        
        logger.info(f"[{self.name}] ⚙️ System Evolutie: {filename}")
        
        with open(target, 'r') as f: code = f.read()
        
        prompt = f"""
        Je bent een Senior Python Developer.
        BESTAND: {filename}
        CODE: {code[:3000]}
        
        OPDRACHT:
        Vind 1 punt om deze code robuuster, sneller of leesbaarder te maken.
        Bijvoorbeeld: Error handling, Logging, Type Hinting, Async optimalisatie.
        
        FORMAT:
        Titel: SYSTEM: Optimaliseer {filename}
        Body: Verbeter de code van {filename}. Focus op [Jouw Punt].
        """
        await self._create_ticket(prompt, "system-optimization")

    # --- 3. RESEARCH EVOLUTIE ---
    async def _improve_research(self):
        target = self._get_random_file(self.research_dir, ".md")
        if not target: 
            # Als er nog geen research is, stel een nieuw onderwerp voor
            await self._create_ticket("""
            Verzin een interessant tech-onderwerp om te onderzoeken (bijv. AI Trends, Crypto, Nieuwe Frameworks).
            FORMAT: Titel: RESEARCH: [Onderwerp] \n Body: Zoek uit wat [Onderwerp] is.
            """, "research-needed")
            return

        filename = os.path.basename(target)
        logger.info(f"[{self.name}] 📚 Kennis Evolutie: {filename}")
        
        with open(target, 'r') as f: content = f.read()
        
        prompt = f"""
        Je bent een Wetenschapsredacteur.
        RAPPORT: {filename}
        INHOUD: {content[:3000]}
        
        OPDRACHT:
        Dit rapport kan dieper. Verzin een vervolgvraag om dit onderwerp uit te breiden.
        
        FORMAT:
        Titel: RESEARCH: Verdieping van {filename}
        Body: Zoek meer details over een specifiek sub-onderwerp dat hierin genoemd wordt.
        """
        await self._create_ticket(prompt, "research-update")

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
            
            # Check verzadiging
            if repo.get_issues(state='open').totalCount >= 5:
                logger.info(f"[{self.name}] Te druk (5+ issues), ik wacht even.")
                return

            repo.create_issue(title=title, body=body, labels=[label])
            logger.success(f"[{self.name}] 🚀 Evolutie gestart: {title}")
        except Exception as e:
            logger.error(f"GitHub Error: {e}")

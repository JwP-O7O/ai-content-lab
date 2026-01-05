import os
import json
import random
from github import Github
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class EvolutionaryAgent:
    def __init__(self):
        self.name = "EvolutionaryAgent"
        self.ai = AIService()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = "JwP-O7O/ai-content-lab"
        self.mission_file = "data/current_mission.json"

    def _get_current_mission(self):
        """Leest de huidige missie of start een nieuwe"""
        if os.path.exists(self.mission_file):
            with open(self.mission_file, 'r') as f:
                return json.load(f)
        return None

    def _set_new_mission(self, mission_data):
        """Start een nieuw project"""
        os.makedirs("data", exist_ok=True)
        with open(self.mission_file, 'w') as f:
            json.dump(mission_data, f, indent=4)
        logger.success(f"[{self.name}] 🎯 NIEUWE MISSIE GESTART: {mission_data['title']}")

    async def propose_improvement(self):
        mission = self._get_current_mission()

        # 1. GEEN MISSIE? VERZIN ER EEN!
        if not mission or mission.get('status') == 'completed':
            logger.info(f"[{self.name}] Brainstormen over volgende 'Killer App'...")
            
            prompt = """
            Verzin een idee voor een eenvoudige, verslavende browser-game of handige web-tool.
            Het moet in één HTML bestand kunnen werken (HTML5/JS).
            
            Voorbeelden: 
            - Retro Tetris Clone met Neon effecten
            - Persoonlijke Finance Dashboard met grafieken
            - Matrix Code Rain screensaver met klok
            - Space Invaders maar dan met emojis
            
            Geef antwoord in JSON:
            {
                "title": "Naam van project",
                "filename": "naam_van_file.html",
                "description": "Korte beschrijving van de gameplay/functie",
                "style": "Beschrijving van de visuele stijl (bijv. Cyberpunk, Minimalist)"
            }
            """
            response = await self.ai.generate_text(prompt)
            try:
                # Probeer JSON te parsen uit de tekst
                json_str = response.replace("```json", "").replace("```", "").strip()
                if "{" in json_str:
                    json_str = json_str[json_str.find("{"):json_str.rfind("}")+1]
                
                new_mission = json.loads(json_str)
                new_mission['status'] = 'active'
                new_mission['progress'] = 0
                self._set_new_mission(new_mission)
                mission = new_mission
                
                # Maak direct de eerste taak: Het fundament
                await self._create_ticket(
                    f"WEB: Start Project {mission['title']}",
                    f"Bouw de basisstructuur (HTML/CSS/JS) voor {mission['title']}.\nBestandsnaam: apps/{mission['filename']}\nStijl: {mission['style']}\nFunctionaliteit: {mission['description']}"
                )
                return

            except Exception as e:
                logger.error(f"Kon geen missie verzinnen: {e}")
                return

        # 2. WEL EEN MISSIE? BREID HEM UIT!
        logger.info(f"[{self.name}] 🔨 Werken aan missie: {mission['title']}")
        
        # Lees de huidige code (als die al bestaat)
        target_file = f"apps/{mission['filename']}"
        current_code = ""
        if os.path.exists(target_file):
            with open(target_file, 'r') as f: current_code = f.read()

        prompt = f"""
        Je bent de Product Owner van: {mission['title']}
        Beschrijving: {mission['description']}
        Stijl: {mission['style']}
        
        HUIDIGE STATUS CODE (Snippet):
        {current_code[:1000]}... (ingekort)
        
        OPDRACHT:
        Bedenk de VOLGENDE logische stap om dit project beter te maken.
        
        Kies 1 ding:
        - Als het bestand nog niet bestaat of leeg is -> Bouw de kern.
        - Als de basis er is -> Voeg game-loop of functionaliteit toe.
        - Als het werkt -> Voeg styling/CSS toe (maak het mooi!).
        - Als het mooi is -> Voeg geluid of scorebord toe.
        - Als het af is -> Zeg 'COMPLETED'.
        
        FORMAT:
        Titel: WEB: [Jouw Taak Titel]
        Body: [Instructies voor de WebArchitect]
        """
        
        suggestion = await self.ai.generate_text(prompt)
        
        if "COMPLETED" in suggestion:
            mission['status'] = 'completed'
            self._set_new_mission(mission)
            logger.success(f"[{self.name}] ✅ Missie Voltooid! Tijd voor de volgende.")
        else:
            await self._create_ticket_from_raw(suggestion)

    async def _create_ticket(self, title, body):
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.repo_name)
            repo.create_issue(title=title, body=body, labels=['mission-task'])
            logger.success(f"[{self.name}] 🚀 Taak aangemaakt: {title}")
        except Exception as e:
            logger.error(f"GitHub Error: {e}")

    async def _create_ticket_from_raw(self, raw_text):
        lines = raw_text.split('\n')
        title = "UPDATE"
        body = raw_text
        for line in lines:
            if line.startswith("Titel:"): title = line.replace("Titel:", "").strip()
            if line.startswith("Body:"): body = line.replace("Body:", "").strip()
        
        await self._create_ticket(title, body)

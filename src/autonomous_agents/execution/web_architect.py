import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.execution.git_publisher import GitPublisher


class WebArchitect:
    def __init__(self):
        self.name = "FrontendSquad"  # Nieuwe Squad Naam
        self.ai = AIService()
        self.publisher = GitPublisher()
        self.apps_dir = "apps"

        # ACADEMISCH SYSTEEM PROMPT VOOR FRONTEND
        self.system_prompt = """
        JIJ BENT DE 'LEAD FRONTEND ENGINEER' VAN PHOENIX OS.
        
        Jouw taak is het bouwen van moderne, responsieve en robuuste web-applicaties.
        Wij accepteren geen 'spaghetti code'. Wij bouwen Enterprise-grade interfaces.
        
        TECHNISCHE STANDAARDEN:
        1.  **Framework:** Gebruik ALTIJD Bootstrap 5 (via CDN) of moderne CSS Grid/Flexbox voor layout.
        2.  **Visuals:** Gebruik 'Glassmorphism', Neon accenten (#00ff9d) en Dark Mode als standaard.
        3.  **Robustness:** Zorg dat JavaScript fouten worden opgevangen (try/catch) en gelogd in de console.
        4.  **Single File:** Omdat we op mobiel werken, moet alles (HTML, CSS, JS) in EEN bestand blijven, tenzij anders gevraagd.
        
        WERKWIJZE:
        - Analyseer eerst de gebruikersvraag.
        - Bedenk welke UI componenten nodig zijn.
        - Schrijf schone, gecommentarieerde code.
        """

    async def build_website(self, instruction):
        logger.info(f"[{self.name}] 🏗️ Frontend ontwerp starten voor: {instruction}...")

        # 1. Bestandsnaam Bepalen
        name_prompt = f"Geef een korte, logische bestandsnaam (eindigend op .html) voor deze app: {instruction}. Geef ALLEEN de bestandsnaam."
        filename = await self.ai.generate_text(name_prompt)
        filename = filename.strip().lower().replace(" ", "_").replace("`", "")
        if not filename.endswith(".html"):
            filename += ".html"

        target_file = os.path.join(self.apps_dir, filename)

        # 2. Check of bestand al bestaat (voor updates)
        existing_code = ""
        if os.path.exists(target_file):
            with open(target_file, "r") as f:
                existing_code = f.read()
            logger.info(f"[{self.name}] ♻️ Bestaande app updaten: {filename}")

        # 3. De Bouw Prompt
        build_prompt = f"""
        {self.system_prompt}
        
        OPDRACHT: {instruction}
        
        BESTAANDE CODE (indien leeg, begin nieuw):
        {existing_code[:30000]}
        
        Output formaat: Geef ALLEEN de volledige HTML code terug (begin met <!DOCTYPE html>).
        """

        response = await self.ai.generate_text(build_prompt)

        # 4. Schoonmaak & Opslag
        code = response.replace("```html", "").replace("```", "").strip()

        os.makedirs(self.apps_dir, exist_ok=True)

        # SAFETY NET: Eerst backuppen
        await self.publisher.create_backup_commit(
            f"Pre-modification of {os.path.basename(target_file)}"
        )

        with open(target_file, "w") as f:
            f.write(code)

        logger.success(f"[{self.name}] 🌐 App opgeleverd: {filename}")
        return target_file

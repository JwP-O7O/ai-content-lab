import os
import re
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class FeatureArchitect:
    def __init__(self):
        self.name = "FeatureArchitect"
        self.ai = AIService()
        self.playground_dir = "src/playground"
        # Zorg dat de map bestaat
        if not os.path.exists(self.playground_dir):
            os.makedirs(self.playground_dir)

    def _sanitize_filename(self, text):
        """Maakt een schone bestandsnaam van een zin."""
        # Verwijder BUILD: en CODE: prefixes
        clean = re.sub(r'^(BUILD:|CODE:|maak een)', '', text, flags=re.IGNORECASE).strip()
        # Pak de eerste 3-4 woorden
        words = clean.split()[:4]
        # Verbind met underscores en verwijder vreemde tekens
        filename = "_".join(words).lower()
        filename = re.sub(r'[^a-z0-9_]', '', filename)
        return f"{filename}.py"

    async def build_feature(self, task_description):
        logger.info(f"[{self.name}] Ontwerpt: '{task_description}'")
        
        prompt = f"""
        Je bent een Expert Python Developer.
        TAAK: Schrijf een compleet, werkend script voor: "{task_description}".
        
        EISEN:
        1. Geef ALLEEN de ruwe Python code.
        2. Geen markdown blocks (```).
        3. Geen uitleg.
        4. Zorg dat de code self-contained is (geen externe bestanden nodig).
        """
        
        try:
            raw_code = await self.ai.generate_text(prompt)
            
            # Schoonmaakactie
            clean_code = raw_code.replace("```python", "").replace("```", "").strip()
            
            # CHECK: Is de code leeg?
            if not clean_code or len(clean_code) < 10:
                logger.error("❌ AI gaf een leeg bestand terug!")
                return {"status": "failed", "error": "Empty response"}

            # Bepaal bestandsnaam
            filename = self._sanitize_filename(task_description)
            filepath = os.path.join(self.playground_dir, filename)
            
            # Schrijf bestand
            with open(filepath, "w") as f:
                f.write(clean_code)
                
            logger.success(f"🏗️ Code opgeslagen in: {filepath}")
            return {"status": "built", "file": filepath}
            
        except Exception as e:
            logger.error(f"Architect fout: {e}")
            return {"status": "error", "error": str(e)}

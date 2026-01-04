import os
import re
import time
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class WebArchitect:
    def __init__(self):
        self.name = "WebArchitect"
        self.ai = AIService()
        # We zetten websites in een speciale map 'apps' zodat het overzichtelijk blijft
        self.output_dir = "apps"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _sanitize_filename(self, text):
        clean = re.sub(r'^(WEB:|SITE:|APP:|maak een)', '', text, flags=re.IGNORECASE).strip()
        words = clean.split()[:3]
        filename = "_".join(words).lower()
        filename = re.sub(r'[^a-z0-9_]', '', filename)
        return f"{filename}.html"

    async def build_website(self, task_description):
        logger.info(f"[{self.name}] Bouwt website: '{task_description}'")
        
        prompt = f"""
        Je bent een Expert Frontend Developer.
        TAAK: Maak een volledige "Single File" HTML applicatie voor: "{task_description}".
        
        EISEN:
        1. Alles (HTML, CSS, JS) moet in ÉÉN bestand zitten.
        2. Gebruik <style> voor CSS en <script> voor JS.
        3. Maak het modern, kleurrijk en mobiel-vriendelijk (responsive).
        4. Geef ALLEEN de HTML code terug. Geen markdown blocks, geen uitleg.
        """
        
        try:
            raw_code = await self.ai.generate_text(prompt)
            clean_code = raw_code.replace("```html", "").replace("```", "").strip()
            
            if "<html" not in clean_code.lower():
                logger.error("❌ AI gaf geen geldige HTML terug!")
                return {"status": "failed", "error": "Invalid HTML"}

            filename = self._sanitize_filename(task_description)
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(clean_code)
                
            logger.success(f"🌐 Website gebouwd: {filepath}")
            return {"status": "built", "file": filepath, "filename": filename}
            
        except Exception as e:
            logger.error(f"WebArchitect fout: {e}")
            return {"status": "error", "error": str(e)}

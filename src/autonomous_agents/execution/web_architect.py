import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class WebArchitect:
    def __init__(self):
        self.name = "WebArchitect"
        self.ai = AIService()
        self.output_dir = "apps"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def build_website(self, instruction):
        logger.info(f"[{self.name}] 🏗️ Analyseren van instructie: {instruction[:50]}...")
        
        # Probeer te achterhalen of we een bestaand bestand moeten updaten
        target_file = None
        existing_code = ""
        
        # Simpele check: staat er een bestandsnaam in de instructie?
        files = [f for f in os.listdir(self.output_dir) if f.endswith('.html')]
        for f in files:
            if f in instruction:
                target_file = f
                with open(os.path.join(self.output_dir, f), 'r') as read_f:
                    existing_code = read_f.read()
                logger.info(f"[{self.name}] ♻️ Update bestaande app: {target_file}")
                break

        # Prompt bouwen
        prompt = f"""
        Je bent een Expert Web Developer (HTML5/JS/CSS).
        TAAK: {instruction}
        
        BESTAANDE CODE (Indien van toepassing, anders leeg):
        {existing_code[:15000]} 
        
        REGELS:
        1. Geef ALLEEN de volledige HTML code terug. Geen markdown, geen uitleg.
        2. Als er bestaande code is: INTEGREER de nieuwe feature. Verwijder de oude werkende code niet zomaar.
        3. Zorg dat CSS en JS in één bestand zitten (<style> en <script>).
        4. Zorg voor een moderne, mooie UI.
        """
        
        response = await self.ai.generate_text(prompt)
        
        if not response: return {"status": "failed"}

        # Schoonmaak
        clean_html = response.replace("```html", "").replace("```", "").strip()
        if "<!DOCTYPE html>" not in clean_html:
            clean_html = "<!DOCTYPE html>\n" + clean_html

        # Bestandsnaam bepalen
        if not target_file:
            # Vraag AI om een bestandsnaam als we er geen hebben
            name_prompt = f"Geef een korte bestandsnaam (eindigend op .html) voor deze app: {instruction}"
            filename = await self.ai.generate_text(name_prompt)
            filename = filename.strip().replace(" ", "_").lower()
            if not filename.endswith(".html"): filename += ".html"
            # Veiligheidscheck bestandsnaam
            filename = "".join([c for c in filename if c.isalnum() or c in ['_', '.']])
        else:
            filename = target_file

        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(clean_html)
            
        logger.success(f"[{self.name}] 🚀 App gebouwd/geüpdatet: {filename}")
        return {"status": "built", "filename": filename, "file": filepath}

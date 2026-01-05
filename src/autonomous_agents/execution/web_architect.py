import os
import aiofiles
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

        existing_code = ""
        filename = None
        target_file = None # Initialiseer target_file

        files = [f for f in os.listdir(self.output_dir) if f.endswith('.html')]

        # Eerst kijken of er een relevante bestandsnaam is in de instructie
        for f in files:
            if f in instruction:
                target_file = f
                filename = f  # Gebruik f als bestandsnaam
                filepath = os.path.join(self.output_dir, f)  # Bepaal het filepath direct hier
                try:
                    async with aiofiles.open(filepath, mode='r') as read_f:  # Gebruik aiofiles
                        existing_code = await read_f.read()
                    logger.info(f"[{self.name}] ♻️ Update bestaande app: {filename}")
                    break  # Stop zodra er een match is gevonden
                except FileNotFoundError:
                    logger.error(f"[{self.name}] ⚠️ Bestand niet gevonden: {f}")
                    target_file = None  # Reset target_file als het bestand niet kan worden gelezen
                    existing_code = ""
                except Exception as e:
                    logger.error(f"[{self.name}] ⚠️ Fout bij het lezen van bestand: {f} - {e}")
                    target_file = None
                    existing_code = ""

        # Prompt bouwen
        prompt = f"""
        Je bent een Expert Web Developer (HTML5/JS/CSS).
        TAAK: {instruction}

        BESTAANDE CODE (Indien van toepassing, anders leeg):
        {existing_code[:15000]}

        REGELS:
        1. Geef ALLEEN de volledige HTML code terug. Geen markdown, geen uitleg.
        2. Als er bestaande code is: INTEGREER de nieuwe feature in de bestaande code. Verwijder de oude werkende code niet zomaar.
        3. Zorg dat CSS en JS in één bestand zitten (<style> en <script>).
        4. Zorg voor een moderne, mooie UI.
        """

        response = await self.ai.generate_text(prompt)

        if not response: return {"status": "failed"}

        # Schoonmaak
        clean_html = response.replace("", "").replace("", "").strip()
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


        filepath = os.path.join(self.output_dir, filename)

        # Schrijven naar bestand (async)
        try:
            async with aiofiles.open(filepath, mode='w') as f: # Gebruik aiofiles
                await f.write(clean_html)
            logger.info(f"[{self.name}] 💾 Bestand succesvol opgeslagen: {filename}")
            return {"status": "built", "filename": filename, "file": filepath}
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Fout bij het opslaan van bestand: {filename} - {e}")
            return {"status": "failed", "error": str(e)}
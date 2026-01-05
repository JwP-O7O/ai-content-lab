import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class FeatureArchitect:
    def __init__(self):
        self.name = "FeatureArchitect"
        self.ai = AIService()
        self.src_dir = "src"

    def _find_file(self, partial_name):
        """Zoekt een bestaand bestand in src/"""
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if partial_name in file:
                    return os.path.join(root, file)
        return None

    async def build_feature(self, instruction):
        logger.info(f"[{self.name}] ⚙️ Code Feature bouwen: {instruction[:50]}...")
        
        # 1. Probeer te zien of we een bestaand bestand moeten hebben
        target_file = None
        existing_code = ""
        
        # Slimme gok: zoek naar woorden die op .py lijken in de instructie
        words = instruction.split()
        for word in words:
            if ".py" in word:
                found = self._find_file(word.strip())
                if found:
                    target_file = found
                    with open(target_file, 'r') as f: existing_code = f.read()
                    logger.info(f"[{self.name}] ♻️ Modificeren van bestand: {target_file}")
                    break

        # 2. De Prompt
        prompt = f"""
        Je bent een Expert Python Developer.
        TAAK: {instruction}
        
        BESTAANDE CODE:
        {existing_code[:10000]}
        
        INSTRUCTIES:
        - Als er bestaande code is: Pas deze aan/breid deze uit. Verwijder geen essentiële onderdelen.
        - Als het nieuw is: Schrijf de volledige class/script.
        - Geef ALLEEN de Python code terug (geen markdown blokken).
        - Zorg voor imports, error handling en logging.
        """
        
        response = await self.ai.generate_text(prompt)
        if not response: return {"status": "failed"}

        # 3. Schoonmaak
        code = response.replace("```python", "").replace("```", "").strip()
        
        # 4. Opslaan
        if not target_file:
            # Nieuw bestand? Vraag naam.
            name_p = f"Bestandsnaam voor deze python code (eindigend op .py, max 1 woord): {instruction}"
            fname = await self.ai.generate_text(name_p)
            fname = fname.strip().lower().replace(" ", "_")
            if not fname.endswith(".py"): fname += ".py"
            # Zet nieuwe bestanden standaard in execution folder als we het niet weten
            target_file = os.path.join("src/autonomous_agents/execution", fname)

        # Zorg dat map bestaat
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        with open(target_file, 'w') as f:
            f.write(code)
            
        logger.success(f"[{self.name}] 💾 Code geschreven naar: {target_file}")
        return {"status": "built", "file": target_file}

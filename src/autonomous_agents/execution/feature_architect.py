import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class FeatureArchitect:
    def __init__(self):
        self.name = "FeatureArchitect"
        self.ai = AIService()
        self.src_dir = "src"

    def _find_file(self, partial_name):
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if partial_name in file:
                    return os.path.join(root, file)
        return None

    async def build_feature(self, instruction):
        logger.info(f"[{self.name}] ⚙️ Feature bouwen: {instruction[:50]}...")
        
        # 🚫 VEILIGHEIDSPROTOCOL: Verbied __init__.py
        if "__init__" in instruction:
            logger.warning(f"[{self.name}] 🚫 Wijzigen van __init__.py is verboden om crashes te voorkomen.")
            return {"status": "skipped"}

        # 1. Zoek bestaand bestand
        target_file = None
        existing_code = ""
        
        words = instruction.split()
        for word in words:
            if ".py" in word:
                found = self._find_file(word.strip())
                if found:
                    target_file = found
                    with open(target_file, 'r') as f: existing_code = f.read()
                    break

        # 2. De Prompt
        prompt = f"""
        Je bent een Expert Python Developer.
        TAAK: {instruction}
        
        BESTAANDE CODE:
        {existing_code[:8000]}
        
        REGELS:
        1. Geef ALLEEN de volledige Python code terug.
        2. Raak GEEN __init__.py bestanden aan.
        3. Zorg dat imports kloppen (gebruik 'from src...' waar nodig).
        """
        
        response = await self.ai.generate_text(prompt)
        if not response: return {"status": "failed"}

        # 3. Schoonmaak
        code = response.replace("```python", "").replace("```", "").strip()
        
        # 4. Opslaan
        if not target_file:
            name_p = f"Bestandsnaam (eindigend op .py): {instruction}"
            fname = await self.ai.generate_text(name_p)
            fname = fname.strip().lower().replace(" ", "_")
            if not fname.endswith(".py"): fname += ".py"
            # 🚫 DUBBELE CHECK
            if "__init__" in fname: fname = "mod_safety_override.py"
            target_file = os.path.join("src/autonomous_agents/execution", fname)

        # Zorg dat map bestaat
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # 🚫 LAATSTE CHECK: Schrijf nooit naar __init__.py
        if "__init__.py" in target_file:
            logger.error(f"[{self.name}] 🛑 Poging tot sabotage geblokkeerd.")
            return {"status": "failed"}

        with open(target_file, 'w') as f:
            f.write(code)
            
        logger.success(f"[{self.name}] 💾 Code geschreven naar: {target_file}")
        return {"status": "built", "file": target_file}

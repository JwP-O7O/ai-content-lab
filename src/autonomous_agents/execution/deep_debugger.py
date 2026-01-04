import subprocess
import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class DeepDebugger:
    def __init__(self):
        self.name = "DeepDebugger"
        self.ai = AIService()

    async def fix_broken_code(self, filepath, error_log):
        logger.info(f"[{self.name}] 🚑 Start spoedoperatie op: {filepath}")
        try:
            with open(filepath, 'r') as f: broken_code = f.read()
            prompt = f"Herschrijf deze Python code zodat de volgende error wordt opgelost. Geef ALLEEN de code:\nERROR:\n{error_log}\nCODE:\n{broken_code}"
            fixed_code = await self.ai.generate_text(prompt)
            with open(filepath, 'w') as f: f.write(fixed_code)
            logger.success(f"✅ [{self.name}] Bestand gerepareerd.")
            return {"status": "fixed", "file": filepath}
        except Exception as e:
            logger.error(f"Debugger faalde: {e}")
            return {"status": "failed"}

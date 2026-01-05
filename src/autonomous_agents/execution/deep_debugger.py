import subprocess
import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService
import traceback

class DeepDebugger:
    def __init__(self):
        self.name = "DeepDebugger"
        self.ai = AIService()

    async def fix_broken_code(self, filepath, error_log):
        logger.info(f"[{self.name}] 🚑 Start spoedoperatie op: {filepath}")
        try:
            with open(filepath, 'r') as f:
                broken_code = f.read()
            prompt = f"Herschrijf deze Python code zodat de volgende error wordt opgelost. Geef ALLEEN de code:\nERROR:\n{error_log}\nCODE:\n{broken_code}"
            fixed_code = await self.ai.generate_text(prompt)
            with open(filepath, 'w') as f:
                f.write(fixed_code)
            logger.success(f"✅ [{self.name}] Bestand gerepareerd.")
            return {"status": "fixed", "file": filepath}

        except FileNotFoundError:
            logger.error(f"[{self.name}] ❌ Bestand niet gevonden: {filepath}")
            return {"status": "failed", "error": "FileNotFoundError", "file": filepath}

        except PermissionError:
            logger.error(f"[{self.name}] ❌ Geen toestemming om bestand te lezen/schrijven: {filepath}")
            return {"status": "failed", "error": "PermissionError", "file": filepath}

        except OSError as e:
            logger.error(f"[{self.name}] ❌ OS Error bij lezen/schrijven bestand {filepath}: {e}")
            return {"status": "failed", "error": "OSError", "file": filepath, "details": str(e)}

        except Exception as e:
            logger.error(f"[{self.name}] ❌ Debugger faalde door een onbekende reden: {e}\nTraceback:\n{traceback.format_exc()}")
            return {"status": "failed", "error": "UnknownError", "details": str(e), "traceback": traceback.format_exc()}
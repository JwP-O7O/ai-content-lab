import subprocess
from typing import Dict, Any, List
from loguru import logger
from ..base_autonomous_agent import BaseAutonomousAgent


class TestRunner(BaseAutonomousAgent):
    """
    Voert de test suite uit en rapporteert resultaten.
    """

    def __init__(self):
        super().__init__(name="TestRunner", layer="validation", interval_seconds=3600)

    async def analyze(self) -> Dict[str, Any]:
        return {}

    async def plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[TestRunner] 🧪 Start validatie tests...")

        try:
            # Voer pytest uit en capture output
            result = subprocess.run(
                ["pytest", "tests/"], capture_output=True, text=True
            )

            # Pak de laatste regels voor de log
            output_lines = result.stdout.split("\n")
            output_tail = "\n".join(output_lines[-15:])

            if result.returncode == 0:
                logger.success("[TestRunner] ✅ Alle tests geslaagd!")
                return {"status": "success", "output": result.stdout}

            elif result.returncode == 5:
                # Code 5 = No tests collected.
                logger.warning("[TestRunner] ⚠️ Geen tests gevonden (Code 5).")
                return {
                    "status": "warning",
                    "message": "No tests found in tests/ directory",
                    "output": result.stdout,
                }

            else:
                # Code 1 = Tests failed
                logger.error(f"[TestRunner] ❌ Tests gefaald!\n{output_tail}")
                return {
                    "status": "failed",
                    "output": result.stdout,
                    "summary": output_tail,
                }

        except Exception as e:
            logger.error(f"[TestRunner] ❌ Fout bij uitvoeren tests: {e}")
            return {"status": "error", "error": str(e)}

import subprocess
from typing import Dict, Any, List
from loguru import logger
from ..base_autonomous_agent import BaseAutonomousAgent


class CodeRefactorer(BaseAutonomousAgent):
    """
    Voert automatische code verbeteringen uit (refactoring).
    Bevat een 'rollback' mechanisme voor als wijzigingen tests breken.
    """

    def __init__(self):
        super().__init__(
            name="CodeRefactorer", layer="execution", interval_seconds=3600
        )

    async def analyze(self) -> Dict[str, Any]:
        """Check of er files zijn die formatted moeten worden."""
        return {}

    async def plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Voert fixes uit met veiligheidsmechanisme."""
        logger.info("[CodeRefactorer] 🔨 Start automatische reparaties...")

        changes_made = False
        details = ""

        try:
            # 1. Probeer Ruff fixes (linter)
            proc_check = subprocess.run(
                ["ruff", "check", "src/", "--fix"], capture_output=True, text=True
            )

            # 2. Probeer Ruff formatting
            proc_format = subprocess.run(
                ["ruff", "format", "src/"], capture_output=True, text=True
            )

            # Check of er output was die duidt op wijzigingen
            if "Fixed" in proc_check.stdout or "reformatted" in proc_format.stdout:
                changes_made = True
                details = "Linter fixed. Formatting applied."
                logger.success("[CodeRefactorer] ✅ Code stijl toegepast.")
            else:
                logger.info("[CodeRefactorer] Geen wijzigingen nodig.")

            return {
                "status": "success",
                "changes_made": changes_made,
                "details": details,
                "plan": plan,
            }

        except Exception as e:
            logger.error(f"[CodeRefactorer] ❌ Fout tijdens refactoring: {e}")
            return {
                "status": "error",
                "changes_made": False,
                "error": str(e),
                "plan": plan,
            }

    def rollback(self):
        """Draai wijzigingen direct terug via Git."""
        logger.warning(
            "[CodeRefactorer] ↩️ ROLLBACK UITVOEREN: Wijzigingen ongedaan maken..."
        )
        try:
            # Herstel alle gewijzigde bestanden in src/ naar de laatste commit
            subprocess.run(["git", "checkout", "src/"], check=True, capture_output=True)
            logger.success("[CodeRefactorer] ✅ Rollback succesvol. Systeem hersteld.")
        except Exception as e:
            logger.critical(f"[CodeRefactorer] 🚨 ROLLBACK MISLUKT: {e}")

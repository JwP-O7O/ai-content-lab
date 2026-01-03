import subprocess
from loguru import logger


class CodeRefactorer:
    def __init__(self):
        self.name = "CodeRefactorer"

    async def execute_fixes(self):
        logger.info(f"[{self.name}] Start automatische reparaties op src/...")
        results = {"fixed": False, "message": ""}

        try:
            # 1. Voer Ruff --fix uit
            fix_proc = subprocess.run(
                ["ruff", "check", "src/", "--fix"], capture_output=True, text=True
            )

            # 2. Voer Ruff format uit (voor nette code volgens JwP standaard)
            format_proc = subprocess.run(
                ["ruff", "format", "src/"], capture_output=True, text=True
            )

            if fix_proc.returncode == 0:
                results["fixed"] = True
                results["message"] = (
                    "Alle repareerbare fouten zijn verholpen en code is geformatteerd."
                )
                logger.success(f"✅ [{self.name}] Succesvol code gerefactord.")
            else:
                results["message"] = (
                    "Sommige fouten konden niet automatisch worden opgelost."
                )
                logger.warning(f"⚠️ [{self.name}] Refactoring gedeeltelijk uitgevoerd.")

        except Exception as e:
            logger.error(f"Fout tijdens refactoring: {e}")
            results["message"] = str(e)

        return results

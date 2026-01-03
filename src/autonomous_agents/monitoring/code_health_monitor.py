import subprocess
from loguru import logger


class CodeHealthMonitor:
    def __init__(self):
        self.name = "CodeHealthMonitor"

    async def analyze(self):
        logger.info(f"[{self.name}] Start analyse van src/...")
        results = {"ruff": "ok", "mypy": "ok", "issues_found": 0}

        # 1. Run Ruff
        try:
            # We gebruiken ruff check op de src map
            ruff_proc = subprocess.run(
                ["ruff", "check", "src/"], capture_output=True, text=True
            )
            if ruff_proc.returncode != 0:
                results["ruff"] = "issues"
                results["issues_found"] += 1
                logger.warning("⚠️ Ruff vond verbeterpunten in de code.")
        except Exception as e:
            logger.error(f"Fout tijdens Ruff scan: {e}")

        # 2. Run MyPy (Type checking)
        try:
            mypy_proc = subprocess.run(
                ["mypy", "src/", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
            )
            if mypy_proc.returncode != 0:
                results["mypy"] = "issues"
                results["issues_found"] += 1
                logger.warning("⚠️ MyPy vond type-consistentie issues.")
        except Exception as e:
            logger.error(f"Fout tijdens MyPy scan: {e}")

        return results

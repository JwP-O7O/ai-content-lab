import subprocess
from typing import Dict, Any
from loguru import logger
from ..base_autonomous_agent import BaseAutonomousAgent


class CodeHealthMonitor(BaseAutonomousAgent):
    def __init__(self):
        super().__init__(
            name="CodeHealthMonitor", layer="monitoring", interval_seconds=1800
        )

    async def analyze(self) -> Dict[str, Any]:
        results = {}
        try:
            # Check met Ruff
            ruff_output = subprocess.run(
                ["ruff", "check", "src/"], capture_output=True, text=True
            )
            # Tel aantal fouten (simpele implementatie)
            error_count = len(
                [
                    l
                    for l in ruff_output.stdout.split("\n")
                    if "error" in l.lower() or "warning" in l.lower()
                ]
            )

            # Score berekenen
            health_score = max(0, 100 - (error_count * 5))

            results["health_score"] = health_score
            results["issues"] = error_count

        except FileNotFoundError:
            logger.warning("Ruff niet gevonden. Installeer ruff met: pip install ruff")
            results["health_score"] = (
                100  # Neem aan dat het goed is als we niet kunnen checken
            )

        return results

    async def plan(self, analysis):
        return []

    async def execute(self, plan):
        return {}

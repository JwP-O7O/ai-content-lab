import subprocess
import json  # Importeer de json module
from typing import Dict, Any, List
from loguru import logger
from ..base_autonomous_agent import BaseAutonomousAgent


class CodeHealthMonitor(BaseAutonomousAgent):
    def __init__(self):
        super().__init__(
            name="CodeHealthMonitor", layer="monitoring", interval_seconds=1800
        )

    async def analyze(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        issues: List[Dict[str, Any]] = []

        try:
            # Check met Ruff, gebruik JSON output
            ruff_output = subprocess.run(
                ["ruff", "check", "src/", "--output-format", "json"],
                capture_output=True,
                text=True,
            )
            try:
                ruff_json_output = json.loads(ruff_output.stdout)  # Parse JSON
                for issue in ruff_json_output:
                    issues.append(
                        {
                            "message": issue.get("message", "Unknown error"),
                            "code": issue.get("code", "Unknown"),
                            "filename": issue.get("filename", "Unknown"),
                            "location": issue.get(
                                "location", {}
                            ),  # added to show line/column
                            "severity": "error"
                            if "E" in issue.get("code", "")
                            else "warning",  # Determine severity
                        }
                    )

                error_count = sum(1 for issue in issues if issue["severity"] == "error")
                warning_count = len(
                    [issue for issue in issues if issue["severity"] == "warning"]
                )

                health_score = max(0, 100 - (error_count * 5) - (warning_count * 2))

                results["health_score"] = health_score
                results["issues"] = error_count + warning_count  # totaal aantal issues
                results["detailed_issues"] = issues  # Sla gedetailleerde info op

            except json.JSONDecodeError:
                logger.error(
                    f"Fout bij het parsen van Ruff JSON output: {ruff_output.stdout}"
                )
                results["health_score"] = 0
                results["issues"] = -1  # Indicate a parsing error
                results["detailed_issues"] = []

        except FileNotFoundError:
            logger.warning("Ruff niet gevonden. Installeer ruff met: pip install ruff")
            results["health_score"] = 100  # Assume good if we cannot check
            results["issues"] = 0  # No issues if ruff is missing

        return results

    async def plan(self, analysis):
        # Implementeer logica om acties te plannen op basis van de analyse
        # Bijvoorbeeld: een commando om Ruff uit te voeren met een `--fix` flag
        # of het aanmaken van een issue in een tracking systeem.
        plan = []
        if analysis and "detailed_issues" in analysis:
            for issue in analysis["detailed_issues"]:
                plan.append(
                    {
                        "action": "fix_issue",
                        "issue_code": issue["code"],
                        "filename": issue["filename"],
                        "line": issue["location"].get("row"),  # Add line for context
                        "column": issue["location"].get(
                            "column"
                        ),  # Add column for context
                        "message": issue["message"],
                    }
                )
        return plan

    async def execute(self, plan):
        if not plan:
            return {}

        results = {}
        for action in plan:
            if action["action"] == "fix_issue":
                try:
                    # Construct command to fix the issue using ruff --fix
                    cmd = ["ruff", "fix", action["filename"]]

                    fix_output = subprocess.run(cmd, capture_output=True, text=True)
                    if fix_output.returncode == 0:
                        logger.info(
                            f"Fixed issue {action['issue_code']} in {action['filename']}  ({action['message']})"
                        )
                    else:
                        logger.error(
                            f"Failed to fix issue {action['issue_code']} in {action['filename']} (Error: {fix_output.stderr})"
                        )
                except FileNotFoundError:
                    logger.error(
                        "Ruff niet gevonden. Installeer ruff met: pip install ruff"
                    )

        return results

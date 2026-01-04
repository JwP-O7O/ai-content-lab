import subprocess
from loguru import logger


class GuardianAgent:
    def __init__(self):
        self.name = "GuardianAgent"
        # Patronen die absoluut verboden zijn in de code
        self.forbidden_patterns = [
            "sk-prod-",
            "ghp_",
            "private_key",
            "password =",
            "passwd =",
        ]

    async def scan_for_secrets(self):
        """Scant de codebase op hardcoded secrets."""
        logger.info(f"[{self.name}] Security Sweep gestart...")
        issues = []

        # Simpele grep scan (snel en effectief op Termux)
        for pattern in self.forbidden_patterns:
            try:
                # grep -r "pattern" src/
                cmd = ["grep", "-r", pattern, "src/"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout:
                    issues.append(f"Gevoelig patroon gevonden: {pattern}")
            except Exception:
                pass

        if issues:
            logger.critical(f"🔒 BEVEILIGINGSLEKKEN GEDETECTEERD: {issues}")
            return {"secure": False, "issues": issues}
        else:
            logger.success(f"🛡️ [{self.name}] Geen secrets aangetroffen.")
            return {"secure": True, "issues": []}

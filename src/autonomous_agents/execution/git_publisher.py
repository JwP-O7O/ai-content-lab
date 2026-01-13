import subprocess
from loguru import logger


class GitPublisher:
    def __init__(self):
        self.name = "GitPublisher"

    async def create_backup_commit(self, message: str):
        """Maakt een lokale backup commit voor veiligheid."""
        try:
            status = (
                subprocess.check_output(["git", "status", "--porcelain"])
                .decode("utf-8")
                .strip()
            )
            if not status:
                return  # Niets te backuppen

            subprocess.check_call(["git", "add", "."])
            subprocess.check_call(
                ["git", "commit", "-m", f"🛡️ SAFETY BACKUP: {message}"]
            )
            logger.info(f"[{self.name}] Safety backup commit created.")
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to create backup commit: {e}")

    async def publish_changes(self):
        """Pusht wijzigingen en logt het harde bewijs"""
        try:
            # 1. Check of er überhaupt iets veranderd is
            status = (
                subprocess.check_output(["git", "status", "--porcelain"])
                .decode("utf-8")
                .strip()
            )

            if not status:
                return {"status": "no_changes"}

            logger.info(f"[{self.name}] Wijzigingen gedetecteerd. Analyseren...")

            # 2. Voeg alles toe
            subprocess.check_call(["git", "add", "."])

            # 3. Krijg de statistieken VOORDAT we committen (Het bewijs)
            # Dit laat zien: "file.py | 10 +-"
            stats = (
                subprocess.check_output(["git", "diff", "--cached", "--stat"])
                .decode("utf-8")
                .strip()
            )

            # Log elke gewijzigde file apart voor de HUD
            for line in stats.split("\n"):
                if "|" in line:
                    # Format: " src/main.py | 5 +--"
                    logger.success(f"[{self.name}] 📝 FILE: {line.strip()}")

            # 4. Commit en Push
            commit_msg = f"🤖 AI Update: {subprocess.check_output(['date', '+%Y-%m-%d %H:%M']).decode('utf-8').strip()}"
            subprocess.check_call(["git", "commit", "-m", commit_msg])
            subprocess.check_call(["git", "push"])

            logger.success(f"[{self.name}] 🚀 Bewijs geleverd & Code gepusht!")
            return {"status": "success"}

        except Exception as e:
            logger.error(f"[{self.name}] Git Error: {e}")
            return {"status": "error"}

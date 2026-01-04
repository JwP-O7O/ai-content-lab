import subprocess
from loguru import logger
from datetime import datetime

class GitPublisher:
    def __init__(self):
        self.name = "GitPublisher"
        # We kijken nu naar de hele root map, niet alleen data/output
        self.repo_root = "."

    async def publish_changes(self):
        try:
            # 1. Check status
            status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            
            if not status.stdout.strip():
                return {"status": "no_changes"}

            logger.info(f"[{self.name}] Wijzigingen gevonden. Start publicatie...")

            # 2. Stage ALLES (Code + Content)
            subprocess.run(['git', 'add', '.'], check=True)

            # 3. Commit
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_msg = f"🤖 AI Auto-Publish: Update {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            logger.success(f"📦 Lokaal ge-commit: '{commit_msg}'")

            # 4. Push
            try:
                push_res = subprocess.run(['git', 'push'], capture_output=True, text=True)
                if push_res.returncode == 0:
                    logger.success("🚀 Succesvol gepusht naar GitHub!")
                    return {"status": "published"}
                else:
                    logger.warning(f"⚠️ Push mislukt: {push_res.stderr}")
                    return {"status": "committed_local_only"}
            except Exception:
                 return {"status": "committed_local_only"}

        except Exception as e:
            logger.error(f"Git fout: {e}")
            return {"status": "error"}

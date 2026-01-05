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
            push_res = subprocess.run(['git', 'push'], capture_output=True, text=True)
            if push_res.returncode == 0:
                logger.success("🚀 Succesvol gepusht naar GitHub!")
                return {"status": "published"}
            else:
                logger.warning(f"⚠️ Push mislukt: {push_res.stderr}")
                if "authentication required" in push_res.stderr.lower():
                    logger.error("❌ Authenticatie mislukt. Controleer je GitHub credentials of SSH-configuratie.")
                    return {"status": "push_failed_authentication"}
                elif "failed to push some refs" in push_res.stderr.lower():
                    logger.error("❌ Push mislukt: Merge conflict of andere ref-gerelateerde problemen.  Los de conflicten lokaal op en probeer opnieuw.")
                    return {"status": "push_failed_conflict"}
                else:
                    logger.error(f"❌ Onbekende push-fout: {push_res.stderr}")
                    return {"status": "push_failed_unknown"}


        except subprocess.CalledProcessError as e:
            logger.error(f"Git commando mislukt: {e}.  Uitvoer: {e.stderr}")
            return {"status": "error"}
        except Exception as e:
            logger.error(f"Onverwachte Git fout: {e}")
            return {"status": "error"}
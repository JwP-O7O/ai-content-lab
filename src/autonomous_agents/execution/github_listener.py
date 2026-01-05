from github import Github
from loguru import logger
import os
from dotenv import load_dotenv
import time  # Nodig voor retry-mechanisme
from ratelimit import limits, sleep_and_retry  # Gebruik een rate limiter, installeer met: pip install ratelimit

# Laad de kluis
load_dotenv()

# Haal token veilig op
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "JwP-O7O/ai-content-lab"

# GitHub API rate limits - pas aan op basis van je gebruiksbehoefte en GitHub's documentatie
# Dit is een voorbeeld, controleer de Github API documentatie.
# Hier proberen we 50 calls per uur.
RATE_LIMIT_CALLS = 50
RATE_LIMIT_PERIOD = 3600  # seconds (1 hour)

class GitHubListener:
    def __init__(self):
        self.name = "GitHubListener"
        self.token = GITHUB_TOKEN
        self.repo_name = REPO_NAME

        if not self.token:
            logger.critical("❌ GITHUB_TOKEN ontbreekt in .env bestand!")

    @sleep_and_retry
    @limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
    def _safe_github_api_call(self, func, *args, **kwargs):
        """ Wrapper voor GitHub API calls met rate limiting en retries."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"GitHub API Fout tijdens call: {e}.  Probeer opnieuw.")
            raise  # Her-raise de exception om de retry te activeren.  De ratelimit decorator zal dit afhandelen.


    async def check_for_orders(self):
        """Checkt GitHub Issues voor nieuwe opdrachten"""
        if not self.token:
            return {"status": "error", "error": "No token"}

        try:
            g = Github(self.token)
            repo = g.get_repo(self.repo_name)

            # Pak alle open issues
            open_issues = repo.get_issues(state='open')

            tasks = []

            for issue in open_issues:
                if "🤖" in issue.title:
                    continue

                logger.info(f"[{self.name}] Order ontvangen: {issue.title}")
                title_upper = issue.title.upper()

                # ANALYSE
                if "WEB:" in title_upper or "SITE:" in title_upper:
                    task_type = "web"
                elif "IMG:" in title_upper:
                    task_type = "image"
                elif "BUILD:" in title_upper or "CODE:" in title_upper:
                    task_type = "code"
                else:
                    task_type = "content"

                tasks.append({
                    "type": task_type,
                    "title": issue.title,
                    "body": issue.body,
                    "issue_obj": issue
                })

                try:
                    await self._safe_github_api_call(issue.edit, title=f"🤖 [WIP] {issue.title}")  # Gebruik _safe_github_api_call
                    await self._safe_github_api_call(issue.create_comment, f"🤖 **Opdracht Geaccepteerd**\nTaak Type: `{task_type}`\nIk ga aan de slag.")  # Gebruik _safe_github_api_call
                except Exception as e:
                    logger.warning(f"Kon GitHub issue niet updaten: {e}")

            if tasks:
                return {"status": "new_tasks", "tasks": tasks}
            else:
                return {"status": "no_tasks"}

        except Exception as e:
            logger.error(f"GitHub Listener Fout: {e}")
            return {"status": "error", "error": str(e)}
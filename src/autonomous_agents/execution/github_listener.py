from github import Github
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "JwP-O7O/ai-content-lab"

class GitHubListener:
    def __init__(self):
        self.name = "GitHubListener"
        self.token = GITHUB_TOKEN
        self.repo_name = REPO_NAME
        
    async def check_for_orders(self):
        if not self.token: return {"status": "error", "error": "No token"}

        try:
            g = Github(self.token)
            repo = g.get_repo(self.repo_name)
            open_issues = repo.get_issues(state='open')
            
            tasks = []
            for issue in open_issues:
                # Als we er al mee bezig zijn (herkenbaar aan de robot), sla over
                if "🤖" in issue.title: continue
                
                logger.info(f"[{self.name}] Order ontvangen: {issue.title}")
                
                # Probeer de status te updaten, maar crash niet als het mislukt
                try:
                    issue.edit(title=f"🤖 [WIP] {issue.title}")
                    issue.create_comment(f"🤖 **Gestart**\nIk ga hiermee aan de slag.")
                except Exception as update_err:
                    logger.warning(f"Kon GitHub status niet updaten (geen ramp): {update_err}")

                tasks.append({
                    "title": issue.title.replace("🤖 [WIP]", "").strip(), # Schone titel
                    "body": issue.body,
                    "issue_obj": issue
                })

            if tasks: return {"status": "new_tasks", "tasks": tasks}
            else: return {"status": "no_tasks"}

        except Exception as e:
            logger.error(f"GitHub Listener Critical Error: {e}")
            return {"status": "error", "error": str(e)}

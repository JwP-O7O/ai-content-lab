from github import Github
from loguru import logger
import os
from dotenv import load_dotenv

# Laad de kluis
load_dotenv()

# Haal token veilig op
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "JwP-O7O/ai-content-lab"

class GitHubListener:
    def __init__(self):
        self.name = "GitHubListener"
        self.token = GITHUB_TOKEN
        self.repo_name = REPO_NAME
        
        if not self.token:
            logger.critical("❌ GITHUB_TOKEN ontbreekt in .env bestand!")
        
    async def check_for_orders(self):
        """Checkt GitHub Issues voor nieuwe opdrachten"""
        if not self.token: return {"status": "error", "error": "No token"}

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
                    issue.edit(title=f"🤖 [WIP] {issue.title}")
                    issue.create_comment(f"🤖 **Opdracht Geaccepteerd**\nTaak Type: `{task_type}`\nIk ga aan de slag.")
                except Exception as e:
                    logger.warning(f"Kon GitHub issue niet updaten: {e}")

            if tasks:
                return {"status": "new_tasks", "tasks": tasks}
            else:
                return {"status": "no_tasks"}

        except Exception as e:
            logger.error(f"GitHub Listener Fout: {e}")
            return {"status": "error", "error": str(e)}
# Security verified

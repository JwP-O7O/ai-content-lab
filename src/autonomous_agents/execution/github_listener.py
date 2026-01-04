from github import Github
from loguru import logger
import os

# JOUW SPECIFIEKE TOKEN (Hersteld)
GITHUB_TOKEN = "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"
REPO_NAME = "JwP-O7O/ai-content-lab"

class GitHubListener:
    def __init__(self):
        self.name = "GitHubListener"
        self.token = GITHUB_TOKEN
        self.repo_name = REPO_NAME
        
    async def check_for_orders(self):
        """Checkt GitHub Issues voor nieuwe opdrachten"""
        try:
            g = Github(self.token)
            repo = g.get_repo(self.repo_name)
            
            # Pak alle open issues
            open_issues = repo.get_issues(state='open')
            
            tasks = []
            
            for issue in open_issues:
                # 1. Veiligheidscheck: Hebben we dit al behandeld?
                if "🤖" in issue.title:
                    continue
                
                logger.info(f"[{self.name}] Order ontvangen: {issue.title}")
                title_upper = issue.title.upper()
                
                # 2. ANALYSE: Wat voor taak is dit?
                if "WEB:" in title_upper or "SITE:" in title_upper:
                    task_type = "web"
                elif "IMG:" in title_upper:
                    task_type = "image"
                elif "BUILD:" in title_upper or "CODE:" in title_upper:
                    task_type = "code"
                else:
                    task_type = "content"
                
                # 3. Voeg toe aan takenlijst
                tasks.append({
                    "type": task_type,
                    "title": issue.title,
                    "body": issue.body,
                    "issue_obj": issue
                })
                
                # 4. Markeer direct als 'Gezien' op GitHub
                try:
                    issue.edit(title=f"🤖 [WIP] {issue.title}")
                    issue.create_comment(f"🤖 **Opdracht Geaccepteerd**\nTaak Type: `{task_type}`\nIk ga aan de slag op S21 Ultra.")
                except Exception as e:
                    logger.warning(f"Kon GitHub issue niet updaten: {e}")

            if tasks:
                return {"status": "new_tasks", "tasks": tasks}
            else:
                return {"status": "no_tasks"}

        except Exception as e:
            logger.error(f"GitHub Listener Fout: {e}")
            return {"status": "error", "error": str(e)}

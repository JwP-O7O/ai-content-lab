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
        self.github_instance = None  # Store the Github instance for reuse

        # Validate configuration during initialization
        self._validate_config()

    def _validate_config(self):
        """Validates the configuration and logs warnings if issues are found."""
        if not self.token:
            logger.warning(
                f"[{self.name}] GITHUB_TOKEN is not set. GitHub functionality will be severely limited."
            )
        if not self.repo_name:
            logger.warning(
                f"[{self.name}] REPO_NAME is not set.  GitHub functionality will be severely limited."
            )

    def _get_github_instance(self):
        """
        Returns a Github instance, creating it if it doesn't exist.  Handles token errors.
        """
        if self.github_instance is None:
            if not self.token:
                logger.error(
                    f"[{self.name}] No GitHub token available. Cannot initialize Github instance."
                )
                return None
            try:
                self.github_instance = Github(self.token)
            except Exception as e:
                logger.error(f"[{self.name}] Error initializing Github instance: {e}")
                return None
        return self.github_instance

    async def check_for_orders(self):
        """
        Checks for new orders (GitHub issues) and processes them.
        """
        if not self.token:
            return {"status": "error", "error": "No GitHub token provided."}

        g = self._get_github_instance()
        if g is None:
            return {"status": "error", "error": "Failed to initialize Github instance."}

        try:
            repo = g.get_repo(self.repo_name)
            open_issues = repo.get_issues(state="open")

            tasks = []
            for issue in open_issues:
                # Skip if already being processed (identified by the robot emoji)
                if "🤖" in issue.title:
                    continue

                logger.info(f"[{self.name}] Order received: {issue.title}")

                # Update the issue title and comment to indicate processing.  Handle failures gracefully.
                try:
                    new_title = f"🤖 [WIP] {issue.title}"
                    if issue.title != new_title:  # Avoid unnecessary updates
                        issue.edit(title=new_title)
                    issue.create_comment("🤖 **Gestart**\nIk ga hiermee aan de slag.")
                except Exception as update_err:
                    logger.warning(
                        f"[{self.name}] Failed to update GitHub issue status (non-critical): {update_err}"
                    )

                tasks.append(
                    {
                        "title": issue.title.replace(
                            "🤖 [WIP]", ""
                        ).strip(),  # Clean title for task processing
                        "body": issue.body,
                        "issue_obj": issue,
                    }
                )

            if tasks:
                return {"status": "new_tasks", "tasks": tasks}
            else:
                return {"status": "no_tasks"}

        except Exception as e:
            logger.error(f"[{self.name}] Critical error during GitHub order check: {e}")
            return {"status": "error", "error": str(e)}

import os
from loguru import logger


class ContentQualityMonitor:
    def __init__(self):
        self.name = "ContentQualityMonitor"
        self.content_dir = "data/output"
        self.min_words = 50
        self.forbidden_words = ["financieel advies", "gegarandeerde winst"]

    async def analyze(self):
        if not os.path.exists(self.content_dir):
            return {"status": "skipped", "reason": "No content dir found"}

        logger.info(f"[{self.name}] Inspecteren van content kwaliteit...")
        issues = []

        for root, _, files in os.walk(self.content_dir):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r") as f:
                            content = f.read()

                        if len(content.split()) < self.min_words:
                            issues.append(f"{file}: Te kort")

                        for bad_word in self.forbidden_words:
                            if bad_word in content.lower():
                                issues.append(f"{file}: Verboden term '{bad_word}'")
                    except Exception as e:
                        logger.warning(f"Kon {file} niet lezen: {e}")

        if issues:
            logger.warning(f"⚠️ Content Issues: {issues}")
            return {"status": "issues", "details": issues}
        else:
            logger.success("✅ Content Kwaliteit OK.")
            return {"status": "ok"}

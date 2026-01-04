import os
from loguru import logger
from src.autonomous_agents.ai_service import AIService


class ContentWriter:
    def __init__(self):
        self.name = "ContentWriter"
        self.marker = "[TODO: DEZE SECTIE MOET WORDEN UITGEBREID DOOR WRITER AGENT]"
        self.ai = AIService()

    async def expand_content(self):
        logger.info(f"[{self.name}] Zoeken naar uitbreidingstaken...")
        content_dir = "data/output"
        expanded_count = 0

        if not os.path.exists(content_dir):
            return {"status": "skipped"}

        for root, _, files in os.walk(content_dir):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r") as f:
                            content = f.read()

                        if self.marker in content:
                            logger.info(f"💡 Gemini aan het werk voor: {file}")

                            prompt = f"Schrijf 2 alinea's over dit onderwerp in het Nederlands ter vervanging van de TODO marker: \n\n{content}"
                            new_text = await self.ai.generate_text(prompt)

                            updated_content = content.replace(
                                self.marker, f"\n\n{new_text}\n"
                            )

                            with open(path, "w") as f:
                                f.write(updated_content)

                            expanded_count += 1
                            logger.success(
                                f"✍️ {file} succesvol uitgebreid door Gemini."
                            )

                    except Exception as e:
                        logger.error(f"Fout bij schrijven {file}: {e}")

        return (
            {"status": "success", "count": expanded_count}
            if expanded_count > 0
            else {"status": "no_tasks"}
        )

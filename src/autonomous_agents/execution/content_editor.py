import os
from loguru import logger


class ContentEditor:
    def __init__(self):
        self.name = "ContentEditor"
        self.forbidden_map = {
            "financieel advies": "**financiële educatie**",
            "gegarandeerde winst": "**kansen**",
            "memecoin": "crypto-activum",
        }

    async def fix_content(self, issues):
        """
        Probeert content issues automatisch op te lossen.
        """
        logger.info(f"[{self.name}] Start redactie-proces...")
        fixed_count = 0

        # We halen de unieke bestandsnamen uit de issues lijst
        files_to_fix = set([issue.split(":")[0] for issue in issues])

        for filename in files_to_fix:
            filepath = os.path.join("data/output", filename)
            if not os.path.exists(filepath):
                continue

            try:
                with open(filepath, "r") as f:
                    content = f.read()

                original_content = content

                # 1. Censuur / Vervanging toepassen
                for bad_word, replacement in self.forbidden_map.items():
                    if bad_word in content.lower():
                        # Simpele case-insensitive replace (voor demo)
                        content = content.replace(bad_word, replacement)
                        logger.info(
                            f"✏️ '{bad_word}' vervangen door '{replacement}' in {filename}"
                        )

                # 2. Te korte content markeren (als placeholder voor LLM expansie)
                if len(content.split()) < 50 and "DRAFT" not in content:
                    content += "\n\n[TODO: DEZE SECTIE MOET WORDEN UITGEBREID DOOR WRITER AGENT]"
                    logger.info(f"📏 {filename} gemarkeerd voor uitbreiding.")

                # Alleen wegschrijven als er iets veranderd is
                if content != original_content:
                    with open(filepath, "w") as f:
                        f.write(content)
                    fixed_count += 1

            except Exception as e:
                logger.error(f"Fout bij bewerken {filename}: {e}")

        if fixed_count > 0:
            return {"status": "fixed", "count": fixed_count}
        else:
            return {"status": "no_changes"}

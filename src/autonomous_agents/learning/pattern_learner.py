import os
from loguru import logger


class PatternLearner:
    def __init__(self):
        self.name = "PatternLearner"
        self.memory_path = "data/improvement_plans/lessons_learned.json"

    async def get_avoidance_strategy(self):
        """
        Analyseert eerdere fouten en bepaalt wat we NIET moeten doen.
        """
        avoid_list = []

        if not os.path.exists(self.memory_path):
            return avoid_list

        try:
            with open(self.memory_path, "r") as f:
                content = f.read()

            # Simpele logica: als een module vaak faalt, zet hem op de zwarte lijst
            # In de toekomst kan dit met NLP/LLM, nu rule-based voor snelheid op S21.
            if "tests/" in content:
                # Als tests zelf breken, wees voorzichtig met de test map
                avoid_list.append("tests/")

            # Hier kun je slimme logica toevoegen die bestandsnamen uit de error logs haalt

            if avoid_list:
                logger.info(
                    f"[{self.name}] Geleerde strategie: Vermijd aanpassingen aan {avoid_list}"
                )

        except Exception as e:
            logger.error(f"Fout bij lezen geheugen: {e}")

        return avoid_list

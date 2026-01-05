import json
import os
from loguru import logger

MEMORY_FILE = "data/memory.json"

class GlobalBrain:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self._load_memory()

    def _load_memory(self):
        if not os.path.exists(self.memory_file):
            self.memory = {
                "lessons_learned": [],
                "successful_patterns": [],
                "avoid_errors": []
            }
            self._save_memory()
        else:
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
            except:
                self.memory = {"lessons_learned": []}

    def _save_memory(self):
        # Zorg dat de map bestaat
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def add_lesson(self, category, content):
        """Voegt een nieuwe les toe (bijv: 'Gebruik geen alert() in games')"""
        entry = {"timestamp": str(os.times()), "content": content}
        if category not in self.memory:
            self.memory[category] = []
        
        self.memory[category].append(entry)
        self._save_memory()
        logger.info(f"🧠 [Brain] Nieuwe les opgeslagen in '{category}'")

    def get_context(self):
        """Geeft een samenvatting van wat we geleerd hebben voor de AI prompt"""
        summary = "GELEERDE LESSEN (Hou hier rekening mee):\n"
        for item in self.memory.get("avoid_errors", [])[-5:]: # Laatste 5 fouten
            summary += f"- VERMIJD: {item['content']}\n"
        for item in self.memory.get("successful_patterns", [])[-5:]: # Laatste 5 successen
            summary += f"- GEBRUIK: {item['content']}\n"
        return summary

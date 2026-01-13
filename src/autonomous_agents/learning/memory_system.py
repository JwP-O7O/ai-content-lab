import os
import json
import time
import shutil
from loguru import logger
from src.autonomous_agents.ai_service import AIService

class MemorySystem:
    def __init__(self):
        self.memory_file = "PROJECT_MEMORY.md"
        self.lessons_file = "data/improvement_plans/lessons_learned.json"
        self.ai = AIService()
        
        # Zorg dat de mappen bestaan
        os.makedirs(os.path.dirname(self.lessons_file), exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                f.write("# PROJECT PHOENIX MEMORY & CONTEXT\n\n## 🏗️ Architecture Status\n\n## 🧠 Lessons Learned\n")
        
        # Check if lessons file exists and is valid JSON
        if os.path.exists(self.lessons_file):
            try:
                with open(self.lessons_file, 'r') as f:
                    # Probeer te parsen. Als het faalt, triggert dit de except.
                    content = f.read()
                    if content.strip():
                        json.loads(content)
                    else:
                        self._create_empty_lessons_file()
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Corrupt JSON found in {self.lessons_file}. Backing up and resetting.")
                shutil.move(self.lessons_file, self.lessons_file + ".bak")
                self._create_empty_lessons_file()
        else:
            self._create_empty_lessons_file()

    def _create_empty_lessons_file(self):
        with open(self.lessons_file, 'w') as f:
            json.dump({"successful_patterns": [], "failed_patterns": [], "metrics": {}}, f)

    async def update_context_after_task(self, task_id, title, result, status, duration):
        """
        Leert van de uitgevoerde taak. Dit is de 'Feedback Loop'.
        """
        logger.info(f"🧠 Analyseren van taakresultaat voor optimalisatie...")
        
        # 1. Update Metrics (Performance Monitoring)
        self._update_metrics(status, duration)

        # 2. Update Kennisbank (Context)
        if status == "completed":
            await self._add_success_to_memory(title, result)
        else:
            await self._analyze_failure(title, result)

    def _update_metrics(self, status, duration):
        try:
            data = {}
            with open(self.lessons_file, 'r') as f: 
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    self._create_empty_lessons_file()
                    data = {"successful_patterns": [], "failed_patterns": [], "metrics": {}}

            if "metrics" not in data: data["metrics"] = {"total_tasks": 0, "success_rate": 0, "avg_duration": 0}
            
            m = data["metrics"]
            m["total_tasks"] += 1
            if status == "completed":
                # Moving average voor success (simpel)
                prev_success = m.get("success_count", 0)
                m["success_count"] = prev_success + 1
            
            # Update moving average duration
            m["avg_duration"] = (m["avg_duration"] * (m["total_tasks"] - 1) + duration) / m["total_tasks"]
            
            with open(self.lessons_file, 'w') as f: json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    async def _add_success_to_memory(self, title, result):
        """Voegt succesvolle implementatie toe aan de context."""
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        entry = f"\n- **[{timestamp}] {title}:** Succesvol afgerond. \n"
        
        # Append aan MD file
        with open(self.memory_file, 'a') as f:
            f.write(entry)
            
        # Structurele 'Pattern' opslag (Reinforcement Learning light)
        # We vragen de AI om te extraheren WAT er goed ging
        analysis_prompt = f"""
        ANALYSEER DIT SUCCES:
        Taak: {title}
        Resultaat: {result}
        
        Wat is het 'herbruikbare patroon' hieruit? (Max 1 zin).
        """
        pattern = await self.ai.generate_text(analysis_prompt)
        
        with open(self.lessons_file, 'r+') as f:
            data = json.load(f)
            data["successful_patterns"].append({"task": title, "pattern": pattern.strip()})
            f.seek(0)
            json.dump(data, f, indent=2)

    async def _analyze_failure(self, title, error_msg):
        """Analyseert een fout om herhaling te voorkomen (Bias Mitigation / Robustness)."""
        logger.warning(f"📉 Foutanalyse gestart voor: {title}")
        
        analysis_prompt = f"""
        ANALYSEER DEZE FOUT:
        Taak: {title}
        Error: {error_msg}
        
        Wat moeten we NOOIT meer doen? (Max 1 zin).
        """
        lesson = await self.ai.generate_text(analysis_prompt)
        
        with open(self.lessons_file, 'r+') as f:
            data = json.load(f)
            data["failed_patterns"].append({"task": title, "lesson": lesson.strip()})
            f.seek(0)
            json.dump(data, f, indent=2)
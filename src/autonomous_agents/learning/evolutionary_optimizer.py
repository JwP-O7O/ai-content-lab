import json
import os
import random
from loguru import logger
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.execution.task_queue import TaskQueue

class EvolutionaryOptimizer:
    def __init__(self):
        self.ai = AIService()
        self.queue = TaskQueue()
        self.lessons_file = "data/improvement_plans/lessons_learned.json"
        self.prompts_file = "data/improvement_plans/adaptive_prompts.json"
        
        self._ensure_prompts_file()

    def _ensure_prompts_file(self):
        if not os.path.exists(self.prompts_file):
            # Initieer met standaard prompts als ze nog niet bestaan
            default_prompts = {
                "BackendSquad": "Jij bent een Lead Backend Engineer...",
                "FrontendSquad": "Jij bent een Lead Frontend Engineer..."
            }
            os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
            with open(self.prompts_file, 'w') as f:
                json.dump(default_prompts, f, indent=2)

    async def suggest_improvement(self):
        """
        De kern van de zelfverbetering. Analyseert prestaties en genereert een optimalisatietaak.
        """
        logger.info("🧬 Evolutionary Optimizer: Scanning for improvements...")
        
        # 1. Analyseer Metrics (Performance Metrics & Feedback Loops)
        metrics = self._read_metrics()
        success_rate = metrics.get("success_count", 0) / max(metrics.get("total_tasks", 1), 1)
        
        # 2. Beslis Strategie (Resource Allocation & Learning Rate)
        if success_rate < 0.8:
            logger.warning(f"📉 Success rate is low ({success_rate:.2f}). Triggering Prompt Optimization.")
            return await self._optimize_prompt_strategy()
        
        if random.random() < 0.3: # 30% kans op spontane refactor
            return await self._propose_refactor_strategy()
            
        if random.random() < 0.5: # 50% kans op test coverage
            return await self._propose_testing_strategy()

        logger.info("✅ System healthy. No immediate optimization needed.")
        return None

    def _read_metrics(self):
        try:
            with open(self.lessons_file, 'r') as f:
                data = json.load(f)
                return data.get("metrics", {})
        except Exception:
            return {}

    async def _optimize_prompt_strategy(self):
        """
        Adaptieve Prompting: Herschrijft de systeem-prompts op basis van lessen.
        """
        logger.info("🧠 Optimizing System Prompts via RLHF simulation...")
        
        # Lees lessen
        try:
            with open(self.lessons_file, 'r') as f:
                data = json.load(f)
                failures = data.get("failed_patterns", [])[-5:] # Laatste 5 fouten
        except:
            failures = []

        failures_text = "\n".join([f"- {f.get('lesson', 'Unknown error')}" for f in failures])
        
        # Genereer taak
        instruction = f"SYSTEM: SELF-IMPROVEMENT. Analyseer deze fouten:\n{failures_text}\n\nUpdate 'data/improvement_plans/adaptive_prompts.json' met verbeterde, striktere instructies voor de Agents om deze fouten te voorkomen."
        
        self.queue.add_task(
            title=instruction,
            description="Adaptive Prompt Optimization",
            source="evolutionary_optimizer"
        )
        return "Prompt Optimization Task Queued"

    async def _propose_refactor_strategy(self):
        """
        Code Quality: Zoekt naar 'messy' code en stelt refactor voor.
        """
        # Scan src dir (simpel: zoek grootste bestand)
        target_file = None
        max_size = 0
        for root, _, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    size = os.path.getsize(path)
                    if size > max_size:
                        max_size = size
                        target_file = path
        
        if target_file and max_size > 2000: # Alleen als bestand groot genoeg is
            instruction = f"SYSTEM: REFACTOR. Het bestand `{target_file}` is groot. Analyseer het en pas 'Extract Method' toe om de leesbaarheid te verbeteren. Zorg dat alle functionaliteit behouden blijft en tests blijven slagen."
            self.queue.add_task(title=instruction, description="Automated Refactoring", source="evolutionary_optimizer")
            return f"Refactor Task Queued for {target_file}"
            
        return None

    async def _propose_testing_strategy(self):
        """
        Quality Assurance: Zoekt naar bestanden zonder tests.
        """
        for root, _, files in os.walk("src"):
            for file in files:
                if file.endswith(".py") and "__init__" not in file:
                    test_file = os.path.join("tests", f"test_{file}")
                    if not os.path.exists(test_file):
                        instruction = f"SYSTEM: TEST COVERAGE. Maak een unit test bestand voor `{os.path.join(root, file)}`. Gebruik pytest."
                        self.queue.add_task(title=instruction, description="Missing Test Coverage", source="evolutionary_optimizer")
                        return f"Test Task Queued for {file}"
        return None

import os
import ast
import subprocess
from loguru import logger
from src.autonomous_agents.ai_service import AIService
from src.autonomous_agents.execution.git_publisher import GitPublisher


class FeatureArchitect:
    def __init__(self):
        self.name = "BackendSquad"  # Nieuwe Squad Naam
        self.ai = AIService()
        self.publisher = GitPublisher()
        self.src_dir = "src"

        # ACADEMISCH SYSTEEM PROMPT VOOR BACKEND
        self.system_prompt = """
        JIJ BENT DE 'LEAD BACKEND ENGINEER' VAN PHOENIX OS.
        
        Jouw taak is het schrijven van Python scripts die stabiel, veilig en efficiënt zijn (PEP 8 compliant).
        
        TECHNISCHE STANDAARDEN:
        1.  **Safety First:** Gebruik ALTIJD try/except blokken om crashes te voorkomen.
        2.  **Logging:** Gebruik `from loguru import logger` voor output, geen `print()`.
        3.  **Type Hinting:** Gebruik Python type hints (def func(a: int) -> str:) waar mogelijk.
        4.  **No Hallucinations:** Importeer alleen libraries die standaard zijn of waarvan je zeker weet dat ze geïnstalleerd zijn.
        
        ABSOLUTE VERBODEN:
        - Wijzig NOOIT `__init__.py` bestanden.
        - Verwijder NOOIT zomaar bestanden zonder backup instructie.
        """

    def _find_file(self, partial_name):
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if partial_name in file:
                    return os.path.join(root, file)
        return None
    
    def _format_code(self, code):
        """
        Formatteert de code met 'Black' voor consistente stijl.
        """
        try:
            # Run black via stdin (-)
            process = subprocess.Popen(
                ['black', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            formatted_code, stderr = process.communicate(input=code)
            
            if process.returncode == 0:
                logger.info(f"[{self.name}] ✨ Code formatted with Black.")
                return formatted_code.strip()
            else:
                logger.warning(f"[{self.name}] ⚠️ Black formatting failed: {stderr}. Using raw code.")
                return code
        except Exception as e:
            logger.warning(f"[{self.name}] ⚠️ Formatting error: {e}")
            return code

    async def _generate_and_run_tests(self, code, target_file):
        """
        Genereert een unit test, slaat deze op en voert hem uit.
        """
        filename = os.path.basename(target_file)
        module_name = filename.replace(".py", "")
        # Construct import path (e.g., src.playground.sanity_calc)
        rel_path = os.path.relpath(target_file, os.getcwd()).replace(os.path.sep, ".").replace(".py", "")
        
        test_filename = f"test_{filename}"
        test_file_path = os.path.join("tests", test_filename)
        
        logger.info(f"[{self.name}] 🧪 Generating unit tests for {filename}...")
        
        test_prompt = f"""
        ACT AS: QA Automation Engineer.
        TASK: Write a robust `pytest` unit test for the following Python code.
        
        CONTEXT:
        - The code is located at: `{target_file}`
        - The test will be located at: `{test_file_path}`
        - You MUST import the module using: `from {rel_path} import *`
        - Use `sys.path.append(os.getcwd())` if necessary to fix imports.
        
        CODE TO TEST:
        {code}
        
        OUTPUT:
        - Return ONLY the Python test code.
        - Include `import pytest`.
        """
        
        response = await self.ai.generate_text(test_prompt)
        test_code = response.replace("```python", "").replace("```", "").strip()
        
        # Save test
        os.makedirs("tests", exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write(test_code)
            
        logger.info(f"[{self.name}] 💾 Test opgeslagen: {test_file_path}. Running pytest...")
        
        # Run pytest
        try:
            result = subprocess.run(
                ["pytest", test_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.success(f"[{self.name}] ✅ ALL TESTS PASSED for {filename}!")
                return True
            else:
                logger.error(f"[{self.name}] ❌ TESTS FAILED for {filename}:\n{result.stdout}\n{result.stderr}")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] ⚠️ Failed to run pytest: {e}")
            return False

    async def _validate_and_fix(self, code, attempt=1):
        """
        Valideert de syntax van de code via AST.
        Bij fouten: Vraagt de AI om een correctie (Self-Healing).
        """
        try:
            ast.parse(code)
            return code  # Code is syntactisch correct
        except SyntaxError as e:
            if attempt > 3:
                logger.error(
                    f"[{self.name}] ❌ Code repair failed after 3 attempts. Syntax Error: {e}"
                )
                raise e  # Geef op na 3 pogingen

            logger.warning(
                f"[{self.name}] ⚠️ Syntax Error detected: {e}. Attempting repair {attempt}/3..."
            )

            repair_prompt = f"""
            CRITICAL SYNTAX ERROR DETECTED:
            {e}
            
            BROKEN CODE:
            {code}
            
            ASSIGNMENT: Fix the syntax error. Return ONLY the corrected, valid Python code.
            """
            response = await self.ai.generate_text(repair_prompt)
            new_code = response.replace("```python", "").replace("```", "").strip()
            return await self._validate_and_fix(new_code, attempt + 1)

    async def build_feature(self, instruction):
        logger.info(f"[{self.name}] ⚙️ Backend architecture starten: {instruction}...")

        # Veiligheid
        if "__init__" in instruction:
            logger.warning(
                f"[{self.name}] 🚫 Toegang geweigerd tot systeem-kern (__init__)."
            )
            return {"status": "skipped"}

        # 1. Context zoeken
        target_file = None
        existing_code = ""
        words = instruction.split()
        for word in words:
            if ".py" in word:
                found = self._find_file(word.strip())
                if found:
                    target_file = found
                    with open(target_file, "r") as f:
                        existing_code = f.read()
                    break

        # 2. De Bouw Prompt
        build_prompt = f"""
        {self.system_prompt}
        
        OPDRACHT: {instruction}
        
        BESTAANDE CODE (indien van toepassing):
        {existing_code[:30000]}
        
        Output formaat: Geef ALLEEN de volledige Python code terug.
        """

        response = await self.ai.generate_text(build_prompt)
        if not response:
            return {"status": "failed"}

        # 3. Schoonmaak
        raw_code = response.replace("```python", "").replace("```", "").strip()

        # 4. Validatie & Self-Healing (NIEUW)
        try:
            validated_code = await self._validate_and_fix(raw_code)
        except SyntaxError:
            return {"status": "failed", "msg": "Unfixable Syntax Error"}
            
        # 5. Formatting (Mijlpaal 3.1)
        final_code = self._format_code(validated_code)

        # 6. Opslag (Nieuw bestand of Update)
        if not target_file:
            name_p = f"Kies een Python bestandsnaam (snake_case) voor: {instruction}. ALLEEN de naam."
            fname = await self.ai.generate_text(name_p)
            fname = fname.strip().lower().replace(" ", "_").replace(".py", "") + ".py"
            # Veiligheidshalve opslaan in playground als locatie onbekend is
            target_file = os.path.join("src/playground", fname)

        # Map aanmaken indien nodig
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        if "__init__.py" in target_file:
            return {"status": "failed", "msg": "Protected File"}

        # SAFETY NET: Eerst backuppen
        await self.publisher.create_backup_commit(
            f"Pre-modification of {os.path.basename(target_file)}"
        )

        with open(target_file, "w") as f:
            f.write(final_code)

        # 7. Unit Tests (Mijlpaal 3.2)
        tests_passed = await self._generate_and_run_tests(final_code, target_file)

        logger.success(
            f"[{self.name}] 💾 Code (Validated, Formatted & Tested) geïmplementeerd in: {target_file}"
        )
        return {"status": "success", "file": target_file, "tests_passed": tests_passed}

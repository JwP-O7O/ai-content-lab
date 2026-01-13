import os
import ast
import re
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
        """Formatteert de code met 'Black'."""
        try:
            process = subprocess.Popen(['black', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            formatted_code, stderr = process.communicate(input=code)
            if process.returncode == 0:
                logger.info(f"[{self.name}] ✨ Code formatted with Black.")
                return formatted_code.strip()
            return code
        except Exception:
            return code

    async def _generate_and_run_tests(self, code, target_file):
        """Genereert en runt unit tests. Geeft (success, output) terug."""
        filename = os.path.basename(target_file)
        module_name = filename.replace(".py", "")
        rel_path = os.path.relpath(target_file, os.getcwd()).replace(os.path.sep, ".").replace(".py", "")
        test_filename = f"test_{filename}"
        test_file_path = os.path.join("tests", test_filename)
        
        logger.info(f"[{self.name}] 🧪 Generating unit tests for {filename}...")
        
        test_prompt = f"""
        ACT AS: QA Automation Engineer.
        TASK: Write a robust `pytest` unit test.
        CONTEXT: Code at `{target_file}`, Test at `{test_file_path}`.
        IMPORT: `from {rel_path} import *`. Use `sys.path.append(os.getcwd())`.
        CODE:
        {code}
        OUTPUT: ONLY Python test code. Include `import pytest`.
        """
        
        response = await self.ai.generate_text(test_prompt)
        test_code = response.replace("```python", "").replace("```", "").strip()
        
        os.makedirs("tests", exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write(test_code)
            
        logger.info(f"[{self.name}] 💾 Test saved. Running pytest...")
        
        try:
            result = subprocess.run(["pytest", test_file_path], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.success(f"[{self.name}] ✅ ALL TESTS PASSED!")
                return True, result.stdout
            else:
                logger.error(f"[{self.name}] ❌ TESTS FAILED:\n{result.stdout}")
                return False, result.stdout + "\n" + result.stderr
        except Exception as e:
            return False, str(e)

    async def _functional_self_healing(self, code, test_output, instruction, attempt):
        """Vraagt AI om de code OF de test te fixen op basis van de error."""
        logger.warning(f"[{self.name}] 🩹 Starting Functional Self-Healing (Attempt {attempt})...")
        
        fix_prompt = f"""
        ACT AS: Senior Python Developer & QA Expert.
        
        SITUATION:
        I wrote some code and a unit test, but the tests FAILED.
        
        ORIGINAL INSTRUCTION: {instruction}
        
        CURRENT CODE:
        {code}
        
        TEST FAILURE OUTPUT:
        {test_output}
        
        TASK:
        Analyze the failure. Is the CODE wrong, or is the TEST wrong?
        Fix the CODE to satisfy the test, OR fix the TEST if it was hallucinated/incorrect.
        
        OUTPUT:
        Return ONLY the corrected Python CODE (the implementation, NOT the test). 
        If you think the code is correct and the test is wrong, return the code as is (but usually the code needs adjustment).
        """
        
        response = await self.ai.generate_text(fix_prompt)
        return response.replace("```python", "").replace("```", "").strip()

    async def _validate_syntax(self, code):
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    async def build_feature(self, instruction):
        logger.info(f"[{self.name}] ⚙️ Backend architecture starten: {instruction}...")
        
        if "__init__" in instruction: return {"status": "skipped"}

        # 1. Context zoeken
        target_file = None
        existing_code = ""
        words = instruction.split()
        for word in words:
            if ".py" in word:
                found = self._find_file(word.strip())
                if found:
                    target_file = found
                    with open(target_file, "r") as f: existing_code = f.read()
                    break

        # 2. Initial Build
        build_prompt = f"""
        {self.system_prompt}
        OPDRACHT: {instruction}
        BESTAANDE CODE: {existing_code[:30000]}
        Output: ALLEEN Python code.
        """
        response = await self.ai.generate_text(build_prompt)
        if not response: return {"status": "failed"}
        
        current_code = response.replace("```python", "").replace("```", "").strip()
        
        # Determine filename early if new
        if not target_file:
            name_p = f"Filename for: {instruction}. ONLY the base name (no extension, no path). Snake_case."
            fname_raw = await self.ai.generate_text(name_p)
            # STRICT CLEANING: Keep only letters, numbers, underscores
            fname_clean = re.sub(r'[^a-zA-Z0-9_]', '', fname_raw.strip().lower())
            if not fname_clean: fname_clean = "generated_feature" # Fallback
            target_file = os.path.join("src/playground", fname_clean + ".py")

        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # 3. RECOVERY LOOP (Mijlpaal 3.3)
        max_attempts = 3
        attempt = 1
        tests_passed = False
        
        while attempt <= max_attempts:
            # A. Syntax Check
            if not await self._validate_syntax(current_code):
                pass 
            
            # B. Format
            current_code = self._format_code(current_code)
            
            # C. Save Code
            await self.publisher.create_backup_commit(f"Pre-test attempt {attempt} of {os.path.basename(target_file)}")
            with open(target_file, "w") as f: f.write(current_code)
            
            # D. Generate & Run Tests
            success, output = await self._generate_and_run_tests(current_code, target_file)
            
            if success:
                tests_passed = True
                logger.success(f"[{self.name}] 🎉 Feature Stable after {attempt} attempts!")
                break
            else:
                # E. Self-Healing
                if attempt < max_attempts:
                    current_code = await self._functional_self_healing(current_code, output, instruction, attempt)
                    attempt += 1
                else:
                    logger.error(f"[{self.name}] 💀 Gave up after {max_attempts} attempts.")
                    break

        return {"status": "success", "file": target_file, "tests_passed": tests_passed}
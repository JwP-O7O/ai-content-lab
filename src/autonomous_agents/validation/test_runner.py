import subprocess
from loguru import logger


class TestRunner:
    def __init__(self):
        self.name = "TestRunner"

    async def run_all_tests(self):
        logger.info(f"[{self.name}] Validatiecyclus gestart: Pytest uitvoeren...")
        results = {"passed": False, "summary": ""}

        try:
            # Voer pytest uit op de tests/ map
            test_proc = subprocess.run(
                ["pytest", "tests/", "-v", "--maxfail=3"],
                capture_output=True,
                text=True,
            )

            if test_proc.returncode == 0:
                results["passed"] = True
                results["summary"] = "Alle tests zijn geslaagd."
                logger.success(f"✅ [{self.name}] Systeemvalidatie SUCCESVOL.")
            else:
                results["summary"] = "Tests gefaald na wijzigingen."
                logger.error(f"❌ [{self.name}] Kritieke fout: Tests falen!")
                # Log de eerste paar regels van de fout voor context
                logger.debug(f"Test output snippet: {test_proc.stdout[:200]}")

        except Exception as e:
            logger.error(f"Fout tijdens test-executie: {e}")
            results["summary"] = str(e)

        return results

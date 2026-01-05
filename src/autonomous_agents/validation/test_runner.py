import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from loguru import logger
from ..base_autonomous_agent import BaseAutonomousAgent
import os


class TestRunner(BaseAutonomousAgent):
    """
    Voert de test suite uit en rapporteert resultaten.
    """

    def __init__(self):
        super().__init__(name="TestRunner", layer="validation", interval_seconds=3600)
        self.junit_xml_path = "test_results.xml"

    async def analyze(self) -> Dict[str, Any]:
        return {}

    async def plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[TestRunner] 🧪 Start validatie tests...")

        try:
            # Voer pytest uit en capture output, gebruik `--junitxml`
            result = subprocess.run(
                ["pytest", "tests/", f"--junitxml={self.junit_xml_path}"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Parse het XML bestand voor meer gedetailleerde resultaten
                try:
                    tree = ET.parse(self.junit_xml_path)
                    root = tree.getroot()
                    # Hier zou je de resultaten uit het XML bestand halen
                    # Bijvoorbeeld het aantal tests, errors, failures etc.
                    # Dit is een vereenvoudigde voorbeeld
                    test_summary = {
                        "tests": root.get('tests'),
                        "failures": root.get('failures'),
                        "errors": root.get('errors')
                        # Voeg hier meer informatie toe
                    }

                    logger.success("[TestRunner] ✅ Alle tests geslaagd!")
                    return {
                        "status": "success",
                        "output": result.stdout,
                        "test_summary": test_summary,
                    }
                except FileNotFoundError:
                    logger.error(
                        f"[TestRunner] ❌ Kon test resultaten bestand niet vinden: {self.junit_xml_path}"
                    )
                    return {"status": "error", "error": "JUnit XML file not found"}
                except ET.ParseError as e:
                    logger.error(
                        f"[TestRunner] ❌ Fout bij het parsen van JUnit XML: {e}"
                    )
                    return {"status": "error", "error": f"Error parsing JUnit XML: {e}"}

            elif result.returncode == 5:
                # Code 5 = No tests collected.
                logger.warning("[TestRunner] ⚠️ Geen tests gevonden (Code 5).")
                return {
                    "status": "warning",
                    "message": "No tests found in tests/ directory",
                    "output": result.stdout,
                }
            else:
                logger.error(f"[TestRunner] ❌ Tests mislukt (returncode: {result.returncode})")
                logger.error(f"[TestRunner] 🪵 Stderr output:\n{result.stderr}")

                # Parse het XML bestand voor meer gedetailleerde resultaten
                try:
                    tree = ET.parse(self.junit_xml_path)
                    root = tree.getroot()
                    test_summary = {
                        "tests": root.get('tests') or "0",  # Default to 0 if not present
                        "failures": root.get('failures') or "0",
                        "errors": root.get('errors') or "0",
                    }

                    if int(test_summary["failures"]) > 0 or int(test_summary["errors"]) > 0:
                        logger.error(f"[TestRunner] 💥 Test failures/errors detected.")
                        return {
                            "status": "failure",
                            "output": result.stdout,
                            "stderr": result.stderr,
                            "test_summary": test_summary,
                        }
                    else:
                        return {
                            "status": "error", # Handle unexpected errors.
                            "output": result.stdout,
                            "stderr": result.stderr,
                            "test_summary": test_summary,
                        }

                except FileNotFoundError:
                    logger.error(
                        f"[TestRunner] ❌ Kon test resultaten bestand niet vinden: {self.junit_xml_path}"
                    )
                    return {"status": "error", "error": "JUnit XML file not found", "stderr": result.stderr}
                except ET.ParseError as e:
                    logger.error(
                        f"[TestRunner] ❌ Fout bij het parsen van JUnit XML: {e}"
                    )
                    return {"status": "error", "error": f"Error parsing JUnit XML: {e}", "stderr": result.stderr}
                except Exception as e:
                    logger.error(f"[TestRunner] ❌ Onverwachte fout bij het verwerken van testresultaten: {e}")
                    return {"status": "error", "error": f"Unexpected error: {e}", "stderr": result.stderr}


        except Exception as e:
            logger.error(f"[TestRunner] ❌ Fout bij uitvoeren tests: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            # Opruimen van het xml bestand.
            if os.path.exists(self.junit_xml_path):
                try:
                    os.remove(self.junit_xml_path)
                except Exception as e:
                    logger.warning(f"Kon {self.junit_xml_path} niet verwijderen: {e}")
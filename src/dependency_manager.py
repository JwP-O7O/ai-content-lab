import sys
import subprocess
import os
from loguru import logger

class DependencyManager:
    # Mapping van module naam naar pip package naam
    module_name_mapping = {
        "PIL": "Pillow",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4",
        "dotenv": "python-dotenv",
        # Voeg hier meer mappings toe
    }

    @staticmethod
    def heal(error_message):
        """Probeert een ontbrekende module te installeren o.b.v. de error"""
        if "No module named" not in str(error_message):
            return False

        try:
            missing_module = str(error_message).split("'")[1]

            # Gebruik de mapping om de package naam te bepalen
            package_name = DependencyManager.module_name_mapping.get(missing_module, missing_module)  # Gebruik get() voor default value

            logger.warning(f"🚑 SYSTEM HEALTH: Module '{missing_module}' ontbreekt.")
            logger.info(f"💉 Auto-Installeren van '{package_name}'...")

            # Voeg timeout toe aan subprocess.check_call
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], timeout=60) # Timeout van 60 seconden

            logger.success(f"✔ {package_name} succesvol geïnstalleerd!")
            logger.info("🔄 Systeem herstarten om wijzigingen toe te passen...")

            os.execv(sys.executable, [sys.executable] + sys.argv)
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Auto-Install mislukt: Timeout bij installatie van {package_name}")
            return False
        except Exception as e:
            logger.error(f"❌ Auto-Install mislukt: {e}")
            return False
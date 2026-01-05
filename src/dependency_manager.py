import sys
import subprocess
import os
from loguru import logger

class DependencyManager:
    @staticmethod
    def heal(error_message):
        """Probeert een ontbrekende module te installeren o.b.v. de error"""
        # Error ziet eruit als: "No module named 'ratelimit'"
        if "No module named" not in str(error_message):
            return False

        try:
            # Vis de naam van de module uit de error
            missing_module = str(error_message).split("'")[1]
            
            # Sommige modules heten anders in pip (bijv. PIL -> Pillow)
            # Hier kunnen we uitzonderingen toevoegen, voor nu 1-op-1
            package_name = missing_module
            if missing_module == "PIL": package_name = "Pillow"
            if missing_module == "sklearn": package_name = "scikit-learn"
            if missing_module == "yaml": package_name = "pyyaml"
            if missing_module == "bs4": package_name = "beautifulsoup4"
            if missing_module == "dotenv": package_name = "python-dotenv"

            logger.warning(f"🚑 SYSTEM HEALTH: Module '{missing_module}' ontbreekt.")
            logger.info(f"💉 Auto-Installeren van '{package_name}'...")
            
            # Voer pip install uit
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            
            logger.success(f"✔ {package_name} succesvol geïnstalleerd!")
            logger.info("🔄 Systeem herstarten om wijzigingen toe te passen...")
            
            # Herstart het huidige script volledig
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return True
            
        except Exception as e:
            logger.error(f"❌ Auto-Install mislukt: {e}")
            return False

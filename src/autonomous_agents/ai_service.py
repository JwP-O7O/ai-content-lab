import google.generativeai as genai
import os
from loguru import logger
import time

class AIService:
    def __init__(self):
        # De lijst met sleutels (De Pool)
        self.api_keys = [
            "AIzaSyDgayrzXgtdhNgQd_enucOrVPcg0pXchs8", # Nieuw 1
            "AIzaSyBQXtSC3mopsBJJgvRQI81hQRy877eklGo", # Nieuw 2
            "AIzaSyDz2NaBIhS_d30efumafNjclnS8xcnTG4I"  # Oude (Backup)
        ]
        self.current_key_index = 0
        self.model_name = "models/gemini-1.5-flash" # Snelste model
        self.online = False
        
        self._configure_current_key()

    def _configure_current_key(self):
        """Activeert de huidige sleutel in de lijst."""
        try:
            current_key = self.api_keys[self.current_key_index]
            # Maskeer de sleutel voor logs (laat alleen laatste 4 tekens zien)
            masked_key = f"...{current_key[-4:]}"
            
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.online = True
            logger.info(f"🔑 AI Sleutel geactiveerd: {masked_key} (Index {self.current_key_index + 1}/{len(self.api_keys)})")
        except Exception as e:
            logger.error(f"❌ Kon sleutel niet configureren: {e}")

    def _rotate_key(self):
        """Wisselt naar de volgende sleutel in de lijst."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"🔄 Limiet bereikt! Roteren naar sleutel #{self.current_key_index + 1}...")
        self._configure_current_key()

    async def generate_text(self, prompt):
        if not self.online: return ""
        
        # We proberen het net zo vaak als we sleutels hebben (maximaal 3 pogingen)
        for attempt in range(len(self.api_keys)):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text.replace("```json", "").replace("```python", "").replace("```", "").strip()
                return ""
                
            except Exception as e:
                error_msg = str(e)
                # Check specifiek op Quota errors (429)
                if "429" in error_msg or "Quota" in error_msg or "Resource has been exhausted" in error_msg:
                    # Sleutel is op, draai naar de volgende en probeer in de volgende loop opnieuw
                    self._rotate_key()
                    continue 
                else:
                    # Een echte fout (geen quota), stop met proberen
                    logger.error(f"⚠️ Gemini Error (Niet-Quota): {e}")
                    return ""
        
        logger.error("❌ ALLE sleutels zijn tijdelijk uitgeput. Even pauze nemen.")
        return ""

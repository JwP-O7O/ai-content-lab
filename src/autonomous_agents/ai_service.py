import google.generativeai as genai
import os
from loguru import logger
import time

class AIService:
    def __init__(self):
        # 1. Je API Sleutels
        self.api_keys = [
            "AIzaSyDgayrzXgtdhNgQd_enucOrVPcg0pXchs8",
            "AIzaSyBQXtSC3mopsBJJgvRQI81hQRy877eklGo",
            "AIzaSyDz2NaBIhS_d30efumafNjclnS8xcnTG4I"
        ]
        self.current_key_index = 0
        
        # 2. JOUW SPECIFIEKE MODELLEN (Uit je curl lijst)
        # We zetten 'Lite' bovenaan voor snelheid en stabiliteit.
        self.model_candidates = [
            "models/gemini-2.0-flash-lite",      # De favoriet (Snel & Stabiel)
            "models/gemini-2.0-flash",           # De back-up
            "models/gemini-flash-latest",        # De algemene alias
            "models/gemini-2.5-flash"            # De nieuwste krachtpatser
        ]
        
        self.active_model_name = None
        self.model = None
        self.online = False
        
        self._initialize_connection()

    def _initialize_connection(self):
        """Probeert verbinding te maken met de sleutels en modellen."""
        current_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=current_key)
        
        # Test welk model werkt
        for model_name in self.model_candidates:
            try:
                # We maken het object aan (geen netwerk call nog)
                self.model = genai.GenerativeModel(model_name)
                self.active_model_name = model_name
                self.online = True
                
                # Maskeer key voor logs
                masked_key = f"...{current_key[-4:]}"
                logger.info(f"🧠 AI Verbonden | Model: {model_name} | Key: {masked_key}")
                return
            except Exception:
                continue
        
        logger.warning("⚠️ Kon geen model initialiseren. Check internet/keys.")

    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"🔄 Quota op? Roteren naar API Key #{self.current_key_index + 1}...")
        self._initialize_connection()

    async def generate_text(self, prompt):
        if not self.online: self._initialize_connection()
        if not self.online: return ""

        for attempt in range(len(self.api_keys) * 2): # Probeer keys en modellen
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.replace("```json", "").replace("```python", "").replace("```", "").strip()
                return "" # Leeg antwoord
                
            except Exception as e:
                error_msg = str(e)
                
                # 404 = Model naam fout -> Volgend model in de lijst proberen
                if "404" in error_msg or "not found" in error_msg:
                    logger.warning(f"⚠️ Model {self.active_model_name} niet gevonden. Schakelen...")
                    # Pak index van huidig model
                    try:
                        current_idx = self.model_candidates.index(self.active_model_name)
                        next_idx = (current_idx + 1) % len(self.model_candidates)
                        self.active_model_name = self.model_candidates[next_idx]
                        self.model = genai.GenerativeModel(self.active_model_name)
                        logger.info(f"👉 Nieuw model geselecteerd: {self.active_model_name}")
                        continue
                    except:
                        pass

                # 429 = Quota op -> Nieuwe sleutel
                if "429" in error_msg or "Quota" in error_msg:
                    self._rotate_key()
                    continue
                
                logger.error(f"❌ Gemini Error: {e}")
                return ""
        return ""

import google.generativeai as genai
import os
from loguru import logger
from dotenv import load_dotenv
import backoff

# Laad de geheime kluis
load_dotenv()

class AIService:
    def __init__(self):
        # Haal sleutels uit de omgeving (.env)
        self.api_keys = [
            os.getenv("GEMINI_KEY_1"),
            os.getenv("GEMINI_KEY_2"),
            os.getenv("GEMINI_KEY_3")
        ]
        # Filter lege sleutels eruit (als je er maar 2 hebt ingevuld)
        self.api_keys = [k for k in self.api_keys if k]

        if not self.api_keys:
            logger.critical("❌ GEEN API KEYS GEVONDEN! Check je .env bestand.")
        
        self.current_key_index = 0
        
        # MODEL CONFIGURATIE (Jouw lijst)
        self.model_candidates = [
            "models/gemini-2.0-flash-lite",
            "models/gemini-2.0-flash",
            "models/gemini-flash-latest",
            "models/gemini-1.5-flash"
        ]
        
        self.active_model_name = None
        self.model = None
        self.online = False
        
        self._initialize_connection()

    def _initialize_connection(self):
        if not self.api_keys: return

        current_key = self.api_keys[self.current_key_index]
        try:
            genai.configure(api_key=current_key)
            
            # Test modellen
            for model_name in self.model_candidates:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.active_model_name = model_name
                    self.online = True
                    masked_key = f"...{current_key[-4:]}"
                    logger.info(f"🧠 AI Verbonden | Model: {model_name} | Key: {masked_key}")
                    return
                except Exception:
                    continue
        except Exception as e:
             logger.error(f"Configuratie fout: {e}")
        
        logger.warning("⚠️ Kon geen model initialiseren.")

    def _rotate_key(self):
        if not self.api_keys: return
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"🔄 Roteren naar API Key #{self.current_key_index + 1}...")
        self._initialize_connection()

    @backoff.on_exception(backoff.expo,
                          (Exception,),  # Catch all exceptions (of specifiekere, zoals 'google.api_core.exceptions.ResourceExhausted')
                          max_tries=3,  # Maximaal aantal pogingen
                          on_backoff=lambda details: logger.warning(f"🔄  Retry in {details['wait']:0.1f}s, poging {details['tries']} van 3..."))  # Loggen van retries
    async def generate_text(self, prompt):
        if not self.online:
            self._initialize_connection()
        if not self.online:
            return ""

        try:
            response = await self.model.generate_content_async(prompt)
            if response.text:
                return response.text.replace("", "").replace("", "").replace("", "").replace("", "").strip()
            return ""

        except Exception as e:
            error_msg = str(e)
            # 403 = LEAKED KEY (Direct roteren)
            if "403" in error_msg:  # Checken op 403 error
                self._rotate_key()  # Roteren naar de volgende key
                raise  # Her-raise de exception om de retry te activeren (belangrijk!)

            raise  # Her-raise andere exceptions om de retry te activeren
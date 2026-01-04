import google.generativeai as genai
import os
from loguru import logger
from dotenv import load_dotenv

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

    async def generate_text(self, prompt):
        if not self.online: self._initialize_connection()
        if not self.online: return ""

        # Probeer max 2x per sleutel om loops te voorkomen
        max_attempts = len(self.api_keys) * 2
        
        for attempt in range(max_attempts):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text.replace("```json", "").replace("```python", "").replace("```html", "").replace("```", "").strip()
                return "" 
                
            except Exception as e:
                error_msg = str(e)
                
                # 403 = LEAKED KEY (Direct roteren en hopen dat de volgende werkt)
                if "403" in error_msg or "leaked" in error_msg:
                    logger.error("🚫 Deze sleutel is geblokkeerd/gelekt! Roteren...")
                    self._rotate_key()
                    continue

                # 429 = QUOTA OP
                if "429" in error_msg or "Quota" in error_msg:
                    self._rotate_key()
                    continue
                
                # 404 = MODEL NIET GEVONDEN
                if "404" in error_msg or "not found" in error_msg:
                    # Probeer volgend model in de lijst
                    try:
                        curr_idx = self.model_candidates.index(self.active_model_name)
                        next_idx = (curr_idx + 1) % len(self.model_candidates)
                        self.active_model_name = self.model_candidates[next_idx]
                        self.model = genai.GenerativeModel(self.active_model_name)
                        logger.info(f"👉 Schakelen naar model: {self.active_model_name}")
                        continue
                    except: pass

                logger.error(f"❌ Gemini Error: {e}")
                return ""
        return ""

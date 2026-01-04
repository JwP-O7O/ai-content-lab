import requests
import os
import time
from loguru import logger

class VisionaryAgent:
    def __init__(self):
        self.name = "VisionaryAgent"
        self.output_dir = "data/images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_image(self, prompt, filename_hint="image"):
        """Genereert een afbeelding via Pollinations AI"""
        logger.info(f"[{self.name}] 🎨 Schilderen: '{prompt}'")
        
        # Maak prompt URL-veilig
        safe_prompt = prompt.replace(" ", "%20")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Bestandsnaam genereren
                timestamp = int(time.time())
                clean_hint = "".join([c for c in filename_hint if c.isalnum() or c=='_'])[:15]
                filename = f"{clean_hint}_{timestamp}.jpg"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                    
                logger.success(f"🖼️ Afbeelding opgeslagen: {filepath}")
                return {"status": "success", "file": filepath, "url": url}
            else:
                logger.error(f"Fout bij downloaden: {response.status_code}")
                return {"status": "error"}
        except Exception as e:
            logger.error(f"Visionary error: {e}")
            return {"status": "error"}

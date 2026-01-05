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
        self.max_retries = 3
        self.retry_delay = 1  # in seconds

    def generate_image(self, prompt, filename_hint="image"):
        """Genereert een afbeelding via Pollinations AI"""
        logger.info(f"[{self.name}] 🎨 Schilderen: '{prompt}'")
        
        # Maak prompt URL-veilig
        safe_prompt = prompt.replace(" ", "%20")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, stream=True)  # Gebruik stream=True om de download efficienter te maken
                if response.status_code == 200:
                    # Bestandsnaam genereren
                    timestamp = int(time.time())
                    clean_hint = "".join([c for c in filename_hint if c.isalnum() or c=='_'])[:15]
                    filename = f"{clean_hint}_{timestamp}.jpg"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):  # Chunk downloaden voor efficientie
                            f.write(chunk)
                    
                    logger.success(f"🖼️ Afbeelding opgeslagen: {filepath}")
                    return {"status": "success", "file": filepath, "url": url}
                else:
                    logger.warning(f"Fout bij downloaden (poging {attempt + 1}/{self.max_retries + 1}): {response.status_code}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)  # Wacht voor het opnieuw proberen
                    else:
                        logger.error(f"Alle pogingen mislukt.")
                        return {"status": "error", "error": f"Download mislukt met status code: {response.status_code}"}
            except requests.exceptions.RequestException as e:
                logger.error(f"Visionary download error (poging {attempt + 1}/{self.max_retries + 1}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return {"status": "error", "error": f"Request error: {e}"}
            except Exception as e:
                logger.error(f"Visionary error (poging {attempt + 1}/{self.max_retries + 1}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return {"status": "error", "error": f"Algemene error: {e}"}
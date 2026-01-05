import requests
import os
import time
from loguru import logger
import urllib.parse
from requests.exceptions import RequestException, HTTPError
from tenacity import retry, stop_after_attempt, wait_exponential

class VisionaryAgent:
    def __init__(self):
        self.name = "VisionaryAgent"
        self.output_dir = "data/images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_image(self, prompt, filename_hint="image"):
        logger.info(f"[{self.name}] 🎨 Schilderen: '{prompt}'")
        safe_prompt = urllib.parse.quote_plus(prompt)
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"

        try:
            logger.debug(f"[{self.name}] GET-verzoek: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            timestamp = int(time.time())
            clean_hint = "".join([c for c in filename_hint if c.isalnum() or c=='_'])[:15]
            filename = f"{clean_hint}_{timestamp}.jpg"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.success(f"🖼️ Afbeelding opgeslagen: {filepath}")
            return {"status": "success", "file": filepath, "url": url}

        except HTTPError as e:
            logger.error(f"[{self.name}] HTTP Fout: Status code: {response.status_code} - {e}. Response text: {response.text}")
            raise
        except RequestException as e:
            logger.error(f"[{self.name}] Netwerkfout: {e}")
            raise
        except (IOError, OSError) as e:
            logger.error(f"[{self.name}] Fout bij het opslaan van de afbeelding: {e}")
            return {"status": "error"}
        except Exception as e:
            logger.exception(f"[{self.name}] Onverwachte fout: {e}")
            return {"status": "error"}

if __name__ == '__main__':
    logger.add("visionary_agent.log", rotation="10 MB")
    agent = VisionaryAgent()
    try:
        result = agent.generate_image("A cat in space", "cat_space")
        print(result)
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")
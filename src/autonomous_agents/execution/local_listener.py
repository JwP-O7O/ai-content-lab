import os
import json
from loguru import logger

class LocalListener:
    def __init__(self):
        self.name = "LocalListener"
        self.command_file = "data/local_commands.json"

    async def check_for_orders(self):
        """Kijkt of er berichten zijn uit de Chat Interface"""
        if not os.path.exists(self.command_file):
            return {"status": "no_tasks"}

        try:
            with open(self.command_file, 'r') as f:
                content = f.read().strip()
                
            if not content: return {"status": "no_tasks"}

            data = json.loads(content)
            
            # Wis het bestand direct zodat we het niet dubbel uitvoeren
            open(self.command_file, 'w').close()

            logger.info(f"[{self.name}] 📨 DIRECT BERICHT ONTVANGEN: {data['command']}")
            
            return {
                "status": "new_tasks",
                "tasks": [{
                    "title": data['command'], # De chat tekst is de titel
                    "body": "Direct command from Admin Interface",
                    "source": "chat"
                }]
            }

        except Exception as e:
            # logger.error(f"Local Listener Error: {e}")
            return {"status": "no_tasks"}

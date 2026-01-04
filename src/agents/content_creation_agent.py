import json
from typing import Dict, List
from src.agents.base_agent import BaseAgent
from src.database.connection import get_db
from src.database.models import ContentFormat, ContentPlan
from src.utils.llm_client import llm_client
from config.config import settings

class ContentCreationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContentCreationAgent")
        self.llm_client = llm_client
        self.personality = settings.content_personality

    async def execute(self, *args, **kwargs) -> Dict:
        self.log_info("Executing ContentCreationAgent (Mock)")
        return {"content_created": 1, "tweets": 1}

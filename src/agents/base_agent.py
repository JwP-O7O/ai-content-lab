import time
from abc import ABC, abstractmethod
from typing import Any, Optional
from loguru import logger
from src.database.connection import get_db
from src.database.models import AgentLog

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        logger.info(f"{self.name} initialized")

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        pass

    async def run(self, *args, **kwargs) -> Any:
        action = kwargs.get("action", "execute")
        logger.info(f"{self.name} starting: {action}")
        try:
            result = await self.execute(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            raise # Re-raise for now

    def log_info(self, message: str):
        logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        logger.error(f"[{self.name}] {message}")
        
    def _log_activity(self, **kwargs):
        pass # Stub

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from loguru import logger

# Probeer database te importeren, maar crash niet als het nog niet bestaat
try:
    from src.database.connection import get_db
    from sqlalchemy import text

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger.warning("Database connection modules not found. Running in headless mode.")


class BaseAutonomousAgent(ABC):
    """
    Base class voor alle autonomous improvement agents.
    Zorgt voor de standaard structuur: Analyze -> Plan -> Execute -> Validate.
    """

    def __init__(self, name: str, layer: str, interval_seconds: int = 3600):
        self.name = name
        self.layer = layer
        self.interval_seconds = interval_seconds
        self.running = False
        self.metrics = {}

    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """Analyze current state."""
        pass

    @abstractmethod
    async def plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create improvement plans."""
        pass

    @abstractmethod
    async def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute improvement plan."""
        pass

    async def validate(self, result: Dict[str, Any]) -> bool:
        """Validate result."""
        return result.get("status") == "success"

    async def run_cycle(self):
        """Voert één verbetercyclus uit."""
        # Dit wordt nu voornamelijk door de MasterOrchestrator aangeroepen
        pass

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def _log_activity(self, action: str, status: str, details: Dict[str, Any]):
        """Log activiteit naar database of console."""
        if DB_AVAILABLE:
            try:
                with get_db() as db:
                    # Gebruik raw SQL om dependency op specifieke models te vermijden
                    db.execute(
                        text("""
                            INSERT INTO autonomous_agent_logs 
                            (agent_name, layer, action, status, details, metrics)
                            VALUES (:name, :layer, :action, :status, :details, :metrics)
                        """),
                        {
                            "name": self.name,
                            "layer": self.layer,
                            "action": action,
                            "status": status,
                            "details": str(details),  # Simpele JSON serialisatie
                            "metrics": str(self.metrics),
                        },
                    )
                    db.commit()
            except Exception as e:
                # Fallback naar logger als DB faalt
                logger.error(f"Failed to log to DB: {e}")

        # Altijd ook naar console loggen
        log_msg = f"[{self.name}] {action}: {status}"
        if status == "success":
            logger.info(log_msg)
        elif status == "failed":
            logger.error(log_msg)
        else:
            logger.debug(log_msg)

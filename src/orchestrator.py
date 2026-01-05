import asyncio
from datetime import datetime, timezone
from loguru import logger

# Import all agents (will succeed now because of stubs)
from src.agents.market_scanner_agent import MarketScannerAgent
try:
    from src.agents.analysis_agent import AnalysisAgent
    ANALYSIS_AGENT_AVAILABLE = True
except ImportError:
    AnalysisAgent = None
    ANALYSIS_AGENT_AVAILABLE = False
from src.agents.content_creation_agent import ContentCreationAgent
from src.agents.content_strategist_agent import ContentStrategistAgent
from src.agents.publishing_agent import PublishingAgent
# ... imports voor andere phases ...

class AgentOrchestrator:
    def __init__(self):
        logger.info("Initializing Agent Orchestrator...")
        self.market_scanner_task = asyncio.create_task(self._initialize_market_scanner())
        self.content_creator_task = asyncio.create_task(self._initialize_content_creator())
        # Initialize minimal set for testing
        logger.info("Orchestrator initialization started (agents initializing in background)")

    async def _initialize_market_scanner(self):
        logger.info("Initializing MarketScannerAgent...")
        try:
            self.market_scanner = MarketScannerAgent("MarketScanner")
            logger.info("MarketScannerAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MarketScannerAgent: {e}")
            self.market_scanner = None  # or handle the error appropriately

    async def _initialize_content_creator(self):
        logger.info("Initializing ContentCreationAgent...")
        try:
            self.content_creator = ContentCreationAgent()
            logger.info("ContentCreationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ContentCreationAgent: {e}")
            self.content_creator = None  # or handle the error appropriately

    async def run_full_pipeline(self) -> dict:
        logger.info("Starting full pipeline...")
        # Wacht op initialisatie van alle agents
        try:
            await asyncio.gather(self.market_scanner_task, self.content_creator_task)
            logger.info("All agents initialized. Continuing with pipeline.")
        except Exception as e:
            logger.error(f"Error during agent initialization: {e}")
            return {"status": "error", "message": f"Agent initialization failed: {e}", "agents": {}}

        # Controleer of agents succesvol zijn geïnitialiseerd voordat de pipeline start.
        if self.market_scanner is None or self.content_creator is None:
            logger.error("One or more agents failed to initialize. Pipeline cannot continue.")
            return {"status": "error", "message": "One or more agents failed to initialize.", "agents": {}}


        # Hier komt de rest van de pipeline logica
        return {"status": "success", "agents": {
            "market_scanner": "initialized",
            "content_creator": "initialized",
        }}
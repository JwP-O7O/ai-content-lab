import asyncio
from loguru import logger

# Import all agents (will succeed now because of stubs)
from src.agents.market_scanner_agent import MarketScannerAgent
from src.agents.content_creation_agent import ContentCreationAgent
# ... imports voor andere phases ...

ANALYSIS_AGENT_AVAILABLE = False
AnalysisAgent = None

try:
    from src.agents.analysis_agent import AnalysisAgent

    ANALYSIS_AGENT_AVAILABLE = True
except ImportError:
    logger.warning("AnalysisAgent not available, skipping initialization.")
    pass


class AgentOrchestrator:
    def __init__(self):
        logger.info("Initializing Agent Orchestrator...")
        self.agents = {}  # Store initialized agents
        self.agent_initialization_tasks = []  # Store async tasks

        # Initialize minimal set for testing
        self.agent_initialization_tasks.append(self._initialize_market_scanner())
        self.agent_initialization_tasks.append(self._initialize_content_creator())

        if ANALYSIS_AGENT_AVAILABLE:
            self.agent_initialization_tasks.append(self._initialize_analysis_agent())

        logger.info(
            "Orchestrator initialization started (agents initializing in background)"
        )

    async def _initialize_market_scanner(self):
        logger.info("Initializing MarketScannerAgent...")
        try:
            self.agents["market_scanner"] = MarketScannerAgent("MarketScanner")
            logger.info("MarketScannerAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MarketScannerAgent: {e}")
            self.agents["market_scanner"] = None
        return True  # Return True to indicate successful initialization

    async def _initialize_content_creator(self):
        logger.info("Initializing ContentCreationAgent...")
        try:
            self.agents["content_creator"] = ContentCreationAgent()
            logger.info("ContentCreationAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ContentCreationAgent: {e}")
            self.agents["content_creator"] = None
        return True  # Return True to indicate successful initialization

    async def _initialize_analysis_agent(self):
        logger.info("Initializing AnalysisAgent...")
        try:
            self.agents["analysis_agent"] = AnalysisAgent()
            logger.info("AnalysisAgent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AnalysisAgent: {e}")
            self.agents["analysis_agent"] = None
        return True  # Return True to indicate successful initialization

    async def run_full_pipeline(self) -> dict:
        logger.info("Starting full pipeline...")
        # Wait for all agent initializations to complete
        try:
            await asyncio.gather(*self.agent_initialization_tasks)
            logger.info("All agents initialized. Continuing with pipeline.")
        except Exception as e:
            logger.error(f"Error during agent initialization: {e}")
            return {
                "status": "error",
                "message": f"Agent initialization failed: {e}",
                "agents": {},
            }

        # Check if all required agents initialized correctly
        if (
            self.agents.get("market_scanner") is None
            or self.agents.get("content_creator") is None
        ):
            logger.error(
                "One or more required agents failed to initialize. Pipeline cannot continue."
            )
            return {
                "status": "error",
                "message": "One or more required agents failed to initialize.",
                "agents": {},
            }

        # Pipeline logic, using self.agents dictionary to access initialized agents.
        pipeline_result = {}
        pipeline_result["status"] = "success"
        pipeline_result["agents"] = {}
        for agent_name in self.agents:
            if self.agents[agent_name]:
                pipeline_result["agents"][agent_name] = "initialized"
            else:
                pipeline_result["agents"][agent_name] = "failed"
        return pipeline_result

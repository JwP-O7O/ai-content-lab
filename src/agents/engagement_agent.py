import logging
import time # Import the time module
from contextlib import contextmanager # Import the contextmanager

from .base_agent import BaseAgent

# Configure logging (optional, but good practice)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  # Get a logger for this module


@contextmanager
def execution_timer(agent_name: str):
    """
    Context manager to measure and log the execution time of a method.
    """
    start_time = time.time()
    try:
        yield
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"Error during {agent_name} execution: {e} - Execution time: {execution_time:.2f} seconds", exc_info=True)
        raise # Re-raise the exception to propagate it
    else:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{agent_name} finished successfully - Execution time: {execution_time:.2f} seconds")


class EngagementAgent(BaseAgent):
    async def execute(self):
        logger.info("EngagementAgent started executing.") # Log when the agent starts
        result = {} # Initialize result outside the try block.

        try:
            with execution_timer("EngagementAgent"):  # Use the context manager
                # Placeholder for actual engagement logic. Replace this with your engagement code
                # In this basic example, this stays empty.
                # Simulate some work - Removed async call, keeping the placeholder for future implementation
                pass # Replace this with your agent logic
        except Exception as e:
            # Error handling is now done within the context manager
            result = {} # Return an empty dict if it fails.  Consistent return value.

        finally:
            # Removed the logging of the finish time, as it's handled within the context manager
            return result
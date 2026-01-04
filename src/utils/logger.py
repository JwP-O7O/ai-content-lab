import sys
from loguru import logger
from config.config import settings

def setup_logger():
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level)
    logger.info("Logger initialized")

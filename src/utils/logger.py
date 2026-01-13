import sys
from loguru import logger
from config.config import settings
import os


def setup_logger():
    try:
        logger.remove()  # Verwijder alle bestaande handlers

        # Log naar stdout (console)
        logger.add(
            sys.stdout,
            level=settings.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

        # Log naar bestand
        log_directory = settings.log_directory  # Directory voor de logs
        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
            except OSError as e:
                logger.error(f"Fout bij het aanmaken van de log directory: {e}")
                return  # Stop als we de directory niet kunnen aanmaken.

        log_file_path = os.path.join(
            log_directory, settings.log_file_name
        )  # Volledige pad naar het logbestand
        logger.add(
            log_file_path,
            level=settings.log_level,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )  # Pas de format string aan naar wens.
        logger.info(
            f"Logger initialized.  Logging to console and file: {log_file_path}"
        )  # Verbeterde info message

    except Exception as e:
        logger.error(f"Fout bij het initialiseren van de logger: {e}")

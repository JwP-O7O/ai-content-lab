import asyncio
import os
import sys
import sqlite3
from loguru import logger

# Pad toevoegen zodat imports werken
sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def run_web_integration_test():
    logger.info("🧪 START WEB INTEGRATION TEST: FRONTEND SQUAD")
    
    # 1. Schoonmaak (Verwijder eventuele oude testbestanden)
    test_file_name_expected = "matrix_digital_rain_animation.html" # Still used for logs
    test_file_path_expected = os.path.join("apps", test_file_name_expected)
    if os.path.exists(test_file_path_expected):
        os.remove(test_file_path_expected)
        logger.info(f"🧹 Oude testbestand {test_file_path_expected} verwijderd.")

    # 2. Injecteer Taak
    logger.info("💉 Injecting Web Test Task...")
    instruction = "WEB: Maak een interactieve Matrix Digital Rain animatie in een single HTML bestand, volledig responsive, met Neon accenten en Dark Mode."
    try:
        with get_db() as cursor:
            cursor.execute("""
                INSERT INTO tasks (title, description, source, status)
                VALUES (?, ?, ?, 'pending')
            """, (instruction, "Web Integration Test", "test_script"))
            task_id = cursor.lastrowid
            logger.info(f"✅ Web Taak geïnjecteerd met ID: {task_id}")
    except Exception as e:
        logger.critical(f"❌ Database error: {e}")
        return

    # 3. Start Orchestrator (Single Cycle)
    orchestrator = TermuxMasterOrchestrator()
    
    logger.info("🤖 Running Orchestrator Cycle for Web Task...")
    # The run_cycle now returns the squad's result for the processed task
    squad_result = await orchestrator.run_cycle() 

    # 4. Verificatie
    logger.info("🔍 Verifying Web Integration Test Results...")
    
    # Haal de werkelijke bestandsnaam op uit het resultaat van de squad
    actual_file_path = None
    if squad_result and isinstance(squad_result, dict) and squad_result.get("status") == "success":
        actual_file_path = squad_result.get("file")
    
    if not actual_file_path:
        logger.error("❌ Kon de daadwerkelijke bestandsnaam niet ophalen uit het resultaat van de squad.")
        actual_file_path = "UNKNOWN_FILE" # Voor duidelijke logboekdoeleinden

    # Check 1: File Exists
    if os.path.exists(actual_file_path):
        logger.success(f"✅ Web applicatie {os.path.basename(actual_file_path)} is aangemaakt in {actual_file_path}.")
        with open(actual_file_path, 'r') as f:
            content = f.read()
            logger.info(f"📜 Inhoud preview:\n{content[:500]}...")
            if "<!DOCTYPE html>" in content and "<style>" in content and "<script>" in content:
                logger.success("✅ Basis HTML, CSS en JS structuur gedetecteerd.")
            else:
                logger.warning("⚠️ Basis HTML, CSS of JS structuur niet volledig gedetecteerd.")
    else:
        logger.error(f"❌ Web applicatie NIET gevonden op {actual_file_path}!")

    # Check 2: Memory Updated (from PROJECT_MEMORY.md)
    with open("PROJECT_MEMORY.md", "r") as f:
        memory = f.read()
        if "Matrix Digital Rain" in memory:
            logger.success("✅ Geheugen (PROJECT_MEMORY.md) is bijgewerkt met de Web Task.")
        else:
            logger.warning("⚠️ Geheugen update voor Web Task niet gevonden in MD file.")

    logger.info("🏁 WEB INTEGRATION TEST COMPLETED")
    logger.info(f"\n--- HANDMATIGE VERIFICATIE VEREIST ---")
    if actual_file_path and os.path.exists(actual_file_path):
        logger.info(f"Open het bestand: {os.path.abspath(actual_file_path)} in je browser om de Matrix Digital Rain animatie te bekijken.")
    else:
        logger.info("Kan het bestand niet openen voor handmatige verificatie; bestand niet gevonden.")
    logger.info(f"------------------------------------")


if __name__ == "__main__":
    asyncio.run(run_web_integration_test())
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
    test_file_name = "matrix_digital_rain_animation.html"
    test_file_path = os.path.join("apps", test_file_name)
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        logger.info(f"🧹 Oude testbestand {test_file_path} verwijderd.")

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
    await orchestrator.run_cycle()
    
    # 4. Verificatie
    logger.info("🔍 Verifying Web Integration Test Results...")
    
    # Check 1: File Exists
    if os.path.exists(test_file_path):
        logger.success(f"✅ Web applicatie {test_file_name} is aangemaakt in {test_file_path}.")
        with open(test_file_path, 'r') as f:
            content = f.read()
            logger.info(f"📜 Inhoud preview:\n{content[:500]}...")
            if "<!DOCTYPE html>" in content and "<style>" in content and "<script>" in content:
                logger.success("✅ Basis HTML, CSS en JS structuur gedetecteerd.")
            else:
                logger.warning("⚠️ Basis HTML, CSS of JS structuur niet volledig gedetecteerd.")
    else:
        logger.error(f"❌ Web applicatie {test_file_name} NIET gevonden in {test_file_path}!")

    # Check 2: Memory Updated
    with open("PROJECT_MEMORY.md", "r") as f:
        memory = f.read()
        if "Matrix Digital Rain" in memory:
            logger.success("✅ Geheugen (PROJECT_MEMORY.md) is bijgewerkt met de Web Task.")
        else:
            logger.warning("⚠️ Geheugen update voor Web Task niet gevonden in MD file.")

    logger.info("🏁 WEB INTEGRATION TEST COMPLETED")
    logger.info(f"\n--- HANDMATIGE VERIFICATIE VEREIST ---")
    logger.info(f"Open het bestand: {os.path.abspath(test_file_path)} in je browser om de Matrix Digital Rain animatie te bekijken.")
    logger.info(f"------------------------------------")


if __name__ == "__main__":
    asyncio.run(run_web_integration_test())

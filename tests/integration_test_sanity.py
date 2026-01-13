import asyncio
import os
import sys
import sqlite3
from loguru import logger

# Pad toevoegen zodat imports werken
sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def run_integration_test():
    logger.info("🧪 START INTEGRATION TEST: SELF-HEALING & MEMORY")
    
    # 1. Schoonmaak (Verwijder eventuele oude testbestanden)
    test_file = "src/playground/sanity_calc.py"
    if os.path.exists(test_file):
        os.remove(test_file)
        logger.info("🧹 Oude testbestand verwijderd.")

    # 2. Injecteer Taak
    logger.info("💉 Injecting Test Task...")
    try:
        with get_db() as cursor:
            cursor.execute("""
                INSERT INTO tasks (title, description, source, status)
                VALUES (?, ?, ?, 'pending')
            """, ("SYSTEM: Maak een calculator script (sanity_calc.py) met error handling voor delen door nul.", "Integration Test", "test_script"))
            task_id = cursor.lastrowid
            logger.info(f"✅ Taak geïnjecteerd met ID: {task_id}")
    except Exception as e:
        logger.critical(f"❌ Database error: {e}")
        return

    # 3. Start Orchestrator (Single Cycle)
    orchestrator = TermuxMasterOrchestrator()
    
    logger.info("🤖 Running Orchestrator Cycle...")
    await orchestrator.run_cycle()
    
    # 4. Verificatie
    logger.info("🔍 Verifying Results...")
    
    # Check 1: File Exists
    if os.path.exists(test_file):
        logger.success(f"✅ Bestand {test_file} is aangemaakt.")
        with open(test_file, 'r') as f:
            content = f.read()
            logger.info(f"📜 Inhoud preview:\n{content[:200]}...")
            if "try" in content and "except" in content:
                logger.success("✅ Error handling (try/except) gedetecteerd.")
            else:
                logger.warning("⚠️ Geen expliciete try/except gevonden (kan okay zijn als de logica anders is).")
    else:
        logger.error(f"❌ Bestand {test_file} NIET gevonden!")

    # Check 2: Memory Updated
    with open("PROJECT_MEMORY.md", "r") as f:
        memory = f.read()
        if "sanity_calc.py" in memory or "calculator" in memory.lower():
            logger.success("✅ Geheugen (PROJECT_MEMORY.md) is bijgewerkt.")
        else:
            logger.warning("⚠️ Geheugen update niet gevonden in MD file.")

    logger.info("🏁 TEST COMPLETED")

if __name__ == "__main__":
    asyncio.run(run_integration_test())

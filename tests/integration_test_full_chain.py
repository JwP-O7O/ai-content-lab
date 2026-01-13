import asyncio
import os
import sys
import sqlite3
from loguru import logger

sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def run_full_chain_test():
    logger.info("🔗 START FULL CHAIN INTEGRATION TEST")
    
    # 1. Clean up
    target_file = "src/playground/string_reverser.py"
    test_file = "tests/test_string_reverser.py"
    for f in [target_file, test_file]:
        if os.path.exists(f):
            os.remove(f)
            logger.info(f"🧹 Removed old file: {f}")

    # 2. Inject Task
    instruction = "SYSTEM: Maak een Python script 'string_reverser.py' met een functie 'reverse_string(text)' en error handling voor niet-strings."
    logger.info(f"💉 Injecting Task: {instruction}")
    
    try:
        with get_db() as cursor:
            cursor.execute("INSERT INTO tasks (title, status) VALUES (?, 'pending')", (instruction,))
            task_id = cursor.lastrowid
    except Exception as e:
        logger.critical(f"DB Error: {e}")
        return

    # 3. Run Orchestrator
    orchestrator = TermuxMasterOrchestrator()
    logger.info("🤖 Running Orchestrator Cycle...")
    result = await orchestrator.run_cycle()

    # 4. Verification
    logger.info("🔍 Verifying Results...")
    
    # Check Code File
    if os.path.exists(target_file):
        logger.success(f"✅ Code generated: {target_file}")
    else:
        logger.error(f"❌ Code generation failed for {target_file}")

    # Check Test File
    if os.path.exists(test_file):
        logger.success(f"✅ Test generated: {test_file}")
    else:
        logger.error(f"❌ Test generation failed for {test_file}")

    # Check Execution Result (The Orchestrator returns the squad result)
    if result and result.get("tests_passed") is True:
        logger.success("✅ UNIT TESTS PASSED according to Orchestrator result!")
    elif result:
        logger.warning(f"⚠️ Unit tests did not pass or weren't run. Result: {result}")
    else:
        logger.error("❌ Orchestrator returned no result.")

    logger.info("🏁 FULL CHAIN TEST COMPLETED")

if __name__ == "__main__":
    asyncio.run(run_full_chain_test())

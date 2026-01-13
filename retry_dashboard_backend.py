import asyncio
import os
import sys
import glob
from loguru import logger

sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def retry_backend():
    logger.info("🔧 RETRYING DASHBOARD BACKEND TASK")
    
    # 1. Clean up messy files using Python
    for file in glob.glob("src/playground/*api*.py") + glob.glob("tests/*api*.py"):
        if "```" in file or "\n" in file:
            try:
                os.remove(file)
                logger.info(f"🧹 Removed corrupt file: {file}")
            except Exception as e:
                logger.error(f"Failed to remove {file}: {e}")

    # 2. Inject Task
    task = {
        "title": "SYSTEM: Maak een FastAPI backend (`src/playground/dashboard_api.py`) met CORS enabled. Endpoints: GET /tasks (alle taken uit DB), GET /metrics (uit lessons_learned.json). Gebruik `sqlite3` voor DB en `json` voor metrics.",
        "desc": "Backend API voor Dashboard (Retry)"
    }
    
    try:
        with get_db() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description, source, status) VALUES (?, ?, 'admin', 'pending')", 
                (task['title'], task['desc'])
            )
            logger.success(f"✅ Taak geïnjecteerd: {task['title'][:50]}...")
    except Exception as e:
        logger.critical(f"❌ Database error: {e}")
        return

    # 3. Start Orchestrator
    orchestrator = TermuxMasterOrchestrator()
    logger.info("🤖 Running Orchestrator...")
    # Draai tot max 3 pogingen (normaal 1 taak = 1 cycle, maar voor zekerheid)
    for i in range(2): 
        await orchestrator.run_cycle()
        await asyncio.sleep(1)

    logger.info("🏁 RETRY COMPLETE")

if __name__ == "__main__":
    asyncio.run(retry_backend())

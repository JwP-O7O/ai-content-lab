import asyncio
import os
import sys
from loguru import logger

sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def start_dashboard_project():
    logger.info("🚀 INITIALIZING PHOENIX COMMAND CENTER PROJECT")
    
    tasks = [
        {
            "title": "SYSTEM: Maak een FastAPI backend (`src/dashboard/api.py`) met CORS enabled. Endpoints: GET /tasks (alle taken uit DB), GET /metrics (uit lessons_learned.json). Gebruik `sqlite3` voor DB en `json` voor metrics.",
            "desc": "Backend API voor Dashboard"
        },
        {
            "title": "WEB: Maak een Dashboard UI (`apps/dashboard.html`) die fetch gebruikt om data van `http://localhost:8000` te halen. Toon Takenlijst, Success Rate (Metric) en Memory Log. Auto-refresh elke 5s. Stijl: Cyberpunk Neon.",
            "desc": "Frontend UI voor Dashboard"
        }
    ]
    
    # 1. Inject Tasks
    try:
        with get_db() as cursor:
            for task in tasks:
                cursor.execute(
                    "INSERT INTO tasks (title, description, source, status) VALUES (?, ?, 'admin', 'pending')", 
                    (task['title'], task['desc'])
                )
                logger.success(f"✅ Taak geïnjecteerd: {task['title'][:50]}...")
    except Exception as e:
        logger.critical(f"❌ Database error: {e}")
        return

    # 2. Start Orchestrator (Run until tasks are done)
    logger.info("🤖 Starting Orchestrator to build the Dashboard...")
    orchestrator = TermuxMasterOrchestrator()
    
    # We draaien 3 cycli om zeker te zijn dat beide taken (en eventuele fixes) worden opgepakt
    for i in range(3):
        logger.info(f"🔄 Orchestrator Cycle {i+1}/3")
        await orchestrator.run_cycle()
        await asyncio.sleep(2)

    logger.info("🏁 PROJECT GENERATION COMPLETE. Controleer `src/dashboard/api.py` en `apps/dashboard.html`.")

if __name__ == "__main__":
    asyncio.run(start_dashboard_project())

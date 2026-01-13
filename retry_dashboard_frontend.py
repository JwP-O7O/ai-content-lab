import asyncio
import os
import sys
from loguru import logger

sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
from src.database.connection import get_db

async def retry_frontend():
    logger.info("🎨 BUILDING DASHBOARD FRONTEND")
    
    # Inject Task
    task = {
        "title": "WEB: Maak een Dashboard UI (`apps/dashboard.html`) die fetch gebruikt om data van `http://localhost:8000/tasks` en `http://localhost:8000/metrics` te halen. Toon Takenlijst in een tabel en Metrics in cards. Auto-refresh elke 5s. Stijl: Cyberpunk Neon.",
        "desc": "Frontend UI voor Dashboard"
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

    # Start Orchestrator
    orchestrator = TermuxMasterOrchestrator()
    logger.info("🤖 Running Orchestrator...")
    await orchestrator.run_cycle() # Frontend tasks usually don't need multiple cycles for self-healing yet

    logger.info("🏁 FRONTEND COMPLETE")

if __name__ == "__main__":
    asyncio.run(retry_frontend())

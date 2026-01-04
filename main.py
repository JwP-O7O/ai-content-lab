# Voeg dit toe aan je main.py imports
import asyncio
from src.autonomous_agents.orchestration.master_orchestrator import MasterOrchestrator

# ... in je menu opties ...
print("21. 🧠 Start Autonomous Improvement System (Loop)")

# ... in je keuze logica ...
elif choice == '21':
    print("\n🚀 Starten Autonomous System... (Druk Ctrl+C om te stoppen)")
    try:
        orchestrator = MasterOrchestrator()
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        print("\n🛑 Systeem gestopt door gebruiker.")

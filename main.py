import asyncio
import sys
import os
from loguru import logger

# Ensure src is in path
sys.path.append(os.getcwd())

try:
    from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
except ImportError as e:
    logger.critical(f"Failed to import TermuxMasterOrchestrator: {e}")
    sys.exit(1)

async def main():
    print("==========================================")
    print("   PHOENIX V17 - OPENCODE-AI AUTOMATION   ")
    print("==========================================")
    print("1. Start Autonomous Improvement System (Loop)")
    print("q. Quit")
    
    choice = input("\nSelect option: ").strip().lower()
    
    if choice == '1':
        print("\n🚀 Starting Autonomous System... (Press Ctrl+C to stop)")
        try:
            orchestrator = TermuxMasterOrchestrator()
            await orchestrator.start()
        except KeyboardInterrupt:
            print("\n🛑 System stopped by user.")
        except Exception as e:
            logger.critical(f"System crashed: {e}")
    elif choice == 'q':
        sys.exit(0)
    else:
        print("Invalid option.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
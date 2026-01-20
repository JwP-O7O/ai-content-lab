import asyncio
import sys
import os
import time
from loguru import logger

# Ensure src is in path
sys.path.append(os.getcwd())

from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator

async def run_test():
    print("🧪 INITIALIZING TEST SEQUENCE...")
    start_time = time.time()
    
    try:
        orchestrator = TermuxMasterOrchestrator()
        
        print("🔄 Cycle 1: Processing injected command...")
        # Cycle 1 should pick up the local_commands.json and execute it
        result = await orchestrator.run_cycle()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Execution Time: {duration:.2f} seconds")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_test())

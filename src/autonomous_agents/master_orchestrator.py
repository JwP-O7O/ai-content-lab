import asyncio
import os
import sys
from loguru import logger
from datetime import datetime

# Importeer de agents
from src.autonomous_agents.monitoring.code_health_monitor import CodeHealthMonitor
from src.autonomous_agents.execution.code_refactorer import CodeRefactorer
from src.autonomous_agents.validation.test_runner import TestRunner

# Pad configuratie
sys.path.append(os.getcwd())


class TermuxMasterOrchestrator:
    def __init__(self):
        self.is_running = False
        self.code_monitor = CodeHealthMonitor()
        self.refactorer = CodeRefactorer()
        self.validator = TestRunner()

    async def run_improvement_cycle(self):
        # 1. Monitoring
        logger.info("📡 Stap 1: Scannen op kwaliteit...")
        health = await self.code_monitor.analyze()

        if health["issues_found"] > 0:
            # 2. Execution
            logger.info("📢 Stap 2: Reparatie starten...")
            fix_report = await self.refactorer.execute_fixes()

            # 3. Validation
            logger.info("🧪 Stap 3: Validatie - Werkt alles nog?")
            test_report = await self.validator.run_all_tests()

            if not test_report["passed"]:
                logger.critical(
                    "🚨 WAARSCHUWING: De automatische fix heeft tests gebroken!"
                )
                # Hier zou in de toekomst een 'rollback' agent komen
            else:
                logger.success("💎 Validatie geslaagd: Code is verbeterd en stabiel.")
        else:
            logger.success("✅ Geen verbeterpunten gevonden in deze cyclus.")

    async def run_autonomous_loop(self):
        self.is_running = True
        logger.info("🧠 Autonomous Improvement System V3 ONLINE (S21 Ultra)")

        while self.is_running:
            try:
                logger.debug(
                    f"🔄 Cyclus gestart: {datetime.now().strftime('%H:%M:%S')}"
                )
                await self.run_improvement_cycle()
                logger.info("💤 Ruststand (30 min)...")
                await asyncio.sleep(1800)
            except Exception as e:
                logger.error(f"❌ Fout: {e}")
                await asyncio.sleep(60)


if __name__ == "__main__":
    orchestrator = TermuxMasterOrchestrator()
    try:
        asyncio.run(orchestrator.run_autonomous_loop())
    except KeyboardInterrupt:
        logger.info("🛑 Systeem gestopt.")

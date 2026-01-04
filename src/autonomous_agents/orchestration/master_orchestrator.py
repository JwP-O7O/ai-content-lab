import asyncio
from loguru import logger

# Zorg voor absolute imports om pad-problemen te voorkomen
try:
    from src.autonomous_agents.monitoring.code_health_monitor import CodeHealthMonitor
    from src.autonomous_agents.execution.code_refactorer import CodeRefactorer
    from src.autonomous_agents.validation.test_runner import TestRunner
except ImportError:
    # Fallback voor relatieve imports als het als module gedraaid wordt
    from ..monitoring.code_health_monitor import CodeHealthMonitor
    from ..execution.code_refactorer import CodeRefactorer
    from ..validation.test_runner import TestRunner


class MasterOrchestrator:
    """
    Coördineert alle autonome agents en zorgt voor zelf-herstel (rollback).
    """

    def __init__(self):
        logger.info("Initializing Master Orchestrator V3 (Self-Healing)")
        self.health_monitor = CodeHealthMonitor()
        self.running = False

    async def run_improvement_cycle(self):
        """Voert één volledige verbetercyclus uit met veiligheidschecks."""
        logger.info("🔄 Cyclus gestart")

        # --- STAP 1: MONITORING ---
        logger.info("📡 Stap 1: Scannen op kwaliteit...")
        analysis = await self.health_monitor.analyze()

        health_score = analysis.get("health_score", 100)
        logger.info(f"   Huidige Health Score: {health_score}/100")

        if health_score < 100:
            logger.info("📢 Stap 2: Reparatie nodig. Start Refactorer...")

            # --- STAP 2: EXECUTION ---
            refactorer = CodeRefactorer()
            fix_result = await refactorer.execute({})

            if fix_result.get("changes_made", False):
                logger.info("🧪 Stap 3: Validatie - Werkt alles nog?")

                # --- STAP 3: VALIDATION ---
                test_runner = TestRunner()
                test_result = await test_runner.execute({})

                if test_result["status"] == "failed":
                    logger.critical(
                        "🚨 WAARSCHUWING: De automatische fix heeft tests gebroken!"
                    )
                    logger.error(
                        f"   Foutmelding: {test_result.get('summary', 'Unknown')}"
                    )

                    # --- STAP 4: SELF-HEALING (ROLLBACK) ---
                    refactorer.rollback()
                    logger.info("✅ Systeem hersteld naar vorige veilige staat.")

                elif test_result["status"] == "warning":
                    logger.warning(
                        "⚠️ Geen tests gevonden, maar code is wel aangepast. Handmatige controle aanbevolen."
                    )

                else:
                    logger.success("✅ Fixes succesvol toegepast en gevalideerd!")
            else:
                logger.info("   Geen wijzigingen aangebracht door refactorer.")
        else:
            logger.success("✨ Systeem is gezond. Geen actie nodig.")

    async def start(self):
        self.running = True
        logger.info("🧠 Autonomous System ONLINE")

        while self.running:
            try:
                await self.run_improvement_cycle()
            except Exception as e:
                logger.error(f"Fout in hoofdlus: {e}")

            logger.info("💤 Ruststand (30 min)...")
            await asyncio.sleep(1800)

    def stop(self):
        self.running = False
        logger.info("🛑 Stopping autonomous system")


async def main():
    orchestrator = MasterOrchestrator()
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())

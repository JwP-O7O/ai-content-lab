import pytest
import sys
import os

# Zorg dat src gevonden kan worden
sys.path.append(os.getcwd())

def test_agent_registry_exists():
    """Check of de mappenstructuur klopt voor V8."""
    assert os.path.exists("src/autonomous_agents"), "Agents map mist"
    assert os.path.exists("src/autonomous_agents/execution"), "Execution map mist"
    assert os.path.exists("src/autonomous_agents/monitoring"), "Monitoring map mist"

def test_load_orchestrator():
    """Test of de V8 Master Orchestrator correct kan worden geïmporteerd."""
    try:
        # We importeren nu de juiste class van de juiste plek
        from src.autonomous_agents.master_orchestrator import TermuxMasterOrchestrator
        
        # We proberen hem te instantiëren (dit test gelijk of alle sub-agents laden)
        orchestrator = TermuxMasterOrchestrator()
        assert orchestrator is not None
        assert orchestrator.code_monitor is not None
        assert orchestrator.content_writer is not None
        
    except ImportError as e:
        pytest.fail(f"Import fout: {e}")
    except Exception as e:
        # Dit vangt fouten af zoals missende API keys tijdens init
        pytest.fail(f"Initialisatie fout: {e}")

def test_utils_logger():
    """Test of Loguru (onze logger) werkt."""
    try:
        from loguru import logger
        # Loguru hoeft niet geïnitieerd te worden met argumenten
        logger.debug("Test log bericht vanuit Pytest")
        assert logger is not None
    except Exception as e:
        pytest.fail(f"Logger fout: {e}")

def test_ai_brain_connection():
    """Check of de AI Service module bestaat (Gemini)."""
    try:
        from src.autonomous_agents.ai_service import AIService
        brain = AIService()
        # We checken alleen of het object bestaat, niet of het online is (zodat tests offline werken)
        assert brain is not None
    except ImportError:
        pytest.fail("Kan AI Service niet vinden.")

import os
import sys
import pytest
from pathlib import Path

# Zorg dat src importeerbaar is
sys.path.append(str(Path(__file__).parent.parent))

def test_project_structure():
    """Controleert of de basis mappen bestaan."""
    assert os.path.exists("src"), "SRC map moet bestaan"
    assert os.path.exists("src/autonomous_agents"), "Agents map moet bestaan"

def test_environment_check():
    """Simpele check om te zien of pytest werkt."""
    assert 1 + 1 == 2

def test_import_orchestrator():
    """Probeert de MasterOrchestrator te importeren om syntax fouten te vangen."""
    try:
        from src.autonomous_agents.orchestration.master_orchestrator import MasterOrchestrator
        assert True
    except ImportError as e:
        pytest.fail(f"Kan MasterOrchestrator niet importeren: {e}")
    except Exception as e:
        pytest.fail(f"Fout bij laden MasterOrchestrator: {e}")

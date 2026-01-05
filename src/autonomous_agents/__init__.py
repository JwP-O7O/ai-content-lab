import logging

# Configureer logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from . import module_a
from . import module_b
from . import utils  # Assuming you have a utils module

# Directe import van functies en klassen
try:
    from .module_a import mijn_functie_a
    from .module_b import MijnKlasseB
    from .utils import functie_uit_utils, andere_functie_uit_utils
except ImportError as e:
    logging.error(f"Fout bij het importeren van modules in __init__.py: {e}")
    # Afhankelijk van de vereisten kan verdere foutafhandeling hier nodig zijn,
    # zoals het opnieuw proberen te importeren, het inloggen van een gedetailleerde traceback,
    # of het stoppen van de applicatie.
    mijn_functie_a = None  # Of een placeholder/dummy functie
    MijnKlasseB = None
    functie_uit_utils = None
    andere_functie_uit_utils = None


# __all__ definieert welke namen beschikbaar zijn via 'from my_package import *'
__all__ = ['mijn_functie_a', 'MijnKlasseB', 'functie_uit_utils', 'andere_functie_uit_utils']

# Optioneel: Voorbeeld van het uitvoeren van initialisatie code
# (Deze code wordt uitgevoerd wanneer het pakket wordt geïmporteerd)
logging.info("my_package is geïnitialiseerd.")

# Eventuele andere initialisatie taken die nodig zijn voor het pakket kunnen hier komen.
# Bijvoorbeeld:
# - Configuratie laden
# - Verbindingen met externe services initialiseren
# - Standaard waarden instellen
# - Registratie van plugins

def pak_info():
    """Geeft basis informatie over het pakket"""
    return "Dit is het my_package pakket, versie 1.0"
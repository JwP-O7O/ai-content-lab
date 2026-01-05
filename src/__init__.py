import logging

# Configureer logging. Dit kan worden aangepast aan de behoeften van je project.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#  Deze __init__.py is bedoeld als de basis voor een pakket.
#  Het doel is om modules te importeren en/of variabelen beschikbaar te stellen.
#  Dit vereenvoudigt de import syntax voor de gebruiker.

# Voorbeeld: Stel dat je submodules hebt (niet per se nodig voor een lege init)
# We gaan ervan uit dat we module_a en module_b hebben
from . import module_a
from . import module_b

# Definieer expliciet wat beschikbaar is voor 'from mijn_pakket import *'
__all__ = ['module_a', 'module_b']

# Optioneel: Exporteer specifieke elementen uit de modules
# (Dit is een alternatief voor het exporteren van hele modules)
# from .module_a import functie_x, klasse_y
# from .module_b import functie_z
# __all__ = ['functie_x', 'klasse_y', 'functie_z', 'module_a', 'module_b']  # Update __all__ als je specifieke dingen exporteert

# Voeg eventueel andere initialisatie code toe, zoals configuratie laden.
# Bijvoorbeeld:
try:
    from . import config
    # Configureer iets met behulp van config
    logging.info("Configuratie geladen.")
except ImportError:
    logging.warning("Configuratie module niet gevonden.")
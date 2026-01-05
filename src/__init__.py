import logging

# Configureer logging. Dit kan worden aangepast aan de behoeften van je project.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#  Deze __init__.py is bedoeld als de basis voor een pakket.
#  Het doel is om modules te importeren en/of variabelen beschikbaar te stellen.
#  Dit vereenvoudigt de import syntax voor de gebruiker.

# Voorbeeld: Stel dat je submodules hebt (niet per se nodig voor een lege init)
#  van . import module_a
#  from . import module_b

#  __all__ = ['module_a', 'module_b']  # Optioneel: Definieer expliciet wat beschikbaar is voor 'from mijn_pakket import *'

# Voeg eventueel andere initialisatie code toe, zoals configuratie laden.
# Bijvoorbeeld:
# try:
#     from . import config
#     # Configureer iets met behulp van config
#     logging.info("Configuratie geladen.")
# except ImportError:
#     logging.warning("Configuratie module niet gevonden.")
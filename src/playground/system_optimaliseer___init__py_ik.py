import os
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModuleInitializer:
    """
    Manages the initialization of modules, potentially with lazy loading and thread safety.
    """
    _initialized = False
    _lock = threading.Lock()

    @classmethod
    def initialize(cls):
        """
        Initializes modules in a thread-safe manner, potentially using lazy loading.
        """
        if cls._initialized:
            return

        with cls._lock:
            if not cls._initialized:  # Double-checked locking
                try:
                    # Perform module initialization here. Replace with actual module imports and setup.
                    logging.info("Initializing modules...")
                    import my_module  # Example
                    my_module.setup()
                    logging.info("Modules initialized successfully.")
                    cls._initialized = True
                except ImportError as e:
                    logging.error(f"Failed to import modules: {e}")
                    raise
                except Exception as e:
                    logging.error(f"An unexpected error occurred during initialization: {e}")
                    raise


    @classmethod
    def is_initialized(cls):
        """
        Checks if modules have been initialized.
        """
        return cls._initialized


# Example module (replace with your actual modules)
class MyModule:
    def __init__(self):
        self.data = None

    def setup(self):
        """Perform setup tasks for the module."""
        logging.info("MyModule setup started.")
        self.data = "Initialized data"
        logging.info("MyModule setup finished.")

    def get_data(self):
        return self.data


# __init__.py content
from .module_initializer import ModuleInitializer
from .my_module import MyModule # Assume this exists

ModuleInitializer.initialize() #Initialize modules at import.
import os
import logging
import threading
from typing import List, Callable, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ModuleInitializer:
    """
    Manages the initialization of modules, potentially with lazy loading and thread safety.
    """
    _initialized = False
    _lock = threading.Lock()
    _registered_modules: List[Callable[[], Any]] = []  # Changed from List[str] to List[Callable[[], Any]] - accepts a function that instantiates the module.


    @classmethod
    def register_module(cls, module_initializer: Callable[[], Any]):
        """
        Registers a module initializer function.

        Args:
            module_initializer: A function that initializes and returns a module instance.
        """
        cls._registered_modules.append(module_initializer)

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
                    logging.info("Initializing modules...")
                    for module_initializer in cls._registered_modules:
                        try:
                            module_initializer()  # Calls the function to initialize and set up the module.
                            logging.info(f"Module initialized successfully.")
                        except ImportError as e:
                            logging.error(f"Failed to import module: {e}")
                        except Exception as e:
                            logging.error(f"An unexpected error occurred during module initialization: {e}")

                    logging.info("Modules initialized successfully.")
                    cls._initialized = True
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
from .my_module import MyModule  # Assume this exists


def initialize_my_module():
    """Initializes MyModule and potentially performs setup.  Returns the module instance."""
    my_module_instance = MyModule()
    my_module_instance.setup()  # Call the setup method.
    return my_module_instance


ModuleInitializer.register_module(initialize_my_module)  # Register MyModule with its initializer function
ModuleInitializer.initialize()  # Initialize modules at import.
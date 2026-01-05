import logging
import threading
import time
import functools

class MemoryLoader:
    _instance = None
    _lock = threading.Lock()
    _memory = None
    _memory_loading_lock = threading.Lock()
    _memory_loading_complete = threading.Event()
    _max_retries = 3  # Aantal keer dat we proberen opnieuw te laden
    _retry_delay = 1  # Wachttijd in seconden voor de volgende poging

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _retry(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self._max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1}/{self._max_retries + 1} failed: {e}", exc_info=True)
                    if attempt == self._max_retries:
                        logging.error(f"Memory loading failed after multiple retries.")
                        raise # Herwerp de exception na alle retries
                    time.sleep(self._retry_delay)
            return None # Dit zou niet bereikt moeten worden, maar is voor de volledigheid.
        return wrapper


    @_retry
    def _load_memory_internal(self):
        try:
            logging.info("Starting memory loading...")
            time.sleep(2)  # Simulate loading
            loaded_memory = {"data": "This is the loaded memory."}
            logging.info("Memory loaded successfully.")
            return loaded_memory
        except Exception as e:
            logging.error(f"Error during memory loading: {e}", exc_info=True)
            raise  # Herwerp de exception zodat het retry mechanisme werkt


    def _load_memory_async(self):
        with self._memory_loading_lock:
            if self._memory is not None:
                return
            self._memory = None
            self._memory_loading_complete.clear()

        def load_task():
            try:
                loaded_memory = self._load_memory_internal()
                with self._memory_loading_lock:
                    self._memory = loaded_memory
                    self._memory_loading_complete.set()
            except Exception:
                # Fout is al gelogd in _load_memory_internal via het retry mechanisme.
                pass # geen verdere actie nodig.  Het is al mislukt en geretried.

        threading.Thread(target=load_task, daemon=True).start()


    def load_memory(self):
        self._load_memory_async()
        self._memory_loading_complete.wait()

        with self._memory_loading_lock:
            return self._memory

    def get_memory(self):
        if self._memory is None:
            self.load_memory()
        return self._memory
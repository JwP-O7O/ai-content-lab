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
    _max_retries = 3
    _retry_delay = 1
    _memory_loaded_successfully = False

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
                        raise
                    time.sleep(self._retry_delay)
            return None
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
            raise

    def _load_memory_async(self):
        with self._memory_loading_lock:
            if self._memory_loaded_successfully:
                return

        def load_task():
            try:
                loaded_memory = self._load_memory_internal()
                with self._memory_loading_lock:
                    self._memory = loaded_memory
                    self._memory_loaded_successfully = True
                    self._memory_loading_complete.set()
            except Exception as e:
                logging.error(f"Unhandled exception in loading thread: {e}", exc_info=True)
                with self._memory_loading_lock:
                    self._memory_loading_complete.set()

        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()

    def load_memory(self, timeout=5):
        self._load_memory_async()
        if not self._memory_loading_complete.wait(timeout):
            logging.warning("Memory loading timed out.")
            with self._memory_loading_lock:
                if not self._memory_loaded_successfully:
                     return None
        with self._memory_loading_lock:
            return self._memory

    def get_memory(self):
        with self._memory_loading_lock:
            if self._memory is None and not self._memory_loaded_successfully:
                self.load_memory()
            return self._memory
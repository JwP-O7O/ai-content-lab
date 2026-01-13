import logging
import threading
import time


class MemoryLoader:
    _instance = None
    _lock = threading.Lock()
    _memory = None
    _memory_loading_lock = threading.Lock()
    _memory_loading_complete = threading.Event()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _load_memory_internal(self):
        try:
            logging.info("Starting memory loading...")
            time.sleep(2)  # Simulate loading
            loaded_memory = {"data": "This is the loaded memory."}
            logging.info("Memory loaded successfully.")
            return loaded_memory
        except Exception as e:
            logging.error(f"Error during memory loading: {e}", exc_info=True)
            return None

    def _load_memory_async(self):
        with self._memory_loading_lock:
            if self._memory is not None:
                return
            self._memory = None
            self._memory_loading_complete.clear()

        def load_task():
            loaded_memory = self._load_memory_internal()
            with self._memory_loading_lock:
                self._memory = loaded_memory
                self._memory_loading_complete.set()

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

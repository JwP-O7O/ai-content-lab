import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMClient:
    _instance = None
    _lock = threading.Lock()
    _initialized = False  # Track initialization to avoid redundant calls

    def __init__(self):
        try:
            if LLMClient._initialized:
                raise RuntimeError("LLMClient is a singleton and cannot be initialized more than once.")
            logging.info("Initializing LLM Client...")
            # Simulate LLM client initialization
            self.client = "LLM Client Instance"  # Replace with actual client initialization
            LLMClient._initialized = True
            logging.info("LLM Client initialized.")
        except Exception as e:
            logging.error(f"Error initializing LLMClient: {e}")
            raise  # Re-raise the exception to signal initialization failure


    @staticmethod
    def get_instance():
        if LLMClient._instance is None:
            with LLMClient._lock:
                if LLMClient._instance is None:
                    try:
                        LLMClient._instance = LLMClient()
                    except Exception as e:
                        logging.error(f"Failed to create LLMClient instance: {e}")
                        # Instance creation failed, no need to raise again as init already did
                        return None #Or handle the failure by returning a default, etc.

        return LLMClient._instance


if __name__ == '__main__':
    def worker():
        client = LLMClient.get_instance()
        if client:
            print(f"Client from thread: {client.client}")
        else:
            print("Failed to get LLMClient instance from thread.") # Handle the case where instance creation failed

    threads = []
    for _ in range(5):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify singleton
    client1 = LLMClient.get_instance()
    client2 = LLMClient.get_instance()

    if client1 and client2: # Check if instances were successfully created
        print(f"Are client1 and client2 the same instance? {client1 is client2}")
    else:
        print("Failed to verify singleton due to instance creation failure.")
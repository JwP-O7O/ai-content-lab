import threading

class LLMClient:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Simulate LLM client initialization
        print("Initializing LLM Client...")
        self.client = "LLM Client Instance"  # Replace with actual client initialization
        print("LLM Client initialized.")

    @staticmethod
    def get_instance():
        if LLMClient._instance is None:
            with LLMClient._lock:
                if LLMClient._instance is None:
                    LLMClient._instance = LLMClient()
        return LLMClient._instance


if __name__ == '__main__':
    def worker():
        client = LLMClient.get_instance()
        print(f"Client from thread: {client.client}")

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
    print(f"Are client1 and client2 the same instance? {client1 is client2}")
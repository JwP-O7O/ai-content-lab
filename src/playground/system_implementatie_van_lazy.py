import threading
import time
from typing import Callable, Any, Optional


class BaseAgent:
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Subclasses must implement the execute method")


class LazyAgent(BaseAgent):
    _instance = None
    _lock = threading.Lock()

    def __init__(self, initializer: Callable[[], BaseAgent]):
        self._initializer = initializer
        self._initialized = False
        self._agent: Optional[BaseAgent] = None

    def _initialize(self) -> None:
        with self._lock:
            if not self._initialized:
                self._agent = self._initializer()
                self._initialized = True

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        if not self._initialized:  # Check without locking first
            self._initialize()
        if self._agent:
            return self._agent.execute(*args, **kwargs)
        else:
            raise RuntimeError("Agent not initialized correctly")

    @classmethod
    def get_instance(cls, initializer: Callable[[], BaseAgent]) -> "LazyAgent":
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls(initializer)
        return cls._instance


class AdvancedAgent(BaseAgent):
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        print("Executing advanced functionality...")
        time.sleep(1)
        return "Advanced Result"


def create_advanced_agent() -> BaseAgent:
    return AdvancedAgent()


if __name__ == "__main__":
    lazy_agent = LazyAgent.get_instance(create_advanced_agent)

    def worker(agent: LazyAgent, thread_id: int):
        result = agent.execute()
        print(f"Thread {thread_id}: {result}")

    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(lazy_agent, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    try:
        non_initialized_agent = LazyAgent(create_advanced_agent)
        non_initialized_agent.execute()
    except RuntimeError as e:
        print(f"Caught expected error: {e}")

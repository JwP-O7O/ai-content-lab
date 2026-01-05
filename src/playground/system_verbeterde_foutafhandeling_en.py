import asyncio
import logging
import time
import threading
from contextlib import asynccontextmanager
from typing import Callable, Any, Awaitable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AsyncResource:
    def __init__(self, name: str, init_delay: float = 0.0, fail_init: bool = False):
        self.name = name
        self.initialized = False
        self.init_delay = init_delay
        self.fail_init = fail_init
        self._lock = threading.Lock()
        self._initializer_task = None

    async def _initialize(self):
        if self.initialized:
            return

        with self._lock:
            if self.initialized:
                return
            logging.info(f"[{self.name}] Initializing...")
            await asyncio.sleep(self.init_delay)
            if self.fail_init:
                raise RuntimeError(f"[{self.name}] Initialization failed as requested.")
            self.initialized = True
            logging.info(f"[{self.name}] Initialized.")

    async def __aenter__(self):
        try:
            await self._initialize()
            return self
        except Exception as e:
            logging.exception(f"[{self.name}] Initialization error: {e}")
            raise
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(f"[{self.name}] An error occurred: {exc_val}")
        logging.info(f"[{self.name}] Resource released.")

class SecureFileHandler:
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        try:
            self.file = open(self.filename, self.mode)
            return self.file
        except FileNotFoundError:
            logging.error(f"File not found: {self.filename}")
            raise
        except IOError as e:
            logging.error(f"IOError: {e} while opening {self.filename}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error opening {self.filename}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            try:
                self.file.close()
            except IOError as e:
                logging.error(f"Error closing file {self.filename}: {e}")
            except Exception as e:
                logging.exception(f"Unexpected error closing {self.filename}: {e}")

class AsyncLLMCall:
    def __init__(self, model_name: str, delay: float = 0.5, fail: bool = False):
        self.model_name = model_name
        self.delay = delay
        self.fail = fail

    async def generate_text(self, prompt: str) -> str:
        try:
            logging.info(f"[{self.model_name}] Generating text for prompt: {prompt[:20]}...")
            await asyncio.sleep(self.delay)
            if self.fail:
                raise ValueError(f"[{self.model_name}] Generation failed.")
            response = f"Generated text from {self.model_name} for prompt '{prompt}'"
            logging.info(f"[{self.model_name}] Generated text successfully.")
            return response
        except ValueError as e:
            logging.error(f"[{self.model_name}] Generation error: {e}")
            raise
        except asyncio.CancelledError:
            logging.warning(f"[{self.model_name}] Generation cancelled.")
            raise
        except Exception as e:
            logging.exception(f"[{self.model_name}] Unexpected error during generation: {e}")
            raise

async def process_llm_call(llm_call: AsyncLLMCall, prompt: str):
    try:
        start_time = time.time()
        result = await llm_call.generate_text(prompt)
        end_time = time.time()
        logging.info(f"LLM call completed in {end_time - start_time:.2f} seconds.")
        return result
    except Exception:
        logging.error("Failed to process LLM call.")
        raise

async def main():
    try:
        async with AsyncResource("Resource1", init_delay=0.1) as resource1, \
                   AsyncResource("Resource2", init_delay=0.2, fail_init=False) as resource2:

            logging.info("Resources initialized.")

            file_content = ""
            with SecureFileHandler("example.txt", "w") as f:
                f.write("This is a test.\n")
                file_content = "File written successfully."
            logging.info(file_content)

            async with SecureFileHandler("example.txt", "r") as f:
                content = f.read()
                logging.info(f"File content: {content.strip()}")

            llm_call1 = AsyncLLMCall("ModelA", delay=0.3)
            llm_call2 = AsyncLLMCall("ModelB", delay=0.4, fail=True)

            prompt = "Translate 'Hello world' to French"

            task1 = asyncio.create_task(process_llm_call(llm_call1, prompt))
            task2 = asyncio.create_task(process_llm_call(llm_call2, prompt))

            try:
                await asyncio.gather(task1, task2)
            except Exception as e:
                logging.error(f"An error occurred during LLM calls: {e}")

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
import threading
import asyncio
import logging
import functools
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreadSafeLazy:
    def __init__(self, constructor):
        self._constructor = constructor
        self._lock = threading.Lock()
        self._instance = None

    def get(self):
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._constructor()
        return self._instance

class AsyncContextManager:
    def __init__(self, generator_function, *args, **kwargs):
        self._generator_function = generator_function
        self._args = args
        self._kwargs = kwargs
        self._instance = None

    async def __aenter__(self):
        try:
            self._instance = await self._generator_function(*self._args, **self._kwargs)
            return self._instance
        except Exception as e:
            logging.error(f"Error in __aenter__: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if hasattr(self._instance, 'close'):
                await self._instance.close()
            elif hasattr(self._instance, 'dispose'):
                await self._instance.dispose()
        except Exception as e:
            logging.error(f"Error in __aexit__: {e}")

async def async_generator(data, delay=0.1):
    try:
        for item in data:
            await asyncio.sleep(delay)
            yield item
    except Exception as e:
        logging.error(f"Error in async_generator: {e}")
        raise

def safe_file_read(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except IOError as e:
        logging.error(f"IOError reading file {filepath}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error reading file {filepath}: {e}")
        return None

class LLMService:
    def __init__(self):
        self.model = "GPT-3" # Simulate model loading
        logging.info("LLM Service initialized")

    async def generate_response(self, prompt):
        try:
            await asyncio.sleep(0.5)  # Simulate API call
            response = f"Response from {self.model} to: {prompt}"
            logging.info(f"Generated response: {response}")
            return response
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            raise

    async def close(self):
        logging.info("LLM Service closed")

class Config:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.api_key = None
        self.load_config()

    def load_config(self):
        try:
            config_content = safe_file_read("config.txt")
            if config_content:
                lines = config_content.splitlines()
                for line in lines:
                    if "API_KEY" in line:
                        self.api_key = line.split("=")[1].strip()
                        logging.info("API Key loaded")
                        break
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = Config()
        return cls._instance

async def main():
    config = Config.get_instance()
    if config.api_key:
        logging.info(f"API Key: {config.api_key[:5]}...")
    else:
        logging.warning("API Key not found in config.txt")

    async def create_llm_service():
        return LLMService()

    llm_service = AsyncContextManager(create_llm_service)

    async def call_llm(prompt):
        try:
            async with llm_service as service:
                response = await service.generate_response(prompt)
                return response
        except Exception as e:
            logging.error(f"Error during LLM call: {e}")
            return "Error generating response."

    prompts = ["Tell me a joke.", "What is the capital of France?"]
    tasks = [call_llm(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

    async for item in async_generator(range(3), 0.2):
        print(f"Async generator: {item}")


if __name__ == "__main__":
    asyncio.run(main())
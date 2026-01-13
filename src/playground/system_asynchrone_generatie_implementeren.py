import asyncio
import logging
import time


class LLMClient:
    def __init__(self, api_key: str = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def _make_api_call(self, prompt: str, timeout: int) -> str:
        """Simuleert een asynchrone API call naar een LLM."""
        try:
            self.logger.info(f"Simuleren van API call voor prompt: {prompt}")
            response = await asyncio.wait_for(
                self._simulate_api_call(prompt), timeout=timeout
            )
            self.logger.info(f"Ontvangen response: {response}")
            return response
        except ValueError as e:
            self.logger.error(f"API call error: {e}")
            raise
        except asyncio.TimeoutError:
            self.logger.error("API call timeout!")
            return "API call timed out."
        except Exception as e:
            self.logger.error(f"Onverwachte fout tijdens API call: {e}")
            raise

    async def _simulate_api_call(self, prompt: str):
        await asyncio.sleep(2)
        if "error" in prompt.lower():
            raise ValueError("Simulated API error!")
        return f"Simuleerde LLM generatie voor: {prompt}"

    async def generate(self, prompt: str) -> str:
        """Genereert content van de LLM asynchroon."""
        try:
            start_time = time.time()
            response = await self._make_api_call(prompt, self.timeout)
            end_time = time.time()
            self.logger.info(
                f"Generatie voltooid in {end_time - start_time:.2f} seconden"
            )
            return response
        except Exception as e:
            self.logger.error(f"Fout tijdens generatie: {e}")
            return "Er is een fout opgetreden tijdens de generatie."


async def main():
    client = LLMClient(timeout=5)
    prompts = [
        "Schrijf een korte samenvatting over Python.",
        "Vertel me een grap.",
        "Genereer een antwoord met het woord error erin.",
    ]

    tasks = [client.generate(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Prompt {i + 1}: Fout - {result}")
        else:
            print(f"Prompt {i + 1}: {result}")


if __name__ == "__main__":
    asyncio.run(main())

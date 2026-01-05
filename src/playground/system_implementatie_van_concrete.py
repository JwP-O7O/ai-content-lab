import asyncio
import random
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    _instance = None

    def __init__(self, api_key: str = None):
        if LLMClient._instance is not None:
            raise Exception("This class is a singleton!")
        self.api_key = api_key
        self.logger = logging.getLogger(__name__ + ".LLMClient")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLMClient, cls).__new__(cls)
        return cls._instance

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_text(self, prompt: str) -> str:
        """Simuleer een LLM-aanroep."""
        self.logger.info(f"Simulating LLM call with prompt: {prompt}")
        await asyncio.sleep(random.uniform(0.1, 1.0))  # Simuleer netwerklatentie
        if random.random() < 0.1:  # 10% kans op een fout
            self.logger.error("Simulated LLM error")
            raise Exception("Simulated LLM error")
        response = f"Simulated LLM response for: {prompt}"
        self.logger.info(f"Simulated LLM response: {response}")
        return response

class ConversionAgent:
    def __init__(self, llm_client: LLMClient, ab_test_config: Optional[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__ + ".ConversionAgent")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.ab_test_config = ab_test_config
        self.variant = self._determine_variant()


    def _determine_variant(self) -> Optional[str]:
        if self.ab_test_config:
            if 'variants' in self.ab_test_config and isinstance(self.ab_test_config['variants'], list) and len(self.ab_test_config['variants']) > 0:
                return random.choice(self.ab_test_config['variants'])
            else:
                self.logger.warning("Invalid AB test configuration: 'variants' not correctly defined.  Running base variant.")
                return None
        return None

    async def _execute_conversion(self, input_data: str) -> str:
        try:
            prompt = f"Convert this: '{input_data}'"
            if self.variant:
                prompt += f" using variant: {self.variant}"
            response = await self.llm_client.generate_text(prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error during conversion: {e}")
            raise

    async def execute(self, input_data: str) -> Dict[str, Any]:
        """
        Voert conversies uit met behulp van de LLM. Implementeert AB-testen indien geconfigureerd.
        """
        try:
            start_time = datetime.now()
            self.logger.info(f"Starting conversion with input: {input_data}, variant: {self.variant if self.variant else 'base'}")
            converted_data = await self._execute_conversion(input_data)
            end_time = datetime.now()
            duration = end_time - start_time
            result = {
                "converted_data": converted_data,
                "execution_time": duration.total_seconds(),
                "variant": self.variant,
                "timestamp": datetime.now().isoformat()
            }
            self.logger.info(f"Conversion complete, result: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute conversion: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


async def main():
    logging.basicConfig(level=logging.INFO)
    api_key = "test_api_key"
    llm_client = LLMClient(api_key)

    # AB test config example
    ab_test_config = {
        "variants": ["variant_a", "variant_b"]
    }
    agent = ConversionAgent(llm_client, ab_test_config)

    input_data = "This is a test string."
    result = await agent.execute(input_data)
    print(result)

    # Test without AB testing
    agent_no_ab = ConversionAgent(llm_client)
    result_no_ab = await agent_no_ab.execute(input_data)
    print(result_no_ab)


if __name__ == "__main__":
    asyncio.run(main())
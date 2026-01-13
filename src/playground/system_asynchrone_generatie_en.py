import asyncio
import aiohttp
import time
from typing import Optional


class LLMClient:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"},
                raise_for_status=True,
            )
        return self._session

    async def generate(self, prompt: str) -> str:
        try:
            async with self.session.post(
                f"{self.api_url}/generate", json={"prompt": prompt}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("result", "")
        except aiohttp.ClientError as e:
            print(f"LLMClient Error: {e}")
            raise
        except Exception as e:
            print(f"LLMClient Unexpected Error: {e}")
            raise

    async def close(self):
        if self._session:
            await self._session.close()


class TaskManager:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def execute(self, task_id: int, prompt: str) -> tuple[int, str]:
        start_time = time.time()
        try:
            result = await self.llm_client.generate(prompt)
            end_time = time.time()
            print(f"Task {task_id} completed in {end_time - start_time:.2f}s")
            return task_id, result
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            return task_id, f"Error: {str(e)}"


async def main():
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    api_url = "https://example.com/api"  # Replace with your actual API URL
    llm_client = LLMClient(api_key, api_url)
    task_manager = TaskManager(llm_client)

    tasks = [
        task_manager.execute(1, "Write a short poem about the ocean."),
        task_manager.execute(2, "Translate 'Hello, world!' to French."),
        task_manager.execute(
            3,
            "Summarize the following text: The quick brown fox jumps over the lazy dog.",
        ),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for task_id, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"Task {task_id} failed with error: {result}")
        else:
            print(f"Task {task_id} result: {result[1]}")  # print the result string

    await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())

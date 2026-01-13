import asyncio
import aiohttp


class LLMClient:
    def __init__(self, api_key, api_url, timeout=10):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def generate(self, prompt):
        if not self._session:
            raise RuntimeError(
                "Client is not initialized.  Use 'async with LLMClient(...)'"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {"prompt": prompt}
        try:
            async with self._session.post(
                self.api_url, headers=headers, json=data
            ) as response:
                response.raise_for_status()
                json_response = await response.json()
                return json_response.get("generated_text", "")
        except aiohttp.ClientError as e:
            print(f"Error during API call: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""


async def main():
    api_key = "YOUR_API_KEY"  # Replace with your API key
    api_url = "https://api.example.com/generate"  # Replace with your API URL
    prompt = "Write a short poem about the ocean."

    async with LLMClient(api_key, api_url) as client:
        response = await client.generate(prompt)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())

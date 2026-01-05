import httpx
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageGenerator:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_key}"})

    async def generate_image(self, prompt: str) -> str:
        """
        Generates an image from a given prompt using an external API.
        """
        try:
            payload = {"prompt": prompt}
            async with self.client as client:
                response = await client.post(self.api_url, json=payload, timeout=30.0)
                response.raise_for_status()
                image_url = response.json().get("image_url")  # Assuming API returns {"image_url": "url"}
                if not image_url:
                    logging.warning(f"API returned no image_url: {response.json()}")
                    raise ValueError("API did not return an image URL.")

                return image_url

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTPError: Status code: {e.response.status_code}, Message: {e}, Headers: {e.response.headers}")
            raise  # Re-raise to signal the failure

        except httpx.RequestError as e:
            logging.error(f"RequestError: {e}")
            raise # Re-raise

        except ValueError as e:
            logging.error(f"ValueError: {e}")
            raise

        except Exception as e:
            logging.exception(f"Unexpected error during image generation: {e}")
            raise # Re-raise

    async def close(self):
        await self.client.aclose()


async def main():
    # Replace with your API URL and API key
    api_url = "https://example.com/api/generate_image"
    api_key = "YOUR_API_KEY"
    generator = ImageGenerator(api_url, api_key)

    try:
        image_url = await generator.generate_image("A futuristic cityscape")
        logging.info(f"Generated image URL: {image_url}")
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
    finally:
        await generator.close()

if __name__ == "__main__":
    asyncio.run(main())
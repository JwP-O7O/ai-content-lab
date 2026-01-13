import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LLMClient:
    class Messages:
        def __init__(self, create_response="Mock response"):
            self.create_response = create_response

        def create(self, **kwargs):
            try:
                return self.create_response
            except Exception as e:
                logging.error(f"Error in Messages.create: {e}")
                return "Error in Mock Response"

    def __init__(
        self,
        generate_response="Mock generated content",
        create_response="Mock response",
    ):
        self.generate_response = generate_response
        self.messages = self.Messages(create_response)
        logging.info(
            f"LLMClient initialized with generate_response: {self.generate_response} and create_response: {create_response}"
        )

    async def generate(self, **kwargs):
        try:
            return self.generate_response
        except Exception as e:
            logging.error(f"Error in generate: {e}")
            return "Error in Mock Generated Content"

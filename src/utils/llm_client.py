class LLMClient:
    class Messages:
        def create(self, **kwargs): return "Mock response"
    messages = Messages()
    async def generate(self, **kwargs): return "Mock generated content"

llm_client = LLMClient()

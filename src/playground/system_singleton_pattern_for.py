class LLMClient:
    _instance = None

    def __init__(self):
        if LLMClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            # Initialize LLM client, e.g., setup API key, etc.
            self.api_key = "YOUR_API_KEY"  # Replace with actual API key or config
            print("LLMClient initialized")
            LLMClient._instance = self

    @staticmethod
    def get_instance():
        if LLMClient._instance is None:
            LLMClient()  # Create the instance if it doesn't exist
        return LLMClient._instance

    def generate_text(self, prompt):
        # Simulate text generation
        return f"Generated text based on: {prompt}"


# Example usage
llm_client = LLMClient.get_instance()
response = llm_client.generate_text("Hello, world!")
print(response)

# Demonstrate singleton behavior (should return the same instance)
llm_client2 = LLMClient.get_instance()
print(llm_client is llm_client2)

# Attempt to create a new instance (should raise an exception)
try:
    llm_client3 = LLMClient()
except Exception as e:
    print(e)

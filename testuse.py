from src.api.openai_client import OpenAIClient

# Initialize the client
client = OpenAIClient()

# Generate text
response = client.generate_text("Tell me about artificial intelligence")
print(response)
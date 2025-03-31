from src.api.openai_client import OpenAIClient

# Initialize the client
client = OpenAIClient()

# Generate text
response = client.generate_with_file()
print(response)
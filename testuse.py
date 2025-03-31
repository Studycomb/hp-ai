
from src.api.openai_client import OpenAIClient

# Initialize the client
client = OpenAIClient()

# Generate text
response = client.generate_quiz_from_pdf("res/old_exams/provpass-3-verb-utan-elf.pdf")
print(response)

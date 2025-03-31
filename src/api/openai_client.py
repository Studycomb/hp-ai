import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model = model or os.getenv("MODEL_NAME", "gpt-4")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_text(self, prompt, max_tokens=None, temperature=None):
        """
        Generate text using OpenAI's API

        Args:
            prompt (str): The input prompt
            max_tokens (int, optional): Maximum tokens to generate
            temperature (float, optional): Sampling temperature

        Returns:
            str: The generated text
        """
        max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", 1000))
        temperature = temperature or float(os.getenv("TEMPERATURE", 0.7))

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content
    
    def generate_with_file(self):
        print(os.getcwd())
        uploaded_file = self.client.files.create(
            file=open("res/old_exams/provpass-3-verb-utan-elf.pdf", "rb"),
            purpose="assistants"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate multiple-choice quiz questions based on PDF content."},
                {"role": "user", "content": "Please generate 3 multiple-choice questions based on this PDF."}
            ],
            max_tokens=None,
            temperature=None,
            tools=[{"type": "file_search"}],  # enables file searching
            tool_choice="auto",  # let GPT decide
            file_ids=[uploaded_file.id]
        )
        return response.choices[0].message.content


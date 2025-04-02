import os
from openai import OpenAI
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model = model or os.getenv("MODEL_NAME", "gpt-4")
        self.client = OpenAI(api_key=self.api_key)
        self.assistant = self._create_assistant()

    def _create_assistant(self):
        assistant = self.client.beta.assistants.create(
            name="Quiz Generator",
            instructions="You generate multiple-choice quiz questions based on PDF content.",
            model=self.model,
            tools=[{"type": "file_search"}]
        )
        return assistant
    
    def _upload_file(self, file_path: str) -> str:
        """Upload a PDF file and return the file ID."""
        uploaded_file = self.client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )
        return uploaded_file.id
    
    def _create_vector_store_with_file(self, file_id: str):
        """Create a vector store and attach the uploaded file."""
        vector_store = self.client.vector_stores.create(
            name="Quiz PDF Vector Store",
            file_ids=[file_id]
        )
        return vector_store.id

    def _wait_for_run(self, thread_id: str, run_id: str):
        """Poll the run status until completion."""
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run_status.status == "completed":
                return
            elif run_status.status in ["failed", "expired", "cancelled"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)
    
    def generate_quiz_from_pdf(self, file_path: str) -> str:
        """Complete flow: upload PDF → run assistant → get quiz response."""
        prompt = "Generate 3 multiple-choice quiz questions based on the content in this PDF."

        file_id = self._upload_file(file_path)
        vector_store_id = self._create_vector_store_with_file(file_id)

        thread = self.client.beta.threads.create(
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )

        self._wait_for_run(thread.id, run.id)

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)

        for msg in messages.data[::-1]:  # Newest first
            if msg.role == "assistant":
                return msg.content[0].text.value

        return "No response from assistant."

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
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

        self.model = model or os.getenv("MODEL_NAME", "gpt-4o-mini")
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

    def _get_files_open_ai(self):
        file_dict = {}
        files = self.client.files.list()
        for file in files.data:
            file_dict[file.filename] = file.id

        return file_dict

    def get_all_files(self):
        local_files = os.listdir("res")
        files = self._get_files_open_ai()

        for file in local_files:
            if file not in files:
                files[file] = ""
        return files


    def upload_file(self, file_path: str) -> str:
        """Upload a PDF file and return the file ID."""
        uploaded_file = self.client.files.create(
            file=open(file_path, "rb"),
            purpose="assistants"
        )
        return uploaded_file.id

    def create_vector_store_batch(self, file_id_list: list):
        """Create a vector store and attach the uploaded file."""
        if len(file_id_list) > 0:
            vector_store = self.client.vector_stores.create(
                name="Quiz PDF Vector Store",
                file_ids=file_id_list
            )
            return vector_store.id
        raise AssertionError("Empty file_id list")

    def create_thread(self, vector_store_id: str):
        thread = self.client.beta.threads.create(
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        return thread.id

    def create_message(self, thread_id: str, prompt: str):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )

    def run_thread(self, thread_id: str):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        return run.id


    def wait_for_run(self, thread_id: str, run_id: str):
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

    def get_thread_response(self, thread_id: str):
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)

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
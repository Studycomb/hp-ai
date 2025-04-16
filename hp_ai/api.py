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
        self.file_id_list = []

    def add_file(self, path: str):
        """
        Add a file to the OpenAI API for use in user data.

        If a file with the same name already exists, it uses the existing file ID.
        Otherwise, it uploads the file and stores the new file ID.

        Args:
            path (str): The file path to add

        Returns:
            None: The file ID is appended to the internal file_id_list
        """
        file_id = self.get_file_id(os.path.basename(path))
        if file_id is None:
            # If the file doesn't exist, upload it
            file_id = self.client.files.create(
                file=open(path, "rb"),
                purpose="user_data",
            ).id
        self.file_id_list.append(file_id)

    def get_file_id(self, filename: str):
        """
        Retrieve the file ID for a specified filename from the OpenAI API.

        Searches through the list of files in the OpenAI account to find a file
        with the matching filename.

        Args:
            filename (str): The name of the file to search for

        Returns:
            str or None: The ID of the file if found, None otherwise
        """
        files = self.client.files.list()
        for data in files.data:
            if data.filename == filename:
                return data.id
        return None

    def generate(self, prompt: str):
        """
        Generate a response from the OpenAI API using the provided prompt.
        Args:
            prompt (str): The prompt to generate a response for
        Returns:
            str: The generated response from the OpenAI API
        """

        if not prompt:
            raise ValueError("Prompt cannot be empty")

        user_messages = {
            "role": "user",
            "content": [],
            }

        for file_id in self.file_id_list:
            user_messages["content"].append({
                "type": "file",
                "file": {
                    "file_id": file_id
                }
            })

        user_messages["content"].append({
            "type": "text",
            "text": prompt
        })

        messages = [user_messages]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=int(os.getenv("MAX_TOKENS", 1000)),
            temperature=float(os.getenv("TEMPERATURE", 0.7))
        )

        return response.choices[0].message.content
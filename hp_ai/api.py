import os
from openai import OpenAI
import requests
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
            with open(path, "rb") as file:
                file_id = self.client.files.create(
                    file=file,
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

        if "json" not in prompt.lower():
            prompt += "  Returnera svaret i giltigt JSON-format med hjälp av funktionen create_quiz. Kategorin ska vara 'ORD'."

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

        messages = [
            {
                "role": "system",
                "content": "Du är en hjälpsam assistent som skapar quiz i JSON-format."
            },
            user_messages
        ]

        functions = [
            {
                "name": "create_quiz",
                "description": "Skapa ett flervalsquiz.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "category": {"type": "string"},
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "image": {"type": ["string", "null"]},
                                    "alternatives": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "option_text": {"type": "string"},
                                                "is_correct": {"type": "boolean"}
                                            },
                                            "required": ["option_text", "is_correct"]
                                        }
                                    }
                                },
                                "required": ["question", "image", "alternatives"]
                            }
                        }
                    },
                    "required": ["title", "category", "questions"]
                }
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            functions=functions,
            function_call={"name": "create_quiz"},
            max_tokens=int(os.getenv("MAX_TOKENS", 1000)),
            temperature=float(os.getenv("TEMPERATURE", 0.7))
        )

        return response.choices[0].message.function_call.arguments


class QuizAPIClient:
    def __init__(self):
        self.api_route = os.getenv("QUIZ_ROUTE")
        self.auth_token = os.getenv("AUTH_TOKEN")
        if not self.api_route or not self.auth_token:
            raise ValueError("API route and auth token are required")

    def create_quiz(self, quiz_data):
        """
        Create a quiz using the provided quiz data.
        Args:
            quiz_data (dict): The quiz data to create
        """
        response = requests.post(
            self.api_route,
            json=quiz_data,
            headers={
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            },
        )
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}")

        print("Status Code:", response.status_code)
        print("Response:", response.json())


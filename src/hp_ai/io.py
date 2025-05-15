import os

import tomllib


class PromptManager:
    def __init__(self, prompt_file):
        self.prompt_file = prompt_file
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        with open(self.prompt_file, "rb") as prompt_file:
            return tomllib.load(prompt_file)

    def get_prompt_names(self):
        return list(self.prompts.keys())

    def get_prompt(self, prompt_name):
        return self.prompts[prompt_name]


class DocumentManager:
    def __init__(self, doc_folder):
        self.supported_extensions = [".pdf", ".txt"]
        self.doc_folder = doc_folder

    def get_documents(self):
        documents = []
        for filename in os.listdir(self.doc_folder):
            file_path = os.path.join(self.doc_folder, filename)
            if os.path.isfile(file_path) and filename.endswith(
                tuple(self.supported_extensions)
            ):
                documents.append(filename)
        return documents

    def get_document_path(self, filename):
        return os.path.join(self.doc_folder, filename)

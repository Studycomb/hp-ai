import argparse
import os

import questionary


class CLIHandler:
    def __init__(self):
        self.args = self._parse_arguments()
        self._validate_arguments()

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="HP-AI - A tool for generating quiz questions using OpenAI"
        )
        parser.add_argument(
            "-d",
            "--doc-folder",
            help="Path to folder containing documents",
            default=".",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--prompt-file",
            help="Path to file with prompts",
            default="./prompts.toml",
            type=str,
        )
        return parser.parse_args()

    def _validate_arguments(self):
        if not (
            os.path.exists(self.args.doc_folder) and os.path.isdir(self.args.doc_folder)
        ):
            raise FileNotFoundError(
                f'Document folder "{self.args.doc_folder}" does not exist or is a file'
            )
        if not (
            os.path.exists(self.args.prompt_file)
            and os.path.isfile(self.args.prompt_file)
        ):
            raise FileNotFoundError(
                f'Prompt file "{self.args.prompt_file}" does not exist or is a directory'
            )

    def get_document_folder(self):
        return self.args.doc_folder

    def get_prompt_file(self):
        return self.args.prompt_file

    def select_documents(self, documents):
        return questionary.checkbox(
            "Select documents to process",
            choices=documents,
        ).unsafe_ask()

    def select_prompt(self, prompts):
        return questionary.select(
            f'Select a prompt to use, prompt are defined in "{self.args.prompt_file}"',
            choices=prompts,
        ).unsafe_ask()

    def confirm_continue(self, message="Do you want to continue?"):
        return questionary.confirm(
            message=message,
        ).ask()

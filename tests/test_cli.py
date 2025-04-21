import os
import pytest
from unittest import mock
import argparse
import tempfile

from hp_ai.cli import CLIHandler


class TestCLIHandler:
    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_init_with_valid_args(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/valid/doc/folder"
        mock_args.prompt_file = "/valid/prompt_file.toml"
        mock_parse_args.return_value = mock_args

        # Make path validation pass
        mock_exists.return_value = True
        valid_files = {"/valid/prompt_file.toml"}
        valid_directories = ["/valid/doc/folder"]
        mock_isfile.side_effect = lambda path: path in valid_files
        mock_isdir.side_effect = lambda path: path in valid_directories

        # Initialize handler
        cli_handler = CLIHandler()

        # Verify handler was initialized correctly
        assert cli_handler.args == mock_args
        mock_exists.assert_any_call("/valid/doc/folder")
        mock_exists.assert_any_call("/valid/prompt_file.toml")

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isdir")
    def test_missing_doc_folder(self, mock_isdir, mock_exists, mock_parse_args) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/nonexistent/folder"
        mock_args.prompt_file = "/valid/prompt_file.toml"
        mock_parse_args.return_value = mock_args

        # Make doc folder validation fail
        mock_exists.side_effect = lambda path: path == "/valid/prompt_file.toml"
        mock_isdir.return_value = True

        # Initialize handler should raise FileNotFoundError
        with pytest.raises(
            FileNotFoundError,
            match=f'Document folder "{mock_args.doc_folder}" does not exist or is a file',
        ):
            CLIHandler()

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_doc_folder_is_file(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/path/to/file.txt"
        mock_args.prompt_file = "/valid/prompt_file.toml"
        mock_parse_args.return_value = mock_args

        # Make doc folder exist but as a file
        mock_exists.return_value = True
        mock_isfile.side_effect = (
            lambda path: path == "/path/to/file.txt"
            or path == "/valid/prompt_file.toml"
        )
        mock_isdir.side_effect = lambda path: path != "/path/to/file.txt"

        # Initialize handler should raise FileNotFoundError with appropriate message
        with pytest.raises(
            FileNotFoundError,
            match=f'Document folder "{mock_args.doc_folder}" does not exist or is a file',
        ):
            CLIHandler()

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_missing_prompt_file(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/valid/doc/folder"
        mock_args.prompt_file = "/nonexistent/prompt_file.toml"
        mock_parse_args.return_value = mock_args

        # Make prompt file validation fail but doc folder pass
        mock_exists.side_effect = lambda path: path == "/valid/doc/folder"
        mock_isdir.side_effect = lambda path: path == "/valid/doc/folder"
        mock_isfile.return_value = False

        # Initialize handler should raise FileNotFoundError
        with pytest.raises(
            FileNotFoundError,
            match=f'Prompt file "{mock_args.prompt_file}" does not exist or is a directory',
        ):
            CLIHandler()

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_prompt_file_is_directory(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/valid/doc/folder"
        mock_args.prompt_file = "/path/to/directory"
        mock_parse_args.return_value = mock_args

        # Make prompt file exist but as a directory
        mock_exists.return_value = True
        mock_isdir.side_effect = lambda path: True
        mock_isfile.side_effect = lambda path: False

        # Initialize handler should raise FileNotFoundError with appropriate message
        with pytest.raises(
            FileNotFoundError,
            match=f'Prompt file "{mock_args.prompt_file}" does not exist or is a directory',
        ):
            CLIHandler()

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_get_document_folder(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/test/docs"
        mock_args.prompt_file = "/test/prompts.toml"
        mock_parse_args.return_value = mock_args
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Initialize handler
        cli_handler = CLIHandler()

        # Test the method
        result = cli_handler.get_document_folder()

        # Verify result
        assert result == "/test/docs"

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    def test_get_prompt_file(
        self, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/test/docs"
        mock_args.prompt_file = "/test/prompts.toml"
        mock_parse_args.return_value = mock_args
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Initialize handler
        cli_handler = CLIHandler()

        # Test the method
        result = cli_handler.get_prompt_file()

        # Verify result
        assert result == "/test/prompts.toml"

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    @mock.patch("questionary.checkbox")
    def test_select_documents(
        self, mock_checkbox, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/test/docs"
        mock_args.prompt_file = "/test/prompts.toml"
        mock_parse_args.return_value = mock_args
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Set up mock for questionary
        mock_checkbox_instance = mock.Mock()
        mock_checkbox_instance.unsafe_ask.return_value = ["doc1.pdf", "doc2.pdf"]
        mock_checkbox.return_value = mock_checkbox_instance

        # Initialize handler
        cli_handler = CLIHandler()

        # Test the method
        documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        result = cli_handler.select_documents(documents)

        # Verify questionary was called correctly
        mock_checkbox.assert_called_once_with(
            "Select documents to process", choices=documents
        )

        # Verify result
        assert result == ["doc1.pdf", "doc2.pdf"]

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    @mock.patch("questionary.select")
    def test_select_prompt(
        self, mock_select, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/test/docs"
        mock_args.prompt_file = "/test/prompts.toml"
        mock_parse_args.return_value = mock_args
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Set up mock for questionary
        mock_select_instance = mock.Mock()
        mock_select_instance.unsafe_ask.return_value = "selected_prompt"
        mock_select.return_value = mock_select_instance

        # Initialize handler
        cli_handler = CLIHandler()

        # Test the method
        prompts = ["prompt1", "prompt2", "prompt3"]
        result = cli_handler.select_prompt(prompts)

        # Verify questionary was called correctly
        mock_select.assert_called_once_with(
            f'Select a prompt to use, prompt are defined in "{mock_args.prompt_file}"',
            choices=prompts,
        )

        # Verify result
        assert result == "selected_prompt"

    @mock.patch("argparse.ArgumentParser.parse_args")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.isdir")
    @mock.patch("questionary.confirm")
    def test_confirm_continue(
        self, mock_confirm, mock_isdir, mock_isfile, mock_exists, mock_parse_args
    ) -> None:
        # Set up mocks
        mock_args = mock.Mock()
        mock_args.doc_folder = "/test/docs"
        mock_args.prompt_file = "/test/prompts.toml"
        mock_parse_args.return_value = mock_args
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Set up mock for questionary
        mock_confirm_instance = mock.Mock()
        mock_confirm_instance.ask.return_value = True
        mock_confirm.return_value = mock_confirm_instance

        # Initialize handler
        cli_handler = CLIHandler()

        # Test the method
        result = cli_handler.confirm_continue()

        # Verify questionary was called correctly
        mock_confirm.assert_called_once_with("Do you want to continue?")

        # Verify result
        assert result is True

    def test_integration_with_real_files(self) -> None:
        # Create temporary files to test real initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy prompt file
            prompt_file = os.path.join(temp_dir, "prompts.toml")
            with open(prompt_file, "w") as f:
                f.write('prompt1 = "Test prompt 1"\n')
                f.write('prompt2 = "Test prompt 2"\n')

            # Patch sys.argv to provide command line arguments
            with mock.patch(
                "sys.argv",
                [
                    "program_name",
                    "--doc-folder",
                    temp_dir,
                    "--prompt-file",
                    prompt_file,
                ],
            ):
                # Initialize handler
                cli_handler = CLIHandler()

                # Verify handler initialized correctly with real files
                assert cli_handler.get_document_folder() == temp_dir
                assert cli_handler.get_prompt_file() == prompt_file

import os
import pytest
import tempfile
from unittest import mock
from tomllib import TOMLDecodeError

from hp_ai.io import PromptManager, DocumentManager


class TestPromptManager:
    def test_init_and_load_prompts(self) -> None:
        """Test that PromptManager correctly initializes and loads prompts."""
        # Create a temporary TOML file for testing
        with tempfile.NamedTemporaryFile(
            suffix=".toml", delete=False, mode="wb"
        ) as temp_file:
            temp_file.write(b"""
test_prompt = "This is a test prompt"
another_prompt = "This is another test prompt"
            """)
            temp_file_path = temp_file.name

        try:
            # Test initialization and loading
            pm = PromptManager(temp_file_path)

            # Verify the prompts were loaded correctly
            assert len(pm.prompts) == 2
            assert pm.prompts["test_prompt"] == "This is a test prompt"
            assert pm.prompts["another_prompt"] == "This is another test prompt"
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_get_prompt_names(self) -> None:
        """Test retrieving prompt names."""
        # Mock _load_prompts to return a predefined dictionary
        with mock.patch.object(
            PromptManager,
            "_load_prompts",
            return_value={"prompt1": "Value 1", "prompt2": "Value 2"},
        ):
            pm = PromptManager("dummy_path.toml")
            names = pm.get_prompt_names()

            # Verify prompt names were correctly returned
            assert isinstance(names, list)
            assert set(names) == {"prompt1", "prompt2"}
            assert len(names) == 2

    def test_get_prompt(self) -> None:
        """Test retrieving specific prompts by name."""
        # Mock _load_prompts to return a predefined dictionary
        with mock.patch.object(
            PromptManager,
            "_load_prompts",
            return_value={"prompt1": "Value 1", "prompt2": "Value 2"},
        ):
            pm = PromptManager("dummy_path.toml")

            # Verify individual prompts can be accessed
            assert pm.get_prompt("prompt1") == "Value 1"
            assert pm.get_prompt("prompt2") == "Value 2"

    def test_nonexistent_prompt_file(self) -> None:
        """Test behavior when the prompt file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            PromptManager("nonexistent_file.toml")

    def test_invalid_toml(self) -> None:
        """Test behavior with invalid TOML content."""
        # Create a file with invalid TOML syntax
        with tempfile.NamedTemporaryFile(
            suffix=".toml", delete=False, mode="wb"
        ) as temp_file:
            temp_file.write(b"""
invalid_toml = "unclosed string
            """)
            temp_file_path = temp_file.name

        try:
            # Should raise an exception for invalid TOML
            with pytest.raises(TOMLDecodeError):
                PromptManager(temp_file_path)
        finally:
            # Clean up
            os.unlink(temp_file_path)


class TestDocumentManager:
    def test_init(self) -> None:
        """Test DocumentManager initialization."""
        dm = DocumentManager("/test/path")
        assert dm.doc_folder == "/test/path"

    def test_get_documents(self) -> None:
        """Test getting list of documents from a folder."""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some dummy files
            open(os.path.join(temp_dir, "file1.pdf"), "w").close()
            open(os.path.join(temp_dir, "file2.pdf"), "w").close()

            # Create a subdirectory (which should not be listed)
            os.mkdir(os.path.join(temp_dir, "subdir"))

            dm = DocumentManager(temp_dir)
            documents = dm.get_documents()

            # Verify documents are listed correctly
            assert isinstance(documents, list)
            assert set(documents) == {"file1.pdf", "file2.pdf"}
            assert len(documents) == 2

    def test_get_document_path(self) -> None:
        """Test getting the full path for a document."""
        dm = DocumentManager("/test/path")

        # Test with a simple filename
        path = dm.get_document_path("document.pdf")
        assert path == os.path.join("/test/path", "document.pdf")

        # Test with a nested path
        path = dm.get_document_path("subfolder/document.pdf")
        assert path == os.path.join("/test/path", "subfolder/document.pdf")

    def test_empty_folder(self) -> None:
        """Test behavior with an empty folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dm = DocumentManager(temp_dir)
            documents = dm.get_documents()

            # Should return an empty list
            assert isinstance(documents, list)
            assert documents == []

    def test_nonexistent_folder(self) -> None:
        """Test getting documents from a non-existent folder."""
        # Using a path that's unlikely to exist
        dm = DocumentManager("/path/that/does/not/exist/123456789")

        # Should raise FileNotFoundError when trying to list the directory
        with pytest.raises(FileNotFoundError):
            dm.get_documents()

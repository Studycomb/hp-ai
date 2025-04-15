import pytest
from unittest.mock import patch
import os
import sys
import openai_responses
from openai_responses import OpenAIMock

from openai.types.beta import Assistant
from openai import NotFoundError

# Add the src directory to the path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.openai_client import OpenAIClient

@openai_responses.mock()
@patch.dict(os.environ, {"OPENAI_API_KEY": ""})
def test_missing_api_key():
    """Test that an error is raised when API key is missing."""
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAIClient()

@openai_responses.mock()
def test_create_client():
    """Test that the OpenAIClient is created correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    assert client.api_key == "test_api_key"
    assert client.model == "gpt-4o-mini"
    assert isinstance(client.assistant, Assistant)
    assert client.assistant.name == "Quiz Generator"

@openai_responses.mock()
def test_upload_file():
    """Test that the file upload works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    with pytest.raises(FileNotFoundError):
        client.upload_file("non_existent_file.pdf")

    # Dummy file creation for testing
    test_file_name = "test_file.pdf"
    with open(test_file_name, "w") as f:
        f.write("Dummy content")
    file_id = client.upload_file(test_file_name)
    assert isinstance(file_id, str)
    assert len(file_id) > 0

@openai_responses.mock()
def test_create_vector_store_batch():
    """Test that the vector store creation works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    # Empty file ID test
    with pytest.raises(AssertionError):
        client.create_vector_store_batch([])

    # Dummy file creation for testing
    test_file_name = "test_file.pdf"
    with open(test_file_name, "w") as f:
        f.write("Dummy content")
    file_id = [client.upload_file(test_file_name)]

    vector_store_id = client.create_vector_store_batch(file_id)
    assert isinstance(vector_store_id, str)
    assert len(vector_store_id) > 0

    # Clean up the dummy file
    os.remove(test_file_name)

@openai_responses.mock()
def test_wait_for_run(openai_mock: OpenAIMock):
    """Test that the run waiting works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    # Empty thread ID and run ID test
    with pytest.raises(ValueError):
        client.wait_for_run("", "")

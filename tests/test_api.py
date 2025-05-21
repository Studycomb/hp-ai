import os
from unittest.mock import patch

import openai_responses
import pytest
from openai_responses import OpenAIMock

from src.hp_ai.api import OpenAIClient


@openai_responses.mock()
@patch.dict(os.environ, {"OPENAI_API_KEY": ""})
def test_missing_api_key() -> None:
    """Test that an error is raised when API key is missing."""
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAIClient()


@openai_responses.mock()
def test_get_file_id(openai_mock: OpenAIMock) -> None:
    """Test that the file ID retrieval works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    returned_file_id = client.get_file_id("test_file.pdf")

    assert returned_file_id is None
    assert openai_mock.files.list.route.call_count == 1


@openai_responses.mock()
def test_add_file() -> None:
    """Test that the file addition works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    # Test adding a file that doesn't exist
    with pytest.raises(FileNotFoundError):
        client.add_file("non_existent_file.pdf")


def test_generate() -> None:
    """Test that the generate function works correctly."""
    client = OpenAIClient(api_key="test_api_key", model="gpt-4o-mini")

    # Test with empty prompt
    with pytest.raises(ValueError):
        client.generate("")

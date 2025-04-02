import pytest
from unittest.mock import Mock, patch
import os
import sys
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage

# Add the src directory to the path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.openai_client import OpenAIClient

class TestOpenAIClient:

    @pytest.fixture
    def client(self):
        """Create a client instance for testing with a fake API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-api-key"}):
            return OpenAIClient()

    @pytest.fixture
    def mock_completion_response(self):
        """Create a mock response for chat completions."""
        mock_message = ChatCompletionMessage(role="assistant", content="This is a test response")
        mock_choice = Choice(finish_reason="stop", index=0, message=mock_message)
        return Mock(choices=[mock_choice])

    @patch("openai.OpenAI")
    def test_generate_text(self, mock_openai_class, client, mock_completion_response):
        """Test the generate_text method."""
        # Configure the mock
        mock_openai_instance = mock_openai_class.return_value
        mock_openai_instance.chat.completions.create.return_value = mock_completion_response

        # Call the method
        result = client.generate_text("Test prompt")

        # Assert the result
        assert result == "This is a test response"

        # Verify the API was called with correct parameters
        mock_openai_instance.chat.completions.create.assert_called_once_with(
            model=client.model,
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=1000,
            temperature=0.7
        )

    @patch("openai.OpenAI")
    def test_generate_text_with_custom_params(self, mock_openai_class, client, mock_completion_response):
        """Test generate_text with custom max_tokens and temperature."""
        # Configure the mock
        mock_openai_instance = mock_openai_class.return_value
        mock_openai_instance.chat.completions.create.return_value = mock_completion_response

        # Call the method with custom parameters
        result = client.generate_text("Test prompt", max_tokens=500, temperature=0.5)

        # Assert the result
        assert result == "This is a test response"

        # Verify the API was called with custom parameters
        mock_openai_instance.chat.completions.create.assert_called_once_with(
            model=client.model,
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=500,
            temperature=0.5
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_missing_api_key(self):
        """Test that an error is raised when API key is missing."""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            OpenAIClient()
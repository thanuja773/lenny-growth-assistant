import pytest
from unittest.mock import patch, MagicMock
from app.services.llm.ollama import OllamaProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.service import LLMService
from app.services.retrieval.schemas import RetrievalResponse, SearchResultItem
import requests

def test_ollama_provider_success():
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"message": {"content": "Test answer"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        
        provider = OllamaProvider()
        answer, model = provider.generate("System", "User", [])
        
        assert answer == "Test answer"
        assert model == "llama3"

def test_ollama_provider_timeout():
    with patch("requests.post", side_effect=requests.exceptions.Timeout):
        provider = OllamaProvider()
        with pytest.raises(RuntimeError, match="timed out"):
            provider.generate("System", "User", [])

def test_ollama_provider_unavailable():
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError):
        provider = OllamaProvider()
        with pytest.raises(RuntimeError, match="unavailable"):
            provider.generate("System", "User", [])

def test_anthropic_missing_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    import app.core.config
    app.core.config.settings.ANTHROPIC_API_KEY = ""
    with pytest.raises(ValueError, match="missing or empty"):
        AnthropicProvider()

def test_anthropic_success(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    import app.core.config
    app.core.config.settings.ANTHROPIC_API_KEY = "test-key"
    
    with patch("app.services.llm.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Anthropic answer"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        provider = AnthropicProvider()
        answer, model = provider.generate("System", "User", [])
        
        assert answer == "Anthropic answer"

def test_llm_service_unsupported_provider():
    service = LLMService(db=MagicMock())
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        service._get_provider("invalid")

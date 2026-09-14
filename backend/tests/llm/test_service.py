import pytest
from unittest.mock import patch, MagicMock
from app.services.llm.service import LLMService
from app.services.llm.schemas import ChatRequest
from app.services.retrieval.schemas import RetrievalResponse, SearchResultItem
import uuid

def test_insufficient_evidence():
    db = MagicMock()
    with patch("app.services.retrieval.retriever.RetrievalService") as mock_retrieval:
        mock_instance = MagicMock()
        mock_instance.search.return_value = RetrievalResponse(query="test", results=[], count=0)
        mock_retrieval.return_value = mock_instance
        
        service = LLMService(db=db)
        service.retrieval_service = mock_instance
        
        response = service.generate_chat_response(ChatRequest(query="test"))
        assert "enough evidence" in response.answer.lower()
        assert response.retrieval_count == 0
        assert len(response.sources) == 0

def test_provider_fallback(monkeypatch):
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "anthropic")
    import app.core.config
    app.core.config.settings.LLM_FALLBACK_PROVIDER = "anthropic"
    
    db = MagicMock()
    with patch("app.services.retrieval.retriever.RetrievalService") as mock_retrieval:
        mock_instance = MagicMock()
        mock_item = SearchResultItem(
            chunk_id=uuid.uuid4(),
            transcript_id=uuid.uuid4(),
            transcript_title="Test",
            source_type="podcast",
            chunk_index=1,
            text="Context text",
            similarity_score=0.9
        )
        mock_instance.search.return_value = RetrievalResponse(query="test", results=[mock_item], count=1)
        
        service = LLMService(db=db)
        service.retrieval_service = mock_instance
        
        with patch.object(service, "_try_generate") as mock_generate:
            # First call fails (ollama), second call succeeds (anthropic)
            mock_generate.side_effect = [
                RuntimeError("Ollama failed"),
                ("Fallback answer", "claude", "anthropic")
            ]
            
            response = service.generate_chat_response(ChatRequest(query="test", provider="ollama"))
            
            assert response.answer == "Fallback answer"
            assert response.provider == "anthropic"
            assert mock_generate.call_count == 2

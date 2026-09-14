import pytest
from app.services.retrieval.embedder import QueryEmbedder
from app.core.config import settings


def test_query_embedder_dimension():
    """Verify that valid queries generate exactly 384 dimensions."""
    embedder = QueryEmbedder()
    embedding = embedder.embed_query("How to find product-market fit?")
    assert isinstance(embedding, list)
    assert len(embedding) == settings.EMBEDDING_DIMENSION
    assert len(embedding) == 384
    assert all(isinstance(v, float) for v in embedding)


def test_query_embedder_rejects_empty_query():
    """Verify that empty and whitespace queries are rejected."""
    embedder = QueryEmbedder()
    with pytest.raises(ValueError, match="empty or whitespace-only"):
        embedder.embed_query("")

    with pytest.raises(ValueError, match="empty or whitespace-only"):
        embedder.embed_query("   ")


def test_query_embedder_no_cloud_keys_needed(monkeypatch):
    """Verify embedding works even when all LLM API keys are unset/empty."""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    embedder = QueryEmbedder()
    embedding = embedder.embed_query("Product prioritization frameworks")
    assert len(embedding) == 384


def test_query_embedder_failure_handling(monkeypatch):
    """Verify graceful handling and clean exception when model encoding fails."""
    embedder = QueryEmbedder()
    
    class FailingModel:
        def encode(self, *args, **kwargs):
            raise Exception("Underlying tensor runtime failure")

    monkeypatch.setattr(embedder, "_model", FailingModel())
    with pytest.raises(RuntimeError, match="Embedding generation failed"):
        embedder.embed_query("Test query")

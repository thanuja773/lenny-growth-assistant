import pytest
from app.db.session import SessionLocal
from app.services.retrieval.retriever import RetrievalService
from app.services.retrieval.schemas import RetrievalResponse, SearchResultItem
from app.core.config import settings


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_retriever_response_structure_and_ordering(db_session):
    """Verify response structure, non-empty results, and ordering by similarity descending."""
    service = RetrievalService(db=db_session)
    response = service.search(query="growth loops and retention", top_k=5)

    assert isinstance(response, RetrievalResponse)
    assert response.query == "growth loops and retention"
    assert isinstance(response.results, list)
    assert response.count == len(response.results)

    if response.results:
        # Verify ordering: each score >= next score
        scores = [item.similarity_score for item in response.results]
        assert scores == sorted(scores, reverse=True)

        first = response.results[0]
        assert isinstance(first, SearchResultItem)
        assert first.chunk_id is not None
        assert first.transcript_id is not None
        assert first.transcript_title is not None
        assert first.source_url is not None
        assert "http" in first.source_url
        assert first.source_type == "podcast"
        assert isinstance(first.chunk_index, int)
        assert len(first.text) > 0
        assert 0.0 <= first.similarity_score <= 1.0


def test_retriever_top_k_respected(db_session):
    """Verify top_k parameter strictly caps the returned result count."""
    service = RetrievalService(db=db_session)
    for k in [1, 2, 3]:
        response = service.search(query="marketing strategy", top_k=k)
        assert response.count <= k


def test_retriever_rejects_empty_or_invalid_query(db_session):
    """Verify empty or whitespace query is rejected with ValueError."""
    service = RetrievalService(db=db_session)
    with pytest.raises(ValueError, match="cannot be empty"):
        service.search(query="")

    with pytest.raises(ValueError, match="cannot be empty"):
        service.search(query="   ")


def test_retriever_rejects_invalid_top_k(db_session):
    """Verify top_k < 1 or top_k > MAX_TOP_K raises ValueError."""
    service = RetrievalService(db=db_session)
    with pytest.raises(ValueError, match="top_k must be at least 1"):
        service.search(query="growth", top_k=0)

    with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
        service.search(query="growth", top_k=settings.RETRIEVAL_MAX_TOP_K + 1)


def test_retriever_threshold_filtering(db_session, monkeypatch):
    """Verify that setting an impossibly high similarity threshold returns zero results."""
    monkeypatch.setattr(settings, "RETRIEVAL_MIN_SIMILARITY", 0.99)
    service = RetrievalService(db=db_session)
    response = service.search(query="obscure non-matching query", top_k=5)
    assert response.count == 0
    assert response.results == []


def test_retriever_empty_corpus_handling():
    """Verify searching an empty corpus returns zero results cleanly without error."""
    class EmptyQuery:
        def join(self, *args, **kwargs):
            return self
        def order_by(self, *args, **kwargs):
            return self
        def limit(self, *args, **kwargs):
            return self
        def all(self):
            return []

    class MockEmptyDB:
        def query(self, *args, **kwargs):
            return EmptyQuery()

    service = RetrievalService(db=MockEmptyDB())
    response = service.search(query="startup founder advice", top_k=5)
    assert response.count == 0
    assert response.results == []


def test_retriever_database_failure_handling():
    """Verify database exceptions are caught and raised cleanly."""
    class FailingDB:
        def query(self, *args, **kwargs):
            raise Exception("PostgreSQL connection terminated")

    service = RetrievalService(db=FailingDB())
    with pytest.raises(Exception, match="PostgreSQL connection terminated"):
        service.search(query="startup growth", top_k=5)

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_api_retrieval_search_success():
    """Verify POST /api/retrieval/search returns 200 with valid schema."""
    response = client.post(
        "/api/retrieval/search",
        json={"query": "How do startups find product-market fit?", "top_k": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "How do startups find product-market fit?"
    assert "results" in data
    assert "count" in data
    assert data["count"] == len(data["results"])
    assert data["count"] <= 3

    if data["count"] > 0:
        item = data["results"][0]
        assert "chunk_id" in item
        assert "transcript_title" in item
        assert "source_url" in item
        assert "chunk_index" in item
        assert "similarity_score" in item
        assert "text" in item


def test_api_retrieval_empty_query_rejected():
    """Verify 422 for Pydantic empty-string constraint, 400 for whitespace-only (passes schema but rejected by route)."""
    # Empty string fails Pydantic min_length=1 → 422 Unprocessable Entity
    res1 = client.post("/api/retrieval/search", json={"query": "", "top_k": 5})
    assert res1.status_code == 422
    assert "detail" in res1.json()

    # Whitespace-only passes Pydantic but is rejected by the route handler → 400 Bad Request
    res2 = client.post("/api/retrieval/search", json={"query": "   ", "top_k": 5})
    assert res2.status_code == 400


def test_api_retrieval_invalid_top_k():
    """Verify 422 for top_k < 1 (Pydantic ge=1), 400 for top_k > MAX_TOP_K (app-level check)."""
    # top_k=0 fails Pydantic ge=1 constraint → 422 Unprocessable Entity
    res1 = client.post("/api/retrieval/search", json={"query": "growth", "top_k": 0})
    assert res1.status_code == 422

    # top_k > MAX_TOP_K passes Pydantic but is rejected by the route handler → 400 Bad Request
    res2 = client.post(
        "/api/retrieval/search",
        json={"query": "growth", "top_k": settings.RETRIEVAL_MAX_TOP_K + 1},
    )
    assert res2.status_code == 400


def test_api_retrieval_db_failure():
    """Verify 503 Service Unavailable when DB session fails, without leaking stack traces."""
    from app.db.session import get_db

    class MockFailingSession:
        def query(self, *args, **kwargs):
            raise Exception("Simulated DB connection failure")

    def override_get_db():
        yield MockFailingSession()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            "/api/retrieval/search",
            json={"query": "retention metrics"},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "Retrieval service or database is currently unavailable."
        # Verify stack trace is not exposed
        assert "Traceback" not in response.text
    finally:
        app.dependency_overrides.clear()


def test_api_openapi_schema_contains_retrieval():
    """Verify /api/retrieval/search is documented in FastAPI OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/api/retrieval/search" in paths
    assert "post" in paths["/api/retrieval/search"]

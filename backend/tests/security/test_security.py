import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_oversized_query_rejected():
    """Verify 422 Unprocessable Entity when query exceeds max length."""
    large_query = "a" * 4001
    response = client.post("/api/chat/", json={
        "query": large_query,
        "provider": "ollama"
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("String should have at most 4000 characters" in error["msg"] for error in data["detail"])

def test_oversized_session_id_rejected():
    """Verify 422 when session_id exceeds 36 chars."""
    large_session_id = "a" * 37
    response = client.post("/api/chat/", json={
        "query": "hello",
        "provider": "ollama",
        "session_id": large_session_id
    })
    assert response.status_code == 422

def test_cors_headers():
    """Verify CORS headers are set appropriately."""
    # This requires origin to be frontend url.
    # In test environment, FRONTEND_URL=http://localhost:3000
    response = client.options("/api/chat/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    
def test_request_id_middleware():
    """Verify X-Request-ID is attached."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers

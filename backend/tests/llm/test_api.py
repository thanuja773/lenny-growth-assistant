from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_api_empty_query():
    response = client.post("/api/chat/", json={"query": ""})
    assert response.status_code == 422 # Pydantic min_length=1

    response2 = client.post("/api/chat/", json={"query": "   "})
    assert response2.status_code == 400

def test_chat_api_invalid_provider():
    response = client.post("/api/chat/", json={"query": "test", "provider": "invalid"})
    assert response.status_code == 400

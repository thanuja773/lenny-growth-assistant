import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_session():
    response = client.post("/api/sessions/")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data

def test_get_session():
    response = client.post("/api/sessions/")
    session_id = response.json()["session_id"]
    
    get_resp = client.get(f"/api/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session_id"] == session_id

def test_get_invalid_session():
    import uuid
    invalid_id = str(uuid.uuid4())
    get_resp = client.get(f"/api/sessions/{invalid_id}")
    assert get_resp.status_code == 404

def test_get_session_messages_empty():
    response = client.post("/api/sessions/")
    session_id = response.json()["session_id"]
    
    msg_resp = client.get(f"/api/sessions/{session_id}/messages")
    assert msg_resp.status_code == 200
    assert msg_resp.json() == []

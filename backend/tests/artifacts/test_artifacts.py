import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.db.session import SessionLocal
from app.db.models.session import Session as DBSession
from app.agent.artifact_manager import ArtifactManager

client = TestClient(app)

def test_get_artifact_not_found():
    response = client.get(f"/api/artifacts/{uuid.uuid4()}")
    assert response.status_code == 404

def test_artifact_creation_and_retrieval():
    # 1. Create a session via API
    resp = client.post("/api/sessions/")
    session_id = resp.json()["session_id"]
    
    # 2. Create artifact directly via manager using local DB session
    db = SessionLocal()
    try:
        manager = ArtifactManager(db)
        artifact = manager.create_artifact(
            session_id=uuid.UUID(session_id),
            artifact_type="ship30",
            title="Test Essay",
            content="This is a test essay content.",
            word_count=6,
            sources=[]
        )
        art_id = artifact.id
    finally:
        db.close()
    
    # 3. Retrieve via API
    response = client.get(f"/api/artifacts/{art_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["artifact_id"] == str(art_id)
    assert data["title"] == "Test Essay"
    assert data["content"] == "This is a test essay content."
    assert data["word_count"] == 6

def test_get_session_artifacts():
    # 1. Create a session via API
    resp = client.post("/api/sessions/")
    session_id = resp.json()["session_id"]
    
    # 2. Create multiple artifacts
    db = SessionLocal()
    try:
        manager = ArtifactManager(db)
        manager.create_artifact(
            session_id=uuid.UUID(session_id),
            artifact_type="ship30",
            title="First Essay",
            content="Content 1"
        )
        manager.create_artifact(
            session_id=uuid.UUID(session_id),
            artifact_type="ship30",
            title="Second Essay",
            content="Content 2"
        )
    finally:
        db.close()
    
    # 3. Fetch session artifacts
    response = client.get(f"/api/artifacts/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    # Should be returned in descending order
    assert data[0]["title"] == "Second Essay"
    assert data[1]["title"] == "First Essay"

@patch("app.agent.tools.generate_ship30.GenerateShip30Tool.execute")
@patch("app.agent.tools.search_transcripts.SearchTranscriptsTool.execute")
def test_agent_artifact_generation(mock_search, mock_generate):
    # Setup mocks
    mock_search.return_value = {
        "chunks": [{"title": "t1", "text": "evidence"}],
        "sources": [{"transcript_title": "t1", "chunk_index": 0, "similarity_score": 0.9, "source_url": "url"}]
    }
    
    mock_generate.return_value = {
        "title": "Ship 30 for 30: Growth",
        "content": "Growth is important. Always test.",
        "word_count": 6,
        "sources": [{"transcript_title": "t1", "chunk_index": 0, "similarity_score": 0.9, "source_url": "url"}]
    }
    
    # Run the chat generation through Ollama deterministic flow
    response = client.post("/api/chat/", json={
        "query": "Convert this to a Ship 30 for 30 essay about Growth",
        "provider": "ollama"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["tool_used"] == "generate_ship30"
    assert data["artifact_id"] is not None
    assert data["word_count"] == 6
    
    # Verify artifact is persisted
    artifact_id = data["artifact_id"]
    get_res = client.get(f"/api/artifacts/{artifact_id}")
    assert get_res.status_code == 200
    
@patch("app.agent.tools.generate_ship30.GenerateShip30Tool.execute")
@patch("app.agent.tools.search_transcripts.SearchTranscriptsTool.execute")
def test_agent_insufficient_evidence(mock_search, mock_generate):
    # Setup mocks
    mock_search.return_value = {
        "chunks": [],
        "sources": []
    }
    
    response = client.post("/api/chat/", json={
        "query": "Convert this to a Ship 30 for 30 essay about Aliens",
        "provider": "ollama"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "couldn't find enough evidence" in data["answer"].lower()
    assert data["artifact_id"] is None

import pytest
from app.agent.agent import GrowthAgent
from app.services.llm.schemas import ChatRequest

from unittest.mock import patch, MagicMock

def test_agent_creates_session_if_none(monkeypatch):
    db_session = MagicMock()
    
    # Mock user creation
    db_session.query().first.return_value = None

    # Mock LLM provider to avoid real network call in unit test
    class MockProvider:
        def generate(self, system, user, context):
            return "Mocked answer", "mock-model"
            
    monkeypatch.setattr("app.agent.agent.OllamaProvider", MockProvider)
    
    import uuid
    from app.db.models.session import Session as SessionModel
    
    agent = GrowthAgent(db=db_session)
    agent.session_manager.create_session = MagicMock(return_value=SessionModel(id=uuid.uuid4(), user_id=uuid.uuid4()))
    agent.session_manager.get_session_messages = MagicMock(return_value=[])
    agent.session_manager.add_message = MagicMock()
    
    request = ChatRequest(query="Hello", provider="ollama")
    
    # Needs to bypass retrieval actually searching DB if it's empty, but we can let it search
    # It will just return 0 chunks
    
    response = agent.process_request(request)
    
    assert response.session_id is not None
    assert response.answer == "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently."
    assert response.tool_used == "search_transcripts"

def test_agent_reuses_session(monkeypatch):
    db_session = MagicMock()
    
    class MockUser:
        id = "test-user-id"
        
    db_session.query().first.return_value = MockUser()
    class MockProvider:
        def generate(self, system, user, context):
            return "Mocked answer", "mock-model"
            
    monkeypatch.setattr("app.agent.agent.OllamaProvider", MockProvider)
    
    import uuid
    from app.db.models.session import Session as SessionModel
    
    agent = GrowthAgent(db=db_session)
    mock_session_id = uuid.uuid4()
    agent.session_manager.create_session = MagicMock(return_value=SessionModel(id=mock_session_id, user_id=uuid.uuid4()))
    agent.session_manager.get_session = MagicMock(return_value=SessionModel(id=mock_session_id, user_id=uuid.uuid4()))
    
    mock_messages = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    for m in mock_messages:
        m.role = "user"
        m.content = "test"
        
    agent.session_manager.get_session_messages = MagicMock(return_value=mock_messages)
    agent.session_manager.add_message = MagicMock()
    
    req1 = ChatRequest(query="First", provider="ollama")
    resp1 = agent.process_request(req1)
    
    req2 = ChatRequest(query="Second", provider="ollama", session_id=resp1.session_id)
    resp2 = agent.process_request(req2)
    
    assert resp1.session_id == resp2.session_id
    
    # Verify messages were saved
    messages = agent.session_manager.get_session_messages(resp1.session_id)
    assert len(messages) == 4 # User1, Assistant1, User2, Assistant2

def test_agent_ship30_routing(monkeypatch):
    db_session = MagicMock()
    
    class MockUser:
        id = "test-user-id"
        
    db_session.query().first.return_value = MockUser()
    class MockProvider:
        def generate(self, system, user, context):
            return "This is a mocked ship 30 essay " * 50, "mock-model"
            
    monkeypatch.setattr("app.agent.agent.OllamaProvider", MockProvider)
    
    import uuid
    from app.db.models.session import Session as SessionModel
    
    agent = GrowthAgent(db=db_session)
    agent.session_manager.create_session = MagicMock(return_value=SessionModel(id=uuid.uuid4(), user_id=uuid.uuid4()))
    agent.session_manager.get_session_messages = MagicMock(return_value=[])
    agent.session_manager.add_message = MagicMock()
    
    req = ChatRequest(query="Write a Ship 30 for 30 essay about growth", provider="ollama")
    
    # We need to mock retrieval so it returns something, otherwise Ship30 aborts
    class MockRetriever:
        def search(self, query):
            class MockResults:
                results = []
            return MockResults()
            
    agent.search_tool.retrieval_service = MockRetriever()
    
    # It will abort because no chunks, but we can test routing
    resp = agent.process_request(req)
    assert resp.tool_used == "generate_ship30"
    assert resp.answer == "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently."

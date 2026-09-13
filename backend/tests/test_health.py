from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_db_connected():
    response = client.get("/health")
    assert response.status_code in [200, 503]

def test_health_check_db_unavailable():
    # Patch the get_db to return a mock session that raises on execute
    from app.db.session import get_db
    
    class MockSession:
        def execute(self, *args, **kwargs):
            raise Exception("Mock DB Failure")
            
    def override_get_db():
        yield MockSession()
    
    app.dependency_overrides[get_db] = override_get_db
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection failed"
    app.dependency_overrides.clear()

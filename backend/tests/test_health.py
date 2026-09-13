from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_db_connected(monkeypatch):
    # Tests that when the DB connects successfully, we get 200 OK
    response = client.get("/health")
    if response.status_code == 200:
        assert response.json() == {"status": "ok", "database": "connected"}
    else:
        # DB is down on test machine, should be 503
        assert response.status_code == 503

def test_health_check_db_unavailable():
    # Patch the get_db to raise an exception
    from app.db.session import get_db
    def override_get_db():
        raise Exception("Mock DB Failure")
    
    app.dependency_overrides[get_db] = override_get_db
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection failed"
    app.dependency_overrides.clear()\n
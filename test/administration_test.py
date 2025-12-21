from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metadata():
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "last_update" in data

def test_health():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime" in data
    assert "dataset_loaded" in data

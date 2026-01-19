import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

# Test Health : Ici is_dataset_loaded est une FONCTION, 
# donc le patch passe un argument 'mock_load'
@patch("app.route.administration_routes.is_dataset_loaded")
def test_health(mock_load):
    mock_load.return_value = True
    response = client.get("/api/system/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["dataset_loaded"] is True

# Test Metadata : Ici on patch des VARIABLES (constantes).
# On ne met PAS d'arguments dans la fonction test_metadata.
@patch("app.route.administration_routes.VERSION", "1.0.0-test")
@patch("app.route.administration_routes.BUILD_DATE", "2025-01-01")
def test_metadata():
    response = client.get("/api/system/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0-test"
    assert data["last_update"] == "2025-01-01"
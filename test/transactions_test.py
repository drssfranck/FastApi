import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd

# Mock des données avant d'importer l'app
mock_trans_data = pd.DataFrame([{
    "id": 1,
    "date": "2025-12-20",
    "client_id": 101,
    "card_id": 1,
    "amount": 100.0,
    "use_chip": "Swipe Transaction",
    "merchant_id": 10,
    "merchant_city": "Paris",
    "merchant_state": "IDF",
    "zip": 75000,
    "mcc": 1234,
    "errors": None
}])

mock_card_data = pd.DataFrame([{
    "card_id": 1,
    "client_id": 101,
    "card_type": "Visa"
}])

# Patch avant import
with patch("app.data.load_data.load_card", return_value=mock_card_data), \
     patch("app.data.load_data.load_transactions", return_value=mock_trans_data):
    from app.main import app  
    client = TestClient(app)

# Test de la route racine
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Bienvenue dans l'API des transactions bancaires"
    assert "team" in data
    assert len(data["team"]) > 0

# Test d’une transaction par ID
def test_get_transaction_by_id():
    response = client.get("/api/transactions/1")
    if response.status_code == 200:
        data = response.json()
        assert data["id"] == 1
    else:
        assert response.status_code == 404

def test_get_transaction_types():
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert isinstance(data["types"], list)

def test_get_transactions():
    response = client.get("/api/transactions?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data
    assert len(data["data"]) <= 5

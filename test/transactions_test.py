import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from app.main import app # Import normal ici

client = TestClient(app)

# On prépare des données robustes
MOCK_TRANS = pd.DataFrame([{
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

# 1. Test de la route racine (Pas besoin de mock ici)
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# 2. Test d’une transaction par ID (Avec Mock Dynamique)
@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_by_id(mock_load):
    # On force la fonction appelée par la ROUTE à renvoyer notre DataFrame
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

# 3. Test des types de transactions
@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_types(mock_load):
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    # "Swipe Transaction" est dans notre MOCK_TRANS
    assert "Swipe Transaction" in data["types"]

# 4. Test de la liste des transactions
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions(mock_load):
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= 1
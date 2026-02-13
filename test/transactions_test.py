from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from app.main import app

client = TestClient(app)

# -------------------------------
# MOCK DATA
# -------------------------------
MOCK_TRANS = pd.DataFrame(
    [
        {
            "id": 1,
            "date": "2026-01-01",
            "client_id": 101,
            "card_id": 201,
            "amount": 100.0,
            "use_chip": "Swipe Transaction",
            "merchant_id": 301,
            "merchant_city": "Paris",
            "merchant_state": "IDF",
            "zip": 75001,
            "mcc": 1234,
            "errors": None,
            "step": 1,
            "client_id_dest": 102,
            "isFraud": 0,
        },
        {
            "id": 2,
            "date": "2026-01-02",
            "client_id": 101,
            "card_id": 202,
            "amount": 2000.0,
            "use_chip": "TRANSFER",
            "merchant_id": 302,
            "merchant_city": "Lyon",
            "merchant_state": "ARA",
            "zip": 69001,
            "mcc": 5678,
            "errors": None,
            "step": 2,
            "client_id_dest": 103,
            "isFraud": 1,
        },
        {
            "id": 3,
            "date": "2026-01-03",
            "client_id": 104,
            "card_id": 203,
            "amount": 500.0,
            "use_chip": "CASH_OUT",
            "merchant_id": 303,
            "merchant_city": "Marseille",
            "merchant_state": "PACA",
            "zip": 13001,
            "mcc": 9101,
            "errors": None,
            "step": 3,
            "client_id_dest": 101,
            "isFraud": 0,
        },
    ]
)

# -------------------------------
# TESTS DES ROUTES
# -------------------------------

# 1. Test GET types


@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_types(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert "Swipe Transaction" in data["types"]


# 2. Test GET transactions paginées


@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get("/api/transactions?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["data"]) == 2


# 3. Test GET transaction par ID


@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_by_id(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get("/api/transactions/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


# 4. Test GET transaction ID non existante


@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_by_id_not_found(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get("/api/transactions/999")
    assert response.status_code == 404
    assert "non trouvée" in response.json()["detail"]


# 5. Test POST recherche avancée


@patch("app.route.transaction_routes.load_transactions")
def test_search_transactions(mock_load):
    mock_load.return_value = MOCK_TRANS
    payload = {"type": "TRANSFER", "isFraud": 1, "amount_range": [1000, 5000]}
    response = client.post("/api/transactions/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["use_chip"] == "TRANSFER"


# 6. Test GET transactions récentes


@patch("app.route.transaction_routes.load_transactions")
def test_get_recent_transactions(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get("/api/transactions/recent?n=2")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert len(data["data"]) == 2


# 7. Test DELETE transaction


@patch("app.route.transaction_routes.load_transactions")
def test_delete_transaction(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.delete("/api/transactions/1")
    assert response.status_code == 200
    assert "supprimée" in response.json()["message"]


# 8. Test DELETE transaction non existante


@patch("app.route.transaction_routes.load_transactions")
def test_delete_transaction_not_found(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.delete("/api/transactions/999")
    assert response.status_code == 404


# 9. Test GET transactions par client (origine)


@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_by_customer(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get(
        "/api/transactions/by-customer/101?limit=10&offset=0"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(t["client_id"] == 101 for t in data["data"])


# 10. Test GET transactions par client (destination)


@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_to_customer(mock_load):
    mock_load.return_value = MOCK_TRANS
    response = client.get(
        "/api/transactions/to-customer/101?limit=10&offset=0"
    )
    assert response.status_code == 200
    data = response.json()
    assert any(t["client_id"] == 104 for t in data["data"])
    assert data["total"] >= 1


# 11. Test erreur FileNotFound


@patch("app.route.transaction_routes.load_transactions")
def test_transactions_file_not_found(mock_load):
    mock_load.side_effect = FileNotFoundError("Fichier introuvable")
    response = client.get("/api/transactions")
    assert response.status_code == 404


# 12. Test erreur générique
@patch("app.route.transaction_routes.load_transactions")
def test_transactions_generic_error(mock_load):
    mock_load.side_effect = Exception("Erreur")
    response = client.get("/api/transactions")
    assert response.status_code == 500

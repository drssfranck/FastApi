import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from app.main import app

client = TestClient(app)

# On prépare des données robustes pour les tests
MOCK_TRANS = pd.DataFrame([
    {
        "id": 1,
        "date": "2025-12-20",
        "client_id": 101,
        "originator_id": 101,
        "recipient_id": 202,
        "card_id": 1,
        "amount": 100.0,
        "type": "TRANSFER",
        "isFraud": 0,
        "use_chip": "Swipe Transaction",
        "merchant_id": 10,
        "merchant_city": "Paris",
        "merchant_state": "IDF",
        "zip": 75000,
        "mcc": 1234,
        "errors": None,
        "step": 1
    },
    {
        "id": 2,
        "date": "2025-12-21",
        "client_id": 101,
        "originator_id": 101,
        "recipient_id": 303,
        "card_id": 1,
        "amount": 2500.0,
        "type": "TRANSFER",
        "isFraud": 1,
        "use_chip": "Chip Transaction",
        "merchant_id": 20,
        "merchant_city": "Lyon",
        "merchant_state": "RA",
        "zip": 69000,
        "mcc": 5678,
        "errors": None,
        "step": 2
    },
    {
        "id": 3,
        "date": "2025-12-22",
        "client_id": 202,
        "originator_id": 202,
        "recipient_id": 101,
        "card_id": 2,
        "amount": 500.0,
        "type": "CASH_OUT",
        "isFraud": 0,
        "use_chip": "Swipe Transaction",
        "merchant_id": 30,
        "merchant_city": "Marseille",
        "merchant_state": "PACA",
        "zip": 13000,
        "mcc": 9999,
        "errors": None,
        "step": 3
    }
])


# ============ TESTS DES ROUTES =============

# 1. Test de la route racine
def test_read_root():
    """Test de la route racine de l'API"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "team" in response.json()


# 2. Test de la liste paginée des transactions
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions(mock_load):
    """Test GET /api/transactions - Liste paginée"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "transactions" in data
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["transactions"]) >= 1


# 3. Test de la liste paginée avec filtres
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_with_filters(mock_load):
    """Test GET /api/transactions avec filtres (type, isFraud, montants)"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions?page=1&limit=10&type=TRANSFER&isFraud=1&min_amount=1000&max_amount=5000")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data


# 4. Test d'une transaction par ID
@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_by_id(mock_load):
    """Test GET /api/transactions/{id} - Détails d'une transaction"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["amount"] == 100.0


# 5. Test d'une transaction par ID inexistante
@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_by_id_not_found(mock_load):
    """Test GET /api/transactions/{id} - Transaction non trouvée"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/999")
    assert response.status_code == 404
    assert "non trouvée" in response.json()["detail"]


# 6. Test des types de transactions
@patch("app.route.transaction_routes.load_transactions")
def test_get_transaction_types(mock_load):
    """Test GET /api/transactions/types - Liste des types"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/types")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert "Swipe Transaction" in data["types"]


# 7. Test de la recherche avancée POST
@patch("app.route.transaction_routes.load_transactions")
def test_search_transactions(mock_load):
    """Test POST /api/transactions/search - Recherche multicritère"""
    mock_load.return_value = MOCK_TRANS
    
    search_payload = {
        "type": "TRANSFER",
        "isFraud": 1,
        "amount_range": [1000, 5000]
    }
    
    response = client.post("/api/transactions/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data


# 8. Test de la recherche avancée avec type uniquement
@patch("app.route.transaction_routes.load_transactions")
def test_search_transactions_by_type(mock_load):
    """Test POST /api/transactions/search avec filtre type"""
    mock_load.return_value = MOCK_TRANS
    
    search_payload = {
        "type": "CASH_OUT",
        "isFraud": None,
        "amount_range": None
    }
    
    response = client.post("/api/transactions/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data


# 9. Test de la recherche avancée avec fraude
@patch("app.route.transaction_routes.load_transactions")
def test_search_transactions_by_fraud(mock_load):
    """Test POST /api/transactions/search avec filtre fraude"""
    mock_load.return_value = MOCK_TRANS
    
    search_payload = {
        "type": None,
        "isFraud": 1,
        "amount_range": None
    }
    
    response = client.post("/api/transactions/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data


# 10. Test des transactions récentes
@patch("app.route.transaction_routes.load_transactions")
def test_get_recent_transactions(mock_load):
    """Test GET /api/transactions/recent - N dernières transactions"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/recent?n=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "transactions" in data or "data" in data


# 11. Test de la suppression d'une transaction
@patch("app.route.transaction_routes.load_transactions")
def test_delete_transaction(mock_load):
    """Test DELETE /api/transactions/{id} - Suppression"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.delete("/api/transactions/1")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "supprimée" in data["message"]


# 12. Test de la suppression d'une transaction inexistante
@patch("app.route.transaction_routes.load_transactions")
def test_delete_transaction_not_found(mock_load):
    """Test DELETE /api/transactions/{id} - Non trouvée"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.delete("/api/transactions/999")
    assert response.status_code == 404


# 13. Test des transactions par client (origine)
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_by_customer(mock_load):
    """Test GET /api/transactions/by-customer/{customer_id} - Transactions envoyées"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/by-customer/101?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "customer_id" in data
    assert data["customer_id"] == 101
    assert "transactions" in data
    assert "page" in data
    assert "total" in data


# 14. Test des transactions reçues par client (destination)
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_to_customer(mock_load):
    """Test GET /api/transactions/to-customer/{customer_id} - Transactions reçues"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/to-customer/101?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "customer_id" in data
    assert data["customer_id"] == 101
    assert "transactions" in data
    assert "page" in data
    assert "total" in data


# 15. Test des transactions par client avec pagination
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_by_customer_pagination(mock_load):
    """Test pagination pour transactions par client"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/by-customer/101?page=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) <= 1


# 16. Test des transactions reçues par client avec pagination
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_to_customer_pagination(mock_load):
    """Test pagination pour transactions reçues par client"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions/to-customer/101?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert "transactions" in data


# 17. Test liste paginée avec page > 1
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_page_2(mock_load):
    """Test pagination avec page > 1"""
    mock_load.return_value = MOCK_TRANS
    
    response = client.get("/api/transactions?page=2&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert "transactions" in data


# 18. Test d'erreur lors du chargement des transactions
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_file_not_found(mock_load):
    """Test gestion d'erreur FileNotFoundError"""
    mock_load.side_effect = FileNotFoundError("Fichier introuvable")
    
    response = client.get("/api/transactions")
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"]


# 19. Test d'erreur générale
@patch("app.route.transaction_routes.load_transactions")
def test_get_transactions_generic_error(mock_load):
    """Test gestion d'erreur générique"""
    mock_load.side_effect = Exception("Erreur base de données")
    
    response = client.get("/api/transactions")
    assert response.status_code == 500


# 20. Test recherche sans résultat
@patch("app.route.transaction_routes.load_transactions")
def test_search_transactions_no_result(mock_load):
    """Test recherche sans résultat"""
    mock_load.return_value = MOCK_TRANS
    
    search_payload = {
        "type": "TYPE_INEXISTANT",
        "isFraud": None,
        "amount_range": None
    }
    
    response = client.post("/api/transactions/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["transactions"]) == 0

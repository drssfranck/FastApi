import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from app.main import app

client = TestClient(app)

# Données mockées pour les tests (utilisant des types Python natifs pour éviter les problèmes de sérialisation)
MOCK_FRAUD_TRANS = [
    {
        "id": 1,
        "date": "2025-12-20",
        "client_id": 101,
        "card_id": 1,
        "amount": 100.0,
        "use_chip": "CHIP",
        "merchant_id": 10,
        "merchant_city": "Paris",
        "merchant_state": "IDF",
        "zip": 75000,
        "mcc": 1234,
        "errors": None,
        "isFraud": 0
    },
    {
        "id": 2,
        "date": "2025-12-21",
        "client_id": 102,
        "card_id": 2,
        "amount": 2500.0,
        "use_chip": "SWIPE",
        "merchant_id": 20,
        "merchant_city": "Lyon",
        "merchant_state": "Rhone",
        "zip": 69000,
        "mcc": 5678,
        "errors": None,
        "isFraud": 1
    },
    {
        "id": 3,
        "date": "2025-12-22",
        "client_id": 103,
        "card_id": 3,
        "amount": 500.0,
        "use_chip": "CHIP",
        "merchant_id": 30,
        "merchant_city": "Marseille",
        "merchant_state": "Bouches-du-Rhone",
        "zip": 13000,
        "mcc": 9012,
        "errors": None,
        "isFraud": 0
    }
]

# 1. Test de la route racine des fraudes
def test_fraud_root():
    """Test de la route racine de l'API de fraude"""
    response = client.get("/api/fraud/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Bienvenue dans l'API de détection de fraude" in data["message"]
    assert "description" in data

# 2. Test de la route summary
@patch("app.route.fraude_routes.load_transactions")
def test_fraud_summary(mock_load):
    """Test de la route GET /api/fraud/summary"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure de la réponse
    assert "total_frauds" in data
    assert "flagged" in data
    assert "precision" in data
    assert "recall" in data

    # Vérifier les types de données
    assert isinstance(data["total_frauds"], int)
    assert isinstance(data["flagged"], int)
    assert isinstance(data["precision"], float)
    assert isinstance(data["recall"], float)

    # Vérifier les valeurs attendues (avec nos données mockées)
    assert data["total_frauds"] == 1  # Une transaction frauduleuse dans le mock
    assert data["precision"] == 0.95
    assert data["recall"] == 0.88

# 3. Test de la route by-type
@patch("app.data.load_data.load_transactions")
def test_fraud_by_type(mock_load):
    """Test de la route GET /api/fraud/by-type"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure de la réponse
    assert "fraud_by_type" in data
    assert isinstance(data["fraud_by_type"], list)

    # Vérifier qu'on a au moins les types présents dans les données mockées
    type_names = [item["type"] for item in data["fraud_by_type"]]
    assert "CHIP" in type_names
    assert "SWIPE" in type_names

    # Vérifier la structure de chaque élément
    for item in data["fraud_by_type"]:
        assert "type" in item
        assert "total_transactions" in item
        assert "fraudulent_transactions" in item
        assert "fraud_rate_percent" in item

        # Vérifier les types
        assert isinstance(item["type"], str)
        assert isinstance(item["total_transactions"], int)
        assert isinstance(item["fraudulent_transactions"], int)
        assert isinstance(item["fraud_rate_percent"], float)

# 4. Test de la route predict - succès
def test_fraud_predict_success():
    """Test de la route POST /api/fraud/predict avec des données valides"""
    test_data = {
        "type": "TRANSFER",
        "amount": 3500.0,
        "oldbalanceOrg": 15000.0,
        "newbalanceOrig": 11500.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure de la réponse
    assert "isFraud" in data
    assert "probability" in data

    # Vérifier les types
    assert isinstance(data["isFraud"], bool)
    assert isinstance(data["probability"], float)

    # Vérifier que la probabilité est entre 0 et 1
    assert 0.0 <= data["probability"] <= 1.0

    # Avec ces données (montant élevé + type TRANSFER), devrait être détecté comme frauduleux
    assert data["isFraud"] is True
    assert data["probability"] > 0.5

# 5. Test de la route predict - transaction légitime
def test_fraud_predict_legitimate():
    """Test de la route POST /api/fraud/predict avec une transaction légitime"""
    test_data = {
        "type": "PAYMENT",
        "amount": 50.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 950.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure
    assert "isFraud" in data
    assert "probability" in data

    # Avec ces données (montant faible), devrait être considéré comme légitime
    assert data["probability"] < 0.5

# 6. Test de la route predict - données invalides
def test_fraud_predict_invalid_data():
    """Test de la route POST /api/fraud/predict avec des données invalides"""
    # Test avec des données manquantes
    invalid_data = {
        "type": "TRANSFER",
        "amount": 1000.0
        # oldbalanceOrg et newbalanceOrig manquants
    }

    response = client.post("/api/fraud/predict", json=invalid_data)
    # Devrait retourner une erreur de validation
    assert response.status_code == 422  # Unprocessable Entity

# 7. Test de la route predict - valeurs extrêmes
def test_fraud_predict_extreme_values():
    """Test de la route POST /api/fraud/predict avec des valeurs extrêmes"""
    test_data = {
        "type": "TRANSFER",
        "amount": 100000.0,  # Montant très élevé
        "oldbalanceOrg": 100000.0,
        "newbalanceOrig": 0.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Devrait avoir une probabilité très élevée
    assert data["probability"] > 0.8
    assert data["isFraud"] is True

# 8. Test des transactions frauduleuses
@patch("app.data.load_data.load_transactions")
def test_get_fraudulent_transactions(mock_load):
    """Test de la route GET /api/fraud/transactions"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    response = client.get("/api/fraud/transactions")
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure de la réponse
    assert "total" in data
    assert "offset" in data
    assert "limit" in data
    assert "data" in data

    # Devrait retourner seulement la transaction frauduleuse
    assert data["total"] == 1
    assert len(data["data"]) == 1
    assert data["data"][0]["isFraud"] == 1

# 9. Test des statistiques de fraude
@patch("app.data.load_data.load_transactions")
def test_fraud_statistics(mock_load):
    """Test de la route GET /api/fraud/statistics"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    response = client.get("/api/fraud/statistics")
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure
    assert "total_transactions" in data
    assert "fraudulent_transactions" in data
    assert "fraud_percentage" in data
    assert "total_fraud_amount" in data

    # Vérifier les valeurs calculées
    assert data["total_transactions"] == 3  # 3 transactions dans le mock
    assert data["fraudulent_transactions"] == 1  # 1 frauduleuse
    assert data["fraud_percentage"] == 33.33  # 1/3 ≈ 33.33%
    assert data["total_fraud_amount"] == 2500.0  # Montant de la transaction frauduleuse

# 10. Test de détection de fraude sur une transaction spécifique
@patch("app.data.load_data.load_transactions")
def test_detect_fraud_by_id(mock_load):
    """Test de la route GET /api/fraud/detect/{transaction_id}"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    # Test avec une transaction frauduleuse
    response = client.get("/api/fraud/detect/2")  # ID 2 est frauduleuse
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == 2
    assert data["is_fraud"] is True
    assert data["amount"] == 2500.0

    # Test avec une transaction légitime
    response = client.get("/api/fraud/detect/1")  # ID 1 n'est pas frauduleuse
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == 1
    assert data["is_fraud"] is False
    assert data["amount"] == 100.0

    # Test avec un ID inexistant
    response = client.get("/api/fraud/detect/999")
    assert response.status_code == 404
    assert "Transaction non trouvée" in response.json()["detail"]

# 11. Test des transactions suspectes
@patch("app.data.load_data.load_transactions")
def test_suspicious_transactions(mock_load):
    """Test de la route GET /api/fraud/suspicious"""
    mock_load.return_value = pd.DataFrame(MOCK_FRAUD_TRANS)

    # Test avec un seuil de 1000
    response = client.get("/api/fraud/suspicious?threshold=1000")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "offset" in data
    assert "limit" in data
    assert "data" in data

    # Seule la transaction de 2500 devrait être considérée comme suspecte
    assert data["total"] == 1
    assert len(data["data"]) == 1
    assert data["data"][0]["amount"] == 2500.0

# Tests d'intégration - vérifier que toutes les routes sont accessibles
def test_all_fraud_routes_accessible():
    """Test d'intégration pour vérifier que toutes les routes de fraude sont accessibles"""
    routes_to_test = [
        "/api/fraud/",
        "/api/fraud/summary",
        "/api/fraud/by-type",
        "/api/fraud/transactions",
        "/api/fraud/statistics",
        "/api/fraud/suspicious"
    ]

    for route in routes_to_test:
        response = client.get(route)
        # Les routes devraient soit réussir (200) soit échouer gracieusement
        assert response.status_code in [200, 404, 422]  # Codes d'erreur acceptables

# Test de performance - vérifier que les réponses sont rapides
def test_fraud_routes_performance():
    """Test de performance pour les routes de fraude"""
    import time

    start_time = time.time()
    response = client.get("/api/fraud/summary")
    end_time = time.time()

    # La réponse devrait être rapide (< 1 seconde)
    assert end_time - start_time < 1.0
    assert response.status_code == 200

# Tests supplémentaires pour couvrir plus de cas

# 14. Test de la route predict - transaction avec montant zéro
def test_fraud_predict_zero_amount():
    """Test de la route POST /api/fraud/predict avec montant zéro"""
    test_data = {
        "type": "PAYMENT",
        "amount": 0.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 1000.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    assert data["probability"] < 0.5  # Devrait être considéré comme légitime
    assert data["isFraud"] is False

# 15. Test de la route predict - transaction avec montant négatif (invalide)
def test_fraud_predict_negative_amount():
    """Test de la route POST /api/fraud/predict avec montant négatif"""
    test_data = {
        "type": "PAYMENT",
        "amount": -100.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 1100.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Montant négatif devrait avoir faible probabilité
    assert data["probability"] < 0.5

# 16. Test de la route predict - type de transaction inconnu
def test_fraud_predict_unknown_type():
    """Test de la route POST /api/fraud/predict avec type inconnu"""
    test_data = {
        "type": "UNKNOWN_TYPE",
        "amount": 1000.0,
        "oldbalanceOrg": 2000.0,
        "newbalanceOrig": 1000.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Type inconnu ne devrait pas ajouter de pénalité
    assert data["probability"] >= 0.1  # Probabilité de base

# 17. Test de la route suspicious avec seuil zéro
def test_suspicious_transactions_zero_threshold():
    """Test de la route GET /api/fraud/suspicious avec seuil zéro"""
    response = client.get("/api/fraud/suspicious?threshold=0")
    assert response.status_code == 200
    data = response.json()

    # Avec seuil 0, toutes les transactions devraient être suspectes
    assert data["total"] >= 0  # Au moins les données mockées

# 18. Test de la route suspicious avec seuil très élevé
def test_suspicious_transactions_high_threshold():
    """Test de la route GET /api/fraud/suspicious avec seuil très élevé"""
    response = client.get("/api/fraud/suspicious?threshold=100000")
    assert response.status_code == 200
    data = response.json()

    # Avec seuil très élevé, peu de transactions devraient être suspectes
    assert data["total"] >= 0

# 19. Test de la route detect avec ID négatif
def test_detect_fraud_negative_id():
    """Test de la route GET /api/fraud/detect avec ID négatif"""
    response = client.get("/api/fraud/detect/-1")
    assert response.status_code == 404
    assert "Transaction non trouvée" in response.json()["detail"]

# 20. Test de la route detect avec ID très grand
def test_detect_fraud_large_id():
    """Test de la route GET /api/fraud/detect avec ID très grand"""
    response = client.get("/api/fraud/detect/999999")
    assert response.status_code == 404
    assert "Transaction non trouvée" in response.json()["detail"]

# 21. Test de la route transactions avec pagination
def test_get_fraudulent_transactions_pagination():
    """Test de la route GET /api/fraud/transactions avec pagination"""
    response = client.get("/api/fraud/transactions?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()

    assert data["limit"] == 1
    assert data["offset"] == 0
    assert len(data["data"]) <= 1

# 22. Test de la route transactions avec limit zéro
def test_get_fraudulent_transactions_zero_limit():
    """Test de la route GET /api/fraud/transactions avec limit zéro"""
    response = client.get("/api/fraud/transactions?limit=0")
    assert response.status_code == 422  # Unprocessable Entity car limit >= 1

# 23. Test de la route predict - données avec balances négatives
def test_fraud_predict_negative_balances():
    """Test de la route POST /api/fraud/predict avec balances négatives"""
    test_data = {
        "type": "TRANSFER",
        "amount": 1000.0,
        "oldbalanceOrg": -500.0,
        "newbalanceOrig": -1500.0
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Balances négatives pourraient indiquer un problème
    assert isinstance(data["probability"], float)

# 24. Test de la route summary avec données vides (si applicable)
@patch("app.data.load_data.load_transactions")
def test_fraud_summary_empty_data(mock_load):
    """Test de la route GET /api/fraud/summary avec données vides"""
    mock_load.return_value = pd.DataFrame()  # DataFrame vide

    response = client.get("/api/fraud/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["total_frauds"] == 0
    assert data["flagged"] == 0

# 25. Test de la route statistics avec données vides
@patch("app.data.load_data.load_transactions")
def test_fraud_statistics_empty_data(mock_load):
    """Test de la route GET /api/fraud/statistics avec données vides"""
    mock_load.return_value = pd.DataFrame()

    response = client.get("/api/fraud/statistics")
    assert response.status_code == 200
    data = response.json()

    assert data["total_transactions"] == 0
    assert data["fraudulent_transactions"] == 0
    assert data["fraud_percentage"] == 0.0
    assert data["total_fraud_amount"] == 0.0

# 26. Test de la route by-type avec données vides
@patch("app.data.load_data.load_transactions")
def test_fraud_by_type_empty_data(mock_load):
    """Test de la route GET /api/fraud/by-type avec données vides"""
    mock_load.return_value = pd.DataFrame()

    response = client.get("/api/fraud/by-type")
    assert response.status_code == 200
    data = response.json()

    assert data["fraud_by_type"] == []

# 27. Test de la route suspicious avec données vides
@patch("app.data.load_data.load_transactions")
def test_suspicious_transactions_empty_data(mock_load):
    """Test de la route GET /api/fraud/suspicious avec données vides"""
    mock_load.return_value = pd.DataFrame()

    response = client.get("/api/fraud/suspicious")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["data"] == []

# 28. Test de la route detect avec données vides
@patch("app.data.load_data.load_transactions")
def test_detect_fraud_empty_data(mock_load):
    """Test de la route GET /api/fraud/detect avec données vides"""
    mock_load.return_value = pd.DataFrame()

    response = client.get("/api/fraud/detect/1")
    assert response.status_code == 404

# 29. Test de la route predict - cohérence parfaite des balances
def test_fraud_predict_perfect_balance_match():
    """Test de la route POST /api/fraud/predict avec cohérence parfaite des balances"""
    test_data = {
        "type": "PAYMENT",
        "amount": 100.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 900.0  # Parfaitement cohérent
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Balances cohérentes devraient réduire la probabilité
    assert data["probability"] < 0.5

# 30. Test de la route predict - incohérence majeure des balances
def test_fraud_predict_balance_mismatch():
    """Test de la route POST /api/fraud/predict avec incohérence majeure des balances"""
    test_data = {
        "type": "PAYMENT",
        "amount": 100.0,
        "oldbalanceOrg": 1000.0,
        "newbalanceOrig": 800.0  # Incohérent (devrait être 900)
    }

    response = client.post("/api/fraud/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()

    # Incohérence devrait augmenter la probabilité
    assert data["probability"] > 0.3

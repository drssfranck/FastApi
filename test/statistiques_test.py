# test_stats_routes.py
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from fastapi import FastAPI
from app.route.statistiques_routes import stat_router

# ---------------- Setup de l'application ----------------
app = FastAPI()
app.include_router(stat_router)
client = TestClient(app)

# ---------------- Données mock ----------------
MOCK_TRANSACTIONS = pd.DataFrame(
    [
        {
            "id": 1,
            "date": "2026-01-24",
            "client_id": 101,
            "card_id": 5001,
            "amount": 100.0,
            "use_chip": "chip",
            "merchant_id": 2001,
            "merchant_city": "Paris",
            "merchant_state": "Ile-de-France",
            "zip": 75001,
            "mcc": 5411,
            "errors": None,
        },
        {
            "id": 2,
            "date": "2026-01-23",
            "client_id": 102,
            "card_id": 5002,
            "amount": 500.0,
            "use_chip": "swipe",
            "merchant_id": 2002,
            "merchant_city": "Lyon",
            "merchant_state": "Auvergne-Rhône-Alpes",
            "zip": 69001,
            "mcc": 5812,
            "errors": None,
        },
        {
            "id": 3,
            "date": "2026-01-24",
            "client_id": 103,
            "card_id": 5003,
            "amount": 1000.0,
            "use_chip": "chip",
            "merchant_id": 2003,
            "merchant_city": "Marseille",
            "merchant_state": "Provence-Alpes-Côte d'Azur",
            "zip": 13001,
            "mcc": 5411,
            "errors": None,
        },
    ]
)

MOCK_FRAUD = pd.DataFrame(
    [
        {"transaction_id": 1, "is_fraud": "Yes"},
        {"transaction_id": 2, "is_fraud": "No"},
        {"transaction_id": 3, "is_fraud": "Yes"},
    ]
)

# ---------------- Tests pour /api/stats/overview ----------------


@patch("app.route.statistiques_routes.load_transactions")
@patch("app.route.statistiques_routes.load_train_fraud")
def test_get_stats_overview(mock_load_fraud, mock_load_tx):
    mock_load_tx.return_value = MOCK_TRANSACTIONS
    mock_load_fraud.return_value = MOCK_FRAUD

    response = client.get("/api/stats/overview")
    assert response.status_code == 200

    data = response.json()
    assert data["total_transactions"] == len(MOCK_TRANSACTIONS)
    assert data["fraud_rate"] == round(2 / 3, 5)  # 2 fraudes sur 3
    assert data["avg_amount"] == round(MOCK_TRANSACTIONS["amount"].mean(), 2)
    assert data["most_common_type"] == "chip"


# ---------------- Tests pour /api/stats/amount-distribution ----------------


@patch("app.route.statistiques_routes.load_transactions")
def test_get_amount_distribution(mock_load_tx):
    mock_load_tx.return_value = MOCK_TRANSACTIONS

    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200

    data = response.json()
    assert data["bins"] == ["0-100", "100-500", "500-1000", "1000-5000"]
    # Vérifier que les comptes correspondent
    assert sum(data["counts"]) == len(MOCK_TRANSACTIONS)


# ---------------- Tests pour /api/stats/by-type ----------------


@patch("app.route.statistiques_routes.load_transactions")
def test_get_stats_by_type(mock_load_tx):
    mock_load_tx.return_value = MOCK_TRANSACTIONS

    response = client.get("/api/stats/by-type")
    assert response.status_code == 200

    data = response.json()
    # Vérifier que chaque type est présent
    types = set([d["type"] for d in data])
    assert types == set(MOCK_TRANSACTIONS["use_chip"].unique())


# ---------------- Tests pour /api/stats/daily ----------------


@patch("app.route.statistiques_routes.load_transactions")
def test_get_daily_stats(mock_load_tx):
    mock_load_tx.return_value = MOCK_TRANSACTIONS

    response = client.get("/api/stats/daily")
    assert response.status_code == 200

    data = response.json()
    # Vérifier que chaque date du mock est présente
    mock_dates = set(
        pd.to_datetime(MOCK_TRANSACTIONS["date"]).dt.date.astype(str)
    )
    response_dates = set([d["date"] for d in data])
    assert mock_dates == response_dates

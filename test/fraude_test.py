import pandas as pd
from app.route import fraude_routes as fraud


def mock_prepare_df():
    return pd.DataFrame([
        {
            "id": "1",
            "is_fraud": "Yes",
            "errors": "E1",
            "use_chip": "CHIP"
        },
        {
            "id": "2",
            "is_fraud": "No",
            "errors": None,
            "use_chip": "SWIPE"
        },
        {
            "id": "3",
            "is_fraud": "Yes",
            "errors": "E2",
            "use_chip": "CHIP"
        },
    ])


# -----------------------------
# /api/fraud/summary
# -----------------------------
def test_fraud_summary(client, monkeypatch):
    monkeypatch.setattr(
        fraud,
        "prepare_fraud_merge",
        mock_prepare_df
    )

    response = client.get("/api/fraud/summary")
    data = response.json()

    assert response.status_code == 200
    assert data["total_frauds"] == 2
    assert data["flagged"] == 2
    assert data["precision"] == 1.0
    assert data["recall"] == 1.0


# -----------------------------
# /api/fraud/by-type
# -----------------------------
def test_fraud_by_type(client, monkeypatch):
    monkeypatch.setattr(
        fraud,
        "prepare_fraud_merge",
        mock_prepare_df
    )

    response = client.get("/api/fraud/by-type")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)

    chip = next(item for item in data if item["type"] == "CHIP")
    assert chip["fraud_rate"] == 1.0
    assert chip["total_transactions"] == 2


# -----------------------------
# /api/fraud/predict
# -----------------------------
def test_predict_fraud_positive(client):
    payload = {
        "amount": 2000,
        "type": "TRANSFER",
        "oldbalanceOrg": 5000,
        "newbalanceOrig": 2000
    }

    response = client.post("/api/fraud/predict", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["isFraud"] is True
    assert data["probability"] >= 0.5


def test_predict_fraud_negative(client):
    payload = {
        "amount": 100,
        "type": "PAYMENT",
        "oldbalanceOrg": 1000,
        "newbalanceOrig": 900
    }

    response = client.post("/api/fraud/predict", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["isFraud"] is False
    assert data["probability"] < 0.5

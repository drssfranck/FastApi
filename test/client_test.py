import pytest
import pandas as pd
from fastapi.testclient import TestClient
from app.route import clients_routes as client_module

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_users_df():
    return pd.DataFrame([
        {
            "id": 1,
            "current_age": 30,
            "gender": "M",
            "yearly_income": "50000",
            "credit_score": 700,
            "address": "Paris"
        },
        {
            "id": 2,
            "current_age": 40,
            "gender": "F",
            "yearly_income": "70000",
            "credit_score": 750,
            "address": "Lyon"
        }
    ])


@pytest.fixture
def mock_transactions_df():
    return pd.DataFrame([
        {"client_id": 1, "amount": 100.0},
        {"client_id": 1, "amount": 200.0},
        {"client_id": 2, "amount": 300.0},
    ])

def test_get_client_cards_success(
    client,
    mock_users_df,
    monkeypatch
):

    monkeypatch.setattr(
        client_module,
        "load_user_data",
        lambda: mock_users_df
    )

    response = client.get("/api/client/1")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[0]["current_age"] == 30

def test_get_client_cards_not_found(
    client,
    mock_users_df,
    monkeypatch
):

    monkeypatch.setattr(
        client_module,
        "load_user_data",
        lambda: mock_users_df
    )

    response = client.get("/api/client/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found or no cards available."

def test_get_top_customers_success(
    client,
    mock_users_df,
    mock_transactions_df,
    monkeypatch
):

    monkeypatch.setattr(
        client_module,
        "load_user_data",
        lambda: mock_users_df
    )
    monkeypatch.setattr(
        client_module,
        "load_transactions",
        lambda: mock_transactions_df
    )

    response = client.get("/api/customers/top?n=2")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["client_id"] == 1 or data[0]["client_id"] == 2
    assert "total_spent" in data[0]
    assert "profile" in data[0]

def test_get_top_customers_invalid_n(client):
    response = client.get("/api/customers/top?n=0")

    assert response.status_code == 422

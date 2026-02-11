import pandas as pd
from app.route import administration_routes as admin


def test_health_all_datasets_loaded(client, monkeypatch):
    df = pd.DataFrame([{"a": 1}])

    monkeypatch.setattr(admin, "_transactions_df", df)
    monkeypatch.setattr(admin, "_train_fraud_df", df)
    monkeypatch.setattr(admin, "_mcc_codes_df", df)
    monkeypatch.setattr(admin, "_user_data_df", df)
    monkeypatch.setattr(admin, "_df_card_data", df)

    response = client.get("/api/system/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["dataset_loaded"] is True
    assert "uptime" in data
    assert "latency" in data
    assert data["details"]["missing_datasets"] == []


def test_health_missing_dataset(client, monkeypatch):
    df = pd.DataFrame([{"a": 1}])

    monkeypatch.setattr(admin, "_transactions_df", df)
    monkeypatch.setattr(admin, "_train_fraud_df", None)
    monkeypatch.setattr(admin, "_mcc_codes_df", df)
    monkeypatch.setattr(admin, "_user_data_df", df)
    monkeypatch.setattr(admin, "_df_card_data", df)

    response = client.get("/api/system/health")
    data = response.json()

    assert data["status"] == "degraded"
    assert data["dataset_loaded"] is False
    assert "fraud_labels" in data["details"]["missing_datasets"]


def test_metadata_success(client, tmp_path, monkeypatch):
    monkeypatch.setattr(
        admin, "load_project_metadata", lambda: {"version": "1.2.3"}
    )

    monkeypatch.setattr(admin.Path, "exists", lambda self: True)

    monkeypatch.setattr(admin.os.path, "getmtime", lambda _: 1700000000)

    response = client.get("/api/system/metadata")
    data = response.json()

    assert data["version"] == "1.2.3"
    assert data["last_update"].endswith("Z")


def test_metadata_no_pyproject(client, monkeypatch):
    monkeypatch.setattr(admin, "load_project_metadata", lambda: {})
    monkeypatch.setattr(admin.Path, "exists", lambda self: False)

    response = client.get("/api/system/metadata")
    data = response.json()

    assert data["version"] == "0.0.0"
    assert data["last_update"] == "unknown"

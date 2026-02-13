# test/test_load_data.py
import pandas as pd
from unittest.mock import patch, mock_open

import app.data.load_data as ld


# ---------------------------------------
# Test load_transactions
# ---------------------------------------
@patch("app.data.load_data.pd.read_csv")
def test_load_transactions(mock_read_csv):
    # Création d'un DataFrame fictif
    data = {
        "amount": ["$100.0", "$200.0"],
        "date": ["2026-01-01", "2026-02-01"],
        "use_chip": [1, None],
        "merchant_id": ["m1", "m2"]
    }
    df_mock = pd.DataFrame(data)

    # pd.read_csv doit renvoyer un itérable pour chunksize
    mock_read_csv.return_value = [df_mock]

    # Appel de la fonction
    df = ld.load_transactions(chunksize=1)

    # Vérifications
    assert isinstance(df, pd.DataFrame)
    assert df["amount"].dtype == float
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    # Vérifier les NaN avec pd.isna()
    assert pd.isna(df["use_chip"].iloc[1])
    assert df.shape[0] == 2


# ---------------------------------------
# Test load_card
# ---------------------------------------
@patch("app.data.load_data.pd.read_csv")
def test_load_card(mock_read_csv):
    df_mock = pd.DataFrame({"card_number": [1, 2]})
    mock_read_csv.return_value = df_mock

    df = ld.load_card()
    assert isinstance(df, pd.DataFrame)
    assert "card_number" in df.columns


# ---------------------------------------
# Test load_mcc_codes
# ---------------------------------------
@patch("app.data.load_data.pd.read_json")
def test_load_mcc_codes(mock_read_json):
    df_mock = pd.DataFrame({"mcc_code": [1234]})
    mock_read_json.return_value = df_mock

    df = ld.load_mcc_codes()
    assert isinstance(df, pd.DataFrame)
    assert "mcc_code" in df.columns


# ---------------------------------------
# Test load_train_fraud
# ---------------------------------------
@patch("builtins.open", new_callable=mock_open,
       read_data='{"target": {"1": "Yes"}}')
def test_load_train_fraud(mock_file):
    df = ld.load_train_fraud()
    assert isinstance(df, pd.DataFrame)
    assert "transaction_id" in df.columns
    assert "is_fraud" in df.columns
    assert df["transaction_id"].iloc[0] == 1
    assert df["is_fraud"].iloc[0] == "Yes"


# ---------------------------------------
# Test load_user_data
# ---------------------------------------
@patch("app.data.load_data.pd.read_csv")
def test_load_user_data(mock_read_csv):
    df_mock = pd.DataFrame({"user_id": [1, 2]})
    mock_read_csv.return_value = df_mock

    df = ld.load_user_data()
    assert isinstance(df, pd.DataFrame)
    assert "user_id" in df.columns


# ---------------------------------------
# Test is_dataset_loaded
# ---------------------------------------
def test_is_dataset_loaded(monkeypatch):
    # Tout est None
    monkeypatch.setattr(ld, "_transactions_df", None)
    monkeypatch.setattr(ld, "_df_card_data", None)
    monkeypatch.setattr(ld, "_mcc_codes_df", None)
    monkeypatch.setattr(ld, "_train_fraud_df", None)
    monkeypatch.setattr(ld, "_user_data_df", None)

    assert ld.is_dataset_loaded() is False

    # Remplir toutes les variables
    monkeypatch.setattr(ld, "_transactions_df", pd.DataFrame())
    monkeypatch.setattr(ld, "_df_card_data", pd.DataFrame())
    monkeypatch.setattr(ld, "_mcc_codes_df", pd.DataFrame())
    monkeypatch.setattr(ld, "_train_fraud_df", pd.DataFrame())
    monkeypatch.setattr(ld, "_user_data_df", pd.DataFrame())

    assert ld.is_dataset_loaded() is True

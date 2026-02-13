from pathlib import Path
import pandas as pd

DATA_DIR = Path("app/data/dataset")

_transactions_df = None
_df_card_data = None
_mcc_codes_df = None
_train_fraud_df = None
_user_data_df = None


def load_transactions(chunksize=50_000) -> pd.DataFrame:
    """Charge les transactions en paquets puis renvoie un DataFrame complet
    avec nettoyage."""
    global _transactions_df

    if _transactions_df is None:
        try:
            reader = pd.read_csv(
                DATA_DIR / "transactions_data.csv", chunksize=chunksize
            )
            _transactions_df = pd.concat(reader, ignore_index=True)

            # Nettoyer le montant : enlever $ et convertir en float
            _transactions_df["amount"] = (
                _transactions_df["amount"]
                .replace(r"[\$,]", "", regex=True)
                .astype(float)
            )

            # Convertir les dates en datetime
            _transactions_df["date"] = pd.to_datetime(
                _transactions_df["date"], errors="coerce"
            )

            # Remplacer les NaN des colonnes optionnelles par None
            optional_cols = [
                "use_chip",
                "merchant_id",
                "merchant_city",
                "merchant_state",
                "zip",
                "mcc",
                "errors",
            ]
            for col in optional_cols:
                if col in _transactions_df.columns:
                    _transactions_df[col] = _transactions_df[col].where(
                        pd.notna(_transactions_df[col]), None
                    )

        except FileNotFoundError:
            raise FileNotFoundError(
                "Fichier transactions_data.csv introuvable"
            )
        except Exception as e:
            raise Exception(f"Erreur lors du chargement des transactions: {e}")

    return _transactions_df


def load_card():
    """Charge les données de cartes à partir du fichier csv."""

    global _df_card_data
    _df_card_data = pd.read_csv(DATA_DIR / "cards_data.csv")

    return _df_card_data


def load_mcc_codes():
    """Charge les codes MCC à partir du fichier csv."""

    global _mcc_codes_df
    _mcc_codes_df = pd.read_json(DATA_DIR / "mcc_codes.json")

    return _mcc_codes_df


def load_train_fraud() -> pd.DataFrame:
    """Charge les labels de fraude à partir du fichier JSON."""
    global _train_fraud_df

    # On ne charge que si la variable globale est vide (None)
    if _train_fraud_df is None:
        file_path = DATA_DIR / "train_fraud_labels.json"
        try:
            # Lecture directe du dictionnaire
            import json

            with open(file_path, "r") as f:
                data = json.load(f)

            # Conversion de la clé "target" en DataFrame
            # .items() crée deux colonnes : l'index (ID) et la valeur (Yes/No)
            _train_fraud_df = pd.DataFrame(
                list(data["target"].items()),
                columns=["transaction_id", "is_fraud"],
            )

            # Optimisation optionnelle : convertir les ID en numérique
            _train_fraud_df["transaction_id"] = pd.to_numeric(
                _train_fraud_df["transaction_id"]
            )

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Fichier {file_path.name} introuvable dans {DATA_DIR}"
            )
        except Exception as e:
            raise Exception(f"Erreur lors du chargement des labels: {e}")

    return _train_fraud_df


def load_user_data():
    """Charge les données utilisateur à partir du fichier csv."""

    global _user_data_df
    _user_data_df = pd.read_csv(DATA_DIR / "users_data.csv")

    return _user_data_df


def is_dataset_loaded() -> bool:
    missing = []
    if _user_data_df is None:
        missing.append("users")
    if _df_card_data is None:
        missing.append("cards")
    if _mcc_codes_df is None:
        missing.append("mcc")
    if _train_fraud_df is None:
        missing.append("fraud")
    if _transactions_df is None:
        missing.append("transactions")

    if missing:
        print(f"Datasets non chargés : {', '.join(missing)}")
        return False
    return True

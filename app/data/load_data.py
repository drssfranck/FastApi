from pathlib import Path
import pandas as pd

DATA_DIR = Path("app/data/dataset") 

_transactions_df = None
_df_card_data = None



def load_transactions(chunksize=50_000) -> pd.DataFrame:
    """Charge les transactions en paquets puis renvoie un DataFrame complet avec nettoyage."""
    global _transactions_df

    if _transactions_df is None:
        try:
            reader = pd.read_csv(DATA_DIR / "transactions_data.csv", chunksize=chunksize)
            _transactions_df = pd.concat(reader, ignore_index=True)

            # Nettoyer le montant : enlever $ et convertir en float
            _transactions_df['amount'] = _transactions_df['amount'].replace(r'[\$,]', '', regex=True).astype(float)

            # Convertir les dates en datetime
            _transactions_df['date'] = pd.to_datetime(_transactions_df['date'], errors='coerce')

            # Remplacer les NaN des colonnes optionnelles par None
            optional_cols = ['use_chip', 'merchant_id', 'merchant_city', 'merchant_state', 'zip', 'mcc', 'errors']
            for col in optional_cols:
                if col in _transactions_df.columns:
                    _transactions_df[col] = _transactions_df[col].where(pd.notna(_transactions_df[col]), None)

        except FileNotFoundError:
            raise FileNotFoundError("Fichier transactions_data.csv introuvable")
        except Exception as e:
            raise Exception(f"Erreur lors du chargement des transactions: {e}")

    return _transactions_df


def load_card():
    """Charge les données de cartes à partir du fichier csv."""
    
    global _df_card_data
    _df_card_data = pd.read_csv(DATA_DIR / "cards_data.csv")

    return _df_card_data
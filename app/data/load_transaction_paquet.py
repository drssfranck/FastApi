import pandas as pd
from pathlib import Path
import numpy as np

# --- Définition des types optimisés (DTYPE) ---

# ⚠️ CORRECTION : Utilisation de 'Int32' (avec I majuscule) pour toutes les colonnes
# qui doivent être des entiers mais qui peuvent contenir des valeurs manquantes.
# Cela permet de stocker des NaN/NA (nulles).
DTYPE_PRE_CLEAN = {
    # Types Entiers Nulables pour gérer les NaN
    "id": 'Int32',          # <-- Changé de 'int32' à 'Int32'
    "client_id": 'Int32',    # <-- Changé de 'int32' à 'Int32'
    "card_id": 'Int32',      # <-- Changé de 'int32' à 'Int32'
    "merchant_id": 'Int32',  # <-- Changé de 'int32' à 'Int32'
    "zip": 'Int32',          # <-- Changé de 'int32' à 'Int32' (Colonne 9 du CSV)
    
    # Types non-entiers
    "amount": 'object',        # Reste en 'object' pour le nettoyage du symbole '$'
    "use_chip": 'object',
    "merchant_city": 'object',
    "merchant_state": 'object',
}

# Liste des colonnes à convertir en 'category' après le nettoyage
CATEGORICAL_COLS = ["use_chip", "merchant_city", "merchant_state"]


def convert_csv_to_parquet(csv_path: Path, parquet_path: Path, chunksize=100000):
    """Charge le CSV par morceaux, nettoie (amount), optimise (category), et sauvegarde en Parquet."""
    
    print(f"Starting chunked conversion from {csv_path} to {parquet_path}...")
    
    csv_iterator = pd.read_csv(
        csv_path,
        chunksize=chunksize,
        dtype=DTYPE_PRE_CLEAN,         
        parse_dates=['date'],
        low_memory=False
    )
    
    first_chunk = True
    for i, chunk in enumerate(csv_iterator):
        print(f"Processing chunk {i+1}...")
        
        # 1. Nettoyage et conversion de 'amount'
        try:
            # Retirer le symbole '$'
            chunk['amount'] = chunk['amount'].astype(str).str.replace('$', '', regex=False)
            # Convertir en float32, le NaN (float) est accepté ici
            chunk['amount'] = chunk['amount'].astype(np.float32)
        except Exception as e:
            print(f"Erreur critique dans le chunk {i+1}: Nettoyage de 'amount' échoué. {e}")
            raise 

        # 2. Conversion des colonnes de type string en 'category'
        for col in CATEGORICAL_COLS:
            # S'assurer que les valeurs manquantes sont traitées correctement avant la conversion
            # (Bien que 'category' gère bien les NaN/NA, il est plus sûr d'utiliser 'object' en entrée)
            chunk[col] = chunk[col].astype('category')
        
        # 3. Sauvegarde en Parquet
        if first_chunk:
            chunk.to_parquet(
                parquet_path, 
                index=False, 
                compression='snappy',
                engine='fastparquet'
            )
            first_chunk = False
        else:
            chunk.to_parquet(
                parquet_path, 
                index=False, 
                compression='snappy', 
                engine='fastparquet', 
                append=True
            )
            
    print("\nConversion complete! Parquet file is ready for fast loading.")

# ... (Exécution du script de conversion à la fin du fichier)

# Exemple d'appel (à exécuter une seule fois, en dehors de l'API)
if __name__ == '__main__':
    # Assurez-vous que ces chemins sont corrects
    DATA_DIR = Path("app/data/dataset")
    CSV_FILE = DATA_DIR / "transactions_data.csv"
    PARQUET_FILE = DATA_DIR / "transactions_data.parquet"
    convert_csv_to_parquet(CSV_FILE, PARQUET_FILE)
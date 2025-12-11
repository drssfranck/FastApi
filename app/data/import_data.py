import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

DATA_DIR = Path("app/data/dataset/")
DATA_DIR.mkdir(parents=True, exist_ok=True)

KAGGLE_JSON = Path("app/kaggle.json")  


os.environ['KAGGLE_CONFIG_DIR'] = str(KAGGLE_JSON.parent)

DATASET_NAME = "computingvictor/transactions-fraud-datasets"


required_files = [
    "transactions_data.csv",
    "cards_data.csv",
    "users_data.csv",
    "mcc_codes.json",
    "train_fraud_labels.json"
]

if not all((DATA_DIR / f).exists() for f in required_files):
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(DATASET_NAME, path=str(DATA_DIR), unzip=True, quiet=False)

print("✅ Dataset prêt !")

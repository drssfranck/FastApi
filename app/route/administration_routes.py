import time
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    import tomllib  # pour Python 3.11+
except ImportError:
    import tomli as tomllib
from fastapi import APIRouter

from app.data.load_data import (
    _transactions_df,
    _train_fraud_df,
    _mcc_codes_df,
    _user_data_df,
    _df_card_data,
)

administration_route = APIRouter(tags=["Administration"])

# Temps de démarrage de l'application (pour le calcul de l'uptime)
START_TIME = time.time()


@administration_route.get(
    "/api/system/health",
    summary="État de santé du système",
    description="Retourne l’état global du système, l’uptime, la latence et le statut des datasets."
)
def get_health():
    """
    Endpoint de **health check** pour le monitoring de l’application.

    ### Informations retournées
    - **status** : état global (`ok` ou `degraded`)
    - **uptime** : durée depuis le démarrage de l’API
    - **latency** : latence minimale du système
    - **dataset_loaded** : indique si tous les datasets sont chargés
    - **details** :
        - nombre d’enregistrements par dataset
        - liste des datasets manquants
    """
    # 1. Calcul de l'uptime
    uptime_seconds = int(time.time() - START_TIME)
    uptime = str(timedelta(seconds=uptime_seconds))

    # 2. Vérification du chargement des datasets
    datasets_status = {
        "transactions": _transactions_df is not None and not _transactions_df.empty,
        "fraud_labels": _train_fraud_df is not None and not _train_fraud_df.empty,
        "mcc_codes": _mcc_codes_df is not None and not _mcc_codes_df.empty,
        "users": _user_data_df is not None and not _user_data_df.empty,
        "cards": _df_card_data is not None and not _df_card_data.empty,
    }

    all_loaded = all(datasets_status.values())

    # 3. Mesure de la latence (ping interne)
    start_ping = time.perf_counter()
    _ = 1 + 1
    latency_ms = f"{(time.perf_counter() - start_ping) * 1000:.4f}ms"

    return {
        "status": "ok" if all_loaded else "degraded",
        "uptime": uptime,
        "latency": latency_ms,
        "dataset_loaded": all_loaded,
        "details": {
            "counts": {
                "transactions": len(_transactions_df) if datasets_status["transactions"] else 0,
                "users": len(_user_data_df) if datasets_status["users"] else 0,
                "mcc_codes": len(_mcc_codes_df) if datasets_status["mcc_codes"] else 0,
            },
            "missing_datasets": [
                name for name, loaded in datasets_status.items() if not loaded
            ],
        },
    }


def load_project_metadata() -> dict:
    """
    Charge les métadonnées du projet depuis le fichier `pyproject.toml`.

    ### Retour
    - Dictionnaire contenant les informations de la section `[project]`
    - Retourne `{}` si le fichier est absent ou illisible
    """
    try:
        toml_path = Path(__file__).parents[2] / "pyproject.toml"
        with toml_path.open("rb") as file:
            return tomllib.load(file).get("project", {})
    except Exception:
        return {}


@administration_route.get(
    "/api/system/metadata",
    summary="Métadonnées du système",
    description="Expose la version du projet et la date de dernière mise à jour des données."
)
def get_metadata():
    """
    Endpoint fournissant les **métadonnées système**.

    ### Informations retournées
    - **version** : version du projet (depuis `pyproject.toml`)
    - **last_update** : date de dernière modification des données de transactions
    """
    project_info = load_project_metadata()

    data_file = Path("dataset/transactions_data.csv")
    last_update = "unknown"

    if data_file.exists():
        mtime = os.path.getmtime(data_file)
        last_update = datetime.fromtimestamp(
            mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "version": project_info.get("version", "0.0.0"),
        "last_update": last_update,
    }

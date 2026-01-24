from fastapi import APIRouter
import pandas as pd

from app.data.load_data import load_transactions, load_train_fraud
from app.models.transaction_entry import TransactionEntry

fraud_routes = APIRouter(tags=["Fraude"])


def prepare_fraud_merge() -> pd.DataFrame:
    """
    Prépare et fusionne les données de transactions avec les labels de fraude.

    - Harmonise les colonnes (`id`, `is_fraud`)
    - Convertit les types pour éviter les erreurs de fusion
    - Retourne un DataFrame fusionné
    """
    df_trans = load_transactions()
    df_fraud = load_train_fraud()

    # Transformation de l'index en colonne 'id' si nécessaire
    if "id" not in df_fraud.columns:
        df_fraud = df_fraud.reset_index().rename(columns={"index": "id"})

    # Harmonisation du nom de la colonne fraude
    if "target" in df_fraud.columns:
        df_fraud = df_fraud.rename(columns={"target": "is_fraud"})

    # Conversion forcée des identifiants
    df_trans["id"] = df_trans["id"].astype(str)
    df_fraud["id"] = df_fraud["id"].astype(str)

    return pd.merge(
        df_trans,
        df_fraud[["id", "is_fraud"]],
        on="id",
        how="inner",
    )


@fraud_routes.get(
    "/api/fraud/summary",
    summary="Résumé global de la fraude",
    description="Statistiques globales de fraude incluant précision et rappel simulés."
)
def get_fraud_summary():
    """
    Résumé global de la fraude :

    - **total_frauds** : nombre total de fraudes réelles
    - **flagged** : transactions signalées (simulation)
    - **precision** : précision du système
    - **recall** : rappel du système

    ⚠️ Le champ `flagged` est simulé à partir de la présence d’erreurs.
    """
    df = prepare_fraud_merge()

    total_frauds = len(df[df["is_fraud"] == "Yes"])

    # Simulation du flag (présence d'erreurs)
    df["flagged"] = df["errors"].apply(
        lambda x: len(str(x)) > 0 if pd.notna(x) else False
    )

    flagged_count = int(df["flagged"].sum())

    # Vrais positifs
    true_positives = len(
        df[(df["flagged"]) & (df["is_fraud"] == "Yes")]
    )

    precision = (
        true_positives / flagged_count
        if flagged_count > 0
        else 0
    )
    recall = (
        true_positives / total_frauds
        if total_frauds > 0
        else 0
    )

    return {
        "total_frauds": int(total_frauds),
        "flagged": flagged_count,
        "precision": round(float(precision), 2),
        "recall": round(float(recall), 2),
    }


@fraud_routes.get(
    "/api/fraud/by-type",
    summary="Taux de fraude par type de transaction",
    description="Analyse du taux de fraude selon le type d’utilisation (chip, swipe, online…)."
)
def get_fraud_by_type():
    """
    Statistiques de fraude par type de transaction :

    - **fraud_rate** : taux moyen de fraude
    - **total_transactions** : volume total
    """
    df = prepare_fraud_merge()

    df["is_fraud_val"] = df["is_fraud"].map({"Yes": 1, "No": 0})

    stats_df = (
        df.groupby("use_chip")["is_fraud_val"]
        .agg(["mean", "count"])
        .reset_index()
    )

    return [
        {
            "type": str(row["use_chip"]),
            "fraud_rate": round(float(row["mean"]), 4),
            "total_transactions": int(row["count"]),
        }
        for _, row in stats_df.iterrows()
    ]


@fraud_routes.post(
    "/api/fraud/predict",
    summary="Prédiction de fraude",
    description="Retourne une probabilité de fraude basée sur des règles métier simples."
)
def predict_fraud(data: TransactionEntry):
    """
    Prédiction de fraude basée sur des règles heuristiques.

    """
    amount = data.amount
    trans_type = data.type
    balance_diff = data.oldbalanceOrg - data.newbalanceOrig

    probability = 0.0

    # Règle 1 : transfert élevé
    if trans_type == "TRANSFER" and amount > 1000:
        probability += 0.4

    # Règle 2 : incohérence de solde
    if abs(balance_diff - amount) > 0.1:
        probability += 0.5

    probability = min(probability, 0.99)

    return {
        "isFraud": probability > 0.5,
        "probability": round(probability, 2),
    }

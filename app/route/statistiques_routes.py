"""Routes pour les statistiques sur les transactions."""

from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter

from app.data.load_data import load_train_fraud, load_transactions

stat_router = APIRouter(tags=["Statistics"])


def normalize_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise la colonne `amount` en float si elle est de type object.

    Args:
        df: DataFrame contenant une colonne 'amount'

    Returns:
        DataFrame avec la colonne 'amount' normalisée en float
    """
    if df["amount"].dtype == "object":
        df["amount"] = pd.to_numeric(
            df["amount"].replace({r"\$": "", ",": ""}, regex=True),
            errors="coerce",
        )
    return df


@stat_router.get(
    "/api/stats/overview",
    summary="Vue d'ensemble des transactions",
    description=(
        "Retourne des statistiques globales sur les "
        "transactions et la fraude."
    ),
)
def get_stats_overview() -> Dict[str, Any]:
    """
    Statistiques globales sur les transactions.

    Returns:
        Dict contenant les statistiques globales

    ### Statistiques retournées
    - nombre total de transactions
    - taux de fraude
    - montant moyen
    - type de transaction le plus fréquent
    """
    transactions_df = normalize_amount(load_transactions())
    fraud_df = load_train_fraud()

    total_transactions = len(transactions_df)
    total_fraud = len(fraud_df[fraud_df["is_fraud"] == "Yes"])

    fraud_rate = (
        total_fraud / total_transactions if total_transactions > 0 else 0.0
    )

    avg_amount = transactions_df["amount"].mean()
    most_common_type = (
        transactions_df["use_chip"].mode()[0]
        if not transactions_df["use_chip"].empty
        else None
    )

    avg_amount_value = (
        round(float(avg_amount), 2) if not pd.isna(avg_amount) else 0.0
    )

    return {
        "total_transactions": int(total_transactions),
        "fraud_rate": round(float(fraud_rate), 5),
        "avg_amount": avg_amount_value,
        "most_common_type": str(most_common_type),
    }


@stat_router.get(
    "/api/stats/amount-distribution",
    summary="Distribution des montants",
    description="Distribution des transactions par tranche de montant.",
)
def get_amount_distribution() -> Dict[str, Any]:
    """
    Retourne la distribution des montants de transactions par intervalle.

    Returns:
        Dict contenant les tranches et leur distribution
    """
    df = normalize_amount(load_transactions())
    amounts = df["amount"].dropna()

    bins = [0, 100, 500, 1000, 5000]
    labels = ["0-100", "100-500", "500-1000", "1000-5000"]

    distribution = pd.cut(
        amounts,
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    counts = distribution.value_counts().reindex(labels, fill_value=0).tolist()

    return {
        "bins": labels,
        "counts": [int(value) for value in counts],
    }


@stat_router.get(
    "/api/stats/by-type",
    summary="Statistiques par type de transaction",
    description=(
        "Nombre et montant moyen par type d'utilisation "
        "(chip, swipe, online…)."
    ),
)
def get_stats_by_type() -> List[Dict[str, Any]]:
    """
    Statistiques par type de transaction.

    Returns:
        Liste des statistiques par type

    ### Statistiques retournées
    - nombre total
    - montant moyen
    """
    df = normalize_amount(load_transactions())

    stats_df = (
        df.groupby("use_chip")["amount"].agg(["count", "mean"]).reset_index()
    )

    result: List[Dict[str, Any]] = [
        {
            "type": str(row["use_chip"]),
            "count": int(row["count"]),
            "avg_amount": round(float(row["mean"]), 2),
        }
        for _, row in stats_df.iterrows()
    ]

    return result


@stat_router.get(
    "/api/stats/daily",
    summary="Statistiques journalières",
    description="Volume et montant moyen des transactions par jour.",
)
def get_daily_stats() -> List[Dict[str, Any]]:
    """
    Statistiques journalières des transactions.

    Returns:
        Liste des statistiques par jour

    ### Statistiques retournées
    - nombre de transactions
    - montant moyen par jour
    """
    df = normalize_amount(load_transactions())
    df["date"] = pd.to_datetime(df["date"])

    daily_stats = (
        df.groupby(df["date"].dt.date)["amount"]
        .agg(["count", "mean"])
        .reset_index()
    )

    result: List[Dict[str, Any]] = [
        {
            "date": str(row["date"]),
            "volume": int(row["count"]),
            "avg_amount": round(float(row["mean"]), 2),
        }
        for _, row in daily_stats.iterrows()
    ]

    return result

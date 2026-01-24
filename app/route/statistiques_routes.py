from fastapi import APIRouter
import pandas as pd

from app.data.load_data import load_transactions, load_train_fraud

stat_router =APIRouter(tags=["Statistics"])


def normalize_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise la colonne `amount` en float si elle est de type object.
    """
    if df["amount"].dtype == "object":
        df["amount"] = pd.to_numeric(
            df["amount"].replace({r"\$": "", ",": ""}, regex=True),
            errors="coerce",
        )
    return df


@stat_router.get(
    "/api/stats/overview",
    summary="Vue d’ensemble des transactions",
    description="Retourne des statistiques globales sur les transactions et la fraude."
)
def get_stats_overview():
    """
    Statistiques globales :
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
        total_fraud / total_transactions
        if total_transactions > 0
        else 0
    )

    avg_amount = transactions_df["amount"].mean()
    most_common_type = (
        transactions_df["use_chip"].mode()[0]
        if not transactions_df["use_chip"].empty
        else None
    )

    return {
        "total_transactions": int(total_transactions),
        "fraud_rate": round(float(fraud_rate), 5),
        "avg_amount": round(float(avg_amount), 2) if not pd.isna(avg_amount) else 0.0,
        "most_common_type": str(most_common_type),
    }


@stat_router.get(
    "/api/stats/amount-distribution",
    summary="Distribution des montants",
    description="Distribution des transactions par tranche de montant."
)
def get_amount_distribution():
    """
    Retourne la distribution des montants de transactions par intervalle.
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

    counts = (
        distribution
        .value_counts()
        .reindex(labels, fill_value=0)
        .tolist()
    )

    return {
        "bins": labels,
        "counts": [int(value) for value in counts],
    }


@stat_router.get(
    "/api/stats/by-type",
    summary="Statistiques par type de transaction",
    description="Nombre et montant moyen par type d’utilisation (chip, swipe, online…)."
)
def get_stats_by_type():
    """
    Statistiques par type de transaction :
    - nombre total
    - montant moyen
    """
    df = normalize_amount(load_transactions())

    stats_df = (
        df.groupby("use_chip")["amount"]
        .agg(["count", "mean"])
        .reset_index()
    )

    return [
        {
            "type": str(row["use_chip"]),
            "count": int(row["count"]),
            "avg_amount": round(float(row["mean"]), 2),
        }
        for _, row in stats_df.iterrows()
    ]


@stat_router.get(
    "/api/stats/daily",
    summary="Statistiques journalières",
    description="Volume et montant moyen des transactions par jour."
)
def get_daily_stats():
    """
    Statistiques journalières :
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

    return [
        {
            "date": str(row["date"]),
            "volume": int(row["count"]),
            "avg_amount": round(float(row["mean"]), 2),
        }
        for _, row in daily_stats.iterrows()
    ]

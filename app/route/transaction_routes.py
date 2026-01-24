from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.data.load_data import load_transactions
from app.models.transactions import Transaction
from app.models.transaction_response import TransactionListResponse

router = APIRouter(tags=["Transactions"])


# -------------------------------------------------------------------
# Utilitaires
# -------------------------------------------------------------------

def df_to_records(df: pd.DataFrame) -> list[dict]:
    """
    Convertit un DataFrame Pandas en liste de dicts compatibles Pydantic.
    Remplace tous les NaN/NA par None.
    """
    return df.where(pd.notna(df), None).replace({pd.NA: None, float("nan"): None}).to_dict("records")


def paginate_dataframe(df: pd.DataFrame, offset: int, limit: int):
    """
    Applique une pagination simple sur un DataFrame.
    """
    total = len(df)
    page = df.iloc[offset: offset + limit]
    data = df_to_records(page)
    return total, data


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------

@router.get(
    "/api/transactions/types",
    summary="Lister les types de transactions",
)
def get_transaction_types():
    """
    Retourne la liste des types de transactions disponibles.
    """
    df = load_transactions()
    types = df["use_chip"].dropna().unique().tolist()
    return {"types": types}


@router.get(
    "/api/transactions",
    response_model=TransactionListResponse,
    summary="Lister les transactions",
)
def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    client_id: Optional[int] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """
    Liste paginée des transactions avec filtres optionnels.
    """
    try:
        df = load_transactions()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Filtres dynamiques
    if client_id is not None:
        df = df[df["client_id"] == client_id]

    if min_amount is not None:
        df = df[df["amount"] >= min_amount]

    if max_amount is not None:
        df = df[df["amount"] <= max_amount]

    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]

    total, data = paginate_dataframe(df, offset, limit)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": data,
    }


@router.post(
    "/api/transactions/search",
    response_model=TransactionListResponse,
    summary="Recherche avancée de transactions",
)
def search_transactions(search_query: dict):
    """
    Recherche avancée multicritère.
    """
    df = load_transactions()

    if search_query.get("type"):
        df = df[df["use_chip"] == search_query["type"]]

    if search_query.get("isFraud") is not None:
        df = df[df["isFraud"] == search_query["isFraud"]]

    if search_query.get("amount_range"):
        min_amount, max_amount = search_query["amount_range"]
        df = df[(df["amount"] >= min_amount) & (df["amount"] <= max_amount)]

    total = len(df)
    data = df_to_records(df)

    return {
        "total": total,
        "offset": 0,
        "limit": total,
        "data": data,
    }


@router.get(
    "/api/transactions/recent",
    response_model=TransactionListResponse,
    summary="Transactions récentes",
)
def get_recent_transactions(
    n: int = Query(10, ge=1, le=100),
):
    """
    Retourne les N transactions les plus récentes.
    """
    df = load_transactions()

    df_sorted = df.sort_values("step", ascending=False) if "step" in df.columns else df
    data = df_to_records(df_sorted.head(n))

    return {
        "total": len(data),
        "offset": 0,
        "limit": n,
        "data": data,
    }


@router.get(
    "/api/transactions/{transaction_id}",
    response_model=Transaction,
    summary="Récupérer une transaction par ID",
)
def get_transaction_by_id(transaction_id: int):
    """
    Retourne une transaction par son identifiant.
    """
    df = load_transactions()
    transaction = df[df["id"] == transaction_id]

    if transaction.empty:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return df_to_records(transaction)[0]


@router.delete(
    "/api/transactions/{transaction_id}",
    summary="Supprimer une transaction (mode test)",
)
def delete_transaction(transaction_id: int):
    """
    Suppression simulée d'une transaction.
    """
    df = load_transactions()

    if transaction_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    return {
        "message": f"Transaction {transaction_id} supprimée avec succès",
        "transaction_id": transaction_id,
    }


@router.get(
    "/api/transactions/by-customer/{customer_id}",
    response_model=TransactionListResponse,
    summary="Transactions émises par un client",
)
def get_transactions_by_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Transactions dont le client est l’émetteur.
    """
    df = load_transactions()
    df_customer = df[df["client_id"] == customer_id]

    total, data = paginate_dataframe(df_customer, offset, limit)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": data,
    }


@router.get(
    "/api/transactions/to-customer/{customer_id}",
    response_model=TransactionListResponse,
    summary="Transactions reçues par un client",
)
def get_transactions_to_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Transactions dont le client est le destinataire.
    """
    df = load_transactions()

    if "client_id_dest" in df.columns:
        df_customer = df[df["client_id_dest"] == customer_id]
    elif "receiver_id" in df.columns:
        df_customer = df[df["receiver_id"] == customer_id]
    else:
        raise HTTPException(
            status_code=400,
            detail="Colonne de destination absente (client_id_dest ou receiver_id)",
        )

    total, data = paginate_dataframe(df_customer, offset, limit)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": data,
    }

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.transactions import Transaction
from app.models.transaction_response import TransactionListResponse
from app.data.load_data import load_transactions, load_card

# Router FastAPI pour les transactions
transaction_routes = APIRouter()




# Route racine


@transaction_routes.get("/")
def read_root():
    """
    Route racine de l'API des transactions.

    Returns
    -------
    dict
        Message de bienvenue et informations sur l'équipe.
    """
    team = [
        {
            "name": "Idriss MBE",
            "email": "i_mbe@stu-mba-esg.com",
            "github": "https://github.com/idrissmbe"
        },
        {
            "name": "Nadiath SAKA",
            "email": "y_lam@stu-mba-esg.com",
            "github": "https://github.com/nadiathsaka"
        },
        {
            "name": "Michele FAMENI",
            "email": "y_lam@stu-mba-esg.com",
            "github": "https://github.com/michelefameni"
        },
        {
            "name": "Raouf",
            "email": "y_lam@stu-mba-esg.com",
            "github": "https://github.com/raouf"
        }
    ]

    return {
        "message": "Bienvenue dans l'API des transactions bancaires",
        "team": team
    }




# Liste des types de transactions
@transaction_routes.get(
    "/api/transactions/types",
    summary="Lister les types de transactions",
    tags=["Transactions"]
)
def get_transaction_types():
    """
    Retourne la liste des types de transactions disponibles.
    """
    try:
        df = load_transactions()
        types = df["use_chip"].dropna().unique().tolist()
        return {"types": types}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des types de transactions: {str(e)}")



# Récupération d'une transaction par ID
@transaction_routes.get(
    "/api/transactions/{transaction_id}",
    response_model=Transaction,
    summary="Récupérer une transaction par ID",
    tags=["Transactions"]
)
def get_transaction_by_id(transaction_id: int):
    """
    Récupère une transaction par son ID.
    """
    try:
        df = load_transactions()
        transaction = df[df["id"] == transaction_id]

        if transaction.empty:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        return transaction.iloc[0].to_dict()

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement de la transaction: {str(e)}")


# Liste paginée de transactions
@transaction_routes.get(
    "/api/transactions",
    response_model=TransactionListResponse,
    summary="Lister les transactions",
    tags=["Transactions"]
)
def get_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    client_id: Optional[int] = Query(None, description="Filtrer par ID client"),
    min_amount: Optional[float] = Query(None, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, description="Montant maximum"),
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)")
) -> TransactionListResponse:
    """
    Récupère une liste paginée de transactions avec filtres optionnels.

    Returns
    -------
    TransactionListResponse
        Liste de transactions et informations de pagination.
    """
    try:
        df = load_transactions()
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

        total = len(df)
        df_page = df.iloc[offset: offset + limit]
        transactions = df_page.where(pd.notna(df_page), None).to_dict("records")

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")


# Recherche avancée de transactions
@transaction_routes.get(
    "/api/transactions/search",
    response_model=TransactionListResponse,
    summary="Recherche avancée de transactions",
    tags=["Transactions"]
)
def search_transactions(
    type: Optional[str] = Query(None, description="Type de transaction (ex: TRANSFER)"),
    is_fraud: Optional[int] = Query(None, ge=0, le=1, description="0 = non fraude, 1 = fraude"),
    min_amount: Optional[float] = Query(None, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, description="Montant maximum")
) -> TransactionListResponse:
    """
    Recherche avancée de transactions.
    """
    try:
        df = load_transactions()

        if type:
            df = df[df["type"] == type]

        if is_fraud is not None:
            df = df[df["isFraud"] == is_fraud]

        if min_amount is not None:
            df = df[df["amount"] >= min_amount]

        if max_amount is not None:
            df = df[df["amount"] <= max_amount]

        transactions = df.where(pd.notna(df), None).to_dict("records")

        return {
            "total": len(transactions),
            "offset": 0,
            "limit": len(transactions),
            "data": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")


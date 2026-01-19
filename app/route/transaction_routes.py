import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
from pydantic import BaseModel
from app.models.transactions import Transaction
from app.models.transaction_response import TransactionListResponse
from app.data.load_data import load_transactions, load_card


# Modèle pour la recherche POST
class TransactionSearchRequest(BaseModel):
    type: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None

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




# 4. Liste des types de transactions
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






# 1.Liste paginée de transactions
@transaction_routes.get(
    "/api/transactions",
    summary="Lister les transactions",
    tags=["Transactions"]
)
def get_transactions(
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    type: Optional[str] = Query(None, description="Type de transaction"),
    isFraud: Optional[int] = Query(None, ge=0, le=1, description="0 = non fraude, 1 = fraude"),
    min_amount: Optional[float] = Query(None, description="Montant minimum"),
    max_amount: Optional[float] = Query(None, description="Montant maximum")
):
    """
    Récupère une liste paginée de transactions avec filtres optionnels.

    Parameters
    ----------
    page : int
        Numéro de page (défaut: 1)
    limit : int
        Nombre de transactions par page (défaut: 100)
    type : str
        Filtrer par type de transaction
    isFraud : int
        Filtrer par fraude (0 ou 1)
    min_amount : float
        Montant minimum
    max_amount : float
        Montant maximum

    Returns
    -------
    dict
        Informations de pagination et liste des transactions
    """
    try:
        df = load_transactions()

        # Filtres dynamiques
        if type is not None:
            df = df[df["type"] == type]

        if isFraud is not None:
            df = df[df["isFraud"] == isFraud]

        if min_amount is not None:
            df = df[df["amount"] >= min_amount]

        if max_amount is not None:
            df = df[df["amount"] <= max_amount]

        total = len(df)
        offset = (page - 1) * limit
        df_page = df.iloc[offset: offset + limit]
        transactions = df_page.where(pd.notna(df_page), None).to_dict("records")

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "transactions": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")


# 3. Recherche avancée de transactions (POST)
@transaction_routes.post(
    "/api/transactions/search",
    summary="Recherche multicritère de transactions",
    tags=["Transactions"]
)
def search_transactions(
    search_request: TransactionSearchRequest
):
    """
    Recherche avancée de transactions avec critères POST.

    Parameters
    ----------
    search_request : TransactionSearchRequest
        Objet contenant les critères de recherche (type, isFraud, amount_range)

    Returns
    -------
    dict
        Liste des transactions correspondant aux critères
    """
    try:
        df = load_transactions()

        if search_request.type:
            df = df[df["type"] == search_request.type]

        if search_request.isFraud is not None:
            df = df[df["isFraud"] == search_request.isFraud]

        if search_request.amount_range is not None and len(search_request.amount_range) == 2:
            min_amt, max_amt = search_request.amount_range
            df = df[(df["amount"] >= min_amt) & (df["amount"] <= max_amt)]

        transactions = df.where(pd.notna(df), None).to_dict("records")

        return {
            "total": len(transactions),
            "limit": len(transactions),
            "transactions": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")
    





    # Route 5: Transactions récentes
@transaction_routes.get(
    "/api/transactions/recent",
    response_model=TransactionListResponse,
    summary="Récupérer les transactions récentes",
    tags=["Transactions"]
)
def get_recent_transactions(
    n: int = Query(10, ge=1, le=100, description="Nombre de transactions récentes")
) -> TransactionListResponse:
    """
    Renvoie les N dernières transactions du dataset.

    Parameters
    ----------
    n : int
        Nombre de transactions récentes à retourner (défaut: 10)

    Returns
    -------
    TransactionListResponse
        Liste des N dernières transactions
    """
    try:
        df = load_transactions()
        
        # Tri par step (temps) décroissant pour avoir les plus récentes
        if "step" in df.columns:
            df_sorted = df.sort_values("step", ascending=False)
        else:
            # Sinon prendre les dernières lignes
            df_sorted = df

        recent = df_sorted.head(n)
        transactions = recent.where(pd.notna(recent), None).to_dict("records")

        return {
            "page": 1,
            "total": len(transactions),
            "offset": 0,
            "limit": n,
            "data": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions récentes: {str(e)}")



# 2.Récupération d'une transaction par ID
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


# 6. Suppression d'une transaction (mode test uniquement)
@transaction_routes.delete(
    "/api/transactions/{transaction_id}",
    summary="Supprimer une transaction",
    tags=["Transactions"]
)
def delete_transaction(transaction_id: int):
    """
    Supprime une transaction fictive (utilisée uniquement en mode test).
    
    Parameters
    ----------
    transaction_id : int
        ID de la transaction à supprimer
    
    Returns
    -------
    dict
        Message de confirmation
    """
    try:
        df = load_transactions()
        transaction = df[df["id"] == transaction_id]

        if transaction.empty:
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        return {
            "message": f"Transaction {transaction_id} supprimée avec succès",
            "transaction_id": transaction_id
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


# 7. Liste des transactions associées à un client (origine)
@transaction_routes.get(
    "/api/transactions/by-customer/{customer_id}",
    summary="Transactions envoyées par un client",
    tags=["Transactions"]
)
def get_transactions_by_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    page: int = Query(1, ge=1, description="Numéro de page")
):
    """
    Récupère la liste des transactions associées à un client (en tant qu'origine).
    
    Parameters
    ----------
    customer_id : int
        ID du client
    limit : int
        Nombre de transactions par page (défaut: 100)
    page : int
        Numéro de page (défaut: 1)
    
    Returns
    -------
    dict
        Informations de pagination et liste des transactions
    """
    try:
        df = load_transactions()
        
        # Filtrer par originator_id ou client_id selon la structure du dataset
        if "originator_id" in df.columns:
            df_filtered = df[df["originator_id"] == customer_id]
        else:
            # Alternative si la colonne s'appelle différemment
            df_filtered = df[df["client_id"] == customer_id]

        total = len(df_filtered)
        offset = (page - 1) * limit
        df_page = df_filtered.iloc[offset: offset + limit]
        transactions = df_page.where(pd.notna(df_page), None).to_dict("records")

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "customer_id": customer_id,
            "transactions": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")


# 8. Liste des transactions reçues par un client (destination)
@transaction_routes.get(
    "/api/transactions/to-customer/{customer_id}",
    summary="Transactions reçues par un client",
    tags=["Transactions"]
)
def get_transactions_to_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    page: int = Query(1, ge=1, description="Numéro de page")
):
    """
    Récupère la liste des transactions reçues par un client (en tant que destination).
    
    Parameters
    ----------
    customer_id : int
        ID du client
    limit : int
        Nombre de transactions par page (défaut: 100)
    page : int
        Numéro de page (défaut: 1)
    
    Returns
    -------
    dict
        Informations de pagination et liste des transactions
    """
    try:
        df = load_transactions()
        
        # Filtrer par recipient_id ou destination_id selon la structure du dataset
        if "recipient_id" in df.columns:
            df_filtered = df[df["recipient_id"] == customer_id]
        elif "destination_id" in df.columns:
            df_filtered = df[df["destination_id"] == customer_id]
        else:
            # Alternative si la colonne s'appelle différemment
            df_filtered = df[df["customer_id"] == customer_id]

        total = len(df_filtered)
        offset = (page - 1) * limit
        df_page = df_filtered.iloc[offset: offset + limit]
        transactions = df_page.where(pd.notna(df_page), None).to_dict("records")

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "customer_id": customer_id,
            "transactions": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions: {str(e)}")
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
@transaction_routes.post(
    "/api/transactions/search",
    response_model=TransactionListResponse,
    summary="Recherche avancée de transactions",
    tags=["Transactions"]
)
def search_transactions(search_query: dict):
    """
    Recherche avancée de transactions avec filtres multicritère.
    
    Parameters
    ----------
    search_query : dict
        Corps JSON contenant les critères de recherche:
        - type (str, optional): Type de transaction
        - isFraud (int, optional): 0 = non fraude, 1 = fraude
        - amount_range (list, optional): [montant_min, montant_max]
    
    Returns
    -------
    TransactionListResponse
        Transactions correspondant aux critères
    """
    try:
        df = load_transactions()

        if "type" in search_query and search_query["type"]:
            df = df[df["type"] == search_query["type"]]

        if "isFraud" in search_query and search_query["isFraud"] is not None:
            df = df[df["isFraud"] == search_query["isFraud"]]

        if "amount_range" in search_query and search_query["amount_range"]:
            min_amount, max_amount = search_query["amount_range"]
            df = df[(df["amount"] >= min_amount) & (df["amount"] <= max_amount)]

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


# 6. Suppression d'une transaction (mode test)
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
        Message de confirmation de suppression
    """
    try:
        df = load_transactions()
        
        if transaction_id not in df["id"].values:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} non trouvée")
        
        # Simulation de suppression (dans un vrai projet, on mettrait à jour la DB)
        return {
            "message": f"Transaction {transaction_id} supprimée avec succès",
            "transaction_id": transaction_id
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


# 7. Transactions par client (origine - émetteur)
@transaction_routes.get(
    "/api/transactions/by-customer/{customer_id}",
    response_model=TransactionListResponse,
    summary="Transactions émises par un client",
    tags=["Transactions"]
)
def get_transactions_by_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
) -> TransactionListResponse:
    """
    Récupère toutes les transactions émises par un client (origine).
    
    Parameters
    ----------
    customer_id : int
        ID du client émetteur
    limit : int
        Nombre maximum de transactions à retourner
    offset : int
        Décalage pour la pagination
        
    Returns
    -------
    TransactionListResponse
        Liste paginée des transactions du client
    """
    try:
        df = load_transactions()
        
        # Filtrer par client_id (émetteur/origine)
        df_customer = df[df["client_id"] == customer_id]

        if df_customer.empty:
            return {
                "total": 0,
                "offset": offset,
                "limit": limit,
                "data": []
            }

        total = len(df_customer)
        df_page = df_customer.iloc[offset: offset + limit]
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


# 8. Transactions reçues par un client (destination)
@transaction_routes.get(
    "/api/transactions/to-customer/{customer_id}",
    response_model=TransactionListResponse,
    summary="Transactions reçues par un client",
    tags=["Transactions"]
)
def get_transactions_to_customer(
    customer_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
) -> TransactionListResponse:
    """
    Récupère toutes les transactions reçues par un client (destination).
    
    Parameters
    ----------
    customer_id : int
        ID du client destinataire
    limit : int
        Nombre maximum de transactions à retourner
    offset : int
        Décalage pour la pagination
        
    Returns
    -------
    TransactionListResponse
        Liste paginée des transactions reçues par le client
    """
    try:
        df = load_transactions()
        
        # Filtrer par client_id_dest ou receiver_id selon la structure du dataset
        # Adapter le nom de la colonne selon votre dataset
        if "client_id_dest" in df.columns:
            df_customer = df[df["client_id_dest"] == customer_id]
        elif "receiver_id" in df.columns:
            df_customer = df[df["receiver_id"] == customer_id]
        else:
            # Si aucune colonne de destination, retourner un message explicite
            raise HTTPException(
                status_code=400, 
                detail="Colonne de destination non trouvée dans le dataset (attendu: client_id_dest ou receiver_id)"
            )

        if df_customer.empty:
            return {
                "total": 0,
                "offset": offset,
                "limit": limit,
                "data": []
            }

        total = len(df_customer)
        df_page = df_customer.iloc[offset: offset + limit]
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
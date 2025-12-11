from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Optional, List
import pandas as pd
from app.models.transactions import Transaction


from app.data.load_data import load_transactions, load_card

transaction_routes = APIRouter()
df_transactions = load_transactions()
df_card = load_card()

@transaction_routes.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API des transactions bancaires"}


@transaction_routes.get("/api/transactions/{transaction_id}")
def get_transaction_by_id(transaction_id: int):
    """
    Récupère une transaction par son ID
    
    - **transaction_id**: ID de la transaction
    """
    df = load_transactions()
    transaction = df[df['id'] == transaction_id]
    
    if transaction.empty:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    t = transaction.iloc[0].to_dict()

    t['date'] = t['date'].isoformat() if pd.notna(t['date']) else None

    for key, value in t.items():
        if pd.isna(value):
            t[key] = None
    
    return t

#/api/transactions?limit=10&offset=2'
@transaction_routes.get("/api/transactions")
def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    client_id: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    try:
        df = load_transactions()
        
        # Filtres
        if client_id is not None:
            df = df[df['client_id'] == client_id]
        if min_amount is not None:
            df = df[df['amount'] >= min_amount]
        if max_amount is not None:
            df = df[df['amount'] <= max_amount]
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        
        total = len(df)
        
        # Pagination
        result = df.iloc[offset:offset + limit]
        
        # Convertir NaN → None et créer la liste de transactions
        transactions = result.where(pd.notna(result), None).to_dict('records')
        
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

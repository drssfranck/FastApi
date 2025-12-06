from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Optional, List
import pandas as pd


from app.data.load_data import load_transactions

transaction_routes = APIRouter()
df = load_transactions()

@transaction_routes.get("/api/transactions")
def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    client_id: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Récupère les transactions avec filtres optionnels
    
    - **limit**: Nombre max de résultats (1-1000)
    - **offset**: Pagination
    - **client_id**: Filtrer par client
    - **min_amount/max_amount**: Filtrer par montant
    - **start_date/end_date**: Filtrer par date (format: YYYY-MM-DD)
    """
    df = load_transactions()
    
    # Appliquer les filtres
    if client_id:
        df = df[df['client_id'] == client_id]
    
    if min_amount is not None:
        df = df[df['amount'] >= min_amount]
    
    if max_amount is not None:
        df = df[df['amount'] <= max_amount]
    
    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]
    
    # Pagination
    result = df.iloc[offset:offset + limit]
    
    # Convertir en dict
    transactions = result.to_dict('records')
    
    # Formater les dates
    for t in transactions:
        t['date'] = t['date'].isoformat() if pd.notna(t['date']) else None
        # Nettoyer les NaN
        for key, value in t.items():
            if pd.isna(value):
                t[key] = None
    
    return transactions
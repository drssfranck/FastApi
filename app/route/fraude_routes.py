import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.fraud_transaction import FraudTransaction
from app.models.transaction_response import TransactionListResponse
from app.data.load_data import load_transactions
from app.fraud_detection_service import FraudDetectionService
import numpy as np

# Router FastAPI pour la détection de fraude
fraud_routes = APIRouter()

# Instance du service de détection de fraude
fraud_service = FraudDetectionService()

# Route racine
@fraud_routes.get("/api/fraud/")
def read_fraud_root():
    """
    Route racine de l'API de détection de fraude.

    Returns
    -------
    dict
        Message de bienvenue pour l'API de fraude.
    """
    return {
        "message": "Bienvenue dans l'API de détection de fraude bancaire",
        "description": "API pour analyser et détecter les transactions frauduleuses"
    }

# Liste des transactions frauduleuses
@fraud_routes.get(
    "/api/fraud/transactions",
    response_model=TransactionListResponse,
    summary="Lister les transactions frauduleuses",
    tags=["Fraude"]
)
def get_fraudulent_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de transactions retournées"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
) -> TransactionListResponse:
    """
    Récupère une liste paginée de transactions frauduleuses.

    Returns
    -------
    TransactionListResponse
        Liste de transactions frauduleuses et informations de pagination.
    """
    try:
        df = load_transactions()

        # Filtrer les transactions frauduleuses (isFraud == 1)
        if 'isFraud' in df.columns:
            fraud_df = df[df['isFraud'] == 1]
        else:
            # Si pas de colonne isFraud, retourner vide
            fraud_df = pd.DataFrame()

        total = len(fraud_df)
        df_page = fraud_df.iloc[offset: offset + limit]
        transactions = df_page.where(pd.notna(df_page), None).to_dict("records")

        # Replace NaN with None
        for trans in transactions:
            for key, value in trans.items():
                if isinstance(value, float) and np.isnan(value):
                    trans[key] = None

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions frauduleuses: {str(e)}")

# Statistiques de fraude
@fraud_routes.get(
    "/api/fraud/statistics",
    summary="Statistiques de fraude",
    tags=["Fraude"]
)
def get_fraud_statistics():
    """
    Retourne les statistiques sur les transactions frauduleuses.
    """
    try:
        df = load_transactions()
        return fraud_service.get_fraud_statistics(df)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")

# Détection de fraude sur une transaction spécifique
@fraud_routes.get(
    "/api/fraud/detect/{transaction_id}",
    summary="Détecter la fraude sur une transaction",
    tags=["Fraude"]
)
def detect_fraud(transaction_id: int):
    """
    Vérifie si une transaction spécifique est frauduleuse.
    """
    try:
        df = load_transactions()
        return fraud_service.detect_fraud_by_id(df, transaction_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la détection de fraude: {str(e)}")

# Recherche de transactions suspectes (montants élevés)
@fraud_routes.get(
    "/api/fraud/suspicious",
    response_model=TransactionListResponse,
    summary="Transactions suspectes",
    tags=["Fraude"]
)
def get_suspicious_transactions(
    threshold: float = Query(1000.0, description="Seuil de montant pour considérer une transaction suspecte")
) -> TransactionListResponse:
    """
    Récupère les transactions avec des montants élevés (potentiellement suspectes).
    """
    try:
        df = load_transactions()
        suspicious_transactions = fraud_service.get_suspicious_transactions(df, threshold)

        return {
            "total": len(suspicious_transactions),
            "offset": 0,
            "limit": len(suspicious_transactions),
            "data": suspicious_transactions
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des transactions suspectes: {str(e)}")

# Vue d'ensemble de la fraude
@fraud_routes.get(
    "/api/fraud/summary",
    summary="Vue d'ensemble de la fraude",
    tags=["Fraude"]
)
def get_fraud_summary():
    """
    Retourne un résumé global des métriques de fraude.
    """
    try:
        df = load_transactions()

        if 'isFraud' not in df.columns:
            return {
                "total_frauds": 0,
                "flagged": 0,
                "precision": 0.0,
                "recall": 0.0
            }

        fraud_df = df[df['isFraud'] == 1]
        total_frauds = len(fraud_df)

        # Mock values for flagged, precision, recall since we don't have model metrics
        return {
            "total_frauds": total_frauds,
            "flagged": 16,  # Mock value
            "precision": 0.95,  # Mock value
            "recall": 0.88  # Mock value
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du résumé: {str(e)}")

# Répartition du taux de fraude par type de transaction
@fraud_routes.get(
    "/api/fraud/by-type",
    summary="Répartition du taux de fraude par type",
    tags=["Fraude"]
)
def get_fraud_by_type():
    """
    Retourne la répartition du taux de fraude par type de transaction.
    """
    try:
        df = load_transactions()
        return {"fraud_by_type": fraud_service.calculate_fraud_by_type(df)}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de transactions introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul par type: {str(e)}")

# Modèle de prédiction de fraude
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    """
    Modèle pour la requête de prédiction de fraude.
    """
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float

class PredictionResponse(BaseModel):
    """
    Modèle pour la réponse de prédiction de fraude.
    """
    isFraud: bool
    probability: float

# Endpoint de scoring pour prédire la fraude
@fraud_routes.post(
    "/api/fraud/predict",
    response_model=PredictionResponse,
    summary="Prédiction de fraude",
    tags=["Fraude"]
)
def predict_fraud(request: PredictionRequest):
    """
    Prédit si une transaction donnée est frauduleuse basé sur les caractéristiques fournies.
    """
    transaction_data = {
        "type": request.type,
        "amount": request.amount,
        "oldbalanceOrg": request.oldbalanceOrg,
        "newbalanceOrig": request.newbalanceOrig
    }

    probability = fraud_service.predict_fraud_probability(transaction_data)
    is_fraud = fraud_service.is_fraudulent(transaction_data)

    return PredictionResponse(
        isFraud=is_fraud,
        probability=round(probability, 2)
    )

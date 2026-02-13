"""Routes pour la gestion des clients."""

from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.data.load_data import load_transactions, load_user_data

client_route = APIRouter(tags=["Clients"])


@client_route.get(
    "/api/client/{client_id}",
    summary="Récupérer les informations d'un client",
    description=(
        "Retourne les informations et cartes associées à un client donné."
    ),
)
def get_client_cards(client_id: int) -> List[Dict[str, Any]]:
    """
    Récupère les informations d'un client à partir de son identifiant.

    Args:
        client_id: Identifiant unique du client

    Returns:
        Liste contenant les informations du client

    Raises:
        HTTPException: 404 si client inexistant ou aucune donnée disponible
    """
    users_df = load_user_data()

    client_df = users_df[users_df["id"] == client_id]

    if client_df.empty:
        raise HTTPException(
            status_code=404, detail="Client not found or no cards available."
        )

    return client_df.to_dict(orient="records")


@client_route.get(
    "/api/customers/top",
    summary="Top clients par volume de dépenses",
    description=(
        "Retourne les clients ayant dépensé le plus, "
        "classés par montant total."
    ),
)
def get_top_customers(
    n: int = Query(
        default=10, gt=0, description="Nombre de clients à retourner"
    )
) -> List[Dict[str, Any]]:
    """
    Calcule le total des dépenses par client.

    Retourne les **n** clients ayant le plus dépensé.

    Args:
        n: Nombre de clients à retourner (par défaut 10)

    Returns:
        Liste des clients avec leurs dépenses totales et profil

    ### Données retournées
    - Identifiant du client
    - Montant total dépensé
    - Profil client (âge, genre, revenus, score de crédit, adresse)
    """
    transactions_df = load_transactions()
    users_df = load_user_data()

    # Calcul du total des dépenses par client
    spending_by_client = (
        transactions_df.groupby("client_id")["amount"].sum().reset_index()
    )

    # Sélection des N meilleurs clients
    top_clients = spending_by_client.sort_values(
        by="amount", ascending=False
    ).head(n)

    # Jointure avec les données clients
    merged_df = pd.merge(
        top_clients, users_df, left_on="client_id", right_on="id"
    )

    # Format de réponse
    result: List[Dict[str, Any]] = [
        {
            "client_id": int(row["client_id"]),
            "total_spent": round(float(row["amount"]), 2),
            "profile": {
                "current_age": int(row["current_age"]),
                "gender": str(row["gender"]),
                "yearly_income": str(row["yearly_income"]),
                "credit_score": int(row["credit_score"]),
                "address": str(row["address"]),
            },
        }
        for _, row in merged_df.iterrows()
    ]

    return result


@client_route.get(
    "/api/customers",
    summary="Liste paginée des clients",
    description=(
        "Retourne une liste paginée des clients " "extraits du champ nameOrig."
    ),
)
def list_customers(
    page: int = Query(default=1, ge=1, description="Numéro de page"),
    limit: int = Query(
        default=20, ge=1, le=200, description="Nombre d'éléments par page"
    ),
) -> Dict[str, Any]:
    """
    Liste paginée des clients basés sur le champ **nameOrig**.

    Args:
        page: Numéro de page (>=1)
        limit: Nombre de clients par page (1 à 200)

    Returns:
        Dict contenant la pagination et la liste des clients

    ### Données retournées
    - Liste unique des identifiants clients
    - Pagination : page, total, total_pages
    """
    transactions_df = load_transactions()

    # Extraction des clients uniques
    customers = transactions_df["nameOrig"].unique()
    total = len(customers)

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_customers = customers[start:end]

    total_pages = (total // limit) + (1 if total % limit else 0)

    return {
        "page": page,
        "limit": limit,
        "total_customers": total,
        "total_pages": total_pages,
        "customers": paginated_customers.tolist(),
    }

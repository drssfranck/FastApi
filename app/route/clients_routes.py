from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.data.load_data import load_user_data, load_transactions

client_route = APIRouter(tags=["Clients"])


@client_route.get(
    "/api/client/{client_id}",
    summary="Récupérer les informations d’un client",
    description="Retourne les informations et cartes associées à un client donné."
)
def get_client_cards(client_id: int):
    """
    Récupère les informations d’un client à partir de son identifiant.

    - **client_id** : identifiant unique du client
    - **Retour** : liste contenant les informations du client

    ### Erreurs possibles
    - **404** : client inexistant ou aucune donnée disponible
    """
    users_df = load_user_data()

    client_df = users_df[users_df["id"] == client_id]

    if client_df.empty:
        raise HTTPException(
            status_code=404,
            detail="Client not found or no cards available."
        )

    return client_df.to_dict(orient="records")


@client_route.get(
    "/api/customers/top",
    summary="Top clients par volume de dépenses",
    description="Retourne les clients ayant dépensé le plus, classés par montant total."
)
def get_top_customers(
    n: int = Query(
        default=10,
        gt=0,
        description="Nombre de clients à retourner"
    )
):
    """
    Calcule le total des dépenses par client et retourne les **n** clients
    ayant le plus dépensé.

    - **n** : nombre de clients à retourner (par défaut 10)

    ### Données retournées
    - Identifiant du client
    - Montant total dépensé
    - Profil client (âge, genre, revenus, score de crédit, adresse)
    """
    transactions_df = load_transactions()
    users_df = load_user_data()

    # Calcul du total des dépenses par client
    spending_by_client = (
        transactions_df
        .groupby("client_id")["amount"]
        .sum()
        .reset_index()
    )

    # Sélection des N meilleurs clients
    top_clients = (
        spending_by_client
        .sort_values(by="amount", ascending=False)
        .head(n)
    )

    # Jointure avec les données clients
    merged_df = pd.merge(
        top_clients,
        users_df,
        left_on="client_id",
        right_on="id"
    )

    # Format de réponse
    return [
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

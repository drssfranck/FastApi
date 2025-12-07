from fastapi import  HTTPException, APIRouter
import pandas as pd


from app.data.load_data import load_card

client_route = APIRouter()
df_card = load_card()


@client_route.get("/api/client/{client_id}/cards")
def get_client_cards(client_id: int):
    """
    Récupère les informations des cartes pour un client donné.
    
    - **client_id**: ID du client
    """
    df = load_card()
    client_cards = df[df['client_id'] == client_id]
    
    if client_cards.empty:
        raise HTTPException(status_code=404, detail="Client not found or no cards available.")
    
    cards = client_cards.to_dict('records')
    
    # Nettoyer les NaN
    for card in cards:
        for key, value in card.items():
            if pd.isna(value):
                card[key] = None
    
    return cards
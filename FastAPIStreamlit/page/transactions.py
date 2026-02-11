import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/api"

def app():
    st.title("Transactions Bancaires")

    # Ici tu mets ton code de filtrage, requêtes API, affichage etc.
    # Par exemple :
    resp = requests.get(f"{API_URL}/transactions")
    if resp.status_code == 200:
        data = resp.json()
        df = pd.DataFrame(data.get("data", []))
        st.dataframe(df)
    else:
        st.error("Erreur lors du chargement des transactions")

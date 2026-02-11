import streamlit as st
import requests
from pydantic import BaseModel, Field

API_URL = "http://localhost:8000/api/fraud"

def app():
    st.title("Analyse et Prédiction de Fraude")

    # --- Résumé global de la fraude ---
    st.header("Résumé global de la fraude")
    try:
        resp = requests.get(f"{API_URL}/summary")
        resp.raise_for_status()
        summary = resp.json()

        st.metric("Total fraudes réelles", summary["total_frauds"])
        st.metric("Transactions signalées", summary["flagged"])
        st.metric("Précision (simulée)", summary["precision"])
        st.metric("Rappel (simulé)", summary["recall"])
    except Exception as e:
        st.error(f"Erreur chargement résumé de la fraude : {e}")

    st.markdown("---")

    # --- Taux de fraude par type de transaction ---
    st.header("Taux de fraude par type de transaction")
    try:
        resp = requests.get(f"{API_URL}/by-type")
        resp.raise_for_status()
        stats_by_type = resp.json()

        import pandas as pd
        df = pd.DataFrame(stats_by_type)

        st.dataframe(df)

        import altair as alt
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('type', sort=None),
            y='fraud_rate',
            tooltip=['type', 'fraud_rate', 'total_transactions']
        ).properties(width=600, height=300)

        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur chargement stats fraude par type : {e}")

    st.markdown("---")

    # --- Prédiction de fraude ---
    st.header("Prédiction de fraude (heuristique)")

    class TransactionInput(BaseModel):
        amount: float = Field(..., description="Montant de la transaction")
        type: str = Field(..., description="Type de transaction (e.g. TRANSFER)")
        oldbalanceOrg: float = Field(..., description="Ancien solde de l'émetteur")
        newbalanceOrig: float = Field(..., description="Nouveau solde de l'émetteur")

    with st.form("fraud_predict_form"):
        amount = st.number_input("Montant", min_value=0.0, value=100.0, step=10.0)
        trans_type = st.selectbox("Type de transaction", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"])
        old_balance = st.number_input("Ancien solde (émetteur)", min_value=0.0, value=1000.0, step=100.0)
        new_balance = st.number_input("Nouveau solde (émetteur)", min_value=0.0, value=900.0, step=100.0)

        submitted = st.form_submit_button("Prédire la fraude")

    if submitted:
        try:
            payload = {
                "amount": amount,
                "type": trans_type,
                "oldbalanceOrg": old_balance,
                "newbalanceOrig": new_balance,
            }
            resp = requests.post(f"{API_URL}/predict", json=payload)
            resp.raise_for_status()
            result = resp.json()

            st.write(f"**Probabilité de fraude estimée** : {result['probability']*100:.1f} %")
            st.write(f"**Fraude détectée ?** : {'Oui' if result['isFraud'] else 'Non'}")
        except Exception as e:
            st.error(f"Erreur lors de la prédiction : {e}")

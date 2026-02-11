import streamlit as st
import pandas as pd
import requests
import altair as alt

API_URL = "http://localhost:8000/api"

def app():
    st.title("Statistiques des Transactions")

    # --- Vue d'ensemble ---
    st.header("Vue d'ensemble")
    try:
        resp = requests.get(f"{API_URL}/stats/overview")
        resp.raise_for_status()
        overview = resp.json()
        st.metric("Total Transactions", overview["total_transactions"])
        st.metric("Taux de fraude", f"{overview['fraud_rate']*100:.2f} %")
        st.metric("Montant moyen", f"{overview['avg_amount']:.2f}")
        st.metric("Type de transaction le plus fréquent", overview["most_common_type"])
    except Exception as e:
        st.error(f"Erreur chargement données vue d'ensemble: {e}")

    st.markdown("---")

    # --- Distribution des montants ---
    st.header("Distribution des montants")
    try:
        resp = requests.get(f"{API_URL}/stats/amount-distribution")
        resp.raise_for_status()
        dist = resp.json()
        df_dist = pd.DataFrame({
            "Montant": dist["bins"],
            "Nombre de transactions": dist["counts"]
        })

        bar = alt.Chart(df_dist).mark_bar().encode(
            x=alt.X("Montant", sort=dist["bins"]),
            y="Nombre de transactions"
        )
        st.altair_chart(bar, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur chargement distribution des montants: {e}")

    st.markdown("---")

    # --- Statistiques par type ---
    st.header("Statistiques par type de transaction")
    try:
        resp = requests.get(f"{API_URL}/stats/by-type")
        resp.raise_for_status()
        stats_type = resp.json()
        df_stats = pd.DataFrame(stats_type)
        df_stats["avg_amount"] = df_stats["avg_amount"].round(2)

        st.dataframe(df_stats)

        # Graphique count par type
        bar_count = alt.Chart(df_stats).mark_bar().encode(
            x="type",
            y="count"
        )
        st.altair_chart(bar_count, use_container_width=True)

        # Graphique montant moyen par type
        bar_avg = alt.Chart(df_stats).mark_bar(color="orange").encode(
            x="type",
            y="avg_amount"
        )
        st.altair_chart(bar_avg, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur chargement statistiques par type: {e}")

    st.markdown("---")

    # --- Statistiques journalières ---
    st.header("Statistiques journalières")
    try:
        resp = requests.get(f"{API_URL}/stats/daily")
        resp.raise_for_status()
        daily_stats = resp.json()
        df_daily = pd.DataFrame(daily_stats)
        df_daily["date"] = pd.to_datetime(df_daily["date"])
        df_daily["avg_amount"] = df_daily["avg_amount"].round(2)

        st.line_chart(df_daily.set_index("date")[["volume", "avg_amount"]])
    except Exception as e:
        st.error(f"Erreur chargement statistiques journalières: {e}")

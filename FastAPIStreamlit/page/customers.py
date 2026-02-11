import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_BASE_URL = "http://localhost:8000/api"


# -------------------- Fetch API -------------------- #
def fetch_client_profile(client_id: int):
    """Récupère le profil d'un client par ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/client/{client_id}")
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}
    except requests.HTTPError as e:
        st.error(f"Erreur {e.response.status_code} : {e.response.text}")
        return {}
    except Exception as e:
        st.error(f"Erreur: {e}")
        return {}


def fetch_top_customers(n: int = 10):
    """Récupère les top clients par montant total dépensé"""
    try:
        response = requests.get(f"{API_BASE_URL}/customers/top", params={"n": n})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur: {e}")
        return []


# -------------------- Cartes Client -------------------- #
def create_client_card(client_data: dict, rank: int = None) -> None:
    """Crée une carte client stylisée"""
    client_id = client_data.get('client_id', 'N/A')
    total_spent = client_data.get('total_spent', 0)
    profile = client_data.get('profile', {})
    name = profile.get("address", "Adresse N/A")

    # Couleur et icône (ici on peut ajouter un critère simple pour alertes)
    color = "#6366f1"
    status_icon = "✅"
    status_text = "Client"

    rank_badge = f"""
        <div style='position: absolute; top: 16px; right: 16px; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
             color: white; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 0.875rem;'>{rank}</div>
    """ if rank else ""

    st.markdown(f"""
        <div style='position: relative; background: linear-gradient(135deg, {color}08 0%, {color}03 100%);
             border-left: 4px solid {color}; margin-bottom: 16px; padding:16px; border-radius:8px;'>
            {rank_badge}
            <h3 style='margin:0; color:#1f2937;'>👤 Client {client_id}</h3>
            <p style='margin:4px 0 8px 0; color:{color}; font-weight:600;'>{status_icon} {status_text}</p>
            <p style='margin:0; font-size:0.9rem; color:#6b7280;'>Adresse: {name}</p>
            <p style='margin:4px 0 0 0; font-size:1.25rem; font-weight:700; color:#6366f1;'>Dépenses Totales: {total_spent:,.2f}€</p>
        </div>
    """, unsafe_allow_html=True)


# -------------------- Graphiques -------------------- #
def create_top_customers_chart(customers: list) -> go.Figure:
    """Graphique Top Clients par dépenses"""
    df = pd.DataFrame(customers)
    df = df.sort_values('total_spent', ascending=True).tail(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df['client_id'].astype(str),
        x=df['total_spent'],
        orientation='h',
        text=[f"{v:,.2f}€" for v in df['total_spent']],
        textposition='outside',
        marker=dict(color=df['total_spent'], colorscale='Viridis', showscale=True, colorbar=dict(title="€")),
    ))
    fig.update_layout(
        title="Top 10 Clients par Dépenses",
        xaxis_title="Dépenses Totales (€)",
        yaxis_title="Client ID",
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        showlegend=False
    )
    return fig


# -------------------- Application -------------------- #
def app():
    st.title("📊 Gestion et Analyse des Clients")

    tab1, tab2, tab3 = st.tabs(["👥 Liste des Clients", "🏆 Top Clients", "🔍 Profil Client"])

    # -------------------- Tab Top Clients -------------------- #
    with tab2:
        n_top = st.slider("Nombre de clients à afficher", 5, 50, 10, 5)
        if st.button("🔄 Charger Top Clients"):
            top_customers = fetch_top_customers(n_top)
            if top_customers:
                st.plotly_chart(create_top_customers_chart(top_customers), use_container_width=True)
                st.markdown("### 🏅 Podium")
                for idx, customer in enumerate(top_customers[:10], 1):
                    create_client_card(customer, rank=idx)
            else:
                st.warning("Aucun client trouvé")

    # -------------------- Tab Profil Client -------------------- #
    with tab3:
        client_id = st.number_input("Entrez l'ID du client", min_value=1, step=1)
        if st.button("🔎 Rechercher Client"):
            profile = fetch_client_profile(client_id)
            if profile:
                st.success("✅ Client trouvé")
                st.json(profile)
            else:
                st.error("❌ Client non trouvé")


if __name__ == "__main__":
    app()

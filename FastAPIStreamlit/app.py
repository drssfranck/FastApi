import streamlit as st
from page import transactions, statistique, fraude, customers

# Configuration de la page
st.set_page_config(
    page_title="Banking Analytics Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personnalisé pour un design moderne et professionnel
st.markdown("""
<style>
    /* Import de Google Fonts - Typographie distinctive */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Variables CSS */
    :root {
        --primary-color: #1a1f3a;
        --secondary-color: #2d3561;
        --accent-color: #6366f1;
        --accent-light: #818cf8;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --border-color: #e5e7eb;
    }

    /* Style général */
    .main {
        background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
    }

    /* Typographie */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: var(--primary-color);
        font-weight: 900;
    }

    p, div, span, label {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #2d3561 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Sidebar navigation buttons */
    .css-1d391kg, [data-testid="stSidebar"] .stRadio > label {
        background: transparent;
        padding: 12px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateX(4px);
    }

    /* Cards et containers */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-light) 100%);
        color: white;
        border: none;
        padding: 12px 32px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }

    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border-radius: 8px;
        font-weight: 600;
        color: var(--primary-color);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        color: var(--text-secondary);
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--accent-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }

    /* Alert boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
        padding: 16px;
    }

    /* Header decoration */
    .header-line {
        height: 4px;
        background: linear-gradient(90deg, var(--accent-color) 0%, var(--accent-light) 100%);
        border-radius: 2px;
        margin: 20px 0;
    }

    /* Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-fade-in {
        animation: fadeIn 0.6s ease-out;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-light);
    }
</style>
""", unsafe_allow_html=True)

# Navigation sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px;'>
            <h1 style='font-size: 2rem; margin: 0; color: white !important;'>🏦</h1>
            <h2 style='font-size: 1.5rem; margin: 10px 0 0 0; color: white !important;'>Banking Analytics</h2>
            <p style='font-size: 0.875rem; margin: 8px 0 0 0; opacity: 0.8; color: white !important;'>Transaction Management System</p>
        </div>
    """, unsafe_allow_html=True)

    PAGES = {
        "📊 Transactions": transactions.app,
        "📈 Statistiques": statistique.app,
        "🚨 Fraude": fraude.app,
        "👥 Clients": customers.app,
    }

    st.markdown("### Navigation")
    choice = st.radio("Aller à", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown("---")

    # Informations système
    st.markdown("""
        <div style='margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);'>
            <p style='font-size: 0.75rem; margin: 0; opacity: 0.7; color: white !important;'>Version: 1.0.0</p>
            <p style='font-size: 0.75rem; margin: 4px 0 0 0; opacity: 0.7; color: white !important;'>API Status: <span style='color: #10b981;'>●</span> Online</p>
        </div>
    """, unsafe_allow_html=True)

# Exécuter la page sélectionnée
page = PAGES[choice]
page()
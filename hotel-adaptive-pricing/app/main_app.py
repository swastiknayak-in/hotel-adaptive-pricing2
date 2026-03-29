import streamlit as st
import os
import sys

# ── Path setup ──────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Grandeur Hotel — Adaptive Pricing",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global style injection ───────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Thin gold top accent */
[data-testid="stAppViewContainer"]::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #c9a84c, #e8c96d, #c9a84c);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #2a2a3e;
}
[data-testid="stSidebar"] * {
    color: #ccc !important;
}
[data-testid="stSidebar"] .stButton button {
    background: transparent;
    border: 1px solid #3a3a5e;
    color: #c9a84c !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #c9a84c;
    background: rgba(201,168,76,0.1);
}

/* Main background */
[data-testid="stAppViewContainer"] {
    background: #fdfaf5;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c9a84c, #e8c96d) !important;
    border: none !important;
    color: #1a1a2e !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    border-radius: 2px !important;
}
.stButton > button {
    border-radius: 2px !important;
    font-family: 'Jost', sans-serif;
    letter-spacing: 0.08em;
    font-size: 0.82rem;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #f0ece4;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Jost', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.75rem 2rem;
    color: #999;
}
.stTabs [aria-selected="true"] {
    color: #c9a84c !important;
    border-bottom: 2px solid #c9a84c !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #fff;
    border: 1px solid #f0ece4;
    border-radius: 4px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    color: #c9a84c !important;
}
</style>
""", unsafe_allow_html=True)

# ── Lazy model loader (cached) ───────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_models():
    from core.model_training import load_or_train_models
    return load_or_train_models()

# ── Routing ──────────────────────────────────────────────────────────────────
def main():
    role = st.session_state.get("role")

    if not role:
        from app.login_page import show_login_page
        show_login_page()
        return

    # Load / train models once
    with st.spinner("🔄 Initialising AI pricing engine…"):
        pricing_model, occupancy_model = get_models()

    if role == "Customer":
        from app.customer_interface import show_customer_interface
        show_customer_interface(pricing_model, occupancy_model)

    elif role == "Manager":
        from app.manager_dashboard import show_manager_dashboard
        show_manager_dashboard(pricing_model, occupancy_model)


if __name__ == "__main__":
    main()

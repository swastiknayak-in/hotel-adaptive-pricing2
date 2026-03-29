import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pricing_engine import (
    ROOM_CONFIG, predict_price, compute_demand_score,
    compute_dynamic_price, predict_occupancy
)

STORAGE_PATH = "storage/bookings.csv"

COLORS = {
    "gold": "#c9a84c",
    "navy": "#1a1a2e",
    "cream": "#f9f6f0",
    "green": "#43a047",
    "red": "#e53935",
}

MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}


def manager_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Jost:wght@300;400;500;600&display=swap');

    .dash-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.5rem;
        font-weight: 300;
        color: #1a1a2e;
        letter-spacing: 0.05em;
    }
    .dash-sub {
        font-family: 'Jost', sans-serif;
        font-size: 0.78rem;
        color: #9a8866;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: #fff;
        border: 1px solid #f0ece4;
        border-radius: 4px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    .kpi-value {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        font-weight: 600;
        color: #c9a84c;
    }
    .kpi-label {
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        color: #999;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    .section-hdr {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 2rem 0 1rem;
        border-bottom: 1px solid #f0ece4;
        padding-bottom: 0.5rem;
    }
    .sim-card {
        background: #fff;
        border: 1px solid #e8e0d0;
        border-radius: 4px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)


def load_bookings():
    if os.path.exists(STORAGE_PATH):
        try:
            df = pd.read_csv(STORAGE_PATH)
            if not df.empty and "booking_date" in df.columns:
                df["booking_date"] = pd.to_datetime(df["booking_date"], errors="coerce")
                df["month_num"] = df.get("arrival_month", df["booking_date"].dt.month)
                df["month_name"] = df["month_num"].map(MONTH_NAMES)
                df["week"] = df["booking_date"].dt.isocalendar().week.astype(int)
                return df
        except Exception:
            pass
    return pd.DataFrame()


def make_synthetic_df(n=400):
    np.random.seed(42)
    months = np.random.randint(1, 13, n)
    rooms = np.random.choice(list(ROOM_CONFIG.keys()), n, p=[0.4, 0.3, 0.2, 0.1])
    stay = np.random.randint(1, 10, n)
    guests = np.random.randint(1, 6, n)
    pred_p = np.random.uniform(3000, 9000, n)
    final_p = pred_p * np.random.uniform(0.85, 1.1, n)
    base = datetime(2024, 1, 1)
    dates = [base + timedelta(days=int(x)) for x in np.random.randint(0, 365, n)]
    weeks = [d.isocalendar()[1] for d in dates]

    return pd.DataFrame({
        "customer_name": [f"Guest_{i}" for i in range(n)],
        "room_type": rooms,
        "stay_length": stay,
        "guests": guests,
        "predicted_price": pred_p,
        "final_price": final_p,
        "booking_date": dates,
        "month_num": months,
        "month_name": [MONTH_NAMES[m] for m in months],
        "week": weeks,
    })


def plot_monthly_demand(df):
    month_order = list(MONTH_NAMES.values())
    monthly = df.groupby("month_name").size().reset_index(name="bookings")
    monthly["sort"] = monthly["month_name"].apply(
        lambda x: month_order.index(x) if x in month_order else 99
    )
    monthly = monthly.sort_values("sort")

    fig = px.bar(
        monthly, x="month_name", y="bookings",
        title="Booking Demand by Month",
        labels={"month_name": "Month", "bookings": "Bookings"},
        color="bookings",
        color_continuous_scale=[[0, "#f9f6f0"], [0.5, "#c9a84c"], [1, "#1a1a2e"]],
        text="bookings",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False, coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
    )
    return fig


def plot_revenue_trend(df):
    if "week" not in df.columns:
        return None
    weekly = df.groupby("week")["final_price"].sum().reset_index()
    weekly.columns = ["week", "revenue"]
    weekly = weekly.sort_values("week")
    fig = px.line(
        weekly, x="week", y="revenue",
        title="Weekly Revenue Trend",
        labels={"week": "Week", "revenue": "Revenue (₹)"},
        markers=True,
    )
    fig.update_traces(
        line=dict(color="#c9a84c", width=2.5),
        marker=dict(color="#1a1a2e", size=5),
        fill="tozeroy",
        fillcolor="rgba(201,168,76,0.08)",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
    )
    return fig


def plot_room_popularity(df):
    counts = df["room_type"].value_counts().reset_index()
    counts.columns = ["room_type", "count"]
    fig = px.pie(
        counts, names="room_type", values="count",
        title="Room Popularity",
        hole=0.45,
        color_discrete_sequence=["#c9a84c", "#1a1a2e", "#4A90D9", "#48BB78"],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def plot_stay_distribution(df):
    if "stay_length" not in df.columns:
        return None
    fig = px.histogram(
        df, x="stay_length",
        title="Stay Length Distribution",
        labels={"stay_length": "Nights", "count": "Bookings"},
        nbins=12,
        color_discrete_sequence=["#1a1a2e"],
    )
    fig.update_layout(
        bargap=0.15,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
    )
    return fig


def plot_customer_segmentation(df):
    if "guests" not in df.columns:
        return None
    seg = df.groupby(["room_type", "guests"]).size().reset_index(name="count")
    fig = px.bar(
        seg, x="room_type", y="count", color="guests",
        title="Customer Segmentation by Room & Party Size",
        labels={"room_type": "Room", "count": "Bookings", "guests": "Guests"},
        barmode="stack",
        color_continuous_scale="YlOrBr",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
    )
    return fig


def plot_avg_revenue_by_room(df):
    rev = df.groupby("room_type")["final_price"].mean().reset_index()
    rev.columns = ["room_type", "avg_revenue"]
    rev = rev.sort_values("avg_revenue")
    fig = px.bar(
        rev, x="avg_revenue", y="room_type", orientation="h",
        title="Average Revenue by Room Type",
        labels={"avg_revenue": "Avg Revenue (₹)", "room_type": "Room"},
        color="avg_revenue",
        color_continuous_scale=[[0, "#f9f6f0"], [1, "#c9a84c"]],
        text=rev["avg_revenue"].apply(lambda x: f"₹{x:,.0f}"),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Jost, sans-serif"),
        title_font=dict(family="Cormorant Garamond, serif", size=20),
    )
    return fig


def show_kpis(df):
    cols = st.columns(4)
    metrics = [
        ("💰 Total Revenue", f"₹{df['final_price'].sum():,.0f}"),
        ("📋 Bookings", f"{len(df):,}"),
        ("💵 Avg Value", f"₹{df['final_price'].mean():,.0f}"),
        ("🌙 Avg Nights", f"{df.get('stay_length', pd.Series([3])).mean():.1f}"),
    ]
    for col, (label, val) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def show_pricing_simulator(pricing_model, occupancy_model):
    st.markdown('<div class="section-hdr">🧮 Pricing Simulator</div>', unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            room_type = st.selectbox("Room Type", list(ROOM_CONFIG.keys()), key="sim_room")
            stay_length = st.slider("Stay Length (nights)", 1, 14, 3, key="sim_stay")
            arrival_month = st.selectbox(
                "Arrival Month",
                list(MONTH_NAMES.keys()),
                format_func=lambda x: MONTH_NAMES[x],
                key="sim_month"
            )
        with col2:
            rooms_available = st.slider("Rooms Available", 1, 60, 15, key="sim_rooms")
            expected_guests = st.slider("Expected Guests", 1, 6, 2, key="sim_guests")
            lead_time = st.slider("Lead Time (days)", 0, 180, 30, key="sim_lead")

        predicted = predict_price(
            pricing_model, room_type, lead_time, arrival_month, stay_length, expected_guests
        )
        demand_score = compute_demand_score(lead_time, arrival_month, rooms_available)
        pricing = compute_dynamic_price(predicted, demand_score)
        occ = predict_occupancy(occupancy_model, stay_length, expected_guests, arrival_month, lead_time)
        expected_rev = pricing["final_price"] * rooms_available * occ

        st.markdown("---")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Recommended Price", f"₹{pricing['final_price']:,.0f}")
        r2.metric("Floor", f"₹{pricing['price_floor']:,.0f}")
        r3.metric("Ceiling", f"₹{pricing['price_ceiling']:,.0f}")
        r4.metric("Expected Revenue", f"₹{expected_rev:,.0f}")

        st.markdown(f"""
        <div style="margin-top:1rem;">
            <div style="font-family:Jost,sans-serif;font-size:0.8rem;color:#888;margin-bottom:4px;">
                Demand Score: <strong style="color:{'#e53935' if demand_score>0.6 else '#fb8c00' if demand_score>0.35 else '#43a047'};">
                {demand_score:.2f} ({'HIGH' if demand_score>0.6 else 'MEDIUM' if demand_score>0.35 else 'LOW'})</strong>
                &nbsp;·&nbsp; Predicted Occupancy: <strong>{occ*100:.0f}%</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(demand_score * 100, 1),
            title={"text": "Demand Score (%)", "font": {"family": "Cormorant Garamond, serif"}},
            delta={"reference": 50},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"family": "Jost, sans-serif"}},
                "bar": {"color": "#c9a84c"},
                "steps": [
                    {"range": [0, 35], "color": "#e8f5e9"},
                    {"range": [35, 65], "color": "#fff8e1"},
                    {"range": [65, 100], "color": "#ffebee"},
                ],
                "threshold": {
                    "line": {"color": "#1a1a2e", "width": 3},
                    "thickness": 0.75,
                    "value": demand_score * 100,
                }
            }
        ))
        fig.update_layout(
            height=260,
            margin=dict(t=40, b=10, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Jost, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)


def show_manager_dashboard(pricing_model, occupancy_model):
    manager_css()
    username = st.session_state.get("username", "Manager")

    st.markdown(f'<div class="dash-title">Revenue Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-sub">Welcome back, {username} — Grandeur Hotel Analytics</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Controls")
        use_demo = st.checkbox("Use demo data", value=False)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["role", "username"]:
                st.session_state.pop(k, None)
            st.rerun()

    df = load_bookings()
    if df.empty or use_demo or len(df) < 5:
        if not use_demo and not df.empty:
            st.info("ℹ️ Not enough bookings yet — showing demo data alongside.")
        elif df.empty:
            st.info("ℹ️ No bookings recorded yet. Showing demo analytics.")
        df = make_synthetic_df(400)

    tab1, tab2 = st.tabs(["📊 Analytics", "🧮 Pricing Simulator"])

    with tab1:
        show_kpis(df)
        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            fig = plot_monthly_demand(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = plot_revenue_trend(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig = plot_room_popularity(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col4:
            fig = plot_stay_distribution(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            fig = plot_customer_segmentation(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col6:
            fig = plot_avg_revenue_by_room(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        show_pricing_simulator(pricing_model, occupancy_model)

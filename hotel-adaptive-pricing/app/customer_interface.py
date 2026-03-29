import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pricing_engine import (
    ROOM_CONFIG, predict_price, compute_demand_score,
    compute_dynamic_price, apply_discounts, recommend_room
)

STORAGE_PATH = "storage/bookings.csv"
os.makedirs("storage", exist_ok=True)


def save_booking(booking: dict):
    if os.path.exists(STORAGE_PATH):
        df = pd.read_csv(STORAGE_PATH)
    else:
        df = pd.DataFrame()
    new_row = pd.DataFrame([booking])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(STORAGE_PATH, index=False)


def customer_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Jost:wght@300;400;500;600&display=swap');

    .page-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.8rem;
        font-weight: 300;
        color: #1a1a2e;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .page-sub {
        font-family: 'Jost', sans-serif;
        font-size: 0.8rem;
        color: #9a8866;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    .room-card {
        background: #fff;
        border-radius: 4px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        border: 1px solid #f0ece4;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .room-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.14);
    }
    .room-header {
        padding: 1.5rem 1.5rem 1rem;
        border-bottom: 1px solid #f5f1eb;
    }
    .room-emoji {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .room-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .room-capacity {
        font-family: 'Jost', sans-serif;
        font-size: 0.78rem;
        color: #9a8866;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .room-body {
        padding: 1rem 1.5rem 1.5rem;
    }
    .room-price {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #c9a84c;
        margin-bottom: 0.5rem;
    }
    .room-price-label {
        font-family: 'Jost', sans-serif;
        font-size: 0.7rem;
        color: #bbb;
        letter-spacing: 0.1em;
    }
    .amenity-tag {
        display: inline-block;
        background: #f9f6f0;
        border: 1px solid #e8e0d0;
        border-radius: 20px;
        padding: 3px 10px;
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        color: #7a6e5f;
        margin: 2px;
    }
    .rec-badge {
        background: linear-gradient(135deg, #c9a84c, #e8c96d);
        color: #fff;
        font-family: 'Jost', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .price-breakdown {
        background: #fafaf8;
        border: 1px solid #e8e0d0;
        border-radius: 4px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }
    .breakdown-row {
        display: flex;
        justify-content: space-between;
        font-family: 'Jost', sans-serif;
        font-size: 0.85rem;
        color: #555;
        padding: 4px 0;
    }
    .breakdown-total {
        display: flex;
        justify-content: space-between;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a1a2e;
        border-top: 1px solid #e8e0d0;
        padding-top: 8px;
        margin-top: 4px;
    }
    .demand-bar-wrap {
        background: #eee;
        border-radius: 10px;
        height: 6px;
        margin: 4px 0 8px;
        overflow: hidden;
    }
    .demand-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #4CAF50, #FFC107, #f44336);
    }
    .section-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 2rem 0 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def show_room_cards(rooms_to_highlight: list, pricing_model, lead_time, arrival_month,
                    stay_length, guests, is_repeat, traveler_type):
    cols = st.columns(2)
    for i, (room_name, cfg) in enumerate(ROOM_CONFIG.items()):
        with cols[i % 2]:
            is_rec = room_name in rooms_to_highlight
            predicted = predict_price(
                pricing_model, room_name, lead_time, arrival_month,
                stay_length, guests
            )
            demand_score = compute_demand_score(lead_time, arrival_month)
            pricing = compute_dynamic_price(predicted, demand_score)
            disc = apply_discounts(
                pricing["final_price"], lead_time, stay_length, is_repeat, predicted
            )

            amenity_tags = "".join(
                f'<span class="amenity-tag">{a}</span>' for a in cfg["amenities"]
            )
            rec_badge = '<span class="rec-badge">★ Recommended</span>' if is_rec else ""

            st.markdown(f"""
            <div class="room-card">
                <div class="room-header">
                    {rec_badge}
                    <div class="room-emoji">{cfg["emoji"]}</div>
                    <div class="room-name">{room_name}</div>
                    <div class="room-capacity">Up to {cfg["capacity"]} guests &nbsp;·&nbsp; {stay_length} nights</div>
                </div>
                <div class="room-body">
                    <div class="room-price">₹{disc["final_price"]:,.0f}</div>
                    <div class="room-price-label">TOTAL STAY · TAXES INCLUDED</div>
                    <div style="margin: 0.8rem 0;">{amenity_tags}</div>
                    <div style="font-family:Jost,sans-serif;font-size:0.75rem;color:#888;margin-top:0.8rem;">
                        Demand level &nbsp;
                        <span style="color:{'#e53935' if demand_score > 0.6 else '#fb8c00' if demand_score > 0.35 else '#43a047'};">
                            {'HIGH' if demand_score > 0.6 else 'MEDIUM' if demand_score > 0.35 else 'LOW'}
                        </span>
                    </div>
                    <div class="demand-bar-wrap">
                        <div class="demand-bar-fill" style="width:{int(demand_score*100)}%;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Book {room_name}", key=f"book_{room_name}", use_container_width=True):
                st.session_state["booking_room"] = room_name
                st.session_state["booking_price"] = disc["final_price"]
                st.session_state["booking_predicted"] = predicted
                st.session_state["booking_discounts"] = disc
                st.session_state["booking_pricing"] = pricing
                st.rerun()

        if i == 1:
            cols = st.columns(2)


def show_booking_confirmation(username, stay_length, guests, arrival_month):
    room = st.session_state["booking_room"]
    disc = st.session_state["booking_discounts"]
    pricing = st.session_state["booking_pricing"]
    predicted = st.session_state["booking_predicted"]

    st.markdown(f'<div class="section-title">Confirm Booking — {room}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        breakdown_html = ""
        for name, pct in disc["discounts"]:
            amt = pricing["final_price"] * pct
            breakdown_html += f'<div class="breakdown-row"><span>{name}</span><span style="color:#43a047;">-₹{amt:,.0f} ({int(pct*100)}%)</span></div>'
        if disc["coupon"] > 0:
            breakdown_html += f'<div class="breakdown-row"><span>Promo Coupon</span><span style="color:#43a047;">-₹{disc["coupon"]:,.0f}</span></div>'

        st.markdown(f"""
        <div class="price-breakdown">
            <div class="breakdown-row"><span>Base predicted price</span><span>₹{predicted:,.0f}</span></div>
            <div class="breakdown-row"><span>Dynamic price</span><span>₹{pricing['dynamic_price']:,.0f}</span></div>
            {breakdown_html}
            <div class="breakdown-total"><span>Total</span><span>₹{disc['final_price']:,.0f}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        cfg = ROOM_CONFIG[room]
        st.markdown(f"""
        <div style="background:#f9f6f0;border:1px solid #e8e0d0;border-radius:4px;padding:1.5rem;text-align:center;">
            <div style="font-size:3rem;">{cfg['emoji']}</div>
            <div style="font-family:Cormorant Garamond,serif;font-size:1.4rem;font-weight:600;color:#1a1a2e;">{room}</div>
            <div style="font-family:Jost,sans-serif;font-size:0.8rem;color:#9a8866;margin-top:0.5rem;">
                {stay_length} nights · {guests} guests
            </div>
            <div style="font-family:Cormorant Garamond,serif;font-size:2rem;font-weight:600;color:#c9a84c;margin-top:1rem;">
                ₹{disc['final_price']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Confirm Booking", use_container_width=True, type="primary"):
            booking = {
                "customer_name": username,
                "room_type": room,
                "stay_length": stay_length,
                "guests": guests,
                "predicted_price": round(predicted, 2),
                "final_price": round(disc["final_price"], 2),
                "booking_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "arrival_month": arrival_month,
            }
            save_booking(booking)
            st.success(f"🎉 Booking confirmed! Enjoy your stay at Grandeur Hotel.")
            st.balloons()
            del st.session_state["booking_room"]
    with col_b:
        if st.button("← Back to Rooms", use_container_width=True):
            del st.session_state["booking_room"]
            st.rerun()


def show_customer_interface(pricing_model, occupancy_model):
    customer_css()
    username = st.session_state.get("username", "Guest")

    st.markdown(f'<div class="page-header">Welcome, {username}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Grandeur Hotel — Book Your Perfect Stay</div>', unsafe_allow_html=True)

    # Sidebar config
    with st.sidebar:
        st.markdown("### 🔍 Search & Preferences")
        check_in = st.date_input("Check-in Date", value=date.today() + timedelta(days=7))
        stay_length = st.slider("Nights", 1, 14, 2)
        guests = st.number_input("Guests", 1, 6, 2)
        traveler_type = st.selectbox("Traveler Type", ["Leisure", "Business", "Family"])
        is_repeat = st.checkbox("Returning Guest (5% off)")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["role", "username"]:
                st.session_state.pop(k, None)
            st.rerun()

    lead_time = max(0, (check_in - date.today()).days)
    arrival_month = check_in.month

    recommended = recommend_room(guests, stay_length, traveler_type)

    if "booking_room" not in st.session_state:
        # Recommendation banner
        rec_cfg = ROOM_CONFIG[recommended]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#2d2d44);border-radius:4px;
                    padding:1.2rem 1.8rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem;">
            <span style="font-size:2rem;">{rec_cfg['emoji']}</span>
            <div>
                <div style="font-family:Jost,sans-serif;font-size:0.7rem;color:#c9a84c;
                            letter-spacing:0.25em;text-transform:uppercase;">AI Recommendation</div>
                <div style="font-family:Cormorant Garamond,serif;font-size:1.3rem;
                            color:#fff;font-weight:600;">We suggest the {recommended}</div>
                <div style="font-family:Jost,sans-serif;font-size:0.78rem;color:#888;">
                    Perfect for {guests} guests · {stay_length} nights · {traveler_type} travel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        show_room_cards(
            [recommended], pricing_model, lead_time, arrival_month,
            stay_length, guests, is_repeat, traveler_type
        )
    else:
        show_booking_confirmation(username, stay_length, guests, arrival_month)

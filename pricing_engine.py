import numpy as np
from datetime import datetime

ROOM_CONFIG = {
    "Standard Room": {
        "capacity": 2,
        "base_price_inr": 3500,
        "amenities": ["Free WiFi", "Breakfast Included", "24hr Service"],
        "emoji": "🛏️",
        "color": "#4A90D9",
    },
    "Deluxe Room": {
        "capacity": 3,
        "base_price_inr": 5200,
        "amenities": ["Private Balcony", "Breakfast Included", "Mini Bar"],
        "emoji": "🌟",
        "color": "#7B68EE",
    },
    "Family Suite": {
        "capacity": 5,
        "base_price_inr": 8200,
        "amenities": ["Living Area", "Breakfast Included", "Kids Play Zone"],
        "emoji": "👨‍👩‍👧‍👦",
        "color": "#48BB78",
    },
    "Premium Room": {
        "capacity": 4,
        "base_price_inr": 6500,
        "amenities": ["City View", "Executive Lounge", "Complimentary Spa"],
        "emoji": "💎",
        "color": "#ED8936",
    },
}

ROOM_TYPE_MAP = {
    "Standard Room": "Standard",
    "Deluxe Room": "Deluxe",
    "Family Suite": "Suite",
    "Premium Room": "Premium",
}

HOTEL_MAP = {"City Hotel": 0, "Resort Hotel": 1}


def compute_demand_score(lead_time: int, arrival_month: int, rooms_available: int = 20):
    peak_months = [6, 7, 8, 12, 1]
    month_factor = 0.8 if arrival_month in peak_months else 0.35
    lead_time_factor = max(0, min(1.0, 1.0 - lead_time / 180))
    room_demand_factor = max(0, 1.0 - rooms_available / 50)
    demand_score = (
        0.4 * lead_time_factor
        + 0.3 * month_factor
        + 0.3 * room_demand_factor
    )
    return round(demand_score, 4)


def predict_price(pricing_model, room_type_display: str, lead_time: int,
                  arrival_month: int, stay_length: int, guests: int,
                  prev_cancellations: int = 0, prev_not_canceled: int = 1,
                  hotel_type: str = "City Hotel"):
    import pandas as pd

    room_type_internal = ROOM_TYPE_MAP.get(room_type_display, "Standard")
    stays_week = max(0, stay_length - min(stay_length, 2))
    stays_weekend = stay_length - stays_week

    row = pd.DataFrame([{
        "hotel": hotel_type,
        "lead_time": lead_time,
        "arrival_month": arrival_month,
        "arrival_week_number": max(1, min(52, arrival_month * 4)),
        "stays_in_week_nights": stays_week,
        "stays_in_weekend_nights": stays_weekend,
        "adults": min(guests, 4),
        "children": max(0, guests - 4),
        "babies": 0,
        "room_type": room_type_internal,
        "previous_cancellations": prev_cancellations,
        "previous_bookings_not_canceled": prev_not_canceled,
        "stay_length": stay_length,
        "number_of_guests": guests,
        "cancellation_risk": prev_cancellations / (prev_not_canceled + 1),
    }])

    try:
        predicted_usd = float(pricing_model.predict(row)[0])
        # Convert USD-ish ADR to INR (×75 approx) and scale by stay
        predicted_inr = predicted_usd * 75
    except Exception:
        predicted_inr = ROOM_CONFIG[room_type_display]["base_price_inr"]

    return max(predicted_inr, ROOM_CONFIG[room_type_display]["base_price_inr"] * 0.6)


def compute_dynamic_price(predicted_price: float, demand_score: float) -> dict:
    dynamic_price = predicted_price * (1 + demand_score)
    price_floor = predicted_price * 0.85
    price_ceiling = predicted_price * 1.40
    final_price = max(price_floor, min(dynamic_price, price_ceiling))
    return {
        "predicted_price": round(predicted_price, 2),
        "dynamic_price": round(dynamic_price, 2),
        "price_floor": round(price_floor, 2),
        "price_ceiling": round(price_ceiling, 2),
        "final_price": round(final_price, 2),
        "demand_score": demand_score,
    }


def apply_discounts(price: float, lead_time: int, stay_length: int,
                    is_repeat_guest: bool, predicted_price: float) -> dict:
    discounts = []
    discount_pct = 0.0

    if lead_time > 60:
        discounts.append(("Early Bird (60+ days)", 0.10))
        discount_pct += 0.10
    if stay_length >= 5:
        discounts.append(("Long Stay (5+ nights)", 0.08))
        discount_pct += 0.08
    if is_repeat_guest:
        discounts.append(("Loyalty Guest", 0.05))
        discount_pct += 0.05

    discount_pct = min(discount_pct, 0.20)
    discounted_price = price * (1 - discount_pct)

    coupon = 500 if discounted_price > 5000 else 0
    final_price = discounted_price - coupon

    min_price = predicted_price * 0.80
    final_price = max(final_price, min_price)

    return {
        "discounts": discounts,
        "discount_pct": discount_pct,
        "coupon": coupon,
        "final_price": round(final_price, 2),
    }


def recommend_room(guests: int, stay_length: int, traveler_type: str) -> str:
    if guests >= 4:
        return "Family Suite"
    if traveler_type == "Business":
        return "Premium Room"
    if stay_length >= 5:
        return "Deluxe Room"
    return "Standard Room"


def predict_occupancy(occupancy_model, stay_length: int, guests: int,
                      arrival_month: int, lead_time: int) -> float:
    import pandas as pd
    week_num = max(1, min(52, arrival_month * 4))
    row = pd.DataFrame([{
        "stay_length": stay_length,
        "number_of_guests": guests,
        "arrival_month": arrival_month,
        "lead_time": lead_time,
        "arrival_week_number": week_num,
    }])
    try:
        occ = float(occupancy_model.predict(row)[0])
        return max(0.25, min(0.98, occ))
    except Exception:
        return 0.65

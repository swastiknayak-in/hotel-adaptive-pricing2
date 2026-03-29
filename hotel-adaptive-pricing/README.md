# 🏨 Grandeur Hotel — Adaptive Pricing & Revenue Management

A production-ready hotel booking platform with ML-powered dynamic pricing, demand forecasting, and revenue analytics.

## Features

| Feature | Detail |
|---|---|
| 🤖 ML Pricing | Random Forest trained on 8k bookings, auto-trained at runtime |
| 📈 Dynamic Demand | Demand score × lead time × seasonality × availability |
| 🛎️ Customer Portal | Room cards, AI recommendation, discount engine |
| 📊 Manager Dashboard | 6 Plotly charts + live pricing simulator |
| 💰 Discount Engine | Early bird, long stay, loyalty, promo coupon |
| 🔄 Auto-train | Models trained at first run, cached for speed |

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app/main_app.py
```

## Deploy on Streamlit Cloud

1. Fork / push this repo to GitHub  
2. Go to [share.streamlit.io](https://share.streamlit.io)  
3. Select repo → **Entry file:** `app/main_app.py`  
4. Deploy — models train automatically on first run

> **Note:** The `/models` directory is git-ignored. Models are auto-generated at runtime (< 25 MB each).

## Architecture

```
hotel-adaptive-pricing/
├── app/
│   ├── main_app.py          ← Streamlit entry point
│   ├── login_page.py        ← Role selection
│   ├── customer_interface.py
│   └── manager_dashboard.py
├── core/
│   ├── model_training.py    ← RF + GBR pipelines
│   └── pricing_engine.py    ← Demand, discounts, recommendations
├── storage/
│   └── bookings.csv         ← Auto-created on first booking
├── models/                  ← Auto-generated (git-ignored)
├── data/                    ← Auto-generated training data
└── requirements.txt
```

## Roles

- **Guest** — Browse rooms, get AI recommendation, book with dynamic pricing
- **Manager** — Full analytics dashboard + pricing simulator

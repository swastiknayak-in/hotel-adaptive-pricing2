import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)


def generate_synthetic_hotel_data(n=8000):
    """Generate realistic synthetic hotel booking data."""
    np.random.seed(42)
    hotels = np.random.choice(["City Hotel", "Resort Hotel"], n, p=[0.6, 0.4])
    arrival_month = np.random.randint(1, 13, n)
    arrival_week = np.random.randint(1, 53, n)
    lead_time = np.random.exponential(60, n).astype(int).clip(0, 365)
    stays_weeknights = np.random.randint(0, 8, n)
    stays_weekendnights = np.random.randint(0, 4, n)
    adults = np.random.choice([1, 2, 3, 4], n, p=[0.2, 0.55, 0.15, 0.10])
    children = np.random.choice([0, 1, 2], n, p=[0.75, 0.15, 0.10])
    babies = np.random.choice([0, 1], n, p=[0.95, 0.05])
    room_type = np.random.choice(
        ["Standard", "Deluxe", "Suite", "Premium"], n, p=[0.4, 0.3, 0.15, 0.15]
    )
    prev_cancel = np.random.poisson(0.2, n).clip(0, 5)
    prev_not_cancel = np.random.poisson(1.5, n).clip(0, 10)

    # Simulate ADR with realistic factors
    base_price = {"Standard": 80, "Deluxe": 120, "Suite": 200, "Premium": 160}
    peak_multiplier = np.where(np.isin(arrival_month, [6, 7, 8, 12]), 1.3, 1.0)
    resort_multiplier = np.where(hotels == "Resort Hotel", 1.2, 1.0)
    room_base = np.array([base_price[r] for r in room_type])
    noise = np.random.normal(0, 15, n)

    adr = (room_base * peak_multiplier * resort_multiplier
           + lead_time * 0.05
           + (adults + children) * 8
           + noise).clip(30, 450)

    df = pd.DataFrame({
        "hotel": hotels,
        "lead_time": lead_time,
        "arrival_month": arrival_month,
        "arrival_week_number": arrival_week,
        "stays_in_week_nights": stays_weeknights,
        "stays_in_weekend_nights": stays_weekendnights,
        "adults": adults,
        "children": children,
        "babies": babies,
        "room_type": room_type,
        "previous_cancellations": prev_cancel,
        "previous_bookings_not_canceled": prev_not_cancel,
        "adr": adr,
    })
    return df


def build_features(df):
    df = df.copy()
    df["stay_length"] = df["stays_in_week_nights"] + df["stays_in_weekend_nights"]
    df["number_of_guests"] = df["adults"] + df["children"] + df["babies"]
    df["cancellation_risk"] = df["previous_cancellations"] / (df["previous_bookings_not_canceled"] + 1)
    return df


def get_preprocessor():
    numeric_features = [
        "lead_time", "arrival_month", "arrival_week_number",
        "stays_in_week_nights", "stays_in_weekend_nights",
        "previous_cancellations", "previous_bookings_not_canceled",
        "adults", "children", "babies",
        "stay_length", "number_of_guests", "cancellation_risk",
    ]
    categorical_features = ["hotel", "room_type"]

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ])
    return preprocessor


def train_pricing_model(df):
    df = build_features(df)
    X = df.drop(columns=["adr"])
    y = df["adr"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("preprocessor", get_preprocessor()),
        ("regressor", RandomForestRegressor(
            n_estimators=120,
            max_depth=12,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        )),
    ])
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"[Pricing Model] RMSE: ₹{rmse:.2f}")
    joblib.dump(model, "models/pricing_model.pkl")
    return model


def train_occupancy_model(df):
    df = build_features(df)
    # Synthetic occupancy rate
    np.random.seed(7)
    peak = df["arrival_month"].isin([6, 7, 8, 12]).astype(float)
    occ = (0.55 + peak * 0.2 + np.random.normal(0, 0.08, len(df))).clip(0.2, 0.99)
    df["occupancy_rate"] = occ

    features = ["stay_length", "number_of_guests", "arrival_month",
                "lead_time", "arrival_week_number"]
    X = df[features]
    y = df["occupancy_rate"]

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("regressor", GradientBoostingRegressor(
            n_estimators=80, max_depth=4, random_state=42
        )),
    ])
    model.fit(X, y)
    joblib.dump(model, "models/occupancy_model.pkl")
    print("[Occupancy Model] Trained successfully.")
    return model


def train_models():
    print("Generating training data...")
    csv_path = "data/hotel_bookings.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = generate_synthetic_hotel_data(8000)
        df.to_csv(csv_path, index=False)

    print("Training pricing model...")
    pricing_model = train_pricing_model(df)
    print("Training occupancy model...")
    occupancy_model = train_occupancy_model(df)
    return pricing_model, occupancy_model


def load_or_train_models():
    pricing_path = "models/pricing_model.pkl"
    occupancy_path = "models/occupancy_model.pkl"

    if os.path.exists(pricing_path) and os.path.exists(occupancy_path):
        try:
            pricing_model = joblib.load(pricing_path)
            occupancy_model = joblib.load(occupancy_path)
            print("Models loaded from disk.")
            return pricing_model, occupancy_model
        except Exception:
            pass

    return train_models()

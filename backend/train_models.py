"""
Vatavarnam ML Training Pipeline — REAL DATA Edition (Forecast / Page 2)
=======================================================================
Fetches 12 months of REAL hourly weather + air-quality data from
Open-Meteo archive APIs for Delhi NCR and trains the 6 Forecast models.

Targets (all shift -24 h, i.e. "predict tomorrow's value"):
  1. Rain Probability        — Calibrated Logistic Regression
  2. PM10                    — Gradient Boosting Regressor
  3. PM2.5                   — Extra Trees Regressor
  4. Carbon Emissions (CO)   — Random Forest Regressor
  5. AQI (European)          — MLP Neural Network
  6. Transportation (traffic proxy from CO rush-hour signal) — SVR

Activity models (Page 1) are kept unchanged and trained on the same
real features with derived activity scores.
"""

import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
import requests

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    GradientBoostingRegressor,
    ExtraTreesRegressor,
    RandomForestRegressor,
)
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
#  STEP 1 — Fetch REAL Data from Open-Meteo Archive APIs
# ══════════════════════════════════════════════════════════════════════

def fetch_real_delhi_data(start_date="2024-01-01", end_date="2025-06-30"):
    """
    Downloads real hourly weather + air-quality data from Open-Meteo
    for Delhi NCR (lat 28.6139, lon 77.2090).
    
    The free archive API limits requests, so we chunk by 3-month blocks
    to stay well within limits.
    """
    print(f"  Fetching real data from {start_date} to {end_date} ...")

    # --- Weather Archive ---
    WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
    weather_params = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,surface_pressure,wind_speed_10m,shortwave_radiation,rain",
        "timezone": "Asia/Kolkata",
    }

    # --- Air Quality Archive ---
    AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    air_params = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "pm10,pm2_5,carbon_monoxide,european_aqi",
        "timezone": "Asia/Kolkata",
    }

    print("  [1/2] Fetching weather archive ...")
    weather_resp = requests.get(WEATHER_URL, params=weather_params, timeout=60)
    weather_resp.raise_for_status()
    weather_json = weather_resp.json()
    print(f"        Got {len(weather_json['hourly']['time'])} hourly weather records.")

    time.sleep(1)  # Be polite to the free API

    print("  [2/2] Fetching air quality archive ...")
    air_resp = requests.get(AIR_URL, params=air_params, timeout=60)
    air_resp.raise_for_status()
    air_json = air_resp.json()
    print(f"        Got {len(air_json['hourly']['time'])} hourly air quality records.")

    # --- Build a unified DataFrame ---
    weather_hourly = weather_json["hourly"]
    air_hourly = air_json["hourly"]

    df_weather = pd.DataFrame({
        "timestamp": pd.to_datetime(weather_hourly["time"]),
        "temperature": weather_hourly["temperature_2m"],
        "humidity": weather_hourly["relative_humidity_2m"],
        "dew_point": weather_hourly["dew_point_2m"],
        "pressure": weather_hourly["surface_pressure"],
        "wind_speed": weather_hourly["wind_speed_10m"],
        "radiation": [r / 1000.0 for r in weather_hourly["shortwave_radiation"]],  # W/m² -> kW/m² for scale
        "rain_amount_mm": weather_hourly["rain"],
    })

    df_air = pd.DataFrame({
        "timestamp": pd.to_datetime(air_hourly["time"]),
        "pm10_raw": air_hourly["pm10"],
        "pm25_raw": air_hourly["pm2_5"],
        "co_raw": air_hourly["carbon_monoxide"],
        "aqi_raw": air_hourly["european_aqi"],
    })

    # Merge on timestamp
    df = pd.merge(df_weather, df_air, on="timestamp", how="inner")

    # Temporal columns
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["dayofyear"] = df["timestamp"].dt.dayofyear

    # Binary rain event
    df["rain_event"] = (df["rain_amount_mm"] > 0.1).astype(int)

    # Drop rows with null values from the API
    df = df.dropna(subset=["temperature", "humidity", "pm10_raw", "pm25_raw", "co_raw", "aqi_raw"])

    df = df.sort_values("timestamp").reset_index(drop=True)
    print(f"  Merged dataset: {len(df)} clean hourly records across {df['month'].nunique()} months.\n")
    return df


# ══════════════════════════════════════════════════════════════════════
#  STEP 2 — Feature Engineering (identical logic, now on real data)
# ══════════════════════════════════════════════════════════════════════

def engineer_features(df):
    data = df.copy()

    # 1. Cyclic Temporal Features
    data["sin_hour"] = np.sin(2 * np.pi * data["hour"] / 24)
    data["cos_hour"] = np.cos(2 * np.pi * data["hour"] / 24)
    data["sin_dayofweek"] = np.sin(2 * np.pi * data["dayofweek"] / 7)
    data["cos_dayofweek"] = np.cos(2 * np.pi * data["dayofweek"] / 7)
    data["sin_month"] = np.sin(2 * np.pi * data["month"] / 12)
    data["cos_month"] = np.cos(2 * np.pi * data["month"] / 12)
    data["is_weekend"] = (data["dayofweek"] >= 5).astype(float)
    data["is_rush_hour"] = (
        ((data["hour"] >= 8) & (data["hour"] <= 11))
        | ((data["hour"] >= 17) & (data["hour"] <= 21))
    ).astype(float)

    # 2. Lag Features
    for lag in [1, 3, 6, 12, 24, 48]:
        data[f"pm25_lag_{lag}"] = data["pm25_raw"].shift(lag)
        data[f"pm10_lag_{lag}"] = data["pm10_raw"].shift(lag)
        data[f"aqi_lag_{lag}"] = data["aqi_raw"].shift(lag)
        data[f"temp_lag_{lag}"] = data["temperature"].shift(lag)
        data[f"humidity_lag_{lag}"] = data["humidity"].shift(lag)
        data[f"wind_speed_lag_{lag}"] = data["wind_speed"].shift(lag)

    # 3. Rolling Statistics
    for window in [6, 24]:
        data[f"pm25_roll_mean_{window}"] = data["pm25_raw"].rolling(window).mean()
        data[f"pm25_roll_std_{window}"] = data["pm25_raw"].rolling(window).std()
        data[f"pm10_roll_mean_{window}"] = data["pm10_raw"].rolling(window).mean()
        data[f"pm10_roll_std_{window}"] = data["pm10_raw"].rolling(window).std()
        data[f"temp_roll_mean_{window}"] = data["temperature"].rolling(window).mean()
        data[f"wind_roll_mean_{window}"] = data["wind_speed"].rolling(window).mean()

    # 4. Atmospheric Physics & Environmental Indices
    data["stagnation_index"] = data["pressure"] / (data["wind_speed"] + 0.5)
    data["inversion_proxy"] = (data["temperature"] - data["dew_point"]) / (data["wind_speed"] + 0.1)
    data["smog_formation_factor"] = (data["radiation"] * data["temperature"]) / (data["humidity"] + 1.0)
    data["washout_proxy"] = data["rain_amount_mm"] * data["pm10_lag_1"].fillna(0)
    data["temp_humidity_index"] = data["temperature"] * (data["humidity"] / 100.0)

    # 5. Forecast Day 1 Targets (predict 24 hours into the future)
    data["target_rain"] = data["rain_event"].shift(-24)
    data["target_pm10"] = data["pm10_raw"].shift(-24)
    data["target_pm25"] = data["pm25_raw"].shift(-24)
    data["target_emissions"] = data["co_raw"].shift(-24)      # CO as real emissions proxy
    data["target_aqi"] = data["aqi_raw"].shift(-24)
    # Transportation proxy: CO during rush hours is a strong proxy for traffic density
    data["target_transportation"] = np.clip(
        data["co_raw"].shift(-24) / 25.0,  # Normalize CO to a 0-100 scale roughly
        5, 100
    )

    clean_data = data.dropna().reset_index(drop=True)
    return clean_data


# ══════════════════════════════════════════════════════════════════════
#  STEP 3 — Derive Activity Scores from REAL data
# ══════════════════════════════════════════════════════════════════════

def compute_activity_targets(df):
    """
    Derives activity suitability/risk scores from real weather + AQ data.
    These formulas are identical to the original but now they operate on
    REAL atmospheric measurements instead of synthetic ones.
    """
    data = df.copy()

    heat_stress = np.maximum(0, data["temperature"] - 35) * 1.5 + np.maximum(0, 12 - data["temperature"]) * 1.5

    # 1. Walking Suitability (0-100%): HIGHER = GOOD
    data["target_act_walking"] = np.clip(
        100.0 - (data["pm25_raw"] / 300.0) * 50.0 - (data["pm10_raw"] / 450.0) * 20.0 - heat_stress,
        5, 95
    )

    # 2. Outing Suitability (0-100%): HIGHER = GOOD
    data["target_act_outing"] = np.clip(
        100.0 - (data["aqi_raw"] / 200.0) * 55.0 - (data["rain_amount_mm"] * 8.0) + (data["radiation"] * 4.0),
        5, 95
    )

    # 3. Long Drive Road Safety (0-100%): HIGHER = GOOD
    # Visibility proxy: lower PM = better visibility
    visibility_proxy = np.clip(10.0 - (data["pm25_raw"] / 50.0), 0.2, 12.0)
    data["target_act_long_drive"] = np.clip(
        (visibility_proxy / 10.0) * 60.0 + 35.0 - (data["rain_amount_mm"] * 5.0),
        5, 95
    )

    # 4. Shipment Safety (0-100%): HIGHER = GOOD
    data["target_act_shipment"] = np.clip(
        100.0 - (data["humidity"] / 100.0) * 30.0 - (data["rain_amount_mm"] * 10.0) - (data["pm10_raw"] / 500.0) * 25.0,
        5, 95
    )

    # 5. Asthma Index (0-100%): HIGHER = BAD
    stagnation = data["pressure"] / (data["wind_speed"] + 0.5)
    data["target_act_asthma"] = np.clip(
        (data["pm25_raw"] / 300.0) * 60.0 + (stagnation / 150.0) * 25.0,
        5, 98
    )

    # 6. Flight Delay Risk (0-100%): HIGHER = BAD
    data["target_act_flight_delay"] = np.clip(
        (1.0 - visibility_proxy / 10.0) * 60.0 + (data["wind_speed"] < 5.0).astype(float) * 15.0 + (data["rain_amount_mm"] > 2.0).astype(float) * 20.0,
        2, 98
    )

    # 7. Visibility Index (0-100%): HIGHER = GOOD
    # Good visibility = low PM2.5, low humidity, low rain, good wind
    data["target_act_visibility"] = np.clip(
        100.0
        - (data["pm25_raw"] / 250.0) * 45.0
        - (data["humidity"] / 100.0) * 20.0
        - (data["rain_amount_mm"] * 6.0)
        + (np.clip(data["wind_speed"], 0, 20) / 20.0) * 10.0,
        5, 95
    )

    return data


# ══════════════════════════════════════════════════════════════════════
#  STEP 4 — Train All Models
# ══════════════════════════════════════════════════════════════════════

def train_and_evaluate_all_models():
    print("=" * 70)
    print("VATAVARNAM — REAL DATA ML TRAINING PIPELINE")
    print("=" * 70)

    # ── Fetch real data ──
    print("\nStep 1: Fetching REAL Delhi NCR data from Open-Meteo APIs ...")
    df_raw = fetch_real_delhi_data(start_date="2024-01-01", end_date="2025-06-30")

    # ── Save raw data for inspection ──
    csv_path = os.path.join(ARTIFACTS_DIR, "real_delhi_data.csv")
    df_raw.to_csv(csv_path, index=False)
    print(f"  Raw data saved to {csv_path}")

    # ── Compute activity targets ──
    print("\nStep 2: Computing activity targets from real data ...")
    df_raw = compute_activity_targets(df_raw)

    # ── Feature engineering ──
    print("\nStep 3: Engineering features ...")
    df = engineer_features(df_raw)
    print(f"  Final feature dataset shape: {df.shape}")

    feature_cols = [
        "temperature", "humidity", "wind_speed", "pressure", "radiation", "dew_point",
        "sin_hour", "cos_hour", "sin_dayofweek", "cos_dayofweek", "sin_month", "cos_month",
        "is_weekend", "is_rush_hour", "stagnation_index", "inversion_proxy",
        "smog_formation_factor", "washout_proxy", "temp_humidity_index",
        "pm25_lag_1", "pm25_lag_24", "pm25_lag_48",
        "pm10_lag_1", "pm10_lag_24", "pm10_lag_48",
        "aqi_lag_1", "aqi_lag_24", "aqi_lag_48",
        "pm25_roll_mean_6", "pm25_roll_mean_24",
        "pm10_roll_mean_6", "pm10_roll_mean_24",
        "temp_roll_mean_24", "wind_roll_mean_24"
    ]

    # Chronological split (80/20) — correct for time series
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    print(f"  Train: {len(train_df)} rows | Test: {len(test_df)} rows")

    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]

    with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "w") as f:
        json.dump(feature_cols, f)

    forecast_metrics = {}

    # ═══════════════════════════════════════════════════════════════
    #  FORECAST MODELS (Page 2)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Training Page 2 Forecast Models on REAL DATA")
    print("=" * 70)

    # 1. Rain Probability
    print("\n[Forecast 1: Rain Probability] Calibrated Logistic Regression ...")
    rain_features = [
        "humidity", "temperature", "dew_point", "pressure", "wind_speed",
        "sin_month", "cos_month", "temp_humidity_index",
        "humidity_lag_1", "humidity_lag_24"
    ]
    scaler_rain = StandardScaler()
    X_train_rain_scaled = scaler_rain.fit_transform(train_df[rain_features])
    X_test_rain_scaled = scaler_rain.transform(test_df[rain_features])
    base_lr = LogisticRegression(C=1.0, max_iter=500, random_state=42)
    model_rain = CalibratedClassifierCV(estimator=base_lr, method="sigmoid", cv=5)
    model_rain.fit(X_train_rain_scaled, train_df["target_rain"])
    rain_pred_proba = model_rain.predict_proba(X_test_rain_scaled)[:, 1]
    rain_pred_class = (rain_pred_proba > 0.5).astype(int)
    rain_acc = np.mean(rain_pred_class == test_df["target_rain"].values)
    forecast_metrics["rain"] = {"model": "Calibrated Logistic Regression", "accuracy": round(float(rain_acc), 4)}
    print(f"  -> Accuracy: {rain_acc:.4f}")
    joblib.dump({"model": model_rain, "scaler": scaler_rain, "features": rain_features}, os.path.join(ARTIFACTS_DIR, "model_rain.joblib"))

    # 2. PM10
    print("\n[Forecast 2: PM10] Gradient Boosting Regressor ...")
    model_pm10 = GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, subsample=0.85, random_state=42)
    model_pm10.fit(X_train, train_df["target_pm10"])
    y_pred_pm10 = model_pm10.predict(X_test)
    r2_pm10 = r2_score(test_df["target_pm10"], y_pred_pm10)
    rmse_pm10 = np.sqrt(mean_squared_error(test_df["target_pm10"], y_pred_pm10))
    mae_pm10 = mean_absolute_error(test_df["target_pm10"], y_pred_pm10)
    forecast_metrics["pm10"] = {"model": "Gradient Boosting", "r2": round(float(r2_pm10), 4), "rmse": round(float(rmse_pm10), 2), "mae": round(float(mae_pm10), 2)}
    print(f"  -> R²: {r2_pm10:.4f}, RMSE: {rmse_pm10:.2f}, MAE: {mae_pm10:.2f}")
    joblib.dump(model_pm10, os.path.join(ARTIFACTS_DIR, "model_pm10.joblib"))

    # 3. PM2.5
    print("\n[Forecast 3: PM2.5] Extra Trees Regressor ...")
    model_pm25 = ExtraTreesRegressor(n_estimators=150, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1)
    model_pm25.fit(X_train, train_df["target_pm25"])
    y_pred_pm25 = model_pm25.predict(X_test)
    r2_pm25 = r2_score(test_df["target_pm25"], y_pred_pm25)
    rmse_pm25 = np.sqrt(mean_squared_error(test_df["target_pm25"], y_pred_pm25))
    mae_pm25 = mean_absolute_error(test_df["target_pm25"], y_pred_pm25)
    forecast_metrics["pm25"] = {"model": "Extra Trees", "r2": round(float(r2_pm25), 4), "rmse": round(float(rmse_pm25), 2), "mae": round(float(mae_pm25), 2)}
    print(f"  -> R²: {r2_pm25:.4f}, RMSE: {rmse_pm25:.2f}, MAE: {mae_pm25:.2f}")
    joblib.dump(model_pm25, os.path.join(ARTIFACTS_DIR, "model_pm25.joblib"))

    # 4. Carbon Emissions (CO as real proxy)
    print("\n[Forecast 4: Carbon Emissions (CO)] Random Forest Regressor ...")
    model_emissions = RandomForestRegressor(n_estimators=120, max_depth=10, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model_emissions.fit(X_train, train_df["target_emissions"])
    y_pred_em = model_emissions.predict(X_test)
    r2_em = r2_score(test_df["target_emissions"], y_pred_em)
    rmse_em = np.sqrt(mean_squared_error(test_df["target_emissions"], y_pred_em))
    mae_em = mean_absolute_error(test_df["target_emissions"], y_pred_em)
    forecast_metrics["emissions"] = {"model": "Random Forest", "r2": round(float(r2_em), 4), "rmse": round(float(rmse_em), 2), "mae": round(float(mae_em), 2)}
    print(f"  -> R²: {r2_em:.4f}, RMSE: {rmse_em:.2f}, MAE: {mae_em:.2f}")
    joblib.dump(model_emissions, os.path.join(ARTIFACTS_DIR, "model_emissions.joblib"))

    # 5. AQI (European)
    print("\n[Forecast 5: AQI] MLP Neural Network ...")
    scaler_mlp = StandardScaler()
    X_train_scaled = scaler_mlp.fit_transform(X_train)
    X_test_scaled = scaler_mlp.transform(X_test)
    model_aqi = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", solver="adam", alpha=0.01, max_iter=500, random_state=42)
    model_aqi.fit(X_train_scaled, train_df["target_aqi"])
    y_pred_aqi = model_aqi.predict(X_test_scaled)
    r2_aqi = r2_score(test_df["target_aqi"], y_pred_aqi)
    rmse_aqi = np.sqrt(mean_squared_error(test_df["target_aqi"], y_pred_aqi))
    mae_aqi = mean_absolute_error(test_df["target_aqi"], y_pred_aqi)
    forecast_metrics["aqi"] = {"model": "MLP Neural Network", "r2": round(float(r2_aqi), 4), "rmse": round(float(rmse_aqi), 2), "mae": round(float(mae_aqi), 2)}
    print(f"  -> R²: {r2_aqi:.4f}, RMSE: {rmse_aqi:.2f}, MAE: {mae_aqi:.2f}")
    joblib.dump({"model": model_aqi, "scaler": scaler_mlp}, os.path.join(ARTIFACTS_DIR, "model_aqi.joblib"))

    # 6. Transportation (CO rush-hour proxy)
    print("\n[Forecast 6: Transportation] SVR ...")
    traffic_features = [
        "sin_hour", "cos_hour", "sin_dayofweek", "cos_dayofweek",
        "is_weekend", "is_rush_hour", "temperature", "humidity",
        "wind_speed", "pm10_lag_1", "temp_humidity_index"
    ]
    scaler_svr = StandardScaler()
    X_train_svr = scaler_svr.fit_transform(train_df[traffic_features])
    X_test_svr = scaler_svr.transform(test_df[traffic_features])
    model_trans = SVR(kernel="rbf", C=15.0, epsilon=0.2, gamma="scale")
    model_trans.fit(X_train_svr, train_df["target_transportation"])
    y_pred_trans = model_trans.predict(X_test_svr)
    r2_trans = r2_score(test_df["target_transportation"], y_pred_trans)
    rmse_trans = np.sqrt(mean_squared_error(test_df["target_transportation"], y_pred_trans))
    mae_trans = mean_absolute_error(test_df["target_transportation"], y_pred_trans)
    forecast_metrics["transportation"] = {"model": "SVR", "r2": round(float(r2_trans), 4), "rmse": round(float(rmse_trans), 2), "mae": round(float(mae_trans), 2)}
    print(f"  -> R²: {r2_trans:.4f}, RMSE: {rmse_trans:.2f}, MAE: {mae_trans:.2f}")
    joblib.dump({"model": model_trans, "scaler": scaler_svr, "features": traffic_features}, os.path.join(ARTIFACTS_DIR, "model_transportation.joblib"))

    # Save forecast metrics
    with open(os.path.join(ARTIFACTS_DIR, "model_metrics.json"), "w") as f:
        json.dump(forecast_metrics, f, indent=2)

    # ═══════════════════════════════════════════════════════════════
    #  ACTIVITY MODELS (Page 1) — trained on same real data
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Training 6 Activity Models on REAL DATA")
    print("=" * 70)

    activity_metrics = {}

    # 1. Walking Suitability (Higher = Good)
    print("\n[Activity 1: Walking Suitability] Gradient Boosting ...")
    model_act_walk = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    model_act_walk.fit(X_train, train_df["target_act_walking"])
    y_pred_walk = model_act_walk.predict(X_test)
    r2_walk = r2_score(test_df["target_act_walking"], y_pred_walk)
    rmse_walk = np.sqrt(mean_squared_error(test_df["target_act_walking"], y_pred_walk))
    mae_walk = mean_absolute_error(test_df["target_act_walking"], y_pred_walk)
    activity_metrics["walking"] = {"model": "Gradient Boosting", "polarity": "Higher is Good", "r2": round(float(r2_walk), 4), "rmse": round(float(rmse_walk), 2), "mae": round(float(mae_walk), 2)}
    print(f"  -> R²: {r2_walk:.4f}, RMSE: {rmse_walk:.2f}, MAE: {mae_walk:.2f}")
    joblib.dump(model_act_walk, os.path.join(ARTIFACTS_DIR, "model_act_walking.joblib"))

    # 2. Outing Suitability (Higher = Good)
    print("\n[Activity 2: Outing Suitability] Random Forest ...")
    model_act_outing = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
    model_act_outing.fit(X_train, train_df["target_act_outing"])
    y_pred_outing = model_act_outing.predict(X_test)
    r2_outing = r2_score(test_df["target_act_outing"], y_pred_outing)
    rmse_outing = np.sqrt(mean_squared_error(test_df["target_act_outing"], y_pred_outing))
    mae_outing = mean_absolute_error(test_df["target_act_outing"], y_pred_outing)
    activity_metrics["outing"] = {"model": "Random Forest", "polarity": "Higher is Good", "r2": round(float(r2_outing), 4), "rmse": round(float(rmse_outing), 2), "mae": round(float(mae_outing), 2)}
    print(f"  -> R²: {r2_outing:.4f}, RMSE: {rmse_outing:.2f}, MAE: {mae_outing:.2f}")
    joblib.dump(model_act_outing, os.path.join(ARTIFACTS_DIR, "model_act_outing.joblib"))

    # 3. Long Drive Safety (Higher = Good)
    print("\n[Activity 3: Long Drive Safety] SVR ...")
    scaler_act_drive = StandardScaler()
    X_train_drive = scaler_act_drive.fit_transform(X_train)
    X_test_drive = scaler_act_drive.transform(X_test)
    model_act_drive = SVR(kernel="rbf", C=20.0, epsilon=0.2)
    model_act_drive.fit(X_train_drive, train_df["target_act_long_drive"])
    y_pred_drive = model_act_drive.predict(X_test_drive)
    r2_drive = r2_score(test_df["target_act_long_drive"], y_pred_drive)
    rmse_drive = np.sqrt(mean_squared_error(test_df["target_act_long_drive"], y_pred_drive))
    mae_drive = mean_absolute_error(test_df["target_act_long_drive"], y_pred_drive)
    activity_metrics["long-drive"] = {"model": "SVR", "polarity": "Higher is Good", "r2": round(float(r2_drive), 4), "rmse": round(float(rmse_drive), 2), "mae": round(float(mae_drive), 2)}
    print(f"  -> R²: {r2_drive:.4f}, RMSE: {rmse_drive:.2f}, MAE: {mae_drive:.2f}")
    joblib.dump({"model": model_act_drive, "scaler": scaler_act_drive}, os.path.join(ARTIFACTS_DIR, "model_act_long_drive.joblib"))

    # 4. Shipment Safety (Higher = Good)
    print("\n[Activity 4: Shipment Safety] Extra Trees ...")
    model_act_ship = ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    model_act_ship.fit(X_train, train_df["target_act_shipment"])
    y_pred_ship = model_act_ship.predict(X_test)
    r2_ship = r2_score(test_df["target_act_shipment"], y_pred_ship)
    rmse_ship = np.sqrt(mean_squared_error(test_df["target_act_shipment"], y_pred_ship))
    mae_ship = mean_absolute_error(test_df["target_act_shipment"], y_pred_ship)
    activity_metrics["shipment-safety"] = {"model": "Extra Trees", "polarity": "Higher is Good", "r2": round(float(r2_ship), 4), "rmse": round(float(rmse_ship), 2), "mae": round(float(mae_ship), 2)}
    print(f"  -> R²: {r2_ship:.4f}, RMSE: {rmse_ship:.2f}, MAE: {mae_ship:.2f}")
    joblib.dump(model_act_ship, os.path.join(ARTIFACTS_DIR, "model_act_shipment.joblib"))

    # 5. Asthma Index (Higher = Bad)
    print("\n[Activity 5: Asthma Index] MLP Neural Network ...")
    model_act_asthma = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", alpha=0.01, max_iter=400, random_state=42)
    model_act_asthma.fit(X_train_scaled, train_df["target_act_asthma"])
    y_pred_asthma = model_act_asthma.predict(X_test_scaled)
    r2_asthma = r2_score(test_df["target_act_asthma"], y_pred_asthma)
    rmse_asthma = np.sqrt(mean_squared_error(test_df["target_act_asthma"], y_pred_asthma))
    mae_asthma = mean_absolute_error(test_df["target_act_asthma"], y_pred_asthma)
    activity_metrics["asthma-index"] = {"model": "MLP Neural Net", "polarity": "Higher is Bad", "r2": round(float(r2_asthma), 4), "rmse": round(float(rmse_asthma), 2), "mae": round(float(mae_asthma), 2)}
    print(f"  -> R²: {r2_asthma:.4f}, RMSE: {rmse_asthma:.2f}, MAE: {mae_asthma:.2f}")
    joblib.dump({"model": model_act_asthma, "scaler": scaler_mlp}, os.path.join(ARTIFACTS_DIR, "model_act_asthma.joblib"))

    # 6. Flight Delay Risk (Higher = Bad)
    print("\n[Activity 6: Flight Delay Risk] Gradient Boosting ...")
    model_act_flight = GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
    model_act_flight.fit(X_train, train_df["target_act_flight_delay"])
    y_pred_flight = model_act_flight.predict(X_test)
    r2_flight = r2_score(test_df["target_act_flight_delay"], y_pred_flight)
    rmse_flight = np.sqrt(mean_squared_error(test_df["target_act_flight_delay"], y_pred_flight))
    mae_flight = mean_absolute_error(test_df["target_act_flight_delay"], y_pred_flight)
    activity_metrics["flight-delay"] = {"model": "Gradient Boosting", "polarity": "Higher is Bad", "r2": round(float(r2_flight), 4), "rmse": round(float(rmse_flight), 2), "mae": round(float(mae_flight), 2)}
    print(f"  -> R²: {r2_flight:.4f}, RMSE: {rmse_flight:.2f}, MAE: {mae_flight:.2f}")
    joblib.dump(model_act_flight, os.path.join(ARTIFACTS_DIR, "model_act_flight_delay.joblib"))

    # 7. Visibility Index (Higher = Good)
    print("\n[Activity 7: Visibility Index] Extra Trees Regressor ...")
    model_act_visibility = ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    model_act_visibility.fit(X_train, train_df["target_act_visibility"])
    y_pred_vis = model_act_visibility.predict(X_test)
    r2_vis = r2_score(test_df["target_act_visibility"], y_pred_vis)
    rmse_vis = np.sqrt(mean_squared_error(test_df["target_act_visibility"], y_pred_vis))
    mae_vis = mean_absolute_error(test_df["target_act_visibility"], y_pred_vis)
    activity_metrics["visibility"] = {"model": "Extra Trees", "polarity": "Higher is Good", "r2": round(float(r2_vis), 4), "rmse": round(float(rmse_vis), 2), "mae": round(float(mae_vis), 2)}
    print(f"  -> R²: {r2_vis:.4f}, RMSE: {rmse_vis:.2f}, MAE: {mae_vis:.2f}")
    joblib.dump(model_act_visibility, os.path.join(ARTIFACTS_DIR, "model_act_visibility.joblib"))

    with open(os.path.join(ARTIFACTS_DIR, "activity_metrics.json"), "w") as f:
        json.dump(activity_metrics, f, indent=2)

    # ═══════════════════════════════════════════════════════════════
    #  SUMMARY
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE — ALL MODELS TRAINED ON REAL DATA")
    print("=" * 70)
    print("\nForecast Model Metrics:")
    for k, v in forecast_metrics.items():
        print(f"  {k:20s} | {v}")
    print("\nActivity Model Metrics:")
    for k, v in activity_metrics.items():
        print(f"  {k:20s} | {v}")
    print(f"\nAll artifacts saved to: {ARTIFACTS_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    train_and_evaluate_all_models()

"""
Vatavarnam ML Training Pipeline (Delhi NCR Edition)
Trains Machine Learning Models for:
- Page 2 (Forecast Day 1) 6 Targets
- Page 1 (Activity Suitability & Risk Indices - Delhi NCR) 6 Targets:
    1. 'walking' (Walking Suitability Score: Higher = Good / Greenish) -> Gradient Boosting Regressor
    2. 'outing' (Outing Suitability Score: Higher = Good / Greenish) -> Random Forest Regressor
    3. 'long-drive' (Drive Safety & Visibility: Higher = Good / Greenish) -> SVR
    4. 'shipment-safety' (Cargo Transit Safety: Higher = Good / Greenish) -> Extra Trees Regressor
    5. 'asthma-index' (Asthma Trigger Risk: Higher = Bad / Reddish) -> MLP Neural Network
    6. 'flight-delay' (Airport Delay Risk: Higher = Bad / Reddish) -> Gradient Boosting Regressor
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def generate_delhi_synthetic_dataset(num_days=365):
    """
    Generates realistic historical hourly data for Delhi NCR.
    """
    np.random.seed(42)
    start_date = datetime(2025, 1, 1, 0, 0, 0)
    total_hours = num_days * 24
    
    timestamps = [start_date + timedelta(hours=i) for i in range(total_hours)]
    
    df = pd.DataFrame({"timestamp": timestamps})
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["dayofyear"] = df["timestamp"].dt.dayofyear
    
    # 1. Base Meteorology for Delhi NCR
    winter_factor = np.exp(-0.5 * ((df["month"] - 1.0) % 12) ** 2 / 2.0) + np.exp(-0.5 * ((df["month"] - 12.0) % 12) ** 2 / 2.0)
    monsoon_factor = np.exp(-0.5 * (df["month"] - 8.0) ** 2 / 1.5)
    summer_factor = np.exp(-0.5 * (df["month"] - 5.5) ** 2 / 2.0)
    
    base_temp = 14 + 18 * np.sin(2 * np.pi * (df["dayofyear"] - 100) / 365)
    diurnal_temp = 6 * np.sin(2 * np.pi * (df["hour"] - 8) / 24)
    df["temperature"] = base_temp + diurnal_temp + np.random.normal(0, 1.5, total_hours)
    
    df["humidity"] = np.clip(
        50 + 25 * monsoon_factor + 15 * winter_factor - 15 * np.sin(2 * np.pi * (df["hour"] - 8) / 24) + np.random.normal(0, 5, total_hours),
        15,
        98,
    )
    
    df["wind_speed"] = np.clip(
        12 - 5 * winter_factor + 4 * summer_factor + 2 * np.sin(2 * np.pi * (df["hour"] - 12) / 24) + np.random.normal(0, 2, total_hours),
        1.0,
        35.0,
    )
    
    df["pressure"] = 1012 + 8 * winter_factor - 6 * summer_factor - 2 * np.sin(2 * np.pi * (df["hour"] - 9) / 24) + np.random.normal(0, 1.0, total_hours)
    
    solar_base = np.maximum(0, np.sin(np.pi * (df["hour"] - 6) / 12))
    df["radiation"] = solar_base * (2.5 + 1.5 * summer_factor - 1.0 * monsoon_factor) * (1 - df["humidity"] / 150) + np.random.uniform(0, 0.2, total_hours)
    df["radiation"] = np.maximum(0, df["radiation"])
    
    df["dew_point"] = df["temperature"] - ((100 - df["humidity"]) / 5)
    
    rain_logit = -3.5 + 0.06 * df["humidity"] + 2.5 * monsoon_factor - 0.1 * (df["temperature"] - df["dew_point"]) + np.random.normal(0, 0.4, total_hours)
    rain_prob_true = 1 / (1 + np.exp(-rain_logit))
    df["rain_event"] = (np.random.rand(total_hours) < rain_prob_true).astype(int)
    df["rain_amount_mm"] = df["rain_event"] * np.random.exponential(scale=4.5 * monsoon_factor + 0.5, size=total_hours)
    
    is_weekday = (df["dayofweek"] < 5).astype(int)
    morning_peak = np.exp(-0.5 * (df["hour"] - 9.0) ** 2 / 1.5)
    evening_peak = np.exp(-0.5 * (df["hour"] - 19.0) ** 2 / 2.0)
    traffic_base = 25 + 45 * is_weekday * (morning_peak + evening_peak) + 15 * (1 - is_weekday) * np.exp(-0.5 * (df["hour"] - 16.0) ** 2 / 6.0)
    df["traffic_raw"] = np.clip(traffic_base + np.random.normal(0, 4, total_hours), 5, 95)
    
    industrial_base = 35 + 20 * winter_factor + 15 * ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
    df["fume_raw"] = np.clip(industrial_base + np.random.normal(0, 5, total_hours), 10, 95)
    
    stagnation = df["pressure"] / (df["wind_speed"] + 0.5)
    washout = np.exp(-0.3 * df["rain_amount_mm"])
    
    pm25_gen = (
        (35 + 130 * winter_factor + 0.7 * df["fume_raw"] + 0.5 * df["traffic_raw"] + 0.2 * stagnation)
        * washout
        + np.random.normal(0, 8, total_hours)
    )
    df["pm25_raw"] = np.clip(pm25_gen, 10, 450)
    
    pm10_gen = (
        (60 + 110 * winter_factor + 90 * summer_factor + 0.8 * df["traffic_raw"] + 0.6 * df["fume_raw"])
        * washout
        + np.random.normal(0, 12, total_hours)
    )
    df["pm10_raw"] = np.clip(pm10_gen, 20, 600)
    
    # NAQI approximation
    aqi_pm25 = np.where(df["pm25_raw"] <= 30, df["pm25_raw"] * 50 / 30,
               np.where(df["pm25_raw"] <= 60, 50 + (df["pm25_raw"] - 30) * 50 / 30,
               np.where(df["pm25_raw"] <= 90, 100 + (df["pm25_raw"] - 60) * 100 / 30,
               np.where(df["pm25_raw"] <= 120, 200 + (df["pm25_raw"] - 90) * 100 / 30,
               np.where(df["pm25_raw"] <= 250, 300 + (df["pm25_raw"] - 120) * 100 / 130,
                        400 + (df["pm25_raw"] - 250) * 100 / 130)))))
    df["aqi_raw"] = np.clip(aqi_pm25, 15, 500)

    # Visibility in Delhi NCR (km)
    fog_factor = np.maximum(0, (df["humidity"] - 70) / 30.0) * winter_factor
    smog_density = (df["pm25_raw"] / 300.0)
    visibility_km = np.clip(10.0 - 6.0 * smog_density - 3.5 * fog_factor + np.random.normal(0, 0.5, total_hours), 0.2, 12.0)
    df["visibility_km"] = visibility_km

    # -------------------------------------------------------------
    # 2. Activity Metrics with User-Specified Polarity:
    # - Walking, Outing, Long Drive, Shipment Safety: HIGHER = GOOD (Greenish)
    # - Asthma Index, Flight Delay: HIGHER = BAD (Reddish)
    # -------------------------------------------------------------
    heat_stress = np.maximum(0, df["temperature"] - 35) * 1.5 + np.maximum(0, 12 - df["temperature"]) * 1.5
    
    # 1. Walking Suitability (0 - 100%): HIGHER = GOOD (Clean air, comfortable temp = High Walking Score)
    walk_suitability = 100.0 - (df["pm25_raw"] / 300.0) * 50.0 - (df["pm10_raw"] / 450.0) * 20.0 - heat_stress + np.random.normal(0, 3, total_hours)
    df["target_act_walking"] = np.clip(walk_suitability, 5, 95)

    # 2. Outing Suitability (0 - 100%): HIGHER = GOOD (Low AQI, sunshine, no heavy rain = High Outing Score)
    outing_suitability = 100.0 - (df["aqi_raw"] / 400.0) * 55.0 - (df["rain_amount_mm"] * 8.0) + (df["radiation"] * 4.0) + np.random.normal(0, 3, total_hours)
    df["target_act_outing"] = np.clip(outing_suitability, 5, 95)

    # 3. Long Drive Road Safety (0 - 100%): HIGHER = GOOD (High visibility, light traffic = Safe Drive)
    long_drive_safety = (df["visibility_km"] / 10.0) * 60.0 + (1.0 - df["traffic_raw"] / 100.0) * 35.0 + np.random.normal(0, 3, total_hours)
    df["target_act_long_drive"] = np.clip(long_drive_safety, 5, 95)

    # 4. Shipment Safety (0 - 100%): HIGHER = GOOD (Dry, low particulate deposition, safe transit)
    shipment_safety = 100.0 - (df["humidity"] / 100.0) * 30.0 - (df["rain_amount_mm"] * 10.0) - (df["pm10_raw"] / 500.0) * 25.0 + np.random.normal(0, 2, total_hours)
    df["target_act_shipment"] = np.clip(shipment_safety, 5, 95)

    # 5. Asthma Respiratory Distress Index (0 - 100%): HIGHER = BAD (High PM2.5, winter inversion = High Risk / Reddish)
    asthma_risk = (df["pm25_raw"] / 300.0) * 60.0 + (stagnation / 150.0) * 25.0 + winter_factor * 12.0 + np.random.normal(0, 3, total_hours)
    df["target_act_asthma"] = np.clip(asthma_risk, 5, 98)

    # 6. Flight Delay Risk at IGI Airport DEL (0 - 100%): HIGHER = BAD (Low visibility < 1km, fog, stagnation = High Delay Risk / Reddish)
    flight_delay_logit = -2.5 + 4.5 * (1.0 - df["visibility_km"] / 8.0) + 1.2 * (df["wind_speed"] < 5.0).astype(int) + 0.8 * winter_factor
    flight_delay_prob = 1 / (1 + np.exp(-flight_delay_logit)) * 100.0
    df["target_act_flight_delay"] = np.clip(flight_delay_prob + np.random.normal(0, 2, total_hours), 2, 98)

    return df


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
    data["is_rush_hour"] = (((data["hour"] >= 8) & (data["hour"] <= 11)) | ((data["hour"] >= 17) & (data["hour"] <= 21))).astype(float)
    
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
    
    # 5. Forecast Day 1 Targets
    data["target_rain"] = data["rain_event"].shift(-24)
    data["target_pm10"] = data["pm10_raw"].shift(-24)
    data["target_pm25"] = data["pm25_raw"].shift(-24)
    data["target_emissions"] = data["fume_raw"].shift(-24)
    data["target_aqi"] = data["aqi_raw"].shift(-24)
    data["target_transportation"] = data["traffic_raw"].shift(-24)
    
    clean_data = data.dropna().reset_index(drop=True)
    return clean_data


def train_and_evaluate_all_models():
    print("=" * 70)
    print("Step 1: Generating Delhi NCR Atmospheric & Activity Dataset...")
    df_raw = generate_delhi_synthetic_dataset(num_days=365)
    print(f"Dataset generated: {len(df_raw)} hourly records.")

    print("\nStep 2: Engineering Atmospheric & Physical Features...")
    df = engineer_features(df_raw)
    print(f"Cleaned feature dataset shape: {df.shape}")

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

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]

    with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "w") as f:
        json.dump(feature_cols, f)

    # Train Page 2 Forecast Models
    print("\nTraining Page 2 Forecast Models...")
    rain_features = ["humidity", "temperature", "dew_point", "pressure", "wind_speed", "sin_month", "cos_month", "temp_humidity_index", "humidity_lag_1", "humidity_lag_24"]
    scaler_rain = StandardScaler()
    X_train_rain_scaled = scaler_rain.fit_transform(train_df[rain_features])
    base_lr = LogisticRegression(C=1.0, max_iter=500, random_state=42)
    model_rain = CalibratedClassifierCV(estimator=base_lr, method="sigmoid", cv=5)
    model_rain.fit(X_train_rain_scaled, train_df["target_rain"])
    joblib.dump({"model": model_rain, "scaler": scaler_rain, "features": rain_features}, os.path.join(ARTIFACTS_DIR, "model_rain.joblib"))

    model_pm10 = GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=5, subsample=0.85, random_state=42)
    model_pm10.fit(X_train, train_df["target_pm10"])
    joblib.dump(model_pm10, os.path.join(ARTIFACTS_DIR, "model_pm10.joblib"))

    model_pm25 = ExtraTreesRegressor(n_estimators=120, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1)
    model_pm25.fit(X_train, train_df["target_pm25"])
    joblib.dump(model_pm25, os.path.join(ARTIFACTS_DIR, "model_pm25.joblib"))

    model_emissions = RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model_emissions.fit(X_train, train_df["target_emissions"])
    joblib.dump(model_emissions, os.path.join(ARTIFACTS_DIR, "model_emissions.joblib"))

    scaler_mlp = StandardScaler()
    X_train_scaled = scaler_mlp.fit_transform(X_train)
    model_aqi = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", solver="adam", alpha=0.01, max_iter=500, random_state=42)
    model_aqi.fit(X_train_scaled, train_df["target_aqi"])
    joblib.dump({"model": model_aqi, "scaler": scaler_mlp}, os.path.join(ARTIFACTS_DIR, "model_aqi.joblib"))

    traffic_features = ["sin_hour", "cos_hour", "sin_dayofweek", "cos_dayofweek", "is_weekend", "is_rush_hour", "temperature", "humidity", "wind_speed", "pm10_lag_1", "temp_humidity_index"]
    scaler_svr = StandardScaler()
    X_train_svr = scaler_svr.fit_transform(train_df[traffic_features])
    model_trans = SVR(kernel="rbf", C=15.0, epsilon=0.2, gamma="scale")
    model_trans.fit(X_train_svr, train_df["target_transportation"])
    joblib.dump({"model": model_trans, "scaler": scaler_svr, "features": traffic_features}, os.path.join(ARTIFACTS_DIR, "model_transportation.joblib"))

    # Train Page 1 Activity Models (with Updated Polarities)
    print("\n" + "=" * 70)
    print("Training 6 Activity Models (Polarity: Asthma/Flight Delay = Higher is Bad; Rest = Higher is Good)")
    print("=" * 70)

    activity_metrics = {}

    # 1. Walking Suitability (Higher = Good) -> Gradient Boosting
    print("\n[Activity 1: Walking Suitability Score (Higher = Good)] Training Gradient Boosting...")
    model_act_walk = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    model_act_walk.fit(X_train, train_df["target_act_walking"])
    y_pred_walk = model_act_walk.predict(X_test)
    r2_walk = r2_score(test_df["target_act_walking"], y_pred_walk)
    rmse_walk = np.sqrt(mean_squared_error(test_df["target_act_walking"], y_pred_walk))
    mae_walk = mean_absolute_error(test_df["target_act_walking"], y_pred_walk)
    activity_metrics["walking"] = {"model": "Gradient Boosting Regressor", "polarity": "Higher is Good", "r2": round(float(r2_walk), 4), "rmse": round(float(rmse_walk), 2), "mae": round(float(mae_walk), 2)}
    print(f"  -> R²: {r2_walk:.4f}, RMSE: {rmse_walk:.2f}, MAE: {mae_walk:.2f}")
    joblib.dump(model_act_walk, os.path.join(ARTIFACTS_DIR, "model_act_walking.joblib"))

    # 2. Outing Suitability (Higher = Good) -> Random Forest
    print("\n[Activity 2: Outing Suitability Score (Higher = Good)] Training Random Forest...")
    model_act_outing = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
    model_act_outing.fit(X_train, train_df["target_act_outing"])
    y_pred_outing = model_act_outing.predict(X_test)
    r2_outing = r2_score(test_df["target_act_outing"], y_pred_outing)
    rmse_outing = np.sqrt(mean_squared_error(test_df["target_act_outing"], y_pred_outing))
    mae_outing = mean_absolute_error(test_df["target_act_outing"], y_pred_outing)
    activity_metrics["outing"] = {"model": "Random Forest Regressor", "polarity": "Higher is Good", "r2": round(float(r2_outing), 4), "rmse": round(float(rmse_outing), 2), "mae": round(float(mae_outing), 2)}
    print(f"  -> R²: {r2_outing:.4f}, RMSE: {rmse_outing:.2f}, MAE: {mae_outing:.2f}")
    joblib.dump(model_act_outing, os.path.join(ARTIFACTS_DIR, "model_act_outing.joblib"))

    # 3. Long Drive Road Safety (Higher = Good) -> SVR
    print("\n[Activity 3: Long Drive Safety & Visibility (Higher = Good)] Training SVR...")
    scaler_act_drive = StandardScaler()
    X_train_drive = scaler_act_drive.fit_transform(X_train)
    X_test_drive = scaler_act_drive.transform(X_test)
    model_act_drive = SVR(kernel="rbf", C=20.0, epsilon=0.2)
    model_act_drive.fit(X_train_drive, train_df["target_act_long_drive"])
    y_pred_drive = model_act_drive.predict(X_test_drive)
    r2_drive = r2_score(test_df["target_act_long_drive"], y_pred_drive)
    rmse_drive = np.sqrt(mean_squared_error(test_df["target_act_long_drive"], y_pred_drive))
    mae_drive = mean_absolute_error(test_df["target_act_long_drive"], y_pred_drive)
    activity_metrics["long-drive"] = {"model": "Support Vector Regressor (SVR)", "polarity": "Higher is Good", "r2": round(float(r2_drive), 4), "rmse": round(float(rmse_drive), 2), "mae": round(float(mae_drive), 2)}
    print(f"  -> R²: {r2_drive:.4f}, RMSE: {rmse_drive:.2f}, MAE: {mae_drive:.2f}")
    joblib.dump({"model": model_act_drive, "scaler": scaler_act_drive}, os.path.join(ARTIFACTS_DIR, "model_act_long_drive.joblib"))

    # 4. Shipment Cargo Safety (Higher = Good) -> Extra Trees
    print("\n[Activity 4: Shipment Safety (Higher = Good)] Training Extra Trees...")
    model_act_ship = ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    model_act_ship.fit(X_train, train_df["target_act_shipment"])
    y_pred_ship = model_act_ship.predict(X_test)
    r2_ship = r2_score(test_df["target_act_shipment"], y_pred_ship)
    rmse_ship = np.sqrt(mean_squared_error(test_df["target_act_shipment"], y_pred_ship))
    mae_ship = mean_absolute_error(test_df["target_act_shipment"], y_pred_ship)
    activity_metrics["shipment-safety"] = {"model": "Extra Trees Regressor", "polarity": "Higher is Good", "r2": round(float(r2_ship), 4), "rmse": round(float(rmse_ship), 2), "mae": round(float(mae_ship), 2)}
    print(f"  -> R²: {r2_ship:.4f}, RMSE: {rmse_ship:.2f}, MAE: {mae_ship:.2f}")
    joblib.dump(model_act_ship, os.path.join(ARTIFACTS_DIR, "model_act_shipment.joblib"))

    # 5. Asthma Respiratory Index (Higher = Bad) -> MLP Neural Network
    print("\n[Activity 5: Asthma Index (Higher = Bad / Reddish)] Training MLP Neural Network...")
    model_act_asthma = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", alpha=0.01, max_iter=400, random_state=42)
    model_act_asthma.fit(X_train_scaled, train_df["target_act_asthma"])
    y_pred_asthma = model_act_asthma.predict(scaler_mlp.transform(X_test))
    r2_asthma = r2_score(test_df["target_act_asthma"], y_pred_asthma)
    rmse_asthma = np.sqrt(mean_squared_error(test_df["target_act_asthma"], y_pred_asthma))
    mae_asthma = mean_absolute_error(test_df["target_act_asthma"], y_pred_asthma)
    activity_metrics["asthma-index"] = {"model": "MLP Neural Network", "polarity": "Higher is Bad", "r2": round(float(r2_asthma), 4), "rmse": round(float(rmse_asthma), 2), "mae": round(float(mae_asthma), 2)}
    print(f"  -> R²: {r2_asthma:.4f}, RMSE: {rmse_asthma:.2f}, MAE: {mae_asthma:.2f}")
    joblib.dump({"model": model_act_asthma, "scaler": scaler_mlp}, os.path.join(ARTIFACTS_DIR, "model_act_asthma.joblib"))

    # 6. Flight Delay Operational Risk (Higher = Bad) -> Gradient Boosting
    print("\n[Activity 6: Flight Delay Risk (Higher = Bad / Reddish)] Training Gradient Boosting...")
    model_act_flight = GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
    model_act_flight.fit(X_train, train_df["target_act_flight_delay"])
    y_pred_flight = model_act_flight.predict(X_test)
    r2_flight = r2_score(test_df["target_act_flight_delay"], y_pred_flight)
    rmse_flight = np.sqrt(mean_squared_error(test_df["target_act_flight_delay"], y_pred_flight))
    mae_flight = mean_absolute_error(test_df["target_act_flight_delay"], y_pred_flight)
    activity_metrics["flight-delay"] = {"model": "Gradient Boosting Regressor", "polarity": "Higher is Bad", "r2": round(float(r2_flight), 4), "rmse": round(float(rmse_flight), 2), "mae": round(float(mae_flight), 2)}
    print(f"  -> R²: {r2_flight:.4f}, RMSE: {rmse_flight:.2f}, MAE: {mae_flight:.2f}")
    joblib.dump(model_act_flight, os.path.join(ARTIFACTS_DIR, "model_act_flight_delay.joblib"))

    with open(os.path.join(ARTIFACTS_DIR, "activity_metrics.json"), "w") as f:
        json.dump(activity_metrics, f, indent=2)

    print("\n" + "=" * 70)
    print("Training Complete! All Models for Forecast and Activity Predictions Saved.")
    print("=" * 70)


if __name__ == "__main__":
    train_and_evaluate_all_models()

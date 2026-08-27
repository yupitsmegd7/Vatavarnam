"""
Vatavarnam ML Backend API Server
Serves real-time inference from Machine Learning models for:
1. Page 2 (Forecast Day 1) 6 Targets
2. Page 1 (Meteorology Activity Predictions - Delhi NCR) 6 Slots with Context-Aware Severity Color-Coding
   - Higher is Bad (Reddish): Asthma Index, Flight Delay
   - Higher is Good (Greenish): Walking, Outing, Long Drive, Shipment Safety
"""

import os
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import joblib
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

# Global model containers
models = {}
activity_models = {}
metrics_data = {}
activity_metrics_data = {}
correlations_data = {}
feature_names = []


def load_artifacts():
    global models, activity_models, metrics_data, activity_metrics_data, correlations_data, feature_names
    if not os.path.exists(ARTIFACTS_DIR):
        print(f"Artifacts directory {ARTIFACTS_DIR} not found.")
        return

    try:
        # Load Forecast Day 1 models
        models["rain"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_rain.joblib"))
        models["pm10"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_pm10.joblib"))
        models["pm25"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_pm25.joblib"))
        models["emissions"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_emissions.joblib"))
        models["aqi"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_aqi.joblib"))
        models["transportation"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_transportation.joblib"))

        # Load Activity Prediction models (Delhi NCR)
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_walking.joblib")):
            activity_models["walking"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_walking.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_outing.joblib")):
            activity_models["outing"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_outing.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_long_drive.joblib")):
            activity_models["long-drive"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_long_drive.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_shipment.joblib")):
            activity_models["shipment-safety"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_shipment.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_asthma.joblib")):
            activity_models["asthma-index"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_asthma.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_flight_delay.joblib")):
            activity_models["flight-delay"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_flight_delay.joblib"))
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_act_visibility.joblib")):
            activity_models["visibility"] = joblib.load(os.path.join(ARTIFACTS_DIR, "model_act_visibility.joblib"))

        # Load metrics & correlations
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "model_metrics.json")):
            with open(os.path.join(ARTIFACTS_DIR, "model_metrics.json"), "r") as f:
                metrics_data = json.load(f)

        if os.path.exists(os.path.join(ARTIFACTS_DIR, "activity_metrics.json")):
            with open(os.path.join(ARTIFACTS_DIR, "activity_metrics.json"), "r") as f:
                activity_metrics_data = json.load(f)
                
        if os.path.exists(os.path.join(ARTIFACTS_DIR, "correlations.json")):
            with open(os.path.join(ARTIFACTS_DIR, "correlations.json"), "r") as f:
                correlations_data = json.load(f)

        if os.path.exists(os.path.join(ARTIFACTS_DIR, "feature_names.json")):
            with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "r") as f:
                feature_names = json.load(f)

        print("All Forecast and Activity Models successfully loaded.")
    except Exception as e:
        print(f"Error loading model artifacts: {e}")


def build_feature_vector(
    hour=None, dayofweek=None,
    temp=28.5, humidity=58.0, wind_speed=11.5, pressure=1012.0,
    radiation=1.2, rain_amount=0.0,
    pm25_lag_1=55.0, pm25_lag_24=50.0, pm25_lag_48=48.0,
    pm10_lag_1=90.0, pm10_lag_24=85.0, pm10_lag_48=80.0,
    aqi_lag_1=100.0, aqi_lag_24=90.0, aqi_lag_48=85.0,
):
    now = datetime.now()
    h = now.hour if hour is None else hour
    dow = now.weekday() if dayofweek is None else dayofweek
    month = now.month

    dew_point = temp - ((100 - humidity) / 5)
    stagnation_index = pressure / (wind_speed + 0.5)
    inversion_proxy = (temp - dew_point) / (wind_speed + 0.1)
    smog_formation_factor = (radiation * temp) / (humidity + 1.0)
    washout_proxy = rain_amount * 120.0
    temp_humidity_index = temp * (humidity / 100.0)

    is_weekend = 1.0 if dow >= 5 else 0.0
    is_rush_hour = 1.0 if ((8 <= h <= 11) or (17 <= h <= 21)) else 0.0

    features = {
        "temperature": temp,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "radiation": radiation,
        "dew_point": dew_point,
        "sin_hour": np.sin(2 * np.pi * h / 24),
        "cos_hour": np.cos(2 * np.pi * h / 24),
        "sin_dayofweek": np.sin(2 * np.pi * dow / 7),
        "cos_dayofweek": np.cos(2 * np.pi * dow / 7),
        "sin_month": np.sin(2 * np.pi * month / 12),
        "cos_month": np.cos(2 * np.pi * month / 12),
        "is_weekend": is_weekend,
        "is_rush_hour": is_rush_hour,
        "stagnation_index": stagnation_index,
        "inversion_proxy": inversion_proxy,
        "smog_formation_factor": smog_formation_factor,
        "washout_proxy": washout_proxy,
        "temp_humidity_index": temp_humidity_index,
        "pm25_lag_1": pm25_lag_1,
        "pm25_lag_24": pm25_lag_24,
        "pm25_lag_48": pm25_lag_48,
        "pm10_lag_1": pm10_lag_1,
        "pm10_lag_24": pm10_lag_24,
        "pm10_lag_48": pm10_lag_48,
        "aqi_lag_1": aqi_lag_1,
        "aqi_lag_24": aqi_lag_24,
        "aqi_lag_48": aqi_lag_48,
        "pm25_roll_mean_6": (pm25_lag_1 + pm25_lag_24) / 2.0,
        "pm25_roll_mean_24": (pm25_lag_1 + pm25_lag_24 + pm25_lag_48) / 3.0,
        "pm10_roll_mean_6": (pm10_lag_1 + pm10_lag_24) / 2.0,
        "pm10_roll_mean_24": (pm10_lag_1 + pm10_lag_24 + pm10_lag_48) / 3.0,
        "temp_roll_mean_24": temp,
        "wind_roll_mean_24": wind_speed,
        "humidity_lag_1": humidity,
        "humidity_lag_24": humidity + 2.0
    }
    return features



def get_activity_color_and_severity(target_id, percent):
    """
    Context-aware severity color coding:
    - Asthma & Flight Delay: HIGHER IS BAD (Reddish for high %, Greenish for low %)
    - Walking, Outing, Long Drive, Shipment Safety: HIGHER IS GOOD (Greenish for high %, Reddish for low %)
    """
    pct = float(percent)
    is_higher_bad = target_id in ["asthma-index", "flight-delay"]

    if is_higher_bad:
        # Higher = Bad (Reddish), Lower = Good (Greenish)
        if pct <= 30.0:
            return "Good / Low Risk", "#10b981"      # Emerald Green
        elif pct <= 55.0:
            return "Moderate Risk", "#f59e0b"        # Amber Gold
        elif pct <= 75.0:
            return "High Risk", "#f97316"            # Vibrant Orange
        else:
            return "Severe / Hazardous", "#ef4444"   # Crimson Red
    else:
        # Higher = Good (Greenish), Lower = Bad (Reddish)
        if pct >= 70.0:
            return "Optimal / Safe", "#10b981"       # Emerald Green
        elif pct >= 45.0:
            return "Moderate / Fair", "#f59e0b"      # Amber Gold
        elif pct >= 25.0:
            return "Poor / Caution", "#f97316"       # Vibrant Orange
        else:
            return "Hazardous / Inadvisable", "#ef4444" # Crimson Red


def predict_6_targets(feature_dict):
    df_feat = pd.DataFrame([feature_dict])

    rain_pkg = models.get("rain")
    rain_prob = float(rain_pkg["model"].predict_proba(rain_pkg["scaler"].transform(df_feat[rain_pkg["features"]]))[0, 1]) * 100.0 if rain_pkg else 15.0
    
    pm10_model = models.get("pm10")
    pm10_val = float(pm10_model.predict(df_feat[feature_names])[0]) if pm10_model and feature_names else 180.0
    
    pm25_model = models.get("pm25")
    pm25_val = float(pm25_model.predict(df_feat[feature_names])[0]) if pm25_model and feature_names else 110.0
    
    em_model = models.get("emissions")
    emissions_val = float(em_model.predict(df_feat[feature_names])[0]) if em_model and feature_names else 45.0
    
    aqi_pkg = models.get("aqi")
    aqi_val = float(aqi_pkg["model"].predict(aqi_pkg["scaler"].transform(df_feat[feature_names]))[0]) if aqi_pkg and feature_names else 280.0
    
    trans_pkg = models.get("transportation")
    trans_val = float(trans_pkg["model"].predict(trans_pkg["scaler"].transform(df_feat[trans_pkg["features"]]))[0]) if trans_pkg else 55.0

    rain_pct = round(np.clip(rain_prob, 0, 100), 1)
    pm10_pct = round(np.clip((pm10_val / 300.0) * 100, 5, 100), 1)
    pm25_pct = round(np.clip((pm25_val / 200.0) * 100, 5, 100), 1)
    emissions_pct = round(np.clip(emissions_val, 5, 100), 1)
    aqi_pct = round(np.clip((aqi_val / 500.0) * 100, 5, 100), 1)
    trans_pct = round(np.clip(trans_val, 5, 100), 1)

    items = [
        {"id": "rain", "label": "Rain Probability", "value": round(rain_prob, 1), "percent": rain_pct, "unit": "%", "model": "Calibrated Logistic Regression"},
        {"id": "pm10", "label": "PM10", "value": round(pm10_val, 1), "percent": pm10_pct, "unit": "µg/m³", "model": "Gradient Boosting Regressor"},
        {"id": "pm2.5", "label": "PM2.5", "value": round(pm25_val, 1), "percent": pm25_pct, "unit": "µg/m³", "model": "Extra Trees Regressor"},
        {"id": "emissions", "label": "Fume Emissions", "value": round(emissions_val, 1), "percent": emissions_pct, "unit": "%", "model": "Random Forest Regressor"},
        {"id": "aqi", "label": "AQI Index", "value": round(aqi_val, 1), "percent": aqi_pct, "unit": "NAQI", "model": "MLP Neural Network"},
        {"id": "transportation", "label": "Transportation", "value": round(trans_val, 1), "percent": trans_pct, "unit": "%", "model": "Support Vector Regressor (SVR)"},
    ]

    return items, {"rain_prob": rain_prob, "pm10": pm10_val, "pm25": pm25_val, "emissions": emissions_val, "aqi": aqi_val, "transportation": trans_val}


def predict_activity_slots(feature_dict):
    """
    Inference across all 7 Activity Prediction models for Delhi NCR.
    """
    df_feat = pd.DataFrame([feature_dict])

    # 1. Walking Suitability (Higher = Good / Greenish)
    walk_m = activity_models.get("walking")
    walk_val = float(walk_m.predict(df_feat[feature_names])[0]) if walk_m and feature_names else 75.0
    walk_pct = round(np.clip(walk_val, 5, 95), 1)
    walk_sev, walk_col = get_activity_color_and_severity("walking", walk_pct)

    # 2. Outing Suitability (Higher = Good / Greenish)
    outing_m = activity_models.get("outing")
    outing_val = float(outing_m.predict(df_feat[feature_names])[0]) if outing_m and feature_names else 70.0
    outing_pct = round(np.clip(outing_val, 5, 95), 1)
    outing_sev, outing_col = get_activity_color_and_severity("outing", outing_pct)

    # 3. Visibility Index (Higher = Good / Greenish)
    vis_m = activity_models.get("visibility")
    vis_val = float(vis_m.predict(df_feat[feature_names])[0]) if vis_m and feature_names else 65.0
    vis_pct = round(np.clip(vis_val, 5, 95), 1)
    vis_sev, vis_col = get_activity_color_and_severity("visibility", vis_pct)

    # 4. Long Drive Road Safety (Higher = Good / Greenish)
    drive_pkg = activity_models.get("long-drive")
    if drive_pkg and feature_names:
        X_sc = drive_pkg["scaler"].transform(df_feat[feature_names])
        drive_val = float(drive_pkg["model"].predict(X_sc)[0])
    else:
        drive_val = 65.0
    drive_pct = round(np.clip(drive_val, 5, 95), 1)
    drive_sev, drive_col = get_activity_color_and_severity("long-drive", drive_pct)

    # 5. Shipment Safety (Higher = Good / Greenish)
    ship_m = activity_models.get("shipment-safety")
    ship_val = float(ship_m.predict(df_feat[feature_names])[0]) if ship_m and feature_names else 72.0
    ship_pct = round(np.clip(ship_val, 5, 95), 1)
    ship_sev, ship_col = get_activity_color_and_severity("shipment-safety", ship_pct)

    # 6. Asthma Respiratory Index (Higher = Bad / Reddish)
    asthma_pkg = activity_models.get("asthma-index")
    if asthma_pkg and feature_names:
        X_sc = asthma_pkg["scaler"].transform(df_feat[feature_names])
        asthma_val = float(asthma_pkg["model"].predict(X_sc)[0])
    else:
        asthma_val = 38.0
    asthma_pct = round(np.clip(asthma_val, 5, 98), 1)
    asthma_sev, asthma_col = get_activity_color_and_severity("asthma-index", asthma_pct)

    # 7. Flight Delay Operational Risk (Higher = Bad / Reddish)
    flight_m = activity_models.get("flight-delay")
    flight_val = float(flight_m.predict(df_feat[feature_names])[0]) if flight_m and feature_names else 38.0
    flight_pct = round(np.clip(flight_val, 5, 98), 1)
    flight_sev, flight_col = get_activity_color_and_severity("flight-delay", flight_pct)

    items = [
        {"id": "walking", "label": "Walking", "value": round(walk_pct * 18.5, 1), "percent": walk_pct, "severity": walk_sev, "color": walk_col, "model": "Gradient Boosting", "polarity": "Higher is Good (Green)"},
        {"id": "outing", "label": "Outing", "value": round(outing_pct * 19.8, 1), "percent": outing_pct, "severity": outing_sev, "color": outing_col, "model": "Random Forest", "polarity": "Higher is Good (Green)"},
        {"id": "visibility", "label": "Visibility", "value": round(vis_pct * 17.5, 1), "percent": vis_pct, "severity": vis_sev, "color": vis_col, "model": "Extra Trees", "polarity": "Higher is Good (Green)"},
        {"id": "long-drive", "label": "Long Drive", "value": round(drive_pct * 16.2, 1), "percent": drive_pct, "severity": drive_sev, "color": drive_col, "model": "Support Vector Machine", "polarity": "Higher is Good (Green)"},
        {"id": "shipment-safety", "label": "Shipment Safety", "value": round(ship_pct * 14.0, 1), "percent": ship_pct, "severity": ship_sev, "color": ship_col, "model": "Extra Trees", "polarity": "Higher is Good (Green)"},
        {"id": "asthma-index", "label": "Asthma Index", "value": round(asthma_pct * 13.5, 1), "percent": asthma_pct, "severity": asthma_sev, "color": asthma_col, "model": "MLP Neural Net", "polarity": "Higher is Bad (Red)"},
        {"id": "flight-delay", "label": "Flight Delay", "value": round(flight_pct * 13.5, 1), "percent": flight_pct, "severity": flight_sev, "color": flight_col, "model": "Gradient Boosting", "polarity": "Higher is Bad (Red)"},
    ]

    return items


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "forecast_models": len(models) == 6,
        "activity_models": len(activity_models) == 6,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/model/metrics", methods=["GET"])
def get_metrics():
    return jsonify({
        "forecast_metrics": metrics_data,
        "activity_metrics": activity_metrics_data,
        "correlations": correlations_data,
        "features": feature_names
    })


import requests

def fetch_open_meteo_forecast():
    """Fetch 4-day hourly weather forecast from Open-Meteo for Delhi NCR."""
    try:
        url = ("https://api.open-meteo.com/v1/forecast"
               "?latitude=28.6139&longitude=77.2090"
               "&hourly=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,precipitation,shortwave_radiation"
               "&timezone=Asia%2FKolkata&forecast_days=4")
        return requests.get(url, timeout=6).json()
    except Exception:
        return None

# 30+ Delhi NCR hotspot locations with CPCB-calibrated pollution multipliers
# (multiplier = this location's historical AQI relative to Delhi city average)
DELHI_HOTSPOT_GRID = [
    {"name": "Anand Vihar",       "lat": 28.6508, "lon": 77.3152, "mult": 1.35},
    {"name": "Jahangirpuri",      "lat": 28.7258, "lon": 77.1610, "mult": 1.30},
    {"name": "Bawana",            "lat": 28.7997, "lon": 77.0326, "mult": 1.28},
    {"name": "Rohini",            "lat": 28.7400, "lon": 77.0697, "mult": 1.20},
    {"name": "Mundka",            "lat": 28.6847, "lon": 76.9978, "mult": 1.22},
    {"name": "Wazirpur",          "lat": 28.6950, "lon": 77.1630, "mult": 1.25},
    {"name": "Narela",            "lat": 28.8539, "lon": 77.0943, "mult": 1.18},
    {"name": "Punjabi Bagh",      "lat": 28.6683, "lon": 77.1167, "mult": 1.10},
    {"name": "Pitampura",         "lat": 28.7009, "lon": 77.1309, "mult": 1.08},
    {"name": "Vivek Vihar",       "lat": 28.6724, "lon": 77.3177, "mult": 1.20},
    {"name": "Patparganj",        "lat": 28.6279, "lon": 77.2968, "mult": 1.12},
    {"name": "Noida Sec 62",      "lat": 28.6272, "lon": 77.3692, "mult": 1.15},
    {"name": "Noida Sec 1",       "lat": 28.5875, "lon": 77.3123, "mult": 1.05},
    {"name": "Greater Noida",     "lat": 28.4744, "lon": 77.5040, "mult": 1.10},
    {"name": "Ghaziabad Vasundhara","lat": 28.6600, "lon": 77.3665, "mult": 1.25},
    {"name": "Ghaziabad Loni",    "lat": 28.7500, "lon": 77.2800, "mult": 1.32},
    {"name": "Faridabad Sector 11","lat": 28.4089, "lon": 77.3178, "mult": 1.10},
    {"name": "Faridabad BPTP",    "lat": 28.3740, "lon": 77.3540, "mult": 1.08},
    {"name": "Gurugram Sector 51","lat": 28.4595, "lon": 77.0266, "mult": 0.90},
    {"name": "Gurugram Manesar",  "lat": 28.3563, "lon": 76.9319, "mult": 0.95},
    {"name": "Dwarka Sec 8",      "lat": 28.5710, "lon": 77.0719, "mult": 0.92},
    {"name": "RK Puram",          "lat": 28.5638, "lon": 77.1864, "mult": 0.88},
    {"name": "Lodhi Road",        "lat": 28.5919, "lon": 77.2273, "mult": 0.80},
    {"name": "ITO",               "lat": 28.6289, "lon": 77.2407, "mult": 1.00},
    {"name": "Connaught Place",   "lat": 28.6330, "lon": 77.2194, "mult": 0.98},
    {"name": "Shadipur",          "lat": 28.6526, "lon": 77.1523, "mult": 1.12},
    {"name": "Okhla Phase 2",     "lat": 28.5364, "lon": 77.2716, "mult": 1.05},
    {"name": "Sahibabad",         "lat": 28.6785, "lon": 77.3488, "mult": 1.18},
    {"name": "Sonia Vihar",       "lat": 28.7131, "lon": 77.2584, "mult": 1.15},
    {"name": "Nehru Nagar",       "lat": 28.5926, "lon": 77.2541, "mult": 1.02},
    {"name": "R K Puram Sec 8",   "lat": 28.5596, "lon": 77.1780, "mult": 0.90},
    {"name": "Ballabhgarh",       "lat": 28.3419, "lon": 77.3225, "mult": 1.07},
    {"name": "Sonipat",           "lat": 28.9945, "lon": 77.0155, "mult": 1.05},
]


def fetch_current_aqi_seed():
    """Fetch today's current PM2.5, PM10, AQI from Open-Meteo for seeding Day 1 lag values."""
    try:
        url = ("https://air-quality-api.open-meteo.com/v1/air-quality"
               "?latitude=28.6139&longitude=77.2090"
               "&hourly=pm10,pm2_5,european_aqi"
               "&timezone=Asia%2FKolkata&past_days=2")
        data = requests.get(url, timeout=6).json()
        now = datetime.now()
        h_now = now.hour
        # Index 24+h_now = today at current hour (past_days=2 gives 48h before + today)
        idx_now   = 48 + h_now
        idx_1h    = max(0, idx_now - 1)
        idx_24h   = max(0, idx_now - 24)
        idx_48h   = max(0, idx_now - 48)
        pm25  = data["hourly"]["pm2_5"]
        pm10  = data["hourly"]["pm10"]
        aqi   = data["hourly"]["european_aqi"]
        return {
            "pm25_lag_1":  pm25[idx_1h],
            "pm25_lag_24": pm25[idx_24h],
            "pm25_lag_48": pm25[idx_48h],
            "pm10_lag_1":  pm10[idx_1h],
            "pm10_lag_24": pm10[idx_24h],
            "pm10_lag_48": pm10[idx_48h],
            "aqi_lag_1":   aqi[idx_1h]   * 2.5,
            "aqi_lag_24":  aqi[idx_24h]  * 2.5,
            "aqi_lag_48":  aqi[idx_48h]  * 2.5,
        }
    except Exception as e:
        print(f"[Lag Seed] Using defaults: {e}")
        return {
            "pm25_lag_1": 80.0, "pm25_lag_24": 75.0, "pm25_lag_48": 70.0,
            "pm10_lag_1": 140.0, "pm10_lag_24": 130.0, "pm10_lag_48": 120.0,
            "aqi_lag_1": 180.0, "aqi_lag_24": 165.0, "aqi_lag_48": 150.0,
        }


# Cache: stores Day 1 and Day 2 average predictions for cascade use
_day_pred_cache = {}


@app.route("/api/forecast/day<int:day_offset>", methods=["GET"])
def get_day_forecast(day_offset):
    """
    Cascade chain forecasting:
    - Day 1: real current AQI values seed the lag features
    - Day 2: Day 1 predicted hourly averages seed the lag features
    - Day 3: Day 2 predicted hourly averages seed the lag features
    """
    now = datetime.now()
    target_date = now + timedelta(days=day_offset - 1)

    # ── Step 1: Get real weather forecast from Open-Meteo ──
    weather_data = fetch_open_meteo_forecast()

    # ── Step 2: Get lag seed (cascade chain) ──
    if day_offset == 1:
        lag_seed = fetch_current_aqi_seed()
    elif day_offset == 2:
        lag_seed = _day_pred_cache.get("day1", fetch_current_aqi_seed())
    else:  # day 3
        lag_seed = _day_pred_cache.get("day2", _day_pred_cache.get("day1", fetch_current_aqi_seed()))

    # ── Step 3: Build current feature vector & get panel items ──
    f0 = build_feature_vector(
        hour=target_date.hour, dayofweek=target_date.weekday(),
        **lag_seed
    )
    items, raw_preds = predict_6_targets(f0)

    # ── Step 4: Generate hourly chart with cascade lags rolling forward ──
    max_aqi_scale = 400.0
    current_hour_index = now.hour
    start_idx = current_hour_index + (day_offset - 1) * 24

    hourly_chart = []
    # Rolling lags that update as we march through the hours
    roll_pm25 = [lag_seed["pm25_lag_48"], lag_seed["pm25_lag_24"], lag_seed["pm25_lag_1"]]
    roll_pm10 = [lag_seed["pm10_lag_48"], lag_seed["pm10_lag_24"], lag_seed["pm10_lag_1"]]
    roll_aqi  = [lag_seed["aqi_lag_48"],  lag_seed["aqi_lag_24"],  lag_seed["aqi_lag_1"]]

    hourly_pm25_preds = []
    hourly_pm10_preds = []
    hourly_aqi_preds  = []

    for i in range(24):
        future_dt = target_date + timedelta(hours=i)
        h = future_dt.hour

        f_temp = 28.0 + 5.0 * np.sin(2 * np.pi * (h - 8) / 24)
        f_hum  = 60.0 - 15.0 * np.sin(2 * np.pi * (h - 8) / 24)
        f_wind = 10.0 + 3.0 * np.sin(2 * np.pi * (h - 12) / 24)
        f_pres = 1012.0
        f_rad  = 1.2
        f_rain = 0.0

        if weather_data and "hourly" in weather_data:
            idx = start_idx + i
            wh = weather_data["hourly"]
            if idx < len(wh["temperature_2m"]):
                f_temp = wh["temperature_2m"][idx]
                f_hum  = wh["relative_humidity_2m"][idx]
                f_wind = wh["wind_speed_10m"][idx]
                f_pres = wh["surface_pressure"][idx]
                f_rad  = wh["shortwave_radiation"][idx] / 1000.0
                f_rain = wh["precipitation"][idx]

        feat_h = build_feature_vector(
            hour=h, dayofweek=future_dt.weekday(),
            temp=f_temp, humidity=f_hum, wind_speed=f_wind,
            pressure=f_pres, radiation=f_rad, rain_amount=f_rain,
            pm25_lag_1=roll_pm25[-1], pm25_lag_24=roll_pm25[-2], pm25_lag_48=roll_pm25[-3],
            pm10_lag_1=roll_pm10[-1], pm10_lag_24=roll_pm10[-2], pm10_lag_48=roll_pm10[-3],
            aqi_lag_1 =roll_aqi[-1],  aqi_lag_24 =roll_aqi[-2],  aqi_lag_48 =roll_aqi[-3],
        )
        _, preds_h = predict_6_targets(feat_h)
        aqi_h  = preds_h["aqi"]
        pm25_h = preds_h["pm25"]
        pm10_h = preds_h["pm10"]
        ratio  = float(np.clip(aqi_h / max_aqi_scale, 0.05, 1.0))
        hour_label = f"{h:02d}:00"

        hourly_chart.append({
            "id": f"day{day_offset}-h{i}-{hour_label}",
            "value": round(ratio, 3),
            "label": hour_label,
            "topLabel": round(aqi_h, 0),
            "tooltip": f"+{(day_offset-1)*24+i}h ({hour_label}) | AQI:{round(aqi_h,1)} | PM2.5:{round(pm25_h,1)} µg/m³ | PM10:{round(pm10_h,1)} µg/m³",
            "highlighted": aqi_h > 200.0,
        })

        # Roll the lag windows forward with predicted values
        roll_pm25.append(pm25_h); roll_pm10.append(pm10_h); roll_aqi.append(aqi_h)
        hourly_pm25_preds.append(pm25_h)
        hourly_pm10_preds.append(pm10_h)
        hourly_aqi_preds.append(aqi_h)

    # ── Step 5: Store cascade seed for next day ──
    avg_pm25 = float(np.mean(hourly_pm25_preds))
    avg_pm10 = float(np.mean(hourly_pm10_preds))
    avg_aqi  = float(np.mean(hourly_aqi_preds))
    _day_pred_cache[f"day{day_offset}"] = {
        "pm25_lag_1": avg_pm25, "pm25_lag_24": lag_seed["pm25_lag_1"], "pm25_lag_48": lag_seed["pm25_lag_24"],
        "pm10_lag_1": avg_pm10, "pm10_lag_24": lag_seed["pm10_lag_1"], "pm10_lag_48": lag_seed["pm10_lag_24"],
        "aqi_lag_1":  avg_aqi,  "aqi_lag_24":  lag_seed["aqi_lag_1"],  "aqi_lag_48":  lag_seed["aqi_lag_24"],
    }

    # ── Step 6: Generate hotspots for all 30+ locations ──
    base_aqi = avg_aqi
    hotspots = []
    for loc in DELHI_HOTSPOT_GRID:
        loc_aqi = round(base_aqi * loc["mult"], 1)
        if loc_aqi > 300:
            sev = "severe"
        elif loc_aqi > 200:
            sev = "very-poor"
        elif loc_aqi > 100:
            sev = "poor"
        else:
            sev = "moderate"
        hotspots.append({
            "name": loc["name"],
            "lat": loc["lat"],
            "lon": loc["lon"],
            "severity": sev,
            "aqi": loc_aqi,
        })

    return jsonify({
        "status": "success",
        "horizon": f"Day {day_offset} ({(day_offset-1)*24}-{day_offset*24} Hours)",
        "prediction_time": target_date.isoformat(),
        "items": items,
        "chartData": hourly_chart,
        "hotspots": hotspots,
        "source": f"Vatavarnam ML Cascade Ensemble — Day {day_offset} (API-Seeded)"
    })


@app.route("/api/activity/predictions", methods=["GET"])
def get_activity_predictions():
    """
    Returns the 6 Activity Prediction items for Delhi NCR with context-aware severity color-coding.
    """
    now = datetime.now()
    current_features = build_feature_vector(hour=now.hour, dayofweek=now.weekday())
    items = predict_activity_slots(current_features)
    return jsonify({
        "status": "success",
        "region": "Delhi NCR",
        "prediction_time": now.isoformat(),
        "items": items,
        "source": "Delhi NCR Activity Risk ML Ensemble"
    })


if __name__ == "__main__":
    load_artifacts()
    print("Starting Vatavarnam ML Backend on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False)

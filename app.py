"""Streamlit dashboard for the cleaned Open-Meteo weather data (Gold zone).

Reads data/processed/weather_clean.csv. If it is missing (or the user clicks
"Rafraîchir"), it runs the ETL pipeline on demand. Run with:

    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.pipeline import run_pipeline
from src.transform import PROCESSED_DIR

CSV_PATH = PROCESSED_DIR / "weather_clean.csv"

# Preset locations for the sidebar selector.
LOCATIONS = {
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Bordeaux": (44.8378, -0.5792),
    "Lille": (50.6292, 3.0573),
}

st.set_page_config(page_title="Météo — Dashboard", page_icon="🌦️", layout="wide")


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df


def refresh(lat: float, lon: float, days: int) -> None:
    """Re-run the ETL for the chosen location and clear the cache."""
    with st.spinner("Récupération des données Open-Meteo..."):
        run_pipeline(latitude=lat, longitude=lon, forecast_days=days)
    load_data.clear()


# ---- Sidebar controls -------------------------------------------------------
st.sidebar.header("⚙️ Paramètres")
city = st.sidebar.selectbox("Ville", list(LOCATIONS.keys()))
days = st.sidebar.slider("Jours de prévision", min_value=1, max_value=7, value=3)
lat, lon = LOCATIONS[city]

if st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True):
    refresh(lat, lon, days)

st.sidebar.caption(f"Coordonnées : {lat}, {lon}")
st.sidebar.caption("Source : Open-Meteo (API gratuite, sans clé)")

# ---- Main -------------------------------------------------------------------
st.title("🌦️ Dashboard Météo")

if not CSV_PATH.exists():
    st.info("Aucune donnée locale. Génération du jeu de données initial...")
    refresh(lat, lon, days)

df = load_data(CSV_PATH)

# KPIs (indicateurs clés).
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡️ Temp. moyenne", f"{df['temperature_c'].mean():.1f} °C")
col2.metric("🔺 Temp. max", f"{df['temperature_c'].max():.1f} °C")
col3.metric("💧 Précip. totales", f"{df['precipitation_mm'].sum():.1f} mm")
col4.metric("💨 Vent moyen", f"{df['wind_speed_kmh'].mean():.1f} km/h")

st.divider()

# Temperature over time.
st.subheader("🌡️ Température (°C)")
st.line_chart(df.set_index("timestamp")["temperature_c"])

left, right = st.columns(2)

with left:
    st.subheader("💧 Précipitations (mm)")
    st.bar_chart(df.set_index("timestamp")["precipitation_mm"])

with right:
    st.subheader("💨 Vent & 💧 Humidité")
    st.line_chart(
        df.set_index("timestamp")[["wind_speed_kmh", "humidity_pct"]]
    )

# Map of the current location.
st.subheader("🗺️ Localisation")
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=9)

# Raw table.
with st.expander("📄 Voir les données nettoyées (Gold zone)"):
    st.dataframe(df, use_container_width=True)

st.caption(f"{len(df)} lignes — fichier : {CSV_PATH}")

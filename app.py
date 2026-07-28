"""Streamlit dashboard for the cleaned weather data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.pipeline import run_pipeline
from src.transform import PROCESSED_DIR

CSV_PATH = PROCESSED_DIR / "weather_clean.csv"

LOCATIONS = {
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Bordeaux": (44.8378, -0.5792),
    "Lille": (50.6292, 3.0573),
}

st.set_page_config(page_title="Weather Dashboard", layout="wide")


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["timestamp"])


def refresh(lat: float, lon: float, days: int) -> None:
    with st.spinner("Fetching Open-Meteo data..."):
        run_pipeline(latitude=lat, longitude=lon, forecast_days=days)
    load_data.clear()


st.sidebar.header("Settings")
city = st.sidebar.selectbox("City", list(LOCATIONS.keys()))
days = st.sidebar.slider("Forecast days", min_value=1, max_value=7, value=3)
lat, lon = LOCATIONS[city]

if st.sidebar.button("Refresh data", use_container_width=True):
    refresh(lat, lon, days)

st.sidebar.caption(f"Coordinates: {lat}, {lon}")
st.sidebar.caption("Source: Open-Meteo")

st.title("Weather Dashboard")

if not CSV_PATH.exists():
    refresh(lat, lon, days)

df = load_data(CSV_PATH)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg temp", f"{df['temperature_c'].mean():.1f} C")
col2.metric("Max temp", f"{df['temperature_c'].max():.1f} C")
col3.metric("Total precip", f"{df['precipitation_mm'].sum():.1f} mm")
col4.metric("Avg wind", f"{df['wind_speed_kmh'].mean():.1f} km/h")

st.divider()

st.subheader("Temperature (C)")
st.line_chart(df.set_index("timestamp")["temperature_c"])

left, right = st.columns(2)
with left:
    st.subheader("Precipitation (mm)")
    st.bar_chart(df.set_index("timestamp")["precipitation_mm"])
with right:
    st.subheader("Wind and humidity")
    st.line_chart(df.set_index("timestamp")[["wind_speed_kmh", "humidity_pct"]])

st.subheader("Location")
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=9)

with st.expander("Cleaned data"):
    st.dataframe(df, use_container_width=True)

st.caption(f"{len(df)} rows - {CSV_PATH}")

"""Clean and structure raw Open-Meteo data into a typed DataFrame."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import storage

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
GOLD_BLOB = "weather_clean.csv"

COLUMN_RENAMES = {
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "relative_humidity_2m": "humidity_pct",
    "precipitation": "precipitation_mm",
    "wind_speed_10m": "wind_speed_kmh",
}


def transform_weather(payload: dict) -> pd.DataFrame:
    """Convert a raw Open-Meteo payload into a clean, typed DataFrame."""
    hourly = payload.get("hourly")
    if not hourly or "time" not in hourly:
        raise ValueError("Payload missing 'hourly' data; cannot transform.")

    df = pd.DataFrame(hourly)
    df = df.rename(columns=COLUMN_RENAMES)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    value_cols = [c for c in df.columns if c != "timestamp"]
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["timestamp"])
    df = df.dropna(subset=value_cols, how="all")

    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
    df = df.reset_index(drop=True)

    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    return df


def save_processed(df: pd.DataFrame, processed_dir: Path = PROCESSED_DIR) -> str:
    """Persist the cleaned DataFrame as CSV.

    Uploads to the ADLS gold container when enabled, else writes locally.
    """
    if storage.adls_enabled():
        return storage.upload_text(storage.GOLD_CONTAINER, GOLD_BLOB, df.to_csv(index=False))

    processed_dir.mkdir(parents=True, exist_ok=True)
    out_path = processed_dir / GOLD_BLOB
    df.to_csv(out_path, index=False)
    return str(out_path)

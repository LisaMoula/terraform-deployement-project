"""Transform layer: clean and structure raw Open-Meteo data with pandas.

Turns the nested hourly JSON into a flat, typed DataFrame (Gold zone) and
persists it as CSV. Kept pure/deterministic so it is easy to unit test.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# API variable -> friendly column name.
COLUMN_RENAMES = {
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "relative_humidity_2m": "humidity_pct",
    "precipitation": "precipitation_mm",
    "wind_speed_10m": "wind_speed_kmh",
}


def transform_weather(payload: dict) -> pd.DataFrame:
    """Convert a raw Open-Meteo payload into a clean, typed DataFrame.

    Steps: build frame from `hourly`, rename columns, parse timestamps,
    drop fully-empty rows, coerce numerics, sort and dedupe by timestamp.
    """
    hourly = payload.get("hourly")
    if not hourly or "time" not in hourly:
        raise ValueError("Payload missing 'hourly' data; cannot transform.")

    df = pd.DataFrame(hourly)
    df = df.rename(columns=COLUMN_RENAMES)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    value_cols = [c for c in df.columns if c != "timestamp"]
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with no timestamp or no measurements at all.
    df = df.dropna(subset=["timestamp"])
    df = df.dropna(subset=value_cols, how="all")

    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
    df = df.reset_index(drop=True)

    # Enrichment: local date + hour for easier dashboard grouping.
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    return df


def save_processed(df: pd.DataFrame, processed_dir: Path = PROCESSED_DIR) -> Path:
    """Persist the cleaned DataFrame as CSV (Gold zone)."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_path = processed_dir / "weather_clean.csv"
    df.to_csv(out_path, index=False)
    return out_path

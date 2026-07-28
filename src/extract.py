"""Fetch raw weather data from the Open-Meteo API (no API key needed)."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import requests

from src import storage

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_LATITUDE = 48.8566
DEFAULT_LONGITUDE = 2.3522

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def extract_weather(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    forecast_days: int = 3,
    timeout: int = 30,
) -> dict:
    """Call the Open-Meteo forecast API and return the parsed JSON payload."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_VARIABLES),
        "forecast_days": forecast_days,
        "timezone": "auto",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def save_raw(payload: dict, raw_dir: Path = RAW_DIR) -> str:
    """Persist the raw API payload as timestamped JSON.

    Uploads to the ADLS landing container when enabled, else writes locally.
    """
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"weather_raw_{stamp}.json"
    text = json.dumps(payload, indent=2)

    if storage.adls_enabled():
        return storage.upload_text(storage.LANDING_CONTAINER, name, text)

    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / name
    out_path.write_text(text, encoding="utf-8")
    return str(out_path)


if __name__ == "__main__":
    data = extract_weather()
    path = save_raw(data)
    print(f"Raw weather saved -> {path}")

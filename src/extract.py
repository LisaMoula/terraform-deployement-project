"""Extract layer: fetch raw weather data from the Open-Meteo API.

Open-Meteo is free and requires no API key. We keep this module free of any
transformation logic so the "raw" data can be persisted untouched (Landing zone).
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Default location: Paris. Overridable via extract_weather() args.
DEFAULT_LATITUDE = 48.8566
DEFAULT_LONGITUDE = 2.3522

# Hourly variables we request from the API.
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
    """Call the Open-Meteo forecast API and return the parsed JSON payload.

    Raises requests.HTTPError on a non-2xx response so callers/tests can react.
    """
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


def save_raw(payload: dict, raw_dir: Path = RAW_DIR) -> Path:
    """Persist the raw API payload as timestamped JSON (Landing zone)."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = raw_dir / f"weather_raw_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    data = extract_weather()
    path = save_raw(data)
    print(f"Raw weather saved -> {path}")

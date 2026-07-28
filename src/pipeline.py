"""Pipeline orchestrator: extract -> transform -> load (ETL).

Ties the extract and transform layers together and writes both the raw
Landing payload and the cleaned Gold CSV. Run as a module:

    python -m src.pipeline
"""

from __future__ import annotations

import argparse

from src.extract import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, extract_weather, save_raw
from src.transform import save_processed, transform_weather


def run_pipeline(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    forecast_days: int = 3,
) -> dict:
    """Execute the full ETL and return a summary dict of what was produced."""
    payload = extract_weather(latitude, longitude, forecast_days)
    raw_path = save_raw(payload)

    df = transform_weather(payload)
    processed_path = save_processed(df)

    return {
        "raw_path": str(raw_path),
        "processed_path": str(processed_path),
        "rows": len(df),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open-Meteo weather ETL pipeline")
    parser.add_argument("--lat", type=float, default=DEFAULT_LATITUDE)
    parser.add_argument("--lon", type=float, default=DEFAULT_LONGITUDE)
    parser.add_argument("--days", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    summary = run_pipeline(args.lat, args.lon, args.days)
    print(
        f"Pipeline OK | rows={summary['rows']} | "
        f"raw={summary['raw_path']} | processed={summary['processed_path']}"
    )

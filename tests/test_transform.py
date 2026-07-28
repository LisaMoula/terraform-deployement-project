"""Unit tests for the transform layer. Pure pandas logic, no network."""

from __future__ import annotations

import pandas as pd
import pytest

from src.transform import save_processed, transform_weather


def _raw_payload() -> dict:
    return {
        "hourly": {
            "time": [
                "2026-07-28T02:00",
                "2026-07-28T00:00",
                "2026-07-28T01:00",
                "2026-07-28T01:00",  # duplicate timestamp
            ],
            "temperature_2m": [16.0, 18.1, 17.6, 17.6],
            "relative_humidity_2m": [78, 80, 82, 82],
            "precipitation": [0.1, 0.0, 0.2, 0.2],
            "wind_speed_10m": [8.0, 10.0, 9.4, 9.4],
        }
    }


def test_transform_renames_and_types():
    df = transform_weather(_raw_payload())

    assert "temperature_c" in df.columns
    assert "humidity_pct" in df.columns
    assert "precipitation_mm" in df.columns
    assert "wind_speed_kmh" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_numeric_dtype(df["temperature_c"])


def test_transform_sorts_and_dedupes():
    df = transform_weather(_raw_payload())

    # Duplicate 01:00 removed -> 3 unique rows.
    assert len(df) == 3
    # Sorted ascending by timestamp.
    assert list(df["timestamp"]) == sorted(df["timestamp"])


def test_transform_adds_date_and_hour():
    df = transform_weather(_raw_payload())
    assert "date" in df.columns
    assert "hour" in df.columns
    assert df["hour"].iloc[0] == 0


def test_transform_raises_on_empty_payload():
    with pytest.raises(ValueError):
        transform_weather({"hourly": {}})


def test_save_processed_writes_csv(tmp_path):
    df = transform_weather(_raw_payload())
    out = save_processed(df, processed_dir=tmp_path)

    assert out.exists()
    reloaded = pd.read_csv(out)
    assert len(reloaded) == len(df)

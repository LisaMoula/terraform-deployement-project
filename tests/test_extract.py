"""Unit tests for the extract layer. The HTTP call is mocked (no network)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.extract import HOURLY_VARIABLES, extract_weather, save_raw


def _fake_payload() -> dict:
    return {
        "latitude": 48.86,
        "longitude": 2.35,
        "hourly": {
            "time": ["2026-07-28T00:00", "2026-07-28T01:00"],
            "temperature_2m": [18.1, 17.6],
            "relative_humidity_2m": [80, 82],
            "precipitation": [0.0, 0.2],
            "wind_speed_10m": [10.0, 9.4],
        },
    }


@patch("src.extract.requests.get")
def test_extract_weather_returns_json(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _fake_payload()
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    result = extract_weather(latitude=48.86, longitude=2.35)

    assert "hourly" in result
    # All requested variables were passed to the API.
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["hourly"] == ",".join(HOURLY_VARIABLES)
    assert kwargs["params"]["latitude"] == 48.86


@patch("src.extract.requests.get")
def test_extract_weather_raises_on_http_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
    mock_get.return_value = mock_resp

    with pytest.raises(requests.HTTPError):
        extract_weather()


def test_save_raw_writes_file(tmp_path):
    payload = _fake_payload()
    out = save_raw(payload, raw_dir=tmp_path)

    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8"))["hourly"]["time"][0] == (
        "2026-07-28T00:00"
    )

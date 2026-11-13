"""Tests for forecast interpretation."""
from datetime import datetime, timedelta, timezone

from custom_components.smart_ventilation.forecast import assess_forecast


def test_forecast_detects_imminent_rain():
    now = datetime(2026, 11, 13, 18, tzinfo=timezone.utc)
    result = assess_forecast([{
        "datetime": (now + timedelta(hours=1)).isoformat(),
        "precipitation_probability": 80,
        "precipitation": 0.0,
    }], now, 22)
    assert result["available"]
    assert result["imminent_rain"]


def test_forecast_detects_high_gusts():
    now = datetime(2026, 11, 13, 18, tzinfo=timezone.utc)
    result = assess_forecast([{
        "datetime": (now + timedelta(hours=2)).isoformat(),
        "wind_gust_speed": 55,
    }], now, 22)
    assert result["high_wind"]


def test_forecast_finds_cooler_dry_night_window():
    now = datetime(2026, 11, 13, 19, tzinfo=timezone.utc)
    result = assess_forecast([{
        "datetime": (now + timedelta(hours=2)).isoformat(),
        "temperature": 17,
        "precipitation_probability": 10,
        "precipitation": 0,
        "wind_speed": 5,
        "wind_gust_speed": 10,
    }], now, 22)
    assert result["night_cooling_window"] is not None
    assert "Abkühlung nachts möglich" in result["advice"]


def test_missing_forecast_is_not_treated_as_safe():
    result = assess_forecast([], datetime.now(timezone.utc), 22)
    assert not result["available"]
    assert result["night_cooling_window"] is None

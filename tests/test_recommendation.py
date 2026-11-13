"""Tests for conservative recommendation behavior."""
from datetime import datetime, timedelta, timezone

from custom_components.smart_ventilation.models import Measurement
from custom_components.smart_ventilation.recommendation import recommend


def measurement(value, available=True):
    return Measurement(value if available else None, None, datetime.now(timezone.utc),
                       "sensor.test" if available else None, available)


def sample_room(co2=500, humidity=45, temperature=21):
    return {"temperature": measurement(temperature), "humidity": measurement(humidity),
            "co2": measurement(co2), "volume_m3": 40, "opening_type": "single"}


def sample_outdoor(temperature=10, humidity=50):
    return {"temperature": measurement(temperature), "humidity": measurement(humidity)}


def test_missing_outdoor_measurement_blocks_recommendation():
    outdoor = sample_outdoor()
    outdoor["humidity"] = measurement(None, available=False)
    result = recommend(sample_room(humidity=70), outdoor, {"available": False})
    assert result["state"] == "insufficient_data"
    assert result["duration"] is None


def test_high_co2_triggers_recommendation_when_weather_clear():
    result = recommend(sample_room(co2=1400), sample_outdoor(),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["state"] == "ventilate"
    assert result["method"] == "shock"


def test_humid_outdoor_air_blocks_humidity_driven_recommendation():
    result = recommend(sample_room(humidity=70, temperature=20),
                       sample_outdoor(temperature=20, humidity=95),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["state"] == "caution"
    assert result["duration"] is None


def test_rain_blocks_recommendation():
    result = recommend(sample_room(co2=1400), sample_outdoor(),
                       {"available": True, "condition": "rainy", "attributes": {}})
    assert result["state"] == "caution"


def test_missing_weather_is_explicit_and_lowers_confidence():
    result = recommend(sample_room(co2=1400), sample_outdoor(),
                       {"available": False, "attributes": {}})
    assert result["state"] == "ventilate"
    assert result["confidence"] == "low"
    assert "Regen und Wind konnten nicht geprüft werden" in result["reason"]


def test_cross_opening_selects_cross_ventilation():
    room = sample_room(co2=1400)
    room["opening_type"] = "cross"
    result = recommend(room, sample_outdoor(),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["method"] == "cross"


def test_stale_indoor_measurement_blocks_recommendation():
    room = sample_room(co2=1400)
    room["temperature"] = Measurement(
        21, "°C", datetime.now(timezone.utc), "sensor.test", True, stale=True
    )
    result = recommend(room, sample_outdoor(),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["state"] == "insufficient_data"
    assert "room_temperature" in result["missing"]


def test_stale_co2_is_not_used_as_a_trigger():
    room = sample_room(co2=1500)
    room["co2"] = Measurement(
        1500, "ppm", datetime.now(timezone.utc), "sensor.test", True, stale=True
    )
    result = recommend(room, sample_outdoor(),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["state"] == "no_action"
    assert result["confidence"] == "low"


def test_implausible_humidity_blocks_recommendation():
    room = sample_room(co2=1400)
    room["humidity"] = measurement(140)
    result = recommend(room, sample_outdoor(),
                       {"available": True, "condition": "sunny", "attributes": {}})
    assert result["state"] == "insufficient_data"


def test_hourly_rain_forecast_blocks_ventilation():
    now = datetime(2026, 11, 13, 18, tzinfo=timezone.utc)
    weather = {
        "available": True, "condition": "sunny", "attributes": {},
        "forecast_available": True,
        "forecast": [{
            "datetime": (now + timedelta(hours=1)).isoformat(),
            "precipitation_probability": 85, "precipitation": 0,
        }],
    }
    result = recommend(sample_room(co2=1400), sample_outdoor(), weather, now=now)
    assert result["state"] == "caution"
    assert result["method"] == "none"
    assert "Stundenprognose" in result["reason"]


def test_recommendation_exposes_night_cooling_window():
    now = datetime(2026, 11, 13, 19, tzinfo=timezone.utc)
    weather = {
        "available": True, "condition": "sunny", "attributes": {},
        "forecast_available": True,
        "forecast": [{
            "datetime": (now + timedelta(hours=2)).isoformat(),
            "temperature": 8, "precipitation_probability": 5,
            "precipitation": 0, "wind_speed": 5, "wind_gust_speed": 10,
        }],
    }
    result = recommend(sample_room(co2=500, temperature=22),
                       sample_outdoor(temperature=12, humidity=50),
                       weather, now=now)
    assert result["state"] == "no_action"
    assert result["night_cooling_window"] is not None

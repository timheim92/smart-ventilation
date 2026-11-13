"""Conservative interpretation of Home Assistant hourly forecasts."""
from __future__ import annotations

from datetime import datetime, timedelta
from math import isfinite


def _number(item: dict, key: str) -> float | None:
    try:
        value = float(item[key]) if item.get(key) is not None else None
        return value if value is not None and isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _forecast_time(item: dict) -> datetime | None:
    raw = item.get("datetime")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def assess_forecast(
    forecast: list[dict] | None,
    now: datetime,
    indoor_temperature: float | None = None,
) -> dict:
    """Summarize near-term weather risk and a possible night-cooling interval.

    Forecast units follow Home Assistant's weather entity conventions. Missing
    fields never count as proof of safe weather.
    """
    if not forecast:
        return {
            "available": False, "imminent_rain": False, "high_wind": False,
            "night_cooling_window": None, "advice": "Keine Stundenprognose verfügbar.",
        }

    horizon = now + timedelta(hours=3)
    imminent_rain = False
    high_wind = False
    night_candidates = []
    for item in forecast:
        if not isinstance(item, dict):
            continue
        when = _forecast_time(item)
        if when is None:
            continue
        if when.tzinfo is None and now.tzinfo is not None:
            when = when.replace(tzinfo=now.tzinfo)
        if when.tzinfo is not None and now.tzinfo is None:
            when = when.replace(tzinfo=None)

        probability = _number(item, "precipitation_probability")
        precipitation = _number(item, "precipitation")
        gust = _number(item, "wind_gust_speed")
        wind = _number(item, "wind_speed")
        if now <= when <= horizon:
            if (probability is not None and probability >= 60) or (
                precipitation is not None and precipitation >= 0.2
            ):
                imminent_rain = True
            if (gust is not None and gust > 50) or (wind is not None and wind > 35):
                high_wind = True

        local_hour = when.hour
        is_night = local_hour >= 20 or local_hour < 6
        temp = _number(item, "temperature")
        if (is_night and now <= when <= now + timedelta(hours=12)
                and indoor_temperature is not None and temp is not None
                and temp <= indoor_temperature - 2
                and (probability is not None or precipitation is not None)
                and (probability is None or probability < 40)
                and (precipitation is None or precipitation < 0.2)
                and (gust is not None or wind is not None)
                and (gust is None or gust <= 50)
                and (wind is None or wind <= 35)):
            night_candidates.append(when)

    window = night_candidates[0].isoformat() if night_candidates else None
    if imminent_rain or high_wind:
        advice = "Stundenprognose warnt vor Niederschlag oder starkem Wind in den nächsten 3 Stunden."
    elif window:
        advice = f"Abkühlung nachts möglich; erstes günstiges Zeitfenster ab {window}."
    else:
        advice = "Kein eindeutig günstiges nächtliches Abkühlungsfenster in der Prognose erkannt."
    return {
        "available": True,
        "imminent_rain": imminent_rain,
        "high_wind": high_wind,
        "night_cooling_window": window,
        "advice": advice,
    }

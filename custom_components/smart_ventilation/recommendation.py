"""Conservative, explainable, season-aware ventilation recommendations."""
from __future__ import annotations

import math
from datetime import datetime

from .calculations import absolute_humidity_g_m3, dew_point_c, estimate_ventilation_minutes
from .facade import facade_exposure
from .seasonal import thermal_guidance


def _valid_measurement(measurement, minimum: float, maximum: float) -> bool:
    """Reject unavailable, stale, non-numeric and implausible sensor values."""
    if not measurement.available or measurement.stale or measurement.value is None:
        return False
    try:
        value = float(measurement.value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(value) and minimum <= value <= maximum


def recommend(room: dict, outdoor: dict, weather: dict, now: datetime | None = None) -> dict:
    """Build a recommendation; uncertain sensor data never causes automatic action."""
    t, rh, co2 = room["temperature"], room["humidity"], room["co2"]
    ot, orh = outdoor["temperature"], outdoor["humidity"]
    required = (
        ("room_temperature", t, -50, 60),
        ("room_humidity", rh, 0, 100),
        ("outdoor_temperature", ot, -50, 60),
        ("outdoor_humidity", orh, 0, 100),
    )
    missing = [name for name, measurement, low, high in required
               if not _valid_measurement(measurement, low, high)]
    if missing:
        return {
            "state": "insufficient_data", "method": "none", "duration": None,
            "reason": "Messwerte fehlen, sind veraltet oder unplausibel: " + ", ".join(missing),
            "confidence": "low", "missing": missing,
        }

    ah_in = absolute_humidity_g_m3(float(t.value), float(rh.value))
    ah_out = absolute_humidity_g_m3(float(ot.value), float(orh.value))
    dew = dew_point_c(float(t.value), float(rh.value))
    attrs = weather.get("attributes", {})
    thermal = thermal_guidance(float(t.value), float(ot.value),
                               (now or datetime.now()).month, attrs.get("solar_irradiance"))
    facade = facade_exposure(room.get("orientation"), attrs.get("wind_bearing"))
    co2_valid = _valid_measurement(co2, 250, 10000)
    triggers = []
    if co2_valid and float(co2.value) >= 1000:
        triggers.append(f"CO₂ {float(co2.value):.0f} ppm")
    if float(rh.value) >= 60:
        triggers.append(f"relative Luftfeuchtigkeit {float(rh.value):.0f} %")

    common = {
        "absolute_humidity_indoor": round(ah_in, 2),
        "absolute_humidity_outdoor": round(ah_out, 2),
        "dew_point": round(dew, 2), "season": thermal["season"],
        "thermal_advice": thermal["advice"],
        "facade_exposure": facade["exposure"],
        "facade_confidence": facade["confidence"],
        "forecast_available": weather.get("forecast_available", False),
        "missing": [],
    }
    if not triggers:
        return {
            **common, "state": "no_action", "method": "none", "duration": 0,
            "reason": "Aktuell kein dringender Lüftungsbedarf anhand verfügbarer Messwerte. "
                      + thermal["advice"],
            "confidence": "medium" if co2_valid else "low",
        }

    reason = "Lüftungsbedarf: " + " und ".join(triggers) + ". "
    if ah_out > ah_in + 0.5:
        return {
            **common, "state": "caution", "method": "none", "duration": None,
            "reason": reason + "Außenluft enthält deutlich mehr Wasser; Feuchteeintrag möglich.",
            "confidence": "medium",
        }

    condition = str(weather.get("condition", "")).lower()
    if any(token in condition for token in
           ("rain", "pour", "hail", "lightning-rain", "snow")):
        return {
            **common, "state": "caution", "method": "none", "duration": None,
            "reason": reason + "Wetterquelle meldet Niederschlag. Fenster nicht unbeaufsichtigt öffnen.",
            "confidence": "medium",
        }

    def numeric(key):
        try:
            value = float(attrs[key]) if attrs.get(key) is not None else None
            return value if value is not None and math.isfinite(value) else None
        except (TypeError, ValueError):
            return None

    wind, gust = numeric("wind_speed"), numeric("wind_gust_speed")
    if (wind is not None and wind > 35) or (gust is not None and gust > 50):
        return {
            **common, "state": "caution", "method": "none", "duration": None,
            "reason": reason + "Wind oder Böen sind laut Wetterquelle hoch; örtliche Bedingungen prüfen.",
            "confidence": "low",
        }

    method = "cross" if room.get("opening_type") == "cross" else "shock"
    duration = estimate_ventilation_minutes(
        room.get("volume_m3"), 0.8 if method == "cross" else 0.5
    )
    advice = "Querlüften" if method == "cross" else "Stoßlüften"
    weather_note = (
        "" if weather.get("available")
        else " Wetterdaten fehlen; Regen und Wind konnten nicht geprüft werden."
    )
    return {
        **common, "state": "ventilate", "method": method, "duration": duration,
        "reason": reason + advice + ". " + thermal["advice"] + weather_note,
        "confidence": "medium" if co2_valid and weather.get("available") else "low",
    }

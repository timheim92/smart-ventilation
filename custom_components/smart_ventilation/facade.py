"""Facade exposure heuristics; wind direction is not an airflow measurement."""
from __future__ import annotations
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
def facade_exposure(facade: str | None, wind_bearing: float | None) -> dict:
    if facade not in DIRECTIONS or wind_bearing is None:
        return {"exposure": "unknown", "confidence": "low", "relative_angle_deg": None}
    angle = abs((float(wind_bearing) - DIRECTIONS.index(facade) * 45 + 180) % 360 - 180)
    exposure = "windward" if angle <= 60 else "leeward" if angle >= 120 else "side"
    return {"exposure": exposure, "confidence": "low",
            "relative_angle_deg": round(angle, 1),
            "note": "Windrichtung beschreibt nur die Fassadenexposition, keinen garantierten Luftstrom."}

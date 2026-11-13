"""Season-aware thermal guidance (advisory only)."""
from __future__ import annotations
from datetime import datetime

def season_for_month(month: int) -> str:
    if month in (5, 6, 7, 8, 9): return "summer"
    if month in (11, 12, 1, 2, 3): return "winter"
    return "transition"

def thermal_guidance(indoor_c: float, outdoor_c: float, month: int,
                     solar_w_m2: float | None = None,
                     target_indoor_c: float | None = None) -> dict:
    """Describe thermal consequences; no forecast or building simulation implied."""
    season = season_for_month(month)
    delta = outdoor_c - indoor_c
    if season == "summer":
        if delta >= 1.5:
            advice = "Außenluft ist kühler: Lüften kann zur Abkühlung beitragen."
        elif delta <= -1.5:
            advice = "Außenluft ist wärmer: tagsüber möglichst geschlossen halten."
        else:
            advice = "Temperaturunterschied gering; thermischer Effekt voraussichtlich klein."
        if solar_w_m2 is not None and solar_w_m2 >= 250:
            advice += " Hohe Sonneneinstrahlung: Beschattung berücksichtigen."
    elif season == "winter":
        advice = ("Außenluft ist deutlich kälter: kurz und intensiv statt dauerhaft kippen."
                  if delta <= -5 else "Temperaturverlust beim Lüften im Blick behalten.")
    else:
        advice = ("Außenluft ist kühler und kann zur Abkühlung beitragen."
                  if delta >= 2 else "Temperaturunterschied gering; nach Luftqualität entscheiden.")
    if target_indoor_c is not None and indoor_c <= target_indoor_c:
        advice += " Ziel-Raumtemperatur ist bereits erreicht/unterschritten; unnötige Abkühlung vermeiden."
    return {"season": season, "temperature_delta_c": round(delta, 1),
            "solar_irradiance_w_m2": solar_w_m2, "advice": advice}

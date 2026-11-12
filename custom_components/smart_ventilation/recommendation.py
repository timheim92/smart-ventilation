"""Explainable, conservative room-level ventilation recommendations."""
from __future__ import annotations
from .calculations import absolute_humidity_g_m3, dew_point_c, estimate_ventilation_minutes

def recommend(room: dict, outdoor: dict, weather: dict) -> dict:
    """Recommend ventilation using current data only; no forecast assumptions."""
    t, rh, co2 = room["temperature"], room["humidity"], room["co2"]
    ot, orh = outdoor["temperature"], outdoor["humidity"]
    missing = [name for name, m in (("room_temperature", t), ("room_humidity", rh),
               ("outdoor_temperature", ot), ("outdoor_humidity", orh)) if not m.available]
    if missing:
        return {"state":"insufficient_data","method":"none","duration":None,
                "reason":"Messwerte fehlen: " + ", ".join(missing),
                "confidence":"low","missing":missing}
    ah_in = absolute_humidity_g_m3(t.value, rh.value)
    ah_out = absolute_humidity_g_m3(ot.value, orh.value)
    dew = dew_point_c(t.value, rh.value)
    trigger = False
    reasons = []
    if co2.available and co2.value >= 1000:
        trigger = True
        reasons.append(f"CO₂ {co2.value:.0f} ppm")
    if rh.value >= 60:
        trigger = True
        reasons.append(f"relative Luftfeuchtigkeit {rh.value:.0f} %")
    if not trigger:
        return {"state":"no_action","method":"none","duration":0,
                "reason":"Aktuell kein dringender Lüftungsbedarf anhand der verfügbaren Messwerte.",
                "confidence":"medium" if co2.available else "low",
                "absolute_humidity_indoor":round(ah_in,2),"absolute_humidity_outdoor":round(ah_out,2),
                "dew_point":round(dew,2),"missing":[]}
    reason = "Lüftungsbedarf: " + " und ".join(reasons) + "."
    if ah_out >= ah_in + 0.5:
        return {"state":"caution","method":"none","duration":None,
                "reason":reason+" Außenluft ist deutlich feuchter; Lüften könnte die Feuchte erhöhen.",
                "confidence":"medium","absolute_humidity_indoor":round(ah_in,2),
                "absolute_humidity_outdoor":round(ah_out,2),"dew_point":round(dew,2),"missing":[]}
    attrs = weather.get("attributes", {})
    condition = str(weather.get("condition","")).lower()
    if any(x in condition for x in ("rain","pour","hail","lightning-rain")):
        return {"state":"caution","method":"none","duration":None,
                "reason":reason+" Wetterquelle meldet Niederschlag; Fenster nicht unbeaufsichtigt öffnen.",
                "confidence":"medium","absolute_humidity_indoor":round(ah_in,2),
                "absolute_humidity_outdoor":round(ah_out,2),"dew_point":round(dew,2),"missing":[]}
    try:
        wind = float(attrs["wind_speed"]) if attrs.get("wind_speed") is not None else None
    except (TypeError, ValueError):
        wind = None
    if wind is not None and wind > 35:
        return {"state":"caution","method":"none","duration":None,
                "reason":reason+" Hohe Windgeschwindigkeit laut Wetterquelle; örtliche Bedingungen prüfen.",
                "confidence":"low","absolute_humidity_indoor":round(ah_in,2),
                "absolute_humidity_outdoor":round(ah_out,2),"dew_point":round(dew,2),"missing":[]}
    method = "cross" if room.get("opening_type") == "cross" else "shock"
    duration = estimate_ventilation_minutes(room.get("volume_m3"), 0.8 if method == "cross" else 0.5)
    advice = "Querlüften" if method == "cross" else "Stoßlüften"
    if t.value - ot.value > 8:
        advice += "; im Winter kurz und intensiv lüften"
    elif ot.value > t.value + 2:
        advice += "; Außenluft ist wärmer, daher Bedarf prüfen"
    return {"state":"ventilate","method":method,"duration":duration,
            "reason":reason+" "+advice+".","confidence":"medium" if co2.available else "low",
            "absolute_humidity_indoor":round(ah_in,2),"absolute_humidity_outdoor":round(ah_out,2),
            "dew_point":round(dew,2),"missing":[]}

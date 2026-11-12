"""Conservative, explainable, season-aware ventilation recommendations."""
from __future__ import annotations
from datetime import datetime
from .calculations import absolute_humidity_g_m3, dew_point_c, estimate_ventilation_minutes
from .seasonal import thermal_guidance
from .facade import facade_exposure
def recommend(room: dict, outdoor: dict, weather: dict, now: datetime | None = None) -> dict:
    t, rh, co2 = room["temperature"], room["humidity"], room["co2"]
    ot, orh = outdoor["temperature"], outdoor["humidity"]
    missing = [key for key, m in (("room_temperature", t), ("room_humidity", rh), ("outdoor_temperature", ot), ("outdoor_humidity", orh)) if not m.available]
    if missing:
        return {"state":"insufficient_data","method":"none","duration":None,"reason":"Messwerte fehlen: "+", ".join(missing),"confidence":"low","missing":missing}
    ah_in, ah_out = absolute_humidity_g_m3(t.value, rh.value), absolute_humidity_g_m3(ot.value, orh.value)
    dew = dew_point_c(t.value, rh.value)
    thermal = thermal_guidance(t.value, ot.value, (now or datetime.now()).month, weather.get("attributes", {}).get("solar_irradiance"))
    facade = facade_exposure(room.get("orientation"), weather.get("attributes", {}).get("wind_bearing"))
    triggers=[]
    if co2.available and co2.value >= 1000: triggers.append(f"CO₂ {co2.value:.0f} ppm")
    if rh.value >= 60: triggers.append(f"relative Luftfeuchtigkeit {rh.value:.0f} %")
    common={"absolute_humidity_indoor":round(ah_in,2),"absolute_humidity_outdoor":round(ah_out,2),"dew_point":round(dew,2),"season":thermal["season"],"thermal_advice":thermal["advice"],"facade_exposure":facade["exposure"],"facade_confidence":facade["confidence"],"forecast_available":weather.get("forecast_available",False),"missing":[]}
    if not triggers:
        return {**common,"state":"no_action","method":"none","duration":0,"reason":"Aktuell kein dringender Lüftungsbedarf anhand verfügbarer Messwerte. "+thermal["advice"],"confidence":"medium" if co2.available else "low"}
    reason="Lüftungsbedarf: "+" und ".join(triggers)+". "
    if ah_out > ah_in + 0.5:
        return {**common,"state":"caution","method":"none","duration":None,"reason":reason+"Außenluft enthält deutlich mehr Wasser; Feuchteeintrag möglich.","confidence":"medium"}
    attrs=weather.get("attributes",{})
    condition=str(weather.get("condition","")).lower()
    if any(token in condition for token in ("rain","pour","hail","lightning-rain","snow")):
        return {**common,"state":"caution","method":"none","duration":None,"reason":reason+"Wetterquelle meldet Niederschlag. Fenster nicht unbeaufsichtigt öffnen.","confidence":"medium"}
    def numeric(key):
        try: return float(attrs[key]) if attrs.get(key) is not None else None
        except (TypeError,ValueError): return None
    wind, gust = numeric("wind_speed"), numeric("wind_gust_speed")
    if (wind is not None and wind > 35) or (gust is not None and gust > 50):
        return {**common,"state":"caution","method":"none","duration":None,"reason":reason+"Wind oder Böen sind laut Wetterquelle hoch; örtliche Bedingungen prüfen.","confidence":"low"}
    method="cross" if room.get("opening_type")=="cross" else "shock"
    duration=estimate_ventilation_minutes(room.get("volume_m3"),0.8 if method=="cross" else 0.5)
    advice="Querlüften" if method=="cross" else "Stoßlüften"
    return {**common,"state":"ventilate","method":method,"duration":duration,"reason":reason+advice+". "+thermal["advice"]+("" if weather.get("available") else " Wetterdaten fehlen; Regen/Wind sind ungeprüft."),"confidence":"medium" if co2.available and weather.get("available") else "low"}

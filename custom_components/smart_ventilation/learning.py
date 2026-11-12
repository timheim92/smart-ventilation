"""Passive learning helpers based on observed sensor changes around a window event."""
from __future__ import annotations
def ventilation_observation(before_co2: float | None, after_co2: float | None,
                            before_abs_humidity: float | None, after_abs_humidity: float | None,
                            duration_minutes: float | None) -> dict:
    if duration_minutes is None or duration_minutes <= 0:
        return {"valid": False, "reason": "invalid_duration"}
    if before_co2 is None or after_co2 is None:
        co2_delta = None
    else:
        co2_delta = round(before_co2 - after_co2, 1)
    if before_abs_humidity is None or after_abs_humidity is None:
        humidity_delta = None
    else:
        humidity_delta = round(before_abs_humidity - after_abs_humidity, 2)
    if co2_delta is None and humidity_delta is None:
        return {"valid": False, "reason": "insufficient_before_after_data"}
    return {"valid": True, "duration_minutes": round(duration_minutes, 1),
            "co2_reduction_ppm": co2_delta,
            "absolute_humidity_reduction_g_m3": humidity_delta,
            "note": "Beobachtungswert, keine normierte Luftwechselrate."}

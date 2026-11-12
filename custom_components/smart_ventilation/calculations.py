"""Physics helpers used by the ventilation recommendation engine."""
from __future__ import annotations
import math

def absolute_humidity_g_m3(temperature_c: float, relative_humidity: float) -> float:
    """Calculate absolute humidity using the Magnus approximation."""
    rh = min(100.0, max(0.0, relative_humidity))
    es = 6.112 * math.exp((17.62 * temperature_c) / (243.12 + temperature_c))
    return 216.7 * (es * rh / 100.0) / (273.15 + temperature_c)

def dew_point_c(temperature_c: float, relative_humidity: float) -> float:
    """Calculate dew point in Celsius."""
    rh = min(100.0, max(0.1, relative_humidity))
    a, b = 17.62, 243.12
    gamma = math.log(rh / 100.0) + a * temperature_c / (b + temperature_c)
    return b * gamma / (a - gamma)

def estimate_ventilation_minutes(room_volume_m3: float | None, opening_factor: float) -> int | None:
    """Return a coarse heuristic only; never a guaranteed air-change time."""
    if not room_volume_m3 or room_volume_m3 <= 0:
        return None
    base = 5 if opening_factor >= 0.7 else 10 if opening_factor >= 0.35 else 15
    return max(3, min(30, round(base * min(1.8, max(0.7, room_volume_m3 / 40.0)))))

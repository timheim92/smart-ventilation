"""Safety policy for a future, explicitly confirmed window actuator."""
from __future__ import annotations
def evaluate_open_request(*, enabled: bool, confirmed: bool, rain: bool | None,
                          wind_speed: float | None, gust_speed: float | None,
                          window_contact_open: bool | None = None,
                          max_wind: float = 35.0, max_gust: float = 50.0) -> dict:
    """Fail closed. This policy does not call HA services or move a window."""
    if not enabled: return {"allowed": False, "reason": "actuation_disabled"}
    if not confirmed: return {"allowed": False, "reason": "user_confirmation_required"}
    if rain is not False: return {"allowed": False, "reason": "rain_status_unknown_or_raining"}
    if wind_speed is None or wind_speed > max_wind:
        return {"allowed": False, "reason": "wind_unknown_or_too_strong"}
    if gust_speed is None or gust_speed > max_gust:
        return {"allowed": False, "reason": "gust_unknown_or_too_strong"}
    if window_contact_open is True:
        return {"allowed": False, "reason": "window_already_open"}
    return {"allowed": True, "reason": "checks_passed"}

"""Home Assistant entity adapter with validation and unit normalization."""
from __future__ import annotations
from datetime import datetime, timezone
import math
from homeassistant.core import HomeAssistant, State
from ..models import Measurement

MAX_AGE_SECONDS = 30 * 60

def _timestamp(state: State) -> datetime:
    value = state.last_updated
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

def _normalize(value: float, unit: str | None, expected_unit: str | None) -> float:
    """Convert supported temperature units to Celsius; preserve other units."""
    normalized_unit = (unit or expected_unit or "").strip().lower()
    if expected_unit == "°C":
        if normalized_unit in ("°f", "°f", "f", "fahrenheit"):
            return (value - 32) * 5 / 9
        if normalized_unit in ("k", "kelvin"):
            return value - 273.15
    return value

def _plausibility_error(value: float, expected_unit: str | None) -> str | None:
    if expected_unit == "%" and not 0 <= value <= 100:
        return "outside_valid_range_0_100"
    if expected_unit == "ppm" and value < 0:
        return "negative_concentration"
    if expected_unit == "°C" and not -100 <= value <= 100:
        return "outside_plausible_temperature_range"
    return None

def read_measurement(hass: HomeAssistant, entity_id: str | None,
                     expected_unit: str | None = None,
                     max_age_seconds: int = MAX_AGE_SECONDS) -> Measurement:
    """Read a numeric entity; missing, invalid, or stale data stays unavailable."""
    if not entity_id:
        return Measurement(None, expected_unit, None, None, False, reason="not_configured")
    state = hass.states.get(entity_id)
    if state is None:
        return Measurement(None, expected_unit, None, entity_id, False, reason="entity_not_found")
    observed_at = _timestamp(state)
    source_unit = state.attributes.get("unit_of_measurement")
    try:
        raw_value = float(state.state)
    except (TypeError, ValueError):
        return Measurement(None, source_unit or expected_unit, observed_at, entity_id,
                           False, reason=f"non_numeric_state:{state.state}")
    if not math.isfinite(raw_value):
        return Measurement(None, source_unit or expected_unit, observed_at, entity_id,
                           False, reason="non_finite_value")
    value = _normalize(raw_value, source_unit, expected_unit)
    error = _plausibility_error(value, expected_unit)
    if error:
        return Measurement(None, expected_unit, observed_at, entity_id, False, reason=error)
    age = (datetime.now(timezone.utc) - observed_at).total_seconds()
    if age > max_age_seconds:
        return Measurement(None, expected_unit or source_unit, observed_at, entity_id,
                           False, stale=True, reason="stale_measurement")
    return Measurement(value, expected_unit or source_unit, observed_at, entity_id, True)

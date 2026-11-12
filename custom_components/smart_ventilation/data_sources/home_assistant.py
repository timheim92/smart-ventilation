"""Home Assistant entity adapter with validation and freshness checks."""
from __future__ import annotations
from datetime import datetime, timezone
import math
from homeassistant.core import HomeAssistant, State
from ..models import Measurement

MAX_AGE_SECONDS = 30 * 60

def _timestamp(state: State) -> datetime:
    value = state.last_updated
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

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
    unit = state.attributes.get("unit_of_measurement") or expected_unit
    try:
        value = float(state.state)
    except (TypeError, ValueError):
        return Measurement(None, unit, observed_at, entity_id, False,
                           reason=f"non_numeric_state:{state.state}")
    if not math.isfinite(value):
        return Measurement(None, unit, observed_at, entity_id, False, reason="non_finite_value")
    age = (datetime.now(timezone.utc) - observed_at).total_seconds()
    if age > max_age_seconds:
        return Measurement(None, unit, observed_at, entity_id, False,
                           stale=True, reason="stale_measurement")
    return Measurement(value, unit, observed_at, entity_id, True)

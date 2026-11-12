"""Adapter for Home Assistant weather entities."""
from __future__ import annotations
from homeassistant.core import HomeAssistant

WEATHER_ATTRIBUTES = (
    "temperature", "humidity", "wind_speed", "wind_bearing",
    "pressure", "precipitation",
)

def read_weather(hass: HomeAssistant, entity_id: str | None) -> dict:
    """Read supported current weather attributes without filling gaps."""
    if not entity_id:
        return {"available": False, "source_entity": None, "reason": "not_configured", "attributes": {}}
    state = hass.states.get(entity_id)
    if state is None:
        return {"available": False, "source_entity": entity_id, "reason": "entity_not_found", "attributes": {}}
    values = {key: state.attributes[key] for key in WEATHER_ATTRIBUTES if key in state.attributes}
    return {
        "available": True,
        "source_entity": entity_id,
        "condition": state.state,
        "last_updated": state.last_updated.isoformat(),
        "attributes": values,
    }

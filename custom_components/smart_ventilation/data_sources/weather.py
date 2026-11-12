"""Home Assistant weather adapter, including optional hourly forecast."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
WEATHER_ATTRIBUTES = ("temperature", "humidity", "wind_speed", "wind_gust_speed", "wind_bearing", "pressure", "precipitation", "cloud_coverage")
async def async_read_weather(hass: HomeAssistant, entity_id: str | None) -> dict:
    if not entity_id:
        return {"available": False, "source_entity": None, "reason": "not_configured", "attributes": {}, "forecast": [], "forecast_available": False}
    state = hass.states.get(entity_id)
    if state is None:
        return {"available": False, "source_entity": entity_id, "reason": "entity_not_found", "attributes": {}, "forecast": [], "forecast_available": False}
    attributes = {key: state.attributes[key] for key in WEATHER_ATTRIBUTES if key in state.attributes}
    forecast = []
    try:
        response = await hass.services.async_call("weather", "get_forecasts", {"type": "hourly"}, target={"entity_id": entity_id}, blocking=True, return_response=True)
        forecast = (response or {}).get(entity_id, {}).get("forecast", [])[:24]
    except Exception:
        forecast = []
    return {"available": True, "source_entity": entity_id, "condition": state.state, "last_updated": state.last_updated.isoformat(), "attributes": attributes, "forecast": forecast, "forecast_available": bool(forecast)}

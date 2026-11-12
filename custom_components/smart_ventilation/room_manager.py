"""Room configuration helpers."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from .data_sources.home_assistant import read_measurement

def configured_rooms(options: dict) -> list[dict]:
    """Return valid room definitions stored in config entry options."""
    rooms = options.get("rooms", [])
    if not isinstance(rooms, list):
        return []
    return [room for room in rooms if isinstance(room, dict) and room.get("room_id") and room.get("name")]

def collect_room_data(hass: HomeAssistant, room: dict) -> dict:
    """Collect normalized measurements for one room."""
    return {
        "room_id": room["room_id"],
        "name": room["name"],
        "temperature": read_measurement(hass, room.get("temperature"), "°C"),
        "humidity": read_measurement(hass, room.get("humidity"), "%"),
        "co2": read_measurement(hass, room.get("co2"), "ppm"),
    }

"""Room configuration and normalized measurement collection."""
from __future__ import annotations
from homeassistant.core import HomeAssistant
from .data_sources.home_assistant import read_measurement

def configured_rooms(options: dict) -> list[dict]:
    rooms = options.get("rooms", [])
    if not isinstance(rooms, list):
        return []
    return [room for room in rooms if isinstance(room, dict) and room.get("room_id") and room.get("name")]

def collect_room_data(hass: HomeAssistant, room: dict) -> dict:
    """Collect room sensor data and basic building metadata."""
    area = room.get("area_m2")
    height = room.get("ceiling_height_m")
    try:
        volume = float(area) * float(height) if area and height else None
    except (TypeError, ValueError):
        volume = None
    return {
        "room_id": room["room_id"], "name": room["name"],
        "temperature": read_measurement(hass, room.get("temperature"), "°C"),
        "humidity": read_measurement(hass, room.get("humidity"), "%"),
        "co2": read_measurement(hass, room.get("co2"), "ppm"),
        "area_m2": area, "ceiling_height_m": height, "volume_m3": volume,
        "window_area_m2": room.get("window_area_m2"),
        "orientation": room.get("orientation"),
        "window_type": room.get("window_type"),
        "opening_type": room.get("opening_type"),
        "shading": room.get("shading"),
    }

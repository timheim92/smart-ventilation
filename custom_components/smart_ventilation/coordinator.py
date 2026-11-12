"""Data coordinator for Smart Ventilation."""
from __future__ import annotations
from datetime import timedelta, datetime, timezone
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, UPDATE_INTERVAL_MINUTES
from .data_sources.home_assistant import read_measurement
from .data_sources.weather import async_read_weather
from .room_manager import collect_room_data, configured_rooms
from .recommendation import recommend
_LOGGER = logging.getLogger(__name__)
class SmartVentilationCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass, entry) -> None:
        self.entry = entry
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.title}", update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES))
    async def _async_update_data(self) -> dict:
        options = self.entry.options
        outdoor = {"temperature": read_measurement(self.hass, options.get("outdoor_temperature"), "°C"),
                   "humidity": read_measurement(self.hass, options.get("outdoor_humidity"), "%")}
        weather = await async_read_weather(self.hass, options.get("weather_entity"))
        rooms = [collect_room_data(self.hass, room) for room in configured_rooms(options)]
        all_measurements = list(outdoor.values())
        for room in rooms:
            all_measurements.extend([room["temperature"], room["humidity"], room["co2"]])
            room["recommendation"] = recommend(room, outdoor, weather)
        return {"rooms": rooms, "outdoor": outdoor, "weather": weather,
                "weather_entity": options.get("weather_entity"),
                "available_count": sum(m.available for m in all_measurements),
                "configured_count": sum(m.source_entity is not None for m in all_measurements),
                "stale_count": sum(m.stale for m in all_measurements),
                "room_count": len(rooms), "collected_at": datetime.now(timezone.utc)}

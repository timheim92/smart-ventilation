"""Data coordinator for Smart Ventilation."""
from __future__ import annotations
from datetime import timedelta, datetime, timezone
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, UPDATE_INTERVAL_MINUTES
from .data_sources.home_assistant import read_measurement
from .data_sources.weather import read_weather
from .room_manager import collect_room_data, configured_rooms
_LOGGER = logging.getLogger(__name__)

class SmartVentilationCoordinator(DataUpdateCoordinator[dict]):
    """Normalize global outdoor data and independently configured rooms."""
    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.entry = entry
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.title}",
                         update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES))

    async def _async_update_data(self) -> dict:
        options = self.entry.options
        outdoor_temperature = read_measurement(self.hass, options.get("outdoor_temperature"), "°C")
        outdoor_humidity = read_measurement(self.hass, options.get("outdoor_humidity"), "%")
        weather = read_weather(self.hass, options.get("weather_entity"))
        rooms = [collect_room_data(self.hass, room) for room in configured_rooms(options)]
        all_measurements = [outdoor_temperature, outdoor_humidity]
        for room in rooms:
            all_measurements.extend([room["temperature"], room["humidity"], room["co2"]])
        configured = sum(m.source_entity is not None for m in all_measurements)
        return {
            "rooms": rooms,
            "outdoor": {"temperature": outdoor_temperature, "humidity": outdoor_humidity},
            "weather": weather,
            "weather_entity": options.get("weather_entity"),
            "available_count": sum(m.available for m in all_measurements),
            "configured_count": configured,
            "stale_count": sum(m.stale for m in all_measurements),
            "room_count": len(rooms),
            "collected_at": datetime.now(timezone.utc),
        }

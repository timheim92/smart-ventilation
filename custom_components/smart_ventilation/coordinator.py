"""Data coordinator for Smart Ventilation."""
from __future__ import annotations
from datetime import timedelta, datetime, timezone
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, UPDATE_INTERVAL_MINUTES
from .data_sources.home_assistant import read_measurement
from .models import OutdoorAirData, RoomAirData, VentilationData
_LOGGER = logging.getLogger(__name__)

class SmartVentilationCoordinator(DataUpdateCoordinator[dict]):
    """Normalize configured Home Assistant entities."""
    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.entry = entry
        super().__init__(hass, _LOGGER, name=f"{DOMAIN}_{entry.title}",
                         update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES))

    async def _async_update_data(self) -> dict:
        options = self.entry.options
        indoor = RoomAirData(
            read_measurement(self.hass, options.get("indoor_temperature"), "°C"),
            read_measurement(self.hass, options.get("indoor_humidity"), "%"),
            read_measurement(self.hass, options.get("indoor_co2"), "ppm"))
        outdoor = OutdoorAirData(
            read_measurement(self.hass, options.get("outdoor_temperature"), "°C"),
            read_measurement(self.hass, options.get("outdoor_humidity"), "%"))
        snapshot = VentilationData(indoor, outdoor, options.get("weather_entity"),
                                   datetime.now(timezone.utc))
        measurements = {
            "indoor_temperature": indoor.temperature, "indoor_humidity": indoor.humidity,
            "indoor_co2": indoor.co2, "outdoor_temperature": outdoor.temperature,
            "outdoor_humidity": outdoor.humidity}
        configured = sum(bool(options.get(key)) for key in (
            "indoor_temperature", "indoor_humidity", "indoor_co2",
            "outdoor_temperature", "outdoor_humidity"))
        return {"snapshot": snapshot, "measurements": measurements,
                "available_count": sum(m.available for m in measurements.values()),
                "configured_count": configured,
                "stale_count": sum(m.stale for m in measurements.values()),
                "weather_entity": snapshot.weather_entity}

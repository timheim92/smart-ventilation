"""Sensor entities for Smart Ventilation."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import SmartVentilationCoordinator
from .const import CONF_NAME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Ventilation sensors."""
    coordinator: SmartVentilationCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartVentilationStatusSensor(coordinator, entry)])


class SmartVentilationStatusSensor(
    CoordinatorEntity[SmartVentilationCoordinator], SensorEntity
):
    """Represent the setup/readiness status."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:home-thermometer"

    def __init__(
        self,
        coordinator: SmartVentilationCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Smart Ventilation",
            "model": "Ventilation recommendation engine",
        }

    @property
    def name(self) -> str:
        """Return the sensor name."""
        return "Status"

    @property
    def native_value(self) -> str:
        """Return the current setup status."""
        return self.coordinator.data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose a human-readable status message."""
        return {
            "message": self.coordinator.data.get("message", ""),
            "phase": "Foundation",
        }

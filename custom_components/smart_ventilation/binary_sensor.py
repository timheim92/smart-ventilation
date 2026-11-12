"""Binary sensor indicating whether a room currently needs ventilation."""
from __future__ import annotations
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_NAME, DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RoomVentilationBinarySensor(coordinator, entry, room["room_id"], room["name"])
                        for room in coordinator.data["rooms"]])

class RoomVentilationBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Expose recommendation state; this is not an actuator command."""
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry, room_id: str, room_name: str) -> None:
        super().__init__(coordinator)
        self.room_id = room_id
        self._attr_name = f"{room_name} Lüftungsbedarf"
        self._attr_unique_id = f"{entry.entry_id}_{room_id}_ventilation_needed"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME], "manufacturer":"Smart Ventilation",
            "model":"Room recommendation engine"}
    def _recommendation(self):
        return next((r["recommendation"] for r in self.coordinator.data["rooms"]
                     if r["room_id"] == self.room_id), {})
    @property
    def is_on(self) -> bool:
        return self._recommendation().get("state") == "ventilate"
    @property
    def extra_state_attributes(self) -> dict:
        return self._recommendation()

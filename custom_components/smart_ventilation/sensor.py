"""Sensor entities for Smart Ventilation."""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import SmartVentilationCoordinator
from .const import CONF_NAME, DOMAIN
SENSOR_DEFINITIONS = (
    ("indoor_temperature", "Innentemperatur", "°C"),
    ("indoor_humidity", "Innenluftfeuchtigkeit", "%"),
    ("indoor_co2", "CO₂ innen", "ppm"),
    ("outdoor_temperature", "Außentemperatur", "°C"),
    ("outdoor_humidity", "Außenluftfeuchtigkeit", "%"))

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SmartVentilationCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartVentilationStatusSensor(coordinator, entry)] +
        [MeasurementSensor(coordinator, entry, *item) for item in SENSOR_DEFINITIONS])

class _BaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME], "manufacturer": "Smart Ventilation",
            "model": "Ventilation data engine"}

class SmartVentilationStatusSensor(_BaseSensor):
    _attr_icon = "mdi:home-thermometer"
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Datenstatus"
    @property
    def native_value(self) -> str:
        data = self.coordinator.data
        if data["configured_count"] == 0: return "Nicht konfiguriert"
        if data["available_count"] == 0: return "Keine aktuellen Messwerte"
        if data["stale_count"]: return "Teilweise veraltet"
        return "Daten verfügbar"
    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        return {"konfigurierte_messwerte": data["configured_count"],
            "verfügbare_messwerte": data["available_count"],
            "veraltete_messwerte": data["stale_count"],
            "wetter_entität": data["weather_entity"],
            "hinweis": "Nicht konfigurierte oder veraltete Werte werden nicht geschätzt."}

class MeasurementSensor(_BaseSensor):
    def __init__(self, coordinator, entry: ConfigEntry, key: str,
                 name: str, unit: str) -> None:
        super().__init__(coordinator, entry)
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
    @property
    def native_value(self) -> float | None:
        measurement = self.coordinator.data["measurements"][self.key]
        return measurement.value if measurement.available else None
    @property
    def extra_state_attributes(self) -> dict:
        measurement = self.coordinator.data["measurements"][self.key]
        return {"source_entity": measurement.source_entity,
            "available": measurement.available, "stale": measurement.stale,
            "reason": measurement.reason,
            "observed_at": measurement.observed_at.isoformat() if measurement.observed_at else None}

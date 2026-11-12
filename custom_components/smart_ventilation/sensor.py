"""Dynamic room and global status sensors."""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import SmartVentilationCoordinator
from .const import CONF_NAME, DOMAIN

ROOM_FIELDS = (
    ("temperature", "Temperatur", "°C", "mdi:thermometer"),
    ("humidity", "Luftfeuchtigkeit", "%", "mdi:water-percent"),
    ("co2", "CO₂", "ppm", "mdi:molecule-co2"),
)
OUTDOOR_FIELDS = (
    ("temperature", "Außentemperatur", "°C"),
    ("humidity", "Außenluftfeuchtigkeit", "%"),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SmartVentilationCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [SmartVentilationStatusSensor(coordinator, entry)]
    for room in coordinator.data["rooms"]:
        for key, label, unit, icon in ROOM_FIELDS:
            entities.append(RoomMeasurementSensor(coordinator, entry, room["room_id"],
                                                  room["name"], key, label, unit, icon))
        entities.extend([
            RoomRecommendationSensor(coordinator, entry, room["room_id"], room["name"], "state", "Lüftungsempfehlung"),
            RoomRecommendationSensor(coordinator, entry, room["room_id"], room["name"], "duration", "Lüftungsdauer", "min"),
            RoomRecommendationSensor(coordinator, entry, room["room_id"], room["name"], "absolute_humidity_indoor", "Absolute Innenluftfeuchtigkeit", "g/m³"),
            RoomRecommendationSensor(coordinator, entry, room["room_id"], room["name"], "absolute_humidity_outdoor", "Absolute Außenluftfeuchtigkeit", "g/m³"),
            RoomRecommendationSensor(coordinator, entry, room["room_id"], room["name"], "dew_point", "Taupunkt", "°C"),
        ])
    for key, label, unit in OUTDOOR_FIELDS:
        entities.append(GlobalMeasurementSensor(coordinator, entry, key, label, unit))
    async_add_entities(entities)

class _BaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "Smart Ventilation",
            "model": "Ventilation data engine",
        }

class SmartVentilationStatusSensor(_BaseSensor):
    _attr_icon = "mdi:home-thermometer"
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Datenstatus"
    @property
    def native_value(self):
        data = self.coordinator.data
        if data["configured_count"] == 0: return "Nicht konfiguriert"
        if data["available_count"] == 0: return "Keine aktuellen Messwerte"
        if data["stale_count"]: return "Teilweise veraltet"
        return "Daten verfügbar"
    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "räume": data["room_count"],
            "konfigurierte_messwerte": data["configured_count"],
            "verfügbare_messwerte": data["available_count"],
            "veraltete_messwerte": data["stale_count"],
            "wetter_entität": data["weather_entity"],
            "hinweis": "Nicht konfigurierte oder veraltete Werte werden nicht geschätzt.",
        }

class RoomMeasurementSensor(_BaseSensor):
    def __init__(self, coordinator, entry, room_id, room_name, key, label, unit, icon):
        super().__init__(coordinator, entry)
        self.room_id, self.key = room_id, key
        self._attr_name = f"{room_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{room_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
    def _measurement(self):
        room = next((r for r in self.coordinator.data["rooms"]
                     if r["room_id"] == self.room_id), None)
        return room[self.key] if room else None
    @property
    def native_value(self):
        measurement = self._measurement()
        return measurement.value if measurement and measurement.available else None
    @property
    def extra_state_attributes(self):
        measurement = self._measurement()
        if measurement is None: return {"reason": "room_removed"}
        return {"room_id": self.room_id, "source_entity": measurement.source_entity,
                "available": measurement.available, "stale": measurement.stale,
                "reason": measurement.reason,
                "observed_at": measurement.observed_at.isoformat() if measurement.observed_at else None}

class GlobalMeasurementSensor(_BaseSensor):
    def __init__(self, coordinator, entry, key, label, unit):
        super().__init__(coordinator, entry)
        self.key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.entry_id}_outdoor_{key}"
        self._attr_native_unit_of_measurement = unit
    @property
    def native_value(self):
        m = self.coordinator.data["outdoor"][self.key]
        return m.value if m.available else None
    @property
    def extra_state_attributes(self):
        m = self.coordinator.data["outdoor"][self.key]
        return {"source_entity": m.source_entity, "available": m.available,
                "stale": m.stale, "reason": m.reason}


class RoomRecommendationSensor(_BaseSensor):
    """Expose recommendation details as separate Home Assistant entities."""
    def __init__(self, coordinator, entry, room_id, room_name, key, label, unit=None):
        super().__init__(coordinator, entry)
        self.room_id, self.key = room_id, key
        self._attr_name = f"{room_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{room_id}_recommendation_{key}"
        if unit:
            self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:air-filter" if key == "state" else "mdi:chart-line"
    def _value(self):
        room = next((r for r in self.coordinator.data["rooms"] if r["room_id"] == self.room_id), None)
        return room["recommendation"].get(self.key) if room else None
    @property
    def native_value(self):
        value = self._value()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        return value
    @property
    def extra_state_attributes(self):
        room = next((r for r in self.coordinator.data["rooms"] if r["room_id"] == self.room_id), None)
        return room["recommendation"] if room else {"reason": "room_removed"}

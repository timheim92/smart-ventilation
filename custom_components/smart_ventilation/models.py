"""Normalized data models used by Smart Ventilation."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class Measurement:
    """A normalized measurement; unavailable values remain None."""
    value: float | None
    unit: str | None
    observed_at: datetime | None
    source_entity: str | None
    available: bool
    stale: bool = False
    reason: str | None = None

@dataclass(frozen=True, slots=True)
class RoomAirData:
    """Indoor measurements for one room."""
    temperature: Measurement
    humidity: Measurement
    co2: Measurement

@dataclass(frozen=True, slots=True)
class OutdoorAirData:
    """Outdoor measurements."""
    temperature: Measurement
    humidity: Measurement

@dataclass(frozen=True, slots=True)
class VentilationData:
    """Normalized input snapshot."""
    indoor: RoomAirData
    outdoor: OutdoorAirData
    weather_entity: str | None
    collected_at: datetime

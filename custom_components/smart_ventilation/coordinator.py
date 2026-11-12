"""Data coordinator for Smart Ventilation."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class SmartVentilationCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinate ventilation data and expose integration readiness."""

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, str]:
        """Return a safe initial state until data sources are configured."""
        # Sensor discovery and source adapters will be implemented in a later
        # development step. Missing measurements must never be fabricated.
        return {
            "status": "not_configured",
            "message": "Noch keine Sensor- oder Wetterdatenquellen konfiguriert.",
        }

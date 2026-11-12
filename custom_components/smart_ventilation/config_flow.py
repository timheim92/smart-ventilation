"""Config flow for Smart Ventilation."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import CONF_NAME, DEFAULT_NAME, DOMAIN

ENTITY_FIELDS = ("indoor_temperature", "indoor_humidity", "indoor_co2",
                 "outdoor_temperature", "outdoor_humidity", "weather_entity")

class SmartVentilationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""
    VERSION = 1
    async def async_step_user(self, user_input: dict | None = None):
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            await self.async_set_unique_id(name.casefold())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=name, data={CONF_NAME: name})
        return self.async_show_form(step_id="user", data_schema=vol.Schema(
            {vol.Required(CONF_NAME, default=DEFAULT_NAME): str}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SmartVentilationOptionsFlow(config_entry)

class SmartVentilationOptionsFlow(config_entries.OptionsFlow):
    """Configure Home Assistant sensor and weather entities."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Optional(key, default=self.config_entry.options.get(key)):
                selector.EntitySelector(selector.EntitySelectorConfig())
            for key in ENTITY_FIELDS
        })
        return self.async_show_form(step_id="init", data_schema=schema,
            description_placeholders={"note": "Nicht vorhandene Sensoren leer lassen. Fehlende oder veraltete Werte werden nicht geschätzt."})

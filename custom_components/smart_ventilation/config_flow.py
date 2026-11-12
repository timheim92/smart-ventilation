"""Config flow and room manager for Smart Ventilation."""
from __future__ import annotations
import re
import uuid
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import CONF_NAME, DEFAULT_NAME, DOMAIN

def _entity():
    return selector.EntitySelector(selector.EntitySelectorConfig())

def _room_options(options: dict) -> list[dict]:
    return [{"value": room["room_id"], "label": room["name"]}
            for room in options.get("rooms", [])
            if isinstance(room, dict) and room.get("room_id") and room.get("name")]

class SmartVentilationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create an integration instance."""
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
    """Manage rooms and global weather data."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        return self.async_show_menu(step_id="init", menu_options=[
            "add_room", "remove_room", "global_sources"
        ])

    async def async_step_add_room(self, user_input: dict | None = None):
        if user_input is not None:
            name = user_input["name"].strip()
            if not name:
                return self.async_show_form(step_id="add_room", data_schema=self._room_schema(),
                                           errors={"name": "required"})
            rooms = list(self.config_entry.options.get("rooms", []))
            room_id = re.sub(r"[^a-z0-9_]+", "_", name.casefold()).strip("_") or uuid.uuid4().hex[:8]
            if any(room.get("room_id") == room_id for room in rooms):
                room_id = f"{room_id}_{uuid.uuid4().hex[:4]}"
            rooms.append({
                "room_id": room_id, "name": name,
                "temperature": user_input.get("temperature"),
                "humidity": user_input.get("humidity"), "co2": user_input.get("co2"),
                "area_m2": user_input.get("area_m2"),
                "ceiling_height_m": user_input.get("ceiling_height_m"),
                "window_area_m2": user_input.get("window_area_m2"),
                "orientation": user_input.get("orientation"),
                "window_type": user_input.get("window_type"),
                "opening_type": user_input.get("opening_type"),
                "shading": user_input.get("shading"),
            })
            return self.async_create_entry(title="", data={**self.config_entry.options, "rooms": rooms})
        return self.async_show_form(step_id="add_room", data_schema=self._room_schema())

    def _room_schema(self):
        return vol.Schema({
            vol.Required("name"): str,
            vol.Optional("temperature"): _entity(),
            vol.Optional("humidity"): _entity(),
            vol.Optional("co2"): _entity(),
            vol.Optional("area_m2"): vol.Coerce(float),
            vol.Optional("ceiling_height_m"): vol.Coerce(float),
            vol.Optional("window_area_m2"): vol.Coerce(float),
            vol.Optional("orientation"): vol.In(["N","NE","E","SE","S","SW","W","NW"]),
            vol.Optional("window_type"): vol.In(["tilt_turn","tilt","sliding","fixed","other"]),
            vol.Optional("opening_type"): vol.In(["single","cross","tilt"]),
            vol.Optional("shading"): vol.In(["none","partial","external","internal"]),
        })

    async def async_step_remove_room(self, user_input: dict | None = None):
        rooms = list(self.config_entry.options.get("rooms", []))
        choices = _room_options(self.config_entry.options)
        if user_input is not None:
            remove_id = user_input["room_id"]
            rooms = [room for room in rooms if room.get("room_id") != remove_id]
            return self.async_create_entry(title="", data={**self.config_entry.options, "rooms": rooms})
        if not choices:
            return self.async_abort(reason="no_rooms")
        return self.async_show_form(step_id="remove_room", data_schema=vol.Schema({
            vol.Required("room_id"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=choices, mode=selector.SelectSelectorMode.DROPDOWN))
        }))

    async def async_step_global_sources(self, user_input: dict | None = None):
        keys = ("outdoor_temperature", "outdoor_humidity", "weather_entity")
        if user_input is not None:
            return self.async_create_entry(title="", data={
                **self.config_entry.options,
                **{key: value for key, value in user_input.items() if value}
            })
        return self.async_show_form(step_id="global_sources", data_schema=vol.Schema({
            vol.Optional(key, default=self.config_entry.options.get(key)): _entity()
            for key in keys
        }))

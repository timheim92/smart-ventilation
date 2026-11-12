# Smart Ventilation

A modular Home Assistant integration for intelligent, room-based ventilation recommendations.

The integration is designed for different sensor configurations and interchangeable weather-data providers. Missing or outdated measurements remain unknown and are never replaced with invented values.

## Current status: early development

The first data-foundation iteration provides:

- A Home Assistant configuration flow and options page for selecting indoor/outdoor entities.
- Optional indoor CO2 and weather entity selection.
- A normalized measurement model with source, unit, timestamp, availability, and stale-data metadata.
- Validation of numeric readings, including rejection of non-numeric and non-finite states.
- A 30-minute initial freshness limit for numeric sensor entities.
- A current-weather adapter that preserves supported attributes when supplied by the selected Home Assistant weather entity.
- Status and measurement entities for diagnostics.

This version does **not** yet calculate ventilation recommendations, ingest weather forecasts, normalize all units, or control windows.

## Configuration

Add **Smart Ventilation** through Settings → Devices & services. Then open the integration's options to select the entities available in your installation. Leave optional or unavailable sensors empty.

## Planned capabilities

- Room-specific ventilation recommendations and explanations.
- Absolute humidity, dew point, CO2 and air-quality analysis.
- Forecast-aware seasonal logic, wind, precipitation, solar load and pollen/air-quality inputs where available.
- Replaceable provider adapters for different weather services.
- Optional motorized window control, disabled by default, confirmation-first and safety-checked.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/DATA_MODEL.md](docs/DATA_MODEL.md).

## Design principles

- No fabricated sensor values.
- Sensor and weather sources are replaceable.
- Core calculations are independent of sensor brands.
- Missing and stale data are visible to the user.
- Window actuation remains optional and safety-first.


## Multi-room support

The integration now supports an arbitrary number of independently configured rooms. Use the integration options to add or remove rooms and assign each room its own temperature, humidity, and optional CO2 entity. Outdoor temperature, outdoor humidity, and current weather remain shared global inputs. See [docs/ROOMS.md](docs/ROOMS.md).

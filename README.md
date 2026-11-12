# Smart Ventilation

A modular Home Assistant integration for intelligent, room-based ventilation recommendations.

The integration is designed to work with different sensor configurations and interchangeable weather-data providers. Missing or outdated measurements are treated as unknown and are never replaced with invented values.

## Planned capabilities

- Room-specific ventilation recommendations.
- Indoor and outdoor temperature, humidity, and (when available) CO2 and air-quality measurements.
- Weather forecasts, wind, precipitation, solar load, and seasonal logic.
- Recommendations for ventilation method, timing, and duration.
- Transparent data quality and explanation of each recommendation.
- Optional support for motorized window openers. Window control is opt-in, requires confirmation by default, and is subject to safety checks.

## Current status

**Early development – version 0.1.0 foundation.**

The current code provides the initial Home Assistant integration scaffold, configuration flow, coordinator, and a status entity. It does not yet calculate ventilation recommendations or control windows.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the planned architecture.

## Development

The integration is installed as a custom component in:

```text
custom_components/smart_ventilation/
```

After copying the repository into the Home Assistant `custom_components` directory, restart Home Assistant and add **Smart Ventilation** through Settings → Devices & services.

## Design principles

- No fabricated sensor values.
- Sensor and weather sources are replaceable.
- Core calculations are independent of specific sensor brands.
- Window actuation remains optional and safety-first.

# Architecture

## Design principles

- Sensor and weather providers are replaceable adapters.
- Rooms and windows are modeled independently of any specific hardware brand.
- Missing or stale measurements remain unknown; they are never replaced with fabricated values.
- Recommendations include data-quality and confidence information.
- Window actuation is optional, disabled by default, and requires explicit confirmation by default.
- Safety checks must be evaluated independently of user confirmation.

## Planned components

1. **Configuration and discovery** – map Home Assistant entities to indoor and outdoor measurements.
2. **Data providers** – normalize sensor and weather data from different integrations and services.
3. **Building model** – rooms, dimensions, windows, facade orientation, shading, and opening type.
4. **Calculation core** – humidity, dew point, indoor/outdoor comparisons, weather, wind, solar load, and seasonal behavior.
5. **Recommendation engine** – room-specific action, method, duration, rationale, and data quality.
6. **Window control** – optional actuator adapters, confirmation workflow, safety interlocks, and state verification.
7. **Presentation** – Home Assistant entities, diagnostics, and actionable notifications.

## Current implementation

Version 0.1.0 is only an integration scaffold. It creates a config entry and a status entity. It does not yet calculate or issue ventilation recommendations and does not control windows.

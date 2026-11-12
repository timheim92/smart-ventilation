# Smart Ventilation

A modular Home Assistant custom integration for room-level ventilation recommendations.

## Current development version: 0.2.0 beta foundation

This project is in active development. The current code provides multi-room sensor mapping, basic room/window metadata, sensor freshness checks, psychrometric calculations and conservative, explainable recommendations.

### Included

- Multiple rooms with independent temperature, humidity and optional CO2 sensors.
- Shared outdoor temperature/humidity and a current Home Assistant weather entity.
- Room floor area, ceiling height, calculated room volume, window area, orientation, window type, opening mode and shading metadata.
- Numeric validation, stale-data detection and Celsius normalization.
- Absolute humidity and dew point calculations.
- Room-level recommendation state, rationale, estimated duration, confidence, dew point and humidity entities.
- Binary sensor for current ventilation demand.
- Safety documentation and GitHub Actions checks.

### Important limitations

This is not yet a complete first release and must not control windows. The current recommendation algorithm is heuristic and does not calculate a certified air-change rate. Weather forecast ingestion, solar/pollen/outdoor air-quality forecasts, alternative provider adapters, actuator support and full Home Assistant integration tests are still outstanding. See [the beta scope](docs/V0.2_BETA_SCOPE.md) and [safety notes](docs/SAFETY_AND_LIMITATIONS.md).

## Setup

Install the repository as a custom integration only in a test Home Assistant instance after reviewing the beta scope. Copy `custom_components/smart_ventilation` into the Home Assistant `custom_components` directory, restart Home Assistant, then add Smart Ventilation under Settings → Devices & services.

After adding the integration, open its options to add rooms and select the available entities. Configure outdoor temperature, outdoor humidity and a current weather entity under global sources. Leave optional sensors unset when unavailable.

## Development

Run:

```bash
python -m compileall -q custom_components
pytest -q
ruff check custom_components tests
```

See [docs/ROOMS.md](docs/ROOMS.md), [docs/DATA_MODEL.md](docs/DATA_MODEL.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/V0.2_BETA_SCOPE.md](docs/V0.2_BETA_SCOPE.md).

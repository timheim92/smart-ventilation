# Smart Ventilation – V1 foundation and safety

## Six workstreams

1. Stability: CI and unit tests, numeric validation, stale-data detection and fail-safe missing-data behavior.
2. Recommendations: room CO₂/humidity demand, absolute humidity, dew point, seasonal thermal guidance and confidence labels.
3. Weather: current conditions and optional hourly forecast through Home Assistant's weather service. The adapter is isolated for future Open-Meteo/Ecowitt providers.
4. Building/facade: room volume, window metadata, orientation and advisory windward/leeward exposure. This does not calculate air exchange.
5. Passive learning: calculate observed before/after CO₂ and absolute-humidity changes for manually recorded ventilation events. No automatic training or certified air-change rate.
6. Actuator safety: fail-closed policy helper. Actual window control is not implemented and remains disabled.

## Safety and limitations

- This is advisory software, not a ventilation standard or building-physics simulation.
- Missing indoor/outdoor temperature or humidity prevents a recommendation.
- CO₂ is optional; without a CO₂ sensor no CO₂ value is inferred.
- Forecast fields differ between weather providers; unavailable values remain unknown.
- Wind direction is not a measurement of airflow; facade classification confidence remains low.
- Rain, wind and gust thresholds are conservative guardrails, not guarantees of safety.
- Window actuation is not called. A future implementation needs explicit opt-in and per-action confirmation, rain/wind/gust checks, real position feedback, timeouts, abort/close logic and an audit trail.
- Pollen, outdoor AQI, facade pressure coefficients, solar forecast and thermal mass are future model inputs.

# Data model and source handling

## Home Assistant sensor adapter

The first adapter reads selected numeric Home Assistant entities for indoor temperature, indoor relative humidity, optional indoor CO2, outdoor temperature, and outdoor relative humidity. A weather entity can also be selected; its currently available condition and supported attributes are passed through by a separate adapter.

Every numeric reading carries its source entity, unit, last-updated timestamp, availability, stale flag, and an explanatory reason. Non-numeric, infinite, missing, and stale readings are unavailable. No default measurement is fabricated.

The initial freshness threshold for numeric sensors is 30 minutes. It will become configurable and sensor-class aware in a later iteration. Weather attributes currently preserve the source entity's reported values and are not yet used in ventilation calculations.

## Normalized model

Measurement, RoomAirData, OutdoorAirData, and VentilationData form the provider-independent data contract. Additional providers should normalize their output to these types rather than coupling the calculation engine to vendor-specific entities.

## Current limitations

- One configured indoor sensor set and one outdoor sensor set per integration instance.
- Weather conditions and supported current attributes are exposed as source data only; forecast ingestion is not implemented.
- Values are currently passed through as reported; unit normalization and plausibility bounds are next.
- No ventilation recommendation is generated yet.

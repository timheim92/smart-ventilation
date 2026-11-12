# Safety, confidence and limitations

This is a recommendation beta, not a building-control system.

- A recommendation requires current indoor and outdoor temperature and relative humidity.
- CO2 is an additional trigger when configured; it is not a complete air-quality measurement.
- Absolute humidity and dew point use the Magnus approximation.
- Duration is a coarse heuristic, not a guaranteed air-change or ventilation-rate calculation.
- Weather checks use only attributes exposed by the selected Home Assistant weather entity. Missing rain/wind information is not interpreted as safe.
- This version does not control window actuators. Never use a recommendation state as an actuator command.
- Do not leave windows open unattended based only on this software. Consider security, children, pets, rain ingress, wind, and local building conditions.
- Future actuator support must require explicit confirmation by default, verify device capabilities and position feedback, and provide independent close/abort safety checks.
- This software does not diagnose mould, pollutants, or building defects.

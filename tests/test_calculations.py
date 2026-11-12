"""Tests for psychrometric calculations."""
from custom_components.smart_ventilation.calculations import absolute_humidity_g_m3, dew_point_c

def test_absolute_humidity_increases_with_relative_humidity():
    assert absolute_humidity_g_m3(20, 70) > absolute_humidity_g_m3(20, 40)

def test_dew_point_below_air_temperature():
    assert dew_point_c(20, 50) < 20

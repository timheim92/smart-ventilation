from custom_components.smart_ventilation.seasonal import season_for_month, thermal_guidance
from custom_components.smart_ventilation.facade import facade_exposure
from custom_components.smart_ventilation.learning import ventilation_observation
from custom_components.smart_ventilation.actuator_safety import evaluate_open_request

def test_seasons():
    assert season_for_month(7) == "summer"
    assert season_for_month(1) == "winter"
    assert season_for_month(4) == "transition"

def test_summer_thermal_advice_accounts_for_hot_outdoor_air():
    result = thermal_guidance(23, 30, 7, solar_w_m2=400)
    assert "wärmer" in result["advice"]
    assert result["season"] == "summer"

def test_facade_exposure_is_advisory():
    result = facade_exposure("N", 0)
    assert result["exposure"] == "windward"
    assert result["confidence"] == "low"

def test_facade_unknown_when_inputs_missing():
    assert facade_exposure("N", None)["exposure"] == "unknown"

def test_learning_computes_observed_co2_reduction():
    result = ventilation_observation(1400, 700, 10.0, 8.0, 8)
    assert result["valid"]
    assert result["co2_reduction_ppm"] == 700
    assert result["absolute_humidity_reduction_g_m3"] == 2.0

def test_learning_rejects_missing_observations():
    assert not ventilation_observation(None, None, None, None, 5)["valid"]

def test_actuator_is_disabled_by_default():
    result = evaluate_open_request(enabled=False, confirmed=True, rain=False,
        wind_speed=2, gust_speed=4)
    assert not result["allowed"]
    assert result["reason"] == "actuation_disabled"

def test_actuator_fails_closed_on_unknown_weather():
    result = evaluate_open_request(enabled=True, confirmed=True, rain=None,
        wind_speed=2, gust_speed=4)
    assert not result["allowed"]

def test_actuator_requires_confirmation_and_safe_weather():
    assert not evaluate_open_request(enabled=True, confirmed=False, rain=False,
        wind_speed=2, gust_speed=4)["allowed"]
    assert evaluate_open_request(enabled=True, confirmed=True, rain=False,
        wind_speed=2, gust_speed=4)["allowed"]

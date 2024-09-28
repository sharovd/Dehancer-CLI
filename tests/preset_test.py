import pytest
from pytest import param as test_data  # noqa: PT013

from src.api.models.preset import PresetSettings, PresetSettingsState


@pytest.mark.unit
@pytest.mark.parametrize(("preset_state", "expected_str"), [
    test_data(PresetSettingsState.OFF, "Off", id="'OFF' state"),
    test_data(PresetSettingsState.from_value(0), "0.0", id="'0' state"),
    test_data(PresetSettingsState.from_value(1), "1.0", id="'1' state"),
    test_data(PresetSettingsState.from_value(2.2), "2.2", id="'2.2' state"),
    test_data(PresetSettingsState.from_value(3.125), "3.125", id="'3.125' state"),
    test_data(PresetSettingsState.from_value(-2), "-2.0", id="'-2' state"),
    test_data(PresetSettingsState.from_value(-3.5), "-3.5", id="'-3.5' state"),
    test_data(PresetSettingsState.from_value(-4.854), "-4.854", id="'-4.854' state"),
])
def test_preset_state_str_returns_off_or_float_value_as_string(preset_state: PresetSettingsState, expected_str: str):
    # Act: perform method under test
    actual_str = str(preset_state)
    # Assert: check that the method result contains the expected result
    assert actual_str == expected_str


@pytest.mark.unit
@pytest.mark.parametrize(("settings_a", "settings_b", "expected_equal"), [
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        True, id="Equal settings",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(1, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different exposure",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 1, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different contrast",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 1, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different temperature",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 1, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different tint",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 1,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different color boost",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different grain",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, 0, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different bloom",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, 0,
                       PresetSettingsState.OFF, 55, 15),
        False, id="Different halation",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       1, 55, 15),
        False, id="Different vignette exposure",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 60, 15),
        False, id="Different vignette size",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 25),
        False, id="Different vignette feather",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        "PresetSettings",
        False, id="Different type (str)",  # noqa: FBT003
    ),
    test_data(
        PresetSettings(0, 0, 0, 0, 0,
                       PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                       PresetSettingsState.OFF, 55, 15),
        None,
        False, id="Different type (None)",  # noqa: FBT003
    ),
])
def test_preset_settings_eq_returns_true_or_false(settings_a: PresetSettings, settings_b: PresetSettings,
                                                  expected_equal: bool):  # noqa: FBT001
    # Act: perform method under test
    actual_equal = settings_a == settings_b
    # Assert: check that the method result contains the expected result
    assert actual_equal == expected_equal


@pytest.mark.unit
@pytest.mark.parametrize(("preset_settings", "expected_str"), [
    test_data(PresetSettings.default(),
              ("Exposure: '0.0', Contrast: '0.0', Temperature: '0.0', Tint: '0.0', Color boost: '0.0'\n"
               "Grain: 'Off', Bloom: 'Off', Halation: 'Off'\n"
               "Vignette exposure: 'Off', size: '55.0', feather: '15.0'"), id="Default preset settings"),
    test_data(PresetSettings(0.1, -0.2, 1.125, 2.3, -4,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55, 15),
              ("Exposure: '0.1', Contrast: '-0.2', Temperature: '1.125', Tint: '2.3', Color boost: '-4'\n"
               "Grain: 'Off', Bloom: 'Off', Halation: 'Off'\n"
               "Vignette exposure: 'Off', size: '55', feather: '15'"),
              id="Custom preset settings - only adjustments"),
    test_data(PresetSettings(0, 0, 0, 0, 0, 10, -20, 30.5, -2, 44.2, 18),
              ("Exposure: '0', Contrast: '0', Temperature: '0', Tint: '0', Color boost: '0'\n"
               "Grain: '10', Bloom: '-20', Halation: '30.5'\n"
               "Vignette exposure: '-2', size: '44.2', feather: '18'"),
              id="Custom preset settings - only effects"),
    test_data(PresetSettings(-0.2, 2.4, 2, 0, 0, 90, 20.250, -5.25, 1.4, 32.2, 38.8),
              ("Exposure: '-0.2', Contrast: '2.4', Temperature: '2', Tint: '0', Color boost: '0'\n"
               "Grain: '90', Bloom: '20.25', Halation: '-5.25'\n"
               "Vignette exposure: '1.4', size: '32.2', feather: '38.8'"),
              id="Custom preset settings - adjustments and effects"),
])
def test_preset_settings_repr_returns_string_representation_of_preset_settings(preset_settings: PresetSettings,
                                                                               expected_str: str):
    # Act: perform method under test
    actual_repr = repr(preset_settings)
    # Assert: check that the method result contains the expected result
    assert actual_repr == expected_str


@pytest.mark.unit
@pytest.mark.parametrize(("preset_settings", "expected_str"), [
    test_data(PresetSettings.default(),
              "Exposure: '0.0', Contrast: '0.0', Temperature: '0.0', Tint: '0.0', Color boost: '0.0'",
              id="Default preset settings adjustments"),
    test_data(PresetSettings(0.1, -0.2, 1.125, 2.3, -4,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55, 15),
              "Exposure: '0.1', Contrast: '-0.2', Temperature: '1.125', Tint: '2.3', Color boost: '-4'",
              id="Custom preset settings adjustments"),
])
def test_preset_settings_get_adjustments_str_returns_string_representation_of_adjustments(
        preset_settings: PresetSettings, expected_str: str):
    # Act: perform method under test
    actual_str = preset_settings.get_adjustments_str()
    # Assert: check that the method result contains the expected result
    assert actual_str == expected_str


@pytest.mark.unit
@pytest.mark.parametrize(("preset_settings", "expected_str"), [
    test_data(PresetSettings.default(),
              "Grain: 'Off', Bloom: 'Off', Halation: 'Off', "
              "Vignette exposure: 'Off', Vignette size: '55.0', Vignette feather: '15.0'",
              id="Default preset settings effects"),
    test_data(PresetSettings(0, 0, 0, 0, 0, 10, -20, 30.5, -1.2, 45, 10),
              "Grain: '10', Bloom: '-20', Halation: '30.5', "
              "Vignette exposure: '-1.2', Vignette size: '45', Vignette feather: '10'",
              id="Custom preset settings effects"),
])
def test_preset_settings_get_effects_str_returns_string_representation_of_effects(preset_settings: PresetSettings,
                                                                                  expected_str: str):
    # Act: perform method under test
    actual_str = preset_settings.get_effects_str()
    # Assert: check that the method result contains the expected result
    assert actual_str == expected_str

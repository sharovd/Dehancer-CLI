from unittest.mock import patch

import pytest

from src.api.enums import ExportFormat, ImageQuality, UnknownImageQualityError


@pytest.mark.unit
@pytest.mark.parametrize(("label", "expected_result"), [
    ("low", ImageQuality.LOW),
    ("Low", ImageQuality.LOW),
    ("LoW", ImageQuality.LOW),
    ("LOW", ImageQuality.LOW),
    (" low ", ImageQuality.LOW),
    (" low", ImageQuality.LOW),
    (" low  ", ImageQuality.LOW),
    ("medium", ImageQuality.MEDIUM),
    ("Medium", ImageQuality.MEDIUM),
    ("MeDiUm", ImageQuality.MEDIUM),
    ("MEDIUM", ImageQuality.MEDIUM),
    (" medium ", ImageQuality.MEDIUM),
    (" medium", ImageQuality.MEDIUM),
    (" medium  ", ImageQuality.MEDIUM),
    ("high", ImageQuality.HIGH),
    ("High", ImageQuality.HIGH),
    ("HiGh", ImageQuality.HIGH),
    ("HIGH", ImageQuality.HIGH),
    (" high ", ImageQuality.HIGH),
    (" high", ImageQuality.HIGH),
    (" high  ", ImageQuality.HIGH),
])
def test_image_quality_from_string_for_valid_data_returns_image_quality_enum(label: str, expected_result: ImageQuality):
    # Act: perform method under test
    actual_result = ImageQuality.from_string(label)
    # Assert: check that the method result contains the expected result
    assert actual_result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize("label", [
    "invalid", "LOWER", "mAx", "medium-high", "loww", "mmedium", "high h",
])
def test_image_quality_from_string_for_invalid_data_raises_unknown_image_quality_error(label: str):
    # Assert: check that the expected failure caused by the tested method
    with pytest.raises(UnknownImageQualityError, match=f"Unknown quality level: {label}"):
        # Act: perform method under test
        ImageQuality.from_string(label)


@pytest.mark.unit
@pytest.mark.parametrize(("export_format", "expected_result"), [
    (ExportFormat.WEB, ImageQuality.LOW),
    (ExportFormat.JPEG, ImageQuality.MEDIUM),
    (ExportFormat.TIFF, ImageQuality.HIGH),
])
def test_image_quality_from_export_format_for_valid_data_returns_image_quality_enum(export_format: ExportFormat,
                                                                                    expected_result: ImageQuality):
    # Act: perform method under test
    actual_result = ImageQuality.from_export_format(export_format)
    # Assert: check that the method result contains the expected result
    assert actual_result == expected_result


@pytest.mark.unit
def test_image_quality_from_export_format_for_invalid_data_raises_unknown_image_quality_error():
    with patch.object(ExportFormat, "_value2member_map_", {**ExportFormat._value2member_map_, "custom": "CUSTOM"}):
        export_format = ExportFormat("custom")
        # Assert: check that the expected failure caused by the tested method
        with pytest.raises(UnknownImageQualityError, match=f"Unknown quality level: {export_format}"):
            # Act: perform method under test
            ImageQuality.from_export_format(export_format)

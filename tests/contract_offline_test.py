import pytest
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from src.api.contracts.image_export import ImageExportModel
from src.api.contracts.image_previews import ImagePreviewsModel
from src.api.contracts.image_render import ImageRenderModel
from src.api.contracts.image_upload_prepare import ImageUploadPrepareModel
from src.api.contracts.login_with_email_and_password import LoginWithEmailAndPasswordModel
from src.api.contracts.presets import EXPECTED_NUMBER_OF_PRESETS, PresetsResponseModel
from tests.data.api_mock_responses.image_export import image_export_not_success_response, image_export_success_response
from tests.data.api_mock_responses.image_previews import (
    image_previews_not_success_response,
    image_previews_success_response,
)
from tests.data.api_mock_responses.image_render import image_render_not_success_response, image_render_success_response
from tests.data.api_mock_responses.image_upload_prepare import (
    image_upload_prepare_multipart_success_response,
    image_upload_prepare_not_success_response,
    image_upload_prepare_regular_success_response,
)
from tests.data.api_mock_responses.login_with_email_and_password import (
    login_with_email_and_password_not_success_response,
    login_with_email_and_password_success_response,
)
from tests.data.api_mock_responses.presets import presets_not_success_response, presets_success_response


@pytest.mark.unit
@pytest.mark.contract
def test_presets_mock_success_response_is_valid():
    # Assert: the success mock response payload conforms to the PresetsResponseModel contract
    PresetsResponseModel.model_validate(presets_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_presets_mock_not_success_response_is_valid():
    # Arrange: define expected values
    expected_number_of_errors = 2
    with pytest.raises(ValidationError) as validation_error:
        # Act: the unsuccessful mock response payload conforms to the PresetsResponseModel contract
        PresetsResponseModel.model_validate(presets_not_success_response)
    errors = validation_error.value.errors()
    # Assert: check that the validation result contains the expected data
    assert len(errors) == expected_number_of_errors
    # Get validation errors for the 'presets' and 'presetSections' fields
    presets_errors = [e for e in errors if e.get("loc") and e["loc"][0] == "presets"]
    sections_errors = [e for e in errors if e.get("loc") and e["loc"][0] == "presetSections"]
    # Assert: check that the validation result for 'presets' field contains the expected data
    presets_msgs = " | ".join(e.get("msg", "") for e in presets_errors)
    assert f"The expected number of presets is '{EXPECTED_NUMBER_OF_PRESETS}'" in presets_msgs
    # Assert: check that the validation result for 'presetSections' field contains the expected data
    sections_msgs = " | ".join(e.get("msg", "") for e in sections_errors)
    assert "The field 'presetSections' does not match the expected contract" in sections_msgs


@pytest.mark.unit
@pytest.mark.contract
def test_login_with_email_and_password_mock_success_response_is_valid():
    # Assert: the success mock response payload conforms to the LoginWithEmailAndPasswordModel contract
    LoginWithEmailAndPasswordModel.model_validate(login_with_email_and_password_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_login_with_email_and_password_mock_not_success_response_is_valid():
    # Assert: the unsuccessful mock response payload conforms to the LoginWithEmailAndPasswordModel contract
    LoginWithEmailAndPasswordModel.model_validate(login_with_email_and_password_not_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_upload_prepare_regular_mock_success_response_is_valid():
    # Assert: the success mock response (single-part) payload conforms to the ImageUploadPrepareModel contract
    ImageUploadPrepareModel.model_validate(image_upload_prepare_regular_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_upload_prepare_multipart_mock_success_response_is_valid():
    # Assert: the success mock response (multipart) payload conforms to the ImageUploadPrepareModel contract
    ImageUploadPrepareModel.model_validate(image_upload_prepare_multipart_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_upload_prepare_mock_not_success_response_is_valid():
    # Arrange: define expected values
    expected_number_of_errors = 1
    with pytest.raises(ValidationError) as validation_error:
        # Act: the unsuccessful mock response payload conforms to the ImageUploadPrepareModel contract
        ImageUploadPrepareModel.model_validate(image_upload_prepare_not_success_response)
    errors = validation_error.value.errors()
    # Assert: check that the validation result contains the expected data
    assert len(errors) == expected_number_of_errors
    __assert_fields_required_validation(errors, ["imageId"])


@pytest.mark.unit
@pytest.mark.contract
def test_image_render_mock_success_response_is_valid():
    # Act: the success mock response payload conforms to the ImageRenderModel contract
    ImageRenderModel.model_validate(image_render_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_render_mock_not_success_response_is_valid():
    # Arrange: define expected values
    expected_number_of_errors = 2
    with pytest.raises(ValidationError) as validation_error:
        # Act: the unsuccessful mock response payload conforms to the ImageRenderModel contract
        ImageRenderModel.model_validate(image_render_not_success_response)
    errors = validation_error.value.errors()
    # Assert: check that the validation result contains the expected data
    assert len(errors) == expected_number_of_errors
    __assert_fields_required_validation(errors, ["imageId", "url"])


@pytest.mark.unit
@pytest.mark.contract
def test_image_previews_mock_success_response_is_valid():
    # Act: the success mock response payload conforms to the ImagePreviewsModel contract
    ImagePreviewsModel.model_validate(image_previews_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_previews_mock_not_success_response_is_valid():
    # Arrange: define expected values
    expected_number_of_errors = 1
    with pytest.raises(ValidationError) as validation_error:
        # Act: the unsuccessful mock response payload conforms to the ImagePreviewsModel contract
        ImagePreviewsModel.model_validate(image_previews_not_success_response)
    errors = validation_error.value.errors()
    # Assert: check that the validation result contains the expected data
    assert len(errors) == expected_number_of_errors
    __assert_fields_required_validation(errors, ["images"])


@pytest.mark.unit
@pytest.mark.contract
def test_image_export_mock_success_response_is_valid():
    # Act: the success mock response payload conforms to the ImageExportModel contract
    ImageExportModel.model_validate(image_export_success_response)


@pytest.mark.unit
@pytest.mark.contract
def test_image_export_mock_not_success_response_is_valid():
    # Arrange: define expected values
    expected_number_of_errors = 4
    with pytest.raises(ValidationError) as validation_error:
        # Act: the unsuccessful mock response payload conforms to the ImageExportModel contract
        ImageExportModel.model_validate(image_export_not_success_response)
    errors = validation_error.value.errors()
    # Assert: check that the validation result contains the expected data
    assert len(errors) == expected_number_of_errors
    __assert_fields_required_validation(errors, ["url", "imageId", "lastImage", "filename"])


def __assert_fields_required_validation(errors: list[ErrorDetails], fields_to_check: list[str]) -> None:
    # Assert: check that the validation result for fields contains the expected data
    errors_by_field: dict[str, list] = {}
    for err in errors:
        loc = err.get("loc")
        if not loc:
            continue
        errors_by_field.setdefault(loc[0], []).append(err)
    for field in fields_to_check:
        field_errors = errors_by_field.get(field, [])
        msgs = " | ".join(e.get("msg", "") for e in field_errors)
        assert "Field required" in msgs, f"Expected 'Field required' in {field} errors, got: {msgs or 'no errors'}"

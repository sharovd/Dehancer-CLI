from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from secrets import choice
from unittest.mock import MagicMock, Mock, patch

import pytest
from pytest import param as test_data  # noqa: PT013

from src import utils
from src.api.clients.dehancer_online_client import DehancerOnlineAPIClient
from src.api.constants import (
    BASE_HEADERS,
    HEADER_JSON_CONTENT_TYPE,
    HEADER_TRANSFER_ENCODING_TRAILERS,
    SECURITY_HEADERS,
)
from src.api.enums import ExportFormat, ImageSize
from src.api.models.preset import Preset, PresetSettings, PresetSettingsState
from src.cache.cache_keys import ACCESS_TOKEN, AUTH, PRESETS
from tests.data.api_mock_responses.image_export import (
    image_export_invalid_response,
    image_export_not_success_response,
    image_export_success_response,
)
from tests.data.api_mock_responses.image_previews import (
    image_previews_invalid_response,
    image_previews_not_success_response,
    image_previews_success_response,
)
from tests.data.api_mock_responses.image_render import (
    image_render_invalid_response,
    image_render_not_success_response,
    image_render_success_response,
)
from tests.data.api_mock_responses.image_upload_prepare import (
    image_upload_prepare_invalid_response,
    image_upload_prepare_multipart_success_response,
    image_upload_prepare_not_success_response,
    image_upload_prepare_regular_success_response,
)
from tests.data.api_mock_responses.login_with_email_and_password import (
    login_with_email_and_password_invalid_response,
    login_with_email_and_password_not_success_response,
    login_with_email_and_password_success_headers,
    login_with_email_and_password_success_response,
)
from tests.data.api_mock_responses.presets import (
    presets_invalid_response,
    presets_not_success_response,
    presets_success_response,
)


@pytest.fixture
def mock_requests_session_get() -> MagicMock:
    with patch("requests.Session.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_cache_manager() -> MagicMock:
    mock_cache_manager = Mock()
    mock_cache_manager.get.return_value = None
    return mock_cache_manager


@pytest.fixture
def mock_api_client(mock_cache_manager: MagicMock) -> DehancerOnlineAPIClient:
    return DehancerOnlineAPIClient("https://mock.com/api/v1", mock_cache_manager)


@pytest.fixture
def image_path() -> str:
    return "path/to/image.jpg"


def generate_presets(count: int) -> list[Preset]:
    captions = [f"Preset {i}" for i in range(1, count + 1)]
    return [Preset(caption=caption, creator="Test", preset=f"preset_{i}",
                   exposure=0.5, contrast=0.5, temperature=10, tint=0.2, color_boost=0.1,
                   is_bloom_enabled=True, bloom=0.5, is_halation_enabled=True, halation=0.5,
                   is_grain_enabled=True, grain=0.1,
                   is_vignette_enabled=False,
                   vignette_exposure=-1.2, vignette_feather=15, vignette_size=55)
            for i, caption in enumerate(captions, 1)]


@pytest.mark.unit
def test_login_success(mock_api_client: DehancerOnlineAPIClient, mock_cache_manager: MagicMock):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__login_with_email_and_password",
                      return_value=Mock(headers=login_with_email_and_password_success_headers,
                                        text=json.dumps(login_with_email_and_password_success_response))) as mock_post:
        mock_cookies = login_with_email_and_password_success_headers.get("set-cookie").split("; ")
        expected_auth_data = {}
        for mock_cookie in mock_cookies:
            if mock_cookie.startswith("access-token="):
                expected_auth_data[ACCESS_TOKEN] = mock_cookie.split("=", 1)[1]
            if mock_cookie.startswith("Secure, auth="):
                expected_auth_data[AUTH] = mock_cookie.split("=", 1)[1]
        email = "test@test.com"
        password = "test"  # noqa: S105
        # Act: perform method under test
        result = mock_api_client.login(email, password)
        # Assert: check that the expected method have been called by the tested method
        mock_post.assert_called_once_with(email, password)
        # Assert: check that the method result contains the expected data
        assert result is True
        # Assert: check that the method calls expected method to set cache
        for key, value in expected_auth_data.items():
            mock_cache_manager.set.assert_any_call(key, value)


@pytest.mark.unit
def test_login_success_wo_cookies(mock_api_client: DehancerOnlineAPIClient, mock_cache_manager: MagicMock):
    login_with_email_and_password_success_headers.pop("set-cookie")
    login_with_email_and_password_headers_wo_cookies = login_with_email_and_password_success_headers
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__login_with_email_and_password",
                      return_value=Mock(headers=login_with_email_and_password_headers_wo_cookies,
                                        text=json.dumps(login_with_email_and_password_success_response))) as mock_post:
        email = "test@test.com"
        password = "test"  # noqa: S105
        # Act: perform method under test
        result = mock_api_client.login(email, password)
        # Assert: check that the expected method have been called by the tested method
        mock_post.assert_called_once_with(email, password)
        # Assert: check that the method result contains the expected data
        assert result is False
        # Assert: check that the method does not call expected method to set cache
        mock_cache_manager.set.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(("auth_cookies", "expected_result"), [
    test_data({"access-token": "valid_token", "auth": "valid_auth_value"}, True,  # noqa: FBT003
              id="Authorized if access-token and auth are present"),
    test_data({"access-token": "valid_token"}, True,  # noqa: FBT003
              id="Authorized if only access-token is present"),
    test_data({"auth": "valid_auth_value"}, False,  # noqa: FBT003
              id="Unauthorized if only auth is present"),
    test_data({}, False, id="Unauthorized if empty data: {}"),  # noqa: FBT003
    test_data(None, False, id="Unauthorized if empty data: None"),  # noqa: FBT003
])
def test_is_authorized_returns_auth_state_as_bool_value(mock_api_client: DehancerOnlineAPIClient,
                                                        auth_cookies: dict[str, str], expected_result: bool):  # noqa: FBT001
    # Arrange: setup mock object
    mock_api_client.set_session_cookies(auth_cookies)
    # Act: perform method under test
    is_authorized = mock_api_client.is_authorized
    # Assert: check that the method result contains the expected data
    assert is_authorized == expected_result


@pytest.mark.unit
def test_login_not_success(mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    with (patch.object(mock_api_client, "_DehancerOnlineAPIClient__login_with_email_and_password",
                       return_value=Mock(text=json.dumps(login_with_email_and_password_not_success_response)))
          as mock_post):
        email = "test@test.com"
        password = "test"  # noqa: S105
        # Act: perform method under test
        result = mock_api_client.login(email, password)
        # Assert: check that the expected method have been called by the tested method
        mock_post.assert_called_once_with(email, password)
        # Assert: check that the method result contains the expected data
        assert result is False


@pytest.mark.unit
def test_login_failure(mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__login_with_email_and_password",
                      return_value=Mock(text=json.dumps(login_with_email_and_password_invalid_response))):
        email = "test@test.com"
        password = "test"  # noqa: S105
        # Act: perform method under test
        result = mock_api_client.login(email, password)
        # Assert: check that the method result contains no data and that no logs has been printed
        assert result is False


@pytest.mark.unit
def test_get_available_presets_from_api_success(mock_requests_session_get: MagicMock,
                                                mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = json.dumps(presets_success_response)
    mock_requests_session_get.return_value = mock_response
    expected_number_of_presets = 62
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected API method have been called by the tested method
    mock_requests_session_get.assert_called_once_with("https://mock.com/api/v1/presets")
    # Assert: check that the method result contains the expected data
    assert len(result) == expected_number_of_presets
    assert result[0].caption == "Adox Color Implosion 100"
    assert result[1].caption == "Agfa Agfacolor 100"
    assert all(isinstance(p, Preset) for p in result)


@pytest.mark.unit
def test_get_available_presets_from_api_added_cache_success(mock_requests_session_get: MagicMock,
                                                            mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = json.dumps(presets_success_response)
    mock_requests_session_get.return_value = mock_response
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected cache method have been called by the tested method
    mock_api_client.cache_manager.set.assert_called_once_with(PRESETS, result)


@pytest.mark.unit
def test_get_available_presets_from_cache_success(mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    available_presets = [Preset(**preset) for preset in presets_success_response["presets"]]
    mock_api_client.cache_manager.get.return_value = sorted(available_presets, key=lambda p: p.caption)
    expected_number_of_presets = 62
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected cache method have been called by the tested method
    mock_api_client.cache_manager.get.assert_any_call(PRESETS)
    # Assert: check that the method result contains the expected data
    assert len(result) == expected_number_of_presets
    assert result[0].caption == "AGFA Chrome RSX II 200 (Exp. 2006)"
    assert result[1].caption == "Adox Color Implosion 100"
    assert all(isinstance(p, Preset) for p in result)


@pytest.mark.unit
def test_get_available_presets_from_api_not_success(mock_requests_session_get: MagicMock,
                                                    mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = json.dumps(presets_not_success_response)
    mock_requests_session_get.return_value = mock_response
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected method have been called by the tested method
    mock_requests_session_get.assert_called_once_with("https://mock.com/api/v1/presets")
    # Assert: check that the method result contains no data
    assert len(result) == 0


@pytest.mark.unit
def test_get_available_presets_from_api_failure(mock_requests_session_get: MagicMock,
                                                mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = presets_invalid_response
    mock_requests_session_get.return_value = mock_response
    # Assert: check that the expected failure caused by the tested method
    with pytest.raises(json.JSONDecodeError):
        # Act: perform method under test
        mock_api_client.get_available_presets()


@pytest.mark.unit
def test_upload_regular_image_success(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_prepare",
                         return_value=Mock(text=json.dumps(image_upload_prepare_regular_success_response))), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_put"), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_finish"), \
            patch.object(utils, "is_file_exist", return_value=True), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Act: perform method under test
        result = mock_api_client.upload_image(image_path)
        # Assert: check that the method result contains the expected data
        expected_image_id = image_upload_prepare_regular_success_response.get("imageId")
        assert result == expected_image_id
        # Assert: check that the expected message has been printed in the logs
        mock_logger.debug.assert_any_call("Upload image...")
        mock_logger.debug.assert_any_call("Image was uploaded, id is '%s'", expected_image_id)


@pytest.mark.unit
def test_upload_multipart_image_success(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_prepare",
                         return_value=Mock(text=json.dumps(image_upload_prepare_multipart_success_response))), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_put_multipart",
                         return_value=[
                             Mock(headers={"ETag": "etag-1"}),
                             Mock(headers={"ETag": "etag-2"}),
                         ]), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_finish_multipart"), \
            patch.object(utils, "is_file_exist", return_value=True), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Act: perform method under test
        result = mock_api_client.upload_image(image_path)
        # Assert: check that the method result contains the expected data
        expected_image_id = image_upload_prepare_multipart_success_response.get("imageId")
        assert result == expected_image_id
        # Assert: check that the expected multipart logic was triggered
        mock_api_client._DehancerOnlineAPIClient__image_put_multipart.assert_called_once_with(  # noqa: SLF001
            image_upload_prepare_multipart_success_response["urls"], image_path,
            image_upload_prepare_multipart_success_response["chunkSize"],
        )
        mock_api_client._DehancerOnlineAPIClient__image_upload_finish_multipart.assert_called_once_with(  # noqa: SLF001
            image_upload_prepare_multipart_success_response["imageId"],
            image_upload_prepare_multipart_success_response["uploadId"], ["etag-1", "etag-2"],
            Path(image_path).name,
        )
        # Assert: check that the expected message has been printed in the logs
        mock_logger.debug.assert_any_call("Upload image...")
        mock_logger.debug.assert_any_call("Image was uploaded, id is '%s'", expected_image_id)


@pytest.mark.unit
def test_upload_image_file_not_success(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_prepare",
                         return_value=Mock(text=json.dumps(image_upload_prepare_not_success_response))), \
            patch.object(utils, "is_file_exist", return_value=True), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Act: perform method under test
        result = mock_api_client.upload_image(image_path)
        # Assert: check that the method result contains no data
        assert result is None
        # Assert: check that the expected message has been printed in the logs
        mock_logger.debug.assert_any_call("Upload image...")
        assert "Image was uploaded" not in [call[0][0] for call in mock_logger.debug.call_args_list]


@pytest.mark.unit
def test_upload_image_file_failure(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_upload_prepare",
                         return_value=Mock(text=image_upload_prepare_invalid_response)), \
            patch.object(utils, "is_file_exist", return_value=True), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.upload_image(image_path)


@pytest.mark.unit
def test_upload_image_invalid_file(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=False), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Act: perform method under test
        result = mock_api_client.upload_image(image_path)
        # Assert: check that the method result contains no data and that no logs has been printed
        assert result is None
        mock_logger.debug.assert_not_called()


@pytest.mark.unit
def test_upload_image_file_not_exist(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(utils, "is_file_exist", side_effect=FileNotFoundError), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Assert: check that the expected failure caused by the tested method
        with pytest.raises(FileNotFoundError):
            # Act: perform method under test
            mock_api_client.upload_image(image_path)
        # Assert: check that no logs has been printed
        mock_logger.debug.assert_not_called()


@pytest.mark.unit
def test_get_image_previews_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_previews_success_response))) as mock_post:
        # Act: perform method under test
        result = mock_api_client.get_image_previews(image_id, image_size, presets)
        expected_payload = json.dumps({
            "imageId": image_id,
            "size": image_size.value,
            "states": [asdict(preset) for preset in presets],
        })
        expected_headers = BASE_HEADERS.copy()
        expected_headers.update({
            "TE": HEADER_TRANSFER_ENCODING_TRAILERS,
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        expected_headers.update(SECURITY_HEADERS)
        # Assert: check that the expected request has been sent by the tested method
        mock_post.assert_called_once_with(f"{mock_api_client.api_base_url}/image/previews/{image_id}",
                                          headers=expected_headers, data=expected_payload)
        # Assert: check that the method result contains the expected data
        assert result == {f"Preset {i}": link for i, link in zip(range(1, 63),
                                                                 image_previews_success_response["images"])}


@pytest.mark.unit
def test_get_image_previews_not_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_previews_not_success_response))):
        # Act: perform method under test
        result = mock_api_client.get_image_previews(image_id, image_size, presets)
        # Assert: check that the method result contains no data
        assert result == {}


@pytest.mark.unit
def test_get_image_previews_failure(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(status_code=500, text=image_previews_invalid_response)), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.get_image_previews(image_id, image_size, presets)


@pytest.mark.unit
@pytest.mark.parametrize("preset_settings", [
    test_data(None, id="Without settings"),
    test_data(PresetSettings.default(), id="Default settings"),
    test_data(
        PresetSettings(exposure=1.5, contrast=3.5, temperature=-15, tint=1, color_boost=3,
                       grain=4.1, bloom=4.5, halation=2.2,
                       vignette_exposure=-1.4, vignette_size=1.2, vignette_feather=12), id="Custom settings"),
])
def test_render_image_success(mock_api_client: DehancerOnlineAPIClient, preset_settings: PresetSettings):
    image_id = "123"
    preset = choice(generate_presets(62))
    state = {"preset": preset.preset}
    if preset_settings:
        state.update({key: value for key, value in asdict(preset_settings).items() if value != PresetSettingsState.OFF})
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_render_success_response))) as mock_post:
        # Act: perform method under test
        result = mock_api_client.render_image(image_id, preset, preset_settings)
        if preset_settings is None:
            state.update({key: value for key, value in asdict(PresetSettings.default()).items()
                          if value != PresetSettingsState.OFF})
        expected_payload_dict = {
            "imageId": image_id,
            "state": state,
        }
        actual_payload_dict = json.loads(mock_post.call_args[1]["data"])
        # Assert: check that the expected request has been sent by the tested method
        mock_post.assert_called_once_with(f"{mock_api_client.api_base_url}/image/render/{image_id}",
                                          headers=mock_post.call_args[1]["headers"],
                                          data=mock_post.call_args[1]["data"])
        # Assert: compare the actual and expected payload dictionaries
        assert actual_payload_dict == expected_payload_dict
        # Assert: check that the method result contains the expected data
        assert result == image_render_success_response["url"]


@pytest.mark.unit
def test_render_image_not_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings.default()
    state = {**asdict(preset), **asdict(preset_settings)}
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_render_not_success_response))):
        # Act: perform method under test
        result = mock_api_client.render_image(image_id, preset, preset_settings)
        # Assert: check that the method result contains no data
        assert result is None


@pytest.mark.unit
def test_render_failure(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings.default()
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(status_code=500, text=image_render_invalid_response)), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.render_image(image_id, preset, preset_settings)


@pytest.mark.unit
@pytest.mark.parametrize("preset_settings", [
    test_data(PresetSettings.default(), id="Default settings"),
    test_data(
        PresetSettings(exposure=1.5, contrast=3.5, temperature=-15, tint=1, color_boost=3,
                       bloom=4.5, halation=2.2, grain=4.1,
                       vignette_exposure=-0.2, vignette_size=60.5, vignette_feather=38), id="Custom settings"),
])
def test_export_image_success(mock_api_client: DehancerOnlineAPIClient, preset_settings: PresetSettings):
    image_id = "123"
    preset = choice(generate_presets(62))
    state = {"preset": preset.preset}
    state.update({key: value for key, value in asdict(preset_settings).items() if value != PresetSettingsState.OFF})
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    export_format = choice(list(ExportFormat))
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_export_success_response))) as mock_post:
        # Act: perform method under test
        result = mock_api_client.export_image(image_id, preset, export_format, preset_settings)
        expected_payload_dict = {
            "format": export_format.value,
            "imageId": image_id,
            "state": state,
        }
        actual_payload_dict = json.loads(mock_post.call_args[1]["data"])
        # Assert: check that the expected request has been sent by the tested method
        mock_post.assert_called_once_with(f"{mock_api_client.api_base_url}/image/export/{image_id}",
                                          headers=mock_post.call_args[1]["headers"],
                                          data=mock_post.call_args[1]["data"])
        # Assert: compare the actual and expected payload dictionaries
        assert actual_payload_dict == expected_payload_dict
        # Assert: check that the method result contains the expected data
        assert result == {"url": image_export_success_response["url"],
                          "filename": image_export_success_response["filename"]}


@pytest.mark.unit
def test_export_image_not_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings.default()
    state = {**asdict(preset), **asdict(preset_settings)}
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    export_format = choice(list(ExportFormat))
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(image_export_not_success_response))):
        # Act: perform method under test
        result = mock_api_client.export_image(image_id, preset, export_format, preset_settings)
        # Assert: check that the method result contains no data
        assert result == {"url": None, "filename": None}


@pytest.mark.unit
def test_export_failure(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings.default()
    export_format = choice(list(ExportFormat))
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(status_code=500, text=image_export_invalid_response)), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.export_image(image_id, preset, export_format, preset_settings)

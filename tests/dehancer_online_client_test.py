from __future__ import annotations

import json
from dataclasses import asdict
from secrets import choice
from unittest.mock import MagicMock, Mock, patch

import pytest

from src import utils
from src.api.clients.dehancer_online_client import DehancerOnlineAPIClient
from src.api.constants import (
    BASE_HEADERS,
    HEADER_JSON_CONTENT_TYPE,
    HEADER_TRANSFER_ENCODING_TRAILERS,
    SECURITY_HEADERS,
)
from src.api.models.preset import ImageSize, Preset, PresetSettings
from tests.data.api_mock_responses.get_pane import (
    get_pane_invalid_response,
    get_pane_not_success_response,
    get_pane_success_response,
)
from tests.data.api_mock_responses.render_single_image import (
    render_single_image_invalid_response,
    render_single_image_not_success_response,
    render_single_image_success_response,
)
from tests.data.api_mock_responses.upload_file_put import (
    upload_file_put_invalid_response,
    upload_file_put_not_success_response,
    upload_file_put_success_response,
)
from tests.data.api_mock_responses.whoami import (
    whoami_invalid_response,
    whoami_not_success_response,
    whoami_success_response,
)


@pytest.fixture()
def mock_requests_session_get() -> MagicMock:
    with patch("requests.Session.get") as mock_get:
        yield mock_get


@pytest.fixture()
def mock_api_client() -> DehancerOnlineAPIClient:
    return DehancerOnlineAPIClient("https://mock.com/api")


@pytest.fixture()
def image_path() -> str:
    return "path/to/image.jpg"


def generate_presets(count: int) -> list[Preset]:
    captions = [f"Preset {i}" for i in range(1, count + 1)]
    return [Preset(caption=caption, creator="Test", preset=f"preset_{i}",
                   exposure=0.5, contrast=0.5, temperature=10, tint=0.2, color_boost=0.1,
                   is_bloom_enabled=True, bloom=0.5, is_halation_enabled=True, halation=0.5,
                   is_grain_enabled=True, grain=0.1)
            for i, caption in enumerate(captions, 1)]


@pytest.mark.unit
def test_get_available_presets_success(mock_requests_session_get: MagicMock,
                                       mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = json.dumps(whoami_success_response)
    mock_requests_session_get.return_value = mock_response
    expected_number_of_presets = 62
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected method have been called by the tested method
    mock_requests_session_get.assert_called_once_with("https://mock.com/api/whoami")
    # Assert: check that the method result contains the expected data
    assert len(result) == expected_number_of_presets
    assert result[0].caption == "AGFA Chrome RSX II 200 (Exp. 2006)"
    assert result[1].caption == "Adox Color Implosion 100"
    assert all(isinstance(p, Preset) for p in result)


@pytest.mark.unit
def test_get_available_presets_not_success(mock_requests_session_get: MagicMock,
                                           mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = json.dumps(whoami_not_success_response)
    mock_requests_session_get.return_value = mock_response
    # Act: perform method under test
    result = mock_api_client.get_available_presets()
    # Assert: check that the expected method have been called by the tested method
    mock_requests_session_get.assert_called_once_with("https://mock.com/api/whoami")
    # Assert: check that the method result contains no data
    assert len(result) == 0


@pytest.mark.unit
def test_get_available_presets_failure(mock_requests_session_get: MagicMock,
                                       mock_api_client: DehancerOnlineAPIClient):
    # Arrange: setup mock objects
    mock_response = Mock()
    mock_response.text = whoami_invalid_response
    mock_requests_session_get.return_value = mock_response
    # Assert: check that the expected failure caused by the tested method
    with pytest.raises(json.JSONDecodeError):
        # Act: perform method under test
        mock_api_client.get_available_presets()


@pytest.mark.unit
def test_upload_image_success(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__upload_file",
                         return_value=Mock(text=json.dumps(upload_file_put_success_response))), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_options"), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_put"), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__image_uploaded"), \
            patch.object(utils, "is_file_exist", return_value=True), \
            patch("src.api.clients.dehancer_online_client.logger") as mock_logger:
        # Act: perform method under test
        result = mock_api_client.upload_image(image_path)
        # Assert: check that the method result contains the expected data
        expected_image_id = upload_file_put_success_response.get("imageId")
        assert result == expected_image_id
        # Assert: check that the expected message has been printed in the logs
        mock_logger.debug.assert_any_call("Upload image...")
        mock_logger.debug.assert_any_call("Image was uploaded, id is '%s'", expected_image_id)


@pytest.mark.unit
def test_upload_image_file_not_success(mock_api_client: DehancerOnlineAPIClient, image_path: str):
    # Arrange: setup mock objects
    with patch.object(mock_api_client, "_DehancerOnlineAPIClient__check_image_file", return_value=True), \
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__upload_file",
                         return_value=Mock(text=json.dumps(upload_file_put_not_success_response))), \
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
            patch.object(mock_api_client, "_DehancerOnlineAPIClient__upload_file",
                         return_value=Mock(text=upload_file_put_invalid_response)), \
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
def test_get_pane_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(get_pane_success_response))) as mock_post:
        # Act: perform method under test
        result = mock_api_client.get_pane(image_id, image_size, presets)
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
        mock_post.assert_called_once_with(f"{mock_api_client.api_base_url}/get-pane",
                                          headers=expected_headers, data=expected_payload)
        # Assert: check that the method result contains the expected data
        assert result == {f"Preset {i}": link for i, link in zip(range(1, 63), get_pane_success_response["images"])}


@pytest.mark.unit
def test_get_pane_not_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(get_pane_not_success_response))):
        # Act: perform method under test
        result = mock_api_client.get_pane(image_id, image_size, presets)
        # Assert: check that the method result contains no data
        assert result == {}


@pytest.mark.unit
def test_get_pane_failure(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    image_size = ImageSize.SMALL
    presets = generate_presets(62)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(status_code=500, text=get_pane_invalid_response)), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.get_pane(image_id, image_size, presets)


@pytest.mark.unit
@pytest.mark.parametrize("preset_settings", [
    pytest.param(PresetSettings(0, 0, 0, 0, 0, 0, 0, 0), id="Default settings"),
    pytest.param(
        PresetSettings(exposure=1.5, contrast=3.5, temperature=-15,
                       tint=1, color_boost=3, bloom=4.5, halation=2.2, grain=4.1), id="Custom settings"),
])
def test_render_image_success(mock_api_client: DehancerOnlineAPIClient, preset_settings: PresetSettings):
    image_id = "123"
    preset = choice(generate_presets(62))
    state = {**asdict(preset), **asdict(preset_settings)}
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(render_single_image_success_response))) as mock_post:
        # Act: perform method under test
        result = mock_api_client.render_image(image_id, preset, preset_settings)
        expected_payload = json.dumps({
            "imageId": image_id,
            "state": state,
        })
        expected_headers = BASE_HEADERS.copy()
        expected_headers.update({
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        expected_headers.update(SECURITY_HEADERS)
        # Assert: check that the expected request has been sent by the tested method
        mock_post.assert_called_once_with(f"{mock_api_client.api_base_url}/render-single-image",
                                          headers=expected_headers, data=expected_payload)
        # Assert: check that the method result contains the expected data
        assert result == render_single_image_success_response["url"]


@pytest.mark.unit
def test_render_image_not_success(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings(0, 0, 0, 0, 0, 0, 0, 0)
    state = {**asdict(preset), **asdict(preset_settings)}
    for key in ["caption", "creator", "is_bloom_enabled", "is_halation_enabled", "is_grain_enabled"]:
        state.pop(key, None)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(text=json.dumps(render_single_image_not_success_response))):
        # Act: perform method under test
        result = mock_api_client.render_image(image_id, preset, preset_settings)
        # Assert: check that the method result contains no data
        assert result is None


@pytest.mark.unit
def test_render_failure(mock_api_client: DehancerOnlineAPIClient):
    image_id = "123"
    preset = choice(generate_presets(62))
    preset_settings = PresetSettings(0, 0, 0, 0, 0, 0, 0, 0)
    # Arrange: setup mock objects
    with patch.object(mock_api_client.session, "post",
                      return_value=Mock(status_code=500, text=render_single_image_invalid_response)), \
            pytest.raises(json.JSONDecodeError):  # Assert: check that the expected failure caused by the tested method
        # Act: perform method under test
        mock_api_client.render_image(image_id, preset, preset_settings)

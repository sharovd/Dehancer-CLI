import shutil
from collections.abc import Iterator
from os import getenv
from random import choice, sample

import pytest

import tests.utils.test_data_provider as td
from src.api.clients.dehancer_online_client import DehancerOnlineAPIClient
from src.api.constants import DEHANCER_ONLINE_API_BASE_URL
from src.api.contracts.image_export import ImageExportModel
from src.api.contracts.image_previews import ImagePreviewsModel
from src.api.contracts.image_render import ImageRenderModel
from src.api.contracts.image_upload_prepare import ImageUploadPrepareModel
from src.api.contracts.login_with_email_and_password import LoginWithEmailAndPasswordModel
from src.api.contracts.presets import PresetsResponseModel
from src.api.enums import ExportFormat, ImageSize
from src.api.models.preset import PresetSettings
from src.cache.cache_manager import CacheManager


@pytest.fixture
def cache_manager() -> Iterator[CacheManager]:
    cache_manager = CacheManager("test-application")
    yield cache_manager
    shutil.rmtree(cache_manager.cache_dir, ignore_errors=True)


@pytest.fixture
def api_client(cache_manager: CacheManager) -> DehancerOnlineAPIClient:
    return DehancerOnlineAPIClient(DEHANCER_ONLINE_API_BASE_URL, cache_manager)


@pytest.fixture(scope="session")
def test_images():
    return td.get_all_test_images()


@pytest.fixture(scope="session")
def test_big_images():
    return td.get_big_test_images()


@pytest.mark.contract
def test_presets_success_response_is_valid(api_client: DehancerOnlineAPIClient) -> None:
    # Assert: the success response payload conforms to the PresetsResponseModel contract
    PresetsResponseModel.model_validate(
        # Act: perform method under test
        api_client._get_available_presets_raw().json(),  # noqa: SLF001
    )


@pytest.mark.contract
def test_login_with_email_and_password_success_response_is_valid(api_client: DehancerOnlineAPIClient) -> None:
    # Assert: the success response payload conforms to the LoginWithEmailAndPasswordModel contract
    LoginWithEmailAndPasswordModel.model_validate(
        # Act: perform method under test
        api_client._login_with_email_and_password_raw("test@test.com", "12345678").json(),  # noqa: SLF001
    )


@pytest.mark.contract
def test_image_upload_prepare_regular_success_response_is_valid(api_client: DehancerOnlineAPIClient,
                                                                test_images: list[str]) -> None:
    # Arrange: define test data
    random_test_image_path = choice(test_images)  # noqa: S311
    # Assert: the success response payload conforms to the ImageUploadPrepareModel contract
    model = ImageUploadPrepareModel.model_validate(
        # Act: perform method under test
        api_client._image_upload_prepare_raw(random_test_image_path).json(),  # noqa: SLF001
    )
    # Assert: the response correctly identifies the upload as single-part
    assert not model.is_multipart


@pytest.mark.contract
def test_image_upload_prepare_multipart_success_response_is_valid(api_client: DehancerOnlineAPIClient,
                                                                  test_big_images: list[str]):
    # Arrange: define test data
    random_test_image_path = choice(test_big_images)  # noqa: S311
    # Assert: the success response payload conforms to the ImageUploadPrepareModel contract
    model = ImageUploadPrepareModel.model_validate(
        # Act: perform method under test
        api_client._image_upload_prepare_raw(random_test_image_path).json(),  # noqa: SLF001
    )
    # Assert: the response correctly identifies the upload as multipart
    assert model.is_multipart


@pytest.mark.contract
def test_image_render_success_response_is_valid(api_client: DehancerOnlineAPIClient,
                                                test_images: list[str]):
    # Arrange: define test data
    random_test_image_path = choice(test_images)  # noqa: S311
    random_preset = choice(api_client.get_available_presets())  # noqa: S311
    image_id = api_client.upload_image(random_test_image_path)
    # Assert: the success response payload conforms to the ImageRenderModel contract
    ImageRenderModel.model_validate(
        # Act: perform method under test
        api_client._render_image_raw(image_id, random_preset).json(),  # noqa: SLF001
    )


@pytest.mark.contract
def test_image_previews_success_response_is_valid(api_client: DehancerOnlineAPIClient,
                                                  test_images: list[str]):
    # Arrange: define test data
    random_test_image_path = choice(test_images)  # noqa: S311
    number_of_presets = 3
    random_presets = sample(api_client.get_available_presets(), number_of_presets)
    image_id = api_client.upload_image(random_test_image_path)
    image_small_size = ImageSize.SMALL
    # Assert: the success response payload conforms to the ImagePreviewsModel contract
    ImagePreviewsModel.model_validate(
        # Act: perform method under test
        api_client._get_image_previews_raw(image_id, image_small_size, random_presets).json(),  # noqa: SLF001
        context={"expected_num_of_imgs_urls": number_of_presets},
    )


@pytest.mark.contract
@pytest.mark.skipif(
    not (getenv("DEHANCER_ACCESS_TOKEN") and getenv("DEHANCER_AUTH")),
    reason="Authorization is required for this test — set DEHANCER_ACCESS_TOKEN and DEHANCER_AUTH to run",
)
def test_image_export_success_response_is_valid(api_client: DehancerOnlineAPIClient,
                                                test_images: list[str]):
    # Arrange: define test data
    api_client.session.cookies.set("access-token", getenv("DEHANCER_ACCESS_TOKEN"))
    api_client.session.cookies.set("auth", getenv("DEHANCER_AUTH"))
    random_test_image_path = choice(test_images)  # noqa: S311
    random_preset = choice(api_client.get_available_presets())  # noqa: S311
    image_id = api_client.upload_image(random_test_image_path)
    image_web_format = ExportFormat.WEB
    default_preset_settings = PresetSettings.default()
    # Assert: the success response payload conforms to the ImageExportModel contract
    ImageExportModel.model_validate(
        # Act: perform method under test
        api_client._export_image_raw(image_id, random_preset, image_web_format, default_preset_settings).json(),  # noqa: SLF001
    )

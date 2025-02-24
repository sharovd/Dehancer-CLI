from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.cache.cache_keys import PRESETS

if TYPE_CHECKING:
    from requests import Response  # pragma: no cover

    from src.api.enums import ExportFormat, ImageSize  # pragma: no cover
    from src.cache.cache_manager import CacheManager  # pragma: no cover

import logging.config
from dataclasses import asdict
from json import dumps, loads
from mimetypes import guess_type

from src import utils
from src.api.clients.base_api_client import BaseAPIClient
from src.api.constants import (
    BASE_HEADERS,
    HEADER_ACCEPT_ENCODING,
    HEADER_JSON_CONTENT_TYPE,
    HEADER_PRIORITY_U_0,
    HEADER_TRANSFER_ENCODING_TRAILERS,
    IMAGE_VALID_TYPES,
    SECURITY_HEADERS,
)
from src.api.models.preset import Preset, PresetSettings, PresetSettingsState

logging.config.dictConfig(utils.get_logger_config_dict())
logger = logging.getLogger()


class DehancerOnlineAPIClient(BaseAPIClient):
    """
    A client for interacting with the Dehancer Online API.

    This class provides methods for:
     - Getting available presets.
     - Uploading images.
     - Getting a pane of images with defined size and presets.
     - Rendering an image with defined preset and settings.
     - Exporting an image with defined preset, quality settings.

    Attributes
    ----------
    api_base_url (str): The base URL for the Dehancer Online API.
    cache_manager (CacheManager): The cache manager for storing response data.

    """

    def __init__(self, dehancer_online_api_base_url: str, cache_manager: CacheManager) -> None:
        super().__init__()
        self.api_base_url = dehancer_online_api_base_url
        self.cache_manager = cache_manager
        self.set_session_cookies(utils.get_auth_data_from_cache(self.cache_manager))

    @property
    def is_authorized(self) -> bool:
        """
        Check that the non-empty authorisation data is present in the session cookies.

        The presence of an "access-token" cookie indicates that the user has successfully logged in and is authorised
        to perform actions requiring authentication, such as rendering and exporting without a watermark.

        Returns
        -------
        bool: True if the access token is present in the session cookies, otherwise, False.

        """
        return self.session.cookies.get("access-token", None) is not None

    def login(self, email: str, password: str) -> bool:
        """
        Login with the provided email and password, and saves authorisation cookies from the response in the cache.

        This method attempts to authenticate a user using the provided email and password.
        If authentication is successful, it extracts 'access-token' and 'auth' values from the 'Set-Cookie' header
        in the response and saves it in the cache.

        Returns
        -------
            bool: True if the login is successful, otherwise False.

        Raises
        ------
            JSONDecodeError: If the response body cannot be parsed as JSON.
            KeyError: If the response JSON does not contain the expected keys.

        """
        utils.delete_access_token_and_auth_data_in_cache(self.cache_manager)
        logger.debug("Login and getting access token and auth data...")
        login_response = self.__login_with_email_and_password(email, password)
        login_response_body = loads(login_response.text)
        if not (isinstance(login_response_body, dict) and login_response_body.get("success")):
            return False
        set_cookie_header = login_response.headers.get("set-cookie")
        if not set_cookie_header:
            return False
        auth_cookies = self.__extract_auth_cookies(set_cookie_header)
        for name, value in auth_cookies.items():
            self.session.cookies.set(name, value)
            self.cache_manager.set(name, value)
        return True

    @staticmethod
    def __extract_auth_cookies(set_cookie_header: str) -> dict[str, str]:  # pragma: no cover
        """
        Extract 'access-token' and 'auth' cookies from the 'Set-Cookie' header.

        Args:
        ----
        set_cookie_header (str): The value of the 'Set-Cookie' header from which cookies should be extracted.

        Returns:
        -------
        dict[str, str]: A dictionary containing 'access-token' and 'auth' if present.

        """
        cookies = set_cookie_header.split("; ")
        auth_cookies = {}
        for cookie in cookies:
            if cookie.startswith("access-token="):
                auth_cookies["access-token"] = cookie.split("=", 1)[1]
            elif cookie.startswith("Secure, auth="):
                auth_cookies["auth"] = cookie.split("=", 1)[1]
        return auth_cookies

    def get_available_presets(self) -> list[Preset]:
        """
        Get available presets, sorted by name, from the Dehancer Online API or cache.

        This method first checks for cached presets data.
        If found and valid - returns the cached presets.
        Otherwise - fetches presets from the API, caches them, and returns the result.

        Returns
        -------
            list[Preset]: A list of Preset objects representing the available presets.

        Raises
        ------
            Exception: If there is an error in retrieving or processing the API response.

        """
        logger.debug("Getting available presets...")
        cached_presets = self.cache_manager.get(PRESETS)
        if cached_presets is not None:
            return cached_presets
        response = self.session.get(f"{self.api_base_url}/presets")
        available_presets = [Preset(**preset) for preset in loads(response.text)["presets"]]
        """
        The lower case `p.caption.lower()` is important so that the sorted list is identical to
        the same list returned by the js script `scripts/get-settings-via-browser-console.js`.
        Also note that there is currently at least one preset where the name of the film manufacturer
        is written in UPPER case, even though other names of the same manufacturer are written in Capitalized case.

        Example: "AGFA Chrome RSX II 200 (Exp. 2006)" and "Agfa Agfacolor XRS 200 (Exp. 1991)"
        """
        sorted_available_presets = sorted(available_presets, key=lambda p: p.caption.lower())
        self.cache_manager.set(PRESETS, sorted_available_presets)
        logger.debug("Available presets is '%s'", sorted_available_presets)
        return sorted_available_presets

    def upload_image(self, image_path: str) -> str | None:
        """
        Upload an image to the Dehancer Online API and return the image ID.

        Args:
        ----
            image_path (str): The file path of the image to be uploaded.

        Returns:
        -------
            str: The ID of the uploaded image.

        Raises:
        ------
            Exception: If there is an error during the image upload process.

        """
        if self.__check_image_file(image_path):
            utils.is_file_exist(image_path)
            logger.debug("Upload image...")
            upload_prepare_response = loads(self.__image_upload_prepare(image_path).text)
            if upload_prepare_response["success"]:
                image_id = upload_prepare_response["imageId"]
                # Regular upload (small size image file)
                if not upload_prepare_response.get("isMultipart", False):
                    url = upload_prepare_response["url"]
                    self.__image_put(url, image_path)
                    self.__image_upload_finish(image_id, image_path)
                # Multipart upload (big size image file)
                else:
                    chunk_size = upload_prepare_response["chunkSize"]
                    urls = upload_prepare_response["urls"]
                    upload_id = upload_prepare_response["uploadId"]
                    responses = self.__image_put_multipart(urls, image_path, chunk_size)
                    etags = [response.headers["ETag"] for response in responses]
                    image_file_name = Path(image_path).name
                    self.__image_upload_finish_multipart(image_id, upload_id, etags, image_file_name)
                logger.debug("Image was uploaded, id is '%s'", image_id)
                return image_id
        return None

    def get_image_previews(self, image_id: str, image_size: ImageSize, presets: list[Preset]) -> dict[str, str]:
        """
        Get links to images in accordance with the provide presets for a given image ID and size.

        Args:
        ----
            image_id (str): The ID of the uploaded image.
            image_size (ImageSize): The size of the image to retrieve.
            presets (list[Preset]): A list of Preset objects representing the presets to apply.

        Returns:
        -------
            dict[str, str]: A dictionary where the keys are captions of presets
            and the values are URLs of the corresponding images.

        Raises:
        ------
            Exception: If there is an error in retrieving or processing the API response.

        """
        states = [asdict(preset) for preset in presets]
        url = f"{self.api_base_url}/image/previews/{image_id}"
        payload = dumps({
            "imageId": image_id,
            "size": image_size.value,
            "states": states,
        })
        headers = BASE_HEADERS
        headers.update({
            "TE": HEADER_TRANSFER_ENCODING_TRAILERS,
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        result_images_links = loads(response.text).get("images", None)
        if result_images_links is not None:
            return {preset.caption: value for preset, value in zip(presets, result_images_links)}
        return {}

    def render_image(self, image_id: str, preset: Preset,
                     preset_settings: PresetSettings = None) -> str:
        """
        Render a single image based on the provided image ID, preset, and preset settings.

        Args:
        ----
            image_id (str): The ID of the uploaded image to render.
            preset (Preset): The preset to apply during rendering.
            preset_settings (PresetSettings): The settings to be applied to the preset during rendering.

        Returns:
        -------
            str: The URL of the rendered image.

        Raises:
        ------
            Exception: If there is an error in retrieving or processing the API response.

        """
        if preset_settings is None:
            preset_settings = PresetSettings.default()
        url = f"{self.api_base_url}/image/render/{image_id}"
        state = {"preset": preset.preset}
        state.update({key: value for key, value in asdict(preset_settings).items() if value != PresetSettingsState.OFF})
        payload = dumps({
            "imageId": image_id,
            "state": state,
        })
        headers = BASE_HEADERS
        headers.update({
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        return loads(response.text).get("url", None)

    def export_image(self, image_id: str, preset: Preset, export_format: ExportFormat,
                     preset_settings: PresetSettings) -> dict[str, str]:
        """
        Render a single image for export based on the provided image ID, preset, export format and preset settings.

        Args:
        ----
            image_id (str): The ID of the uploaded image to render.
            preset (Preset): The preset to apply during rendering.
            export_format (ExportFormat): The export format to use when rendering.
            preset_settings (PresetSettings): The settings to be applied to the preset during rendering.

        Returns:
        -------
            dict[str, str]: The dictionary with 'url' and 'filename' of the rendered image.

        Raises:
        ------
            Exception: If there is an error in retrieving or processing the API response.

        """
        url = f"{self.api_base_url}/image/export/{image_id}"
        state = {"preset": preset.preset}
        state.update({key: value for key, value in asdict(preset_settings).items() if value != PresetSettingsState.OFF})
        payload = dumps({
            "format": export_format.value,
            "imageId": image_id,
            "state": state,
        })
        headers = BASE_HEADERS
        headers.update({
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        response_body = loads(response.text)
        url = response_body.get("url", None)
        file_name = response_body.get("filename", None)
        return {"url": url, "filename": file_name}

    def __login_with_email_and_password(self, email: str, password: str) -> Response:  # pragma: no cover
        """
        Send an HTTP POST request with email and password to login to the Dehancer Online API.

        Args:
        ----
            email (str): The email address of the user for authentication.
            password (str): The password of the user for authentication.

        Returns:
        -------
            Response: The HTTP response object.
            In case of successful result, a JSON response object have a 'success' field with a value of 'true'.
            In case of successful result the response also has a 'set-cookie' header with an 'access-token' value.

        Raises:
        ------
            Exception: If there is an error during the login process.

        """
        url = f"{self.api_base_url}/auth/login-with-email-and-password"
        payload = dumps({
            "email": email,
            "password": password,
        })
        headers = BASE_HEADERS
        headers.update({
            "Accept": HEADER_JSON_CONTENT_TYPE,
            "Accept-Encoding": HEADER_ACCEPT_ENCODING,
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
            "Priority": HEADER_PRIORITY_U_0,
            "TE": HEADER_TRANSFER_ENCODING_TRAILERS,
        })
        headers.update(SECURITY_HEADERS)
        return self.session.post(url, headers=headers, data=payload)

    def __image_upload_prepare(self, image_path: str) -> Response:  # pragma: no cover
        """
        Send an HTTP POST request with the image's meta information to the Dehancer Online API.

        Step 1/3 in the image upload flow.

        Args:
        ----
            image_path (str): The file path of the image to be uploaded.

        Returns:
        -------
            Response: The HTTP response object.
            In case of successful result, a JSON response object with fields 'imageId' and 'url' is returned.

        Raises:
        ------
            Exception: If there is an error during the file upload process.

        """
        utils.is_file_exist(image_path)
        url = f"{self.api_base_url}/upload/prepare"
        payload = dumps({
            "mimetype": guess_type(image_path)[0],
            "size": Path(image_path).stat().st_size,
        })
        headers = {
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        }
        return self.session.post(url, headers=headers, data=payload)

    def __image_put(self, url: str, image_path: str) -> Response:  # pragma: no cover
        """
        Send an HTTP PUT request with the image content as bytes to the Dehancer Online API.

        Step 2/3 in the image upload flow.

        Args:
        ----
            url (str): The URL to send the PUT request to.
            image_path (str): The path to the image file to be uploaded.

        Returns:
        -------
            Response: The HTTP response object.
            In case of successful result, a response body is empty.

        Raises:
        ------
            Exception: If there is an error during the PUT request or while reading the image file.

        """
        headers = BASE_HEADERS
        headers.update({
            "Content-Type": guess_type(image_path)[0],
        })
        headers.update(SECURITY_HEADERS)
        with Path(image_path).open("rb") as image_file:
            file_bytes = image_file.read()
        return self.session.put(url, headers=headers, data=file_bytes)

    def __image_put_multipart(self, urls: list[str], image_path: str, chunk_size: int) -> list[Response]:  # noqa: RUF100, E501 # pragma: no cover
        """
        Send an HTTP PUT requests with the large image content as bytes to the Dehancer Online API.

        Step 2/3 in the image upload flow.

        Args:
        ----
            urls (list[str]): The list of URLs to send the PUT request containing part of the image file to.
            image_path (str): The path to the image file to be uploaded.
            chunk_size (int): The size of each chunk to upload.

        Returns:
        -------
            list[Response]: A list of HTTP response objects for each part upload.

        Raises:
        ------
            Exception: If there is an error during the PUT request or while reading the image file.

        """
        headers = BASE_HEADERS
        headers.update({
            "Content-Type": guess_type(image_path)[0],
        })
        headers.update(SECURITY_HEADERS)
        result = []
        with Path(image_path).open("rb") as image_file:
            for _, url in enumerate(urls):
                chunk = image_file.read(chunk_size)
                if not chunk:
                    break
                result.append(self.session.put(url, headers=headers, data=chunk))
        return result

    def __image_upload_finish(self, image_id: str, image_file_name: str) -> Response:  # pragma: no cover
        """
        Send an HTTP POST request notifying the server that an image has been successfully uploaded.

        Step 3/3 in the image upload flow.

        Args:
        ----
            image_id (str): The ID of the uploaded image.
            image_file_name (str): The name of the image file that was uploaded.

        Returns:
        -------
            Response: The HTTP response object containing the result of the notification.
            In case of successful result, a JSON response object with fields
            'userId', 'width', 'height', 'filename', 'originalUrl', 'placeholderUrl' is returned.

        Raises:
        ------
            Exception: If there is an error during the POST request.

        """
        url = f"{self.api_base_url}/upload/finish"
        payload = dumps({
            "imageId": image_id,
            "filename": image_file_name,
        })
        headers = BASE_HEADERS
        headers.update({
            "TE": HEADER_TRANSFER_ENCODING_TRAILERS,
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        headers.update(SECURITY_HEADERS)
        return self.session.post(url, headers=headers, data=payload)

    def __image_upload_finish_multipart(self, image_id: str, upload_id: str,
                                        etags: list[str], image_file_name: str) -> None:  # pragma: no cover
        """
        Send an HTTP POST request notifying the server that an multipart image has been successfully uploaded.

        Step 3/3 in the image upload flow.

        Args:
        ----
            image_id (str): The ID of the uploaded image.
            upload_id (str): The multipart upload ID.
            etags (list[str]): The list of ETags from each part upload.
            image_file_name (str): The name of the image file that was uploaded.

        Raises:
        ------
            Exception: If there is an error during the POST request.

        """
        url = f"{self.api_base_url}/upload/finish"
        payload = dumps({
            "imageId": image_id,
            "uploadId": upload_id,
            "etags": etags,
            "filename": image_file_name,
        })
        headers = BASE_HEADERS
        headers.update({
            "TE": HEADER_TRANSFER_ENCODING_TRAILERS,
            "Content-Type": HEADER_JSON_CONTENT_TYPE,
        })
        headers.update(SECURITY_HEADERS)
        return self.session.post(url, headers=headers, data=payload)

    @staticmethod
    def __check_image_file(image_path: str) -> bool:  # pragma: no cover
        """
        Check if the image file exists and is of a supported format.

        Args:
        ----
            image_path (str): The path to the image file.

        Returns:
        -------
            bool: True if the image file exists and is of a supported format, False otherwise.

        """
        if not utils.is_file_exist(image_path):
            logger.error("File '%s' does not exist", image_path)
            return False
        if not utils.is_supported_format_file(image_path, IMAGE_VALID_TYPES):
            valid_types = IMAGE_VALID_TYPES.keys()
            logger.error("File '%s' is not a supported format.\n"
                         "Only certain image files are allowed: %s", image_path, valid_types)
            return False
        return True

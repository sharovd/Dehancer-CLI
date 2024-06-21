import logging.config
import logging.handlers
from dataclasses import asdict
from json import loads, dumps
from mimetypes import guess_type
from os import path
from typing import List, Union, Dict

from requests import Response

from src import utils
from src.api.clients.base_api_client import BaseAPIClient
from src.api.constants import (HEADER_JSON_CONTENT_TYPE, SECURITY_HEADERS,
                               HEADER_TRANSFER_ENCODING_TRAILERS, BASE_HEADERS, IMAGE_VALID_TYPES)
from src.api.models.preset import Preset, ImageSize, PresetSettings

logging.config.fileConfig(utils.get_logger_config_file_path())
logger = logging.getLogger()


class DehancerOnlineAPIClient(BaseAPIClient):

    def __init__(self, dehancer_online_api_base_url: str) -> None:
        super().__init__()
        self.api_base_url = dehancer_online_api_base_url

    def get_available_presets(self) -> List[Preset]:
        """
        Retrieval of available presets, sorted by name, from the Dehancer Online API.
        Returns:
            List[Preset]: A list of Preset objects representing the available presets.
        Raises:
            Exception: If there is an error in retrieving or processing the API response.
        """
        logger.debug("Getting available presets...")
        response = self.session.get(f"{self.api_base_url}/whoami")
        available_presets = [Preset(**preset) for preset in loads(response.text)["presets"]]
        sorted_available_presets = sorted(available_presets, key=lambda p: p.caption)
        logger.debug(f"Available presets is '{sorted_available_presets}'")
        return sorted_available_presets

    def upload_image(self, image_path: str) -> Union[str, None]:
        """
        Upload an image to the Dehancer Online API and return the image ID.
        Args:
            image_path (str): The file path of the image to be uploaded.
        Returns:
            str: The ID of the uploaded image.
        Raises:
            Exception: If there is an error during the image upload process.
        """
        if self.__check_image_file(image_path):
            utils.is_file_exist(image_path)
            logger.debug("Upload image...")
            upload_file_response = loads(self.__upload_file(image_path).text)
            if upload_file_response["success"]:
                image_id = upload_file_response["imageId"]
                url = upload_file_response["url"]
                self.__image_options(url)
                self.__image_put(url, image_path)
                self.__image_uploaded(image_id, image_path)
                logger.debug(f"Image was uploaded, id is '{image_id}'")
                return image_id
        return None

    def get_pane(self, image_id: str, image_size: ImageSize, presets: List[Preset]) -> Dict[str, str]:
        """
        Retrieval of links to images in accordance with the provided presets for a given image ID and size.
        Args:
            image_id (str): The ID of the uploaded image.
            image_size (ImageSize): The size of the image to retrieve.
            presets (List[Preset]): A list of Preset objects representing the presets to apply.
        Returns:
            Dict[str, str]: A dictionary where the keys are captions of presets and the values are URLs of the corresponding images.
        Raises:
            Exception: If there is an error in retrieving or processing the API response.
        """
        states = [asdict(preset) for preset in presets]
        url = f"{self.api_base_url}/get-pane"
        payload = dumps({
            "imageId": image_id,
            "size": image_size.value,
            "states": states
        })
        headers = BASE_HEADERS
        headers.update({
            'TE': HEADER_TRANSFER_ENCODING_TRAILERS,
            'Content-Type': HEADER_JSON_CONTENT_TYPE
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        result_images_links = loads(response.text).get("images", None)
        if result_images_links is not None:
            return {preset.caption: value for preset, value in zip(presets, result_images_links)}
        else:
            return {}

    def render_image(self, image_id: str, preset: Preset, preset_settings: PresetSettings) -> str:
        """
        Renders a single image based on the provided image ID, preset, and preset settings.
        Args:
            image_id (str): The ID of the uploaded image to render.
            preset (Preset): The preset to apply during rendering.
            preset_settings (PresetSettings): The settings to be applied to the preset during rendering.
        Returns:
            str: The URL of the rendered image.
        Raises:
            Exception: If there is an error in retrieving or processing the API response.
        """
        url = f"{self.api_base_url}/render-single-image"
        state = {'preset': preset.preset}
        state.update(asdict(preset_settings))
        payload = dumps({
            "imageId": image_id,
            "state": state
        })
        headers = BASE_HEADERS
        headers.update({
            'Content-Type': HEADER_JSON_CONTENT_TYPE
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        return loads(response.text).get("url", None)

    def __upload_file(self, image_path: str) -> Response:  # pragma: no cover
        """
        Sends an HTTP POST request with the image's meta information to the Dehancer Online API (Step 1/4 in the image upload flow).
        Args:
            image_path (str): The file path of the image to be uploaded.
        Returns:
            Response: The HTTP response object.
            In case of successful result, a JSON response object with fields 'imageId' and 'url' is returned.
        Raises:
            Exception: If there is an error during the file upload process.
        """
        utils.is_file_exist(image_path)
        url = f"{self.api_base_url}/upload-file-put"
        payload = dumps({
            "mimetype": guess_type(image_path)[0],
            "size": path.getsize(image_path)
        })
        headers = {
            'Content-Type': HEADER_JSON_CONTENT_TYPE
        }
        response = self.session.post(url, headers=headers, data=payload)
        return response

    def __image_options(self, url: str) -> Response:  # pragma: no cover
        """
        Sends an HTTP OPTIONS request to the specified URL (Step 2/4 in image upload flow).
        Args:
            url (str): The URL to send the OPTIONS request to.
        Returns:
            Response: The HTTP response object.
            In case of successful result, a response body is empty.
        Raises:
            Exception: If there is an error during the OPTIONS request.
        """
        headers = BASE_HEADERS
        headers.update({
            'Access-Control-Request-Method': 'PUT',
            'Access-Control-Request-Headers': 'content-type',
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.options(url, headers=headers, data={})
        return response

    def __image_put(self, url: str, image_path: str) -> Response:  # pragma: no cover
        """
        Sends an HTTP PUT request with the image content as bytes to the Dehancer Online API (Step 3/4 in the image upload flow).
        Args:
            url (str): The URL to send the PUT request to.
            image_path (str): The path to the image file to be uploaded.
        Returns:
            Response: The HTTP response object.
            In case of successful result, a response body is empty.
        Raises:
            Exception: If there is an error during the PUT request or while reading the image file.
        """
        headers = BASE_HEADERS
        headers.update({
            'Content-Type': guess_type(image_path)[0]
        })
        headers.update(SECURITY_HEADERS)
        file_bytes = open(image_path, "rb").read()
        response = self.session.put(url, headers=headers, data=file_bytes)
        return response

    def __image_uploaded(self, image_id: str, image_file_name: str) -> Response:  # pragma: no cover
        """
        Sends an HTTP POST request notifying the server that an image has been successfully uploaded (Step 4/4 in the image upload flow).
        Args:
            image_id (str): The ID of the uploaded image.
            image_file_name (str): The name of the image file that was uploaded.
        Returns:
            Response: The HTTP response object containing the result of the notification.
            In case of successful result, a JSON response object with fields 'userId', 'width', 'height', 'filename', 'originalUrl', 'placeholderUrl' is returned.
        Raises:
            Exception: If there is an error during the POST request.
        """
        url = f"{self.api_base_url}/uploaded"
        payload = dumps({
            "imageId": image_id,
            "filename": image_file_name
        })
        headers = BASE_HEADERS
        headers.update({
            'TE': HEADER_TRANSFER_ENCODING_TRAILERS,
            'Content-Type': HEADER_JSON_CONTENT_TYPE
        })
        headers.update(SECURITY_HEADERS)
        response = self.session.post(url, headers=headers, data=payload)
        return response

    @staticmethod
    def __check_image_file(image_path: str) -> bool:  # pragma: no cover
        """
        Checks if the image file exists and is of a supported format.
        Args:
            image_path (str): The path to the image file.
        Returns:
            bool: True if the image file exists and is of a supported format, False otherwise.
        """
        if not utils.is_file_exist(image_path):
            logger.error(f"File '{image_path}' does not exist")
            return False
        if not utils.is_supported_format_file(image_path, IMAGE_VALID_TYPES):
            valid_types = IMAGE_VALID_TYPES.keys()
            logger.error(f"File '{image_path}' is not a supported format.\n"
                         f"Only certain image files are allowed: {valid_types}")
            return False
        return True

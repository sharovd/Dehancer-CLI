from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from src.api.constants import IMAGE_VALID_TYPES
from src.utils import (
    download_file,
    get_filename_without_extension,
    is_file_exist,
    is_supported_format_file,
    read_settings_file,
)


@pytest.mark.unit
@pytest.mark.parametrize(("settings_file_content", "expected_result"), [
    # Valid data and format
    ("contrast=5\nexposure=10\n", {"contrast": 5, "exposure": 10}),
    ("contrast =5\nexposure= 10\n", {"contrast": 5, "exposure": 10}),
    ("contrast=5.2\nexposure=10.8\n", {"contrast": 5.2, "exposure": 10.8}),
    ("contrast=0\nexposure=0.1\n", {"contrast": 0, "exposure": 0.1}),
    ("contrast=-5.2\nexposure=-10.8\n", {"contrast": -5.2, "exposure": -10.8}),
    ("contrast=5\nexposure=10.8\ntemperature=20", {"contrast": 5, "exposure": 10.8, "temperature": 20}),
    # Invalid data of format
    ("contrast=5\nexposure\n", {"contrast": 5}),
    ("contrast=\nexposure=10\n", {"exposure": 10}),
    ("contrast:5\nexposure=10\n", {"exposure": 10}),
    ("contrast=5\nexposure=abc\n", {"contrast": 5}),
    ("contrast=5,\nexposure=10\n", {"exposure": 10}),
    ("contrast=5\nexposure=10\ncontrast=\n", {"contrast": 5, "exposure": 10}),
    ("contrast=\nexposure=\n", {}),
    ("", {}),
])
def test_read_settings_file_returns_dict_with_settings(settings_file_content: str, expected_result: dict[str, float]):
    # Arrange: create temporary settings file with content
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(settings_file_content.encode())
        tmp_file_path = tmp_file.name
    try:
        # Act: perform method under test and get result
        actual_result = read_settings_file(tmp_file_path)
        # Assert
        assert actual_result == expected_result
    finally:
        # Cleanup: remove temporary settings file
        Path(tmp_file_path).unlink()


@pytest.mark.unit
def test_read_settings_file_for_nonexistent_file_raises_error():
    # Arrange: create temporary settings file with content
    non_existent_file_path = "non_existent_file.txt"
    # Assert: 'FileNotFoundError' error occurs with corresponding message
    with pytest.raises(FileNotFoundError, match=f"The file {non_existent_file_path} does not exist."):
        # Act: perform method under test
        read_settings_file(non_existent_file_path)


@pytest.mark.unit
@pytest.mark.parametrize(("file_path", "expected_result"), [
    ("non_existent_file.txt", False),
    (Path.cwd(), False),
    ("", False),
])
def test_is_file_exist_returns_false(file_path: str, expected_result: bool):  # noqa: FBT001
    # Act: perform method under test & Assert
    assert is_file_exist(file_path) == expected_result


@pytest.mark.unit
def test_is_file_exist_returns_true():
    # Arrange: create temporary file
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    try:
        # Act: perform method under test & Assert
        assert is_file_exist(tmp_file_path) is True
    finally:
        # Cleanup: remove temporary settings file
        Path(tmp_file_path).unlink()


@pytest.mark.unit
@pytest.mark.parametrize(("file_content", "file_extension", "expected_result"), [
    (b"\xff\xd8\xff", "jpeg", True),
    (b"\x49\x49\x2A\x00", "tiff", True),
    # TODO: Added valid file content for '*.heif', '*.heic' and '*.avif' formats  # noqa: FIX002
    # (b"\x00\x00\x00\x18ftypheif", "heif", True),  # noqa: ERA001
    # (b"\x00\x00\x00\x18ftypheic", "heic", True),  # noqa: ERA001
    # (b"\x00\x00\x00\x18ftypavif", "avif", True),  # noqa: ERA001
    (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "webp", True),
    (b"MM\x00\x2a", "dng", True),
    (b"\x89PNG\r\n\x1a\n", "png", True),
    (b"dummy content", "txt", False),
])
def test_is_supported_format_file_returns_true_or_false(file_content: bytes, file_extension: str,
                                                        expected_result: bool):  # noqa: FBT001
    if file_content is not None:
        # Arrange: create temporary file with extension
        with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
    else:
        tmp_file_path = "non_existent_file.xyz"
    try:
        # Act: perform method under test and get result
        actual_result = is_supported_format_file(tmp_file_path, IMAGE_VALID_TYPES)
        # Assert
        assert actual_result == expected_result
    finally:
        # Cleanup: remove temporary file
        if file_content is not None:
            Path(tmp_file_path).unlink()


@pytest.mark.unit
def test_is_supported_format_file_for_nonexistent_file_raises_error():
    # Arrange: create temporary settings file with content
    non_existent_file_path = "non_existent_file.txt"
    # Assert: 'FileNotFoundError' error occurs with corresponding message
    with pytest.raises(FileNotFoundError, match=f"The file {non_existent_file_path} does not exist."):
        # Act: perform method under test
        is_supported_format_file(non_existent_file_path, {})


@pytest.mark.unit
@pytest.mark.parametrize(("file_path", "expected_result"), [
    ("/path/to/file/example.txt", "example"),
    ("/path/to/file/archive.tar.gz", "archive.tar"),
    ("/path/to/file/image.jpg", "image"),
    ("/path/to/file/no_extension", "no_extension"),
    ("/path/to/file/.hidden", ".hidden"),
    ("/path/to/file/dotfile.", "dotfile"),
    ("/path/to/file/double.extension.zip", "double.extension"),
    ("example.txt", "example"),
    ("archive.tar.gz", "archive.tar"),
    ("image.jpg", "image"),
    ("no_extension", "no_extension"),
    (".hidden", ".hidden"),
    ("dotfile.", "dotfile"),
    ("double.extension.zip", "double.extension"),
])
def test_get_filename_without_extension_returns_file_name(file_path: str, expected_result: str):
    # Act: perform method under test & Assert
    assert get_filename_without_extension(file_path) == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(("status_code", "dir_exists_before", "expected_logging"), [
    # Response '200 OK', directory to download file exists
    (200, False, "File 'https://example.com/file.txt' downloaded successfully."),
    # Response '200 OK', directory to download file doesn't exist
    (200, True, "File 'https://example.com/file.txt' downloaded successfully."),
    # Response '404 Not Found'
    (404, False, "Failed to download the file 'https://example.com/file.txt'. Status code: 404"),
])
def test_download_file_downloads_file_if_200_ok_or_logs_error_message_otherwise(
        status_code: int, dir_exists_before: bool, expected_logging: str):  # noqa: FBT001
    file_url = "https://example.com/file.txt"
    file_dir = "/path/to/save/file.txt"
    with patch("pathlib.Path.open", new_callable=mock_open) as mock_open_file, \
         patch("requests.get") as mock_request_get, \
         patch("pathlib.Path.exists") as mock_path_exists, \
         patch("pathlib.Path.mkdir") as mock_path_mkdir, \
         patch("src.utils.logger") as mock_logger:
        # Arrange: setup mock objects
        mock_response = Mock(status_code=status_code, content=b"Mock file content")
        mock_request_get.return_value = mock_response
        mock_path_exists.return_value = dir_exists_before
        # Act: perform method under test
        download_file(file_url, file_dir)
        # Assert: check that the expected methods have been called by the tested method
        mock_request_get.assert_called_once_with(file_url, stream=True, timeout=120)
        if status_code == requests.codes.ok:
            mock_path_exists.assert_called_once_with()
        if not dir_exists_before and status_code == requests.codes.ok:
            mock_path_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        else:
            mock_path_mkdir.assert_not_called()
        if status_code == requests.codes.ok:
            mock_open_file.assert_called_once_with("wb")
            mock_open_file().write.assert_called_once_with(b"Mock file content")
        # Assert: check that the expected message has been printed in the logs
        if status_code == requests.codes.ok:
            log_messages = [call[0][0] % call[0][1:] for call in mock_logger.debug.call_args_list]
            assert expected_logging in log_messages
        else:
            log_messages = [call[0][0] % call[0][1:] for call in mock_logger.error.call_args_list]
            assert expected_logging in log_messages

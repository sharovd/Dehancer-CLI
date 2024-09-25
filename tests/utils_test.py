from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, mock_open, patch

import pytest
import requests
from pytest import param as test_data  # noqa: PT013

from src.api.constants import IMAGE_VALID_TYPES
from src.api.models.preset import PresetSettings, PresetSettingsState
from src.utils import (
    download_file,
    get_auth_data,
    get_file_extension,
    get_filename_without_extension,
    is_file_exist,
    is_supported_format_file,
    read_settings_file,
    safe_join,
    update_auth_data,
)


@pytest.mark.unit
@pytest.mark.parametrize(("auth_data", "expected_content"), [
    # Valid auth data
    test_data({"access-token": "abc123", "auth": "def456"}, "access-token=abc123;auth=def456;",
              id="Full auth data: access-token and auth"),
    test_data({"access-token": "abc123"}, "access-token=abc123;",
              id="Partial auth data: only access-token"),
    test_data({"auth": "def456"}, "auth=def456;",
              id="Partial auth data: only auth"),
    test_data({"access-token": "special!@#$%^&*()_+", "auth": "def456"},
              "access-token=special!@#$%^&*()_+;auth=def456;",
              id="Special characters in access-token data"),
    test_data({"access-token": "abc123", "auth": "special!@#$%^&*()_+"},
              "access-token=abc123;auth=special!@#$%^&*()_+;",
              id="Special characters in auth data"),
    test_data({"access-token": "special_1!@#$%^&*()_+", "auth": "special_2!@#$%^&*()_+"},
              "access-token=special_1!@#$%^&*()_+;auth=special_2!@#$%^&*()_+;",
              id="Special characters in access-token and auth data"),
    test_data({}, "", id="Empty auth data: {}"),
    test_data(None, "", id="Empty auth data: None"),
])
def test_update_auth_data_writes_to_exiting_file(auth_data: dict[str, str], expected_content: str):
    # Arrange: setup mock object
    auth_file_path = "test_auth.txt"
    with patch("pathlib.Path.open", new_callable=mock_open) as mock_auth_file:
        # Act: perform method under test
        update_auth_data(auth_file_path, auth_data)
        # Assert: check that the file was opened in write mode if auth data is not empty
        # and the correct content was written
        if auth_data:
            mock_auth_file.assert_called_once_with("w")
            mock_auth_file().write.assert_called_once_with(expected_content)


@pytest.mark.unit
@pytest.mark.parametrize(("file_content", "expected_result"), [
    test_data("access-token=valid_access_token;auth=valid_auth_data;",
              {"access-token": "valid_access_token", "auth": "valid_auth_data"},
              id="Full auth data: access-token and auth"),
    test_data("access-token=valid_access_token;",
              {"access-token": "valid_access_token"},
              id="Partial auth data: only access-token"),
    test_data("auth=valid_auth_data;",
              {"auth": "valid_auth_data"},
              id="Partial auth data: only auth"),
    test_data("access-token=special_1!@#$%^&*()_+;auth=special_2!@#$%^&*()_+;",
              {"access-token": "special_1!@#$%^&*()_+", "auth": "special_2!@#$%^&*()_+"},
              id="Special characters in auth data"),
    test_data("", None,
              id="Empty auth file data"),
    test_data("access-token=valid_access_token_1;auth=valid_auth_data_1;\naccess-token=valid_access_token_2;auth=valid_auth_data_2;",
              {"access-token": "valid_access_token_1", "auth": "valid_auth_data_1"},
              id="Multiline file data (only first line should be read)"),
])
def test_get_auth_data_returns_auth_data(file_content: str, expected_result: dict[str, str] | None):
    # Arrange: create temporary auth file with content
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_content.encode())
        tmp_file_path = tmp_file.name
    try:
        # Act: perform method under test and get result
        actual_result = get_auth_data(tmp_file_path)
        # Assert
        assert actual_result == expected_result
    finally:
        # Cleanup: remove temporary auth file
        Path(tmp_file_path).unlink()


@pytest.mark.unit
def test_get_auth_data_for_nonexistent_file_returns_none():
    # Arrange: path to a non-existent file
    non_existent_file_path = "non_existent_file.txt"
    # Act: perform method under test
    actual_result = get_auth_data(non_existent_file_path)
    # Assert: check that the method result contains the expected result
    assert actual_result is None


@pytest.mark.unit
@pytest.mark.parametrize(("settings_file_content", "expected_result"), [
    test_data(
        """
        adjustments:
            exposure: 2.2
            contrast: 10
            temperature: -10
            tint: -22
            color_boost: 0
        effects:
            grain: Off
            bloom: Off
            halation: Off
        """,
        PresetSettings(exposure=2.2, contrast=10.0, temperature=-10.0, tint=-22.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Full valid adjustments and disabled effects",
    ),
    test_data(
        """
        adjustments:
            exposure: -4
            contrast: 2.5
            temperature: 0
            tint: 0
            color_boost: 12.2
        effects:
            grain: 0
            bloom: 50
            halation: 40.3
        """,
        PresetSettings(exposure=-4, contrast=2.5, temperature=0.0, tint=0, color_boost=12.2,
                       grain=0.0, bloom=50.0, halation=40.3),
        id="Full valid adjustments and enabled effects",
    ),
    test_data(
        """
        adjustments:
            exposure: -1.2
            temperature: 14
        effects:
            grain: Off
            halation: Off
        """,
        PresetSettings(exposure=-1.2, contrast=0.0, temperature=14.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Partially valid adjustments and offed effects",
    ),
    test_data(
        """
        adjustments:
            exposure: 3.2
            contrast: 0
            color_boost: -4
        effects:
            bloom: 25
        """,
        PresetSettings(exposure=3.2, contrast=0.0, temperature=0.0, tint=0.0, color_boost=-4.0,
                       grain=PresetSettingsState.OFF, bloom=25.0, halation=PresetSettingsState.OFF),
        id="Partially valid adjustments and enabled effects",
    ),
    test_data(
        """
        adjustments:
            exposure: 1.2
            contrast: -2.1
        effects:
        """,
        PresetSettings(exposure=1.2, contrast=-2.1, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Partially valid adjustments without effects",
    ),
    test_data(
        """
        adjustments:
            tint: 45
            color_boost: 55
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=45.0, color_boost=55.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Partially valid adjustments without effects section",
    ),
    test_data(
        """
        adjustments:
        effects:
            grain: Off
            bloom: 30
            halation: 12.5
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=30.0, halation=12.5),
        id="Full valid effects without adjustments",
    ),
    test_data(
        """
        effects:
            grain: 100
            bloom: Off
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=100.0, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Partially valid effects without adjustments section",
    ),
    test_data(
        """
        adjustments:
        effects:
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Without adjustments and effects",
    ),
    test_data(
        """
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Without adjustments and effects sections",
    ),
    test_data(
        """
        adjustments:
            exposure: 0
            contrast: 0
            temperature: 0
            tint: 0
            color_boost: 0
        effects:
            grain: 0
            bloom: 0
            halation: 0
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=0.0, bloom=0.0, halation=0.0),
        id="Full valid adjustments and effects with '0' values",
    ),
    test_data(
        """
        adjustments:
            exposure: -0
            contrast: -0.0
            temperature: -123.456
            tint: 123.456
            color_boost: 1.23456
        effects:
            grain: -0
            bloom: -0.0
            halation: 12345.6
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=-123.456, tint=123.456, color_boost=1.23456,
                       grain=0.0, bloom=0.0, halation=12345.6),
        id="Full valid adjustments and effects with non '0' values",
    ),
    test_data(
        """
        adjustments:
            exposure: abc
            contrast: "abc"
            temperature: []
            tint: {}
            color_boost: false
        effects:
            grain: 0x37
            bloom: 12.3015e+05
            halation: null
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=55.0, bloom=1230150.0, halation=PresetSettingsState.OFF),
        id="Full valid adjustments and effects with invalid values",
    ),
    test_data(
        """
        adjustments:
        exposure: 2.2
        contrast: 10
        temperature: -10
        tint: -22
        color_boost: 0
        effects:
        grain: Off
        bloom: Off
        halation: Off
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Full valid adjustments and effects with invalid indent (to the left)",
    ),
    test_data(
        """
        adjustments:
                exposure: 1.1
                contrast: 2
                temperature: 3.3
                tint: -4.4
                color_boost: -5
        effects:
                grain: 1
                bloom: 2
                halation: 3
        """,
        PresetSettings(exposure=1.1, contrast=2.0, temperature=3.3, tint=-4.4, color_boost=-5.0,
                       grain=1.0, bloom=2.0, halation=3.0),
        id="Full valid adjustments and effects with invalid indent (to the right - straight line)",
    ),
    test_data(
        """
        adjustments:
            exposure: 1.1
                contrast: 2
                    temperature: 3.3
                tint: -4.4
                color_boost: -5
        effects:
                grain: 1
            bloom: 2
                halation: 3
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Full valid adjustments and effects with invalid indent (to the right - curve line)",
    ),
    test_data(
        """
        adjustments:
            exxposure: 1.2
            contrast: -2.3
            temperaure: 3.4
            teent: -4.5
            color_boost: 5.6
        effects:
            grain: -6.7
            blum: 7.8
            halation: -8.9
        """,
        PresetSettings(exposure=0.0, contrast=-2.3, temperature=0.0, tint=0.0, color_boost=5.6,
                       grain=-6.7, bloom=PresetSettingsState.OFF, halation=-8.9),
        id="Full valid adjustments and effects with typos in settings names",
    ),
    test_data(
        """
        adjustments:
            exposure: 2.2
            contrast: 10
            temperature: -10
            tint -22
            color_boost: 0
        effects:
            grain: Off
            bloom: Off
            halation: Off
        """,
        PresetSettings(exposure=0.0, contrast=0.0, temperature=0.0, tint=0.0, color_boost=0.0,
                       grain=PresetSettingsState.OFF, bloom=PresetSettingsState.OFF, halation=PresetSettingsState.OFF),
        id="Full valid adjustments and effects with syntax error",
    ),
])
def test_read_settings_file_returns_dict_with_settings(settings_file_content: str, expected_result: PresetSettings):
    # Arrange: create temporary settings file with content
    with NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file:
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
    test_data("non_existent_file.txt", False, id="Non-existent txt file"),  # noqa: FBT003
    test_data(Path.cwd(), False, id="Current working directory"),  # noqa: FBT003
    test_data("", False, id="Empty string"),  # noqa: FBT003
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
    test_data(b"\xff\xd8\xff", "jpeg", True, id="JPEG file"),  # noqa: FBT003
    test_data(b"\x49\x49\x2A\x00", "tiff", True, id="TIFF file"),  # noqa: FBT003
    # TODO: Added valid file content for '*.heif', '*.heic' and '*.avif' formats  # noqa: FIX002
    # (b"\x00\x00\x00\x18ftypheif", "heif", True),  # noqa: ERA001
    # (b"\x00\x00\x00\x18ftypheic", "heic", True),  # noqa: ERA001
    # (b"\x00\x00\x00\x18ftypavif", "avif", True),  # noqa: ERA001
    test_data(b"RIFF\x00\x00\x00\x00WEBPVP8 ", "webp", True, id="WEBP file"),  # noqa: FBT003
    test_data(b"MM\x00\x2a", "dng", True, id="DNG file"),  # noqa: FBT003
    test_data(b"\x89PNG\r\n\x1a\n", "png", True, id="PNG file"),  # noqa: FBT003
    test_data(b"dummy content", "txt", False, id="TXT file"),  # noqa: FBT003
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
@pytest.mark.parametrize(("file_path", "expected_result"), [
    ("/path/to/file/example.txt", "txt"),
    ("/path/to/file/archive.tar.gz", "gz"),
    ("/path/to/file/image.jpg", "jpg"),
    ("/path/to/file/no_extension", ""),
    ("/path/to/file/.hidden", ""),
    ("/path/to/file/.dotfile", ""),
    ("/path/to/file/double.extension.zip", "zip"),
    ("/path/to/file/anotherfile.tar.bz2", "bz2"),
    ("example.txt", "txt"),
    ("archive.tar.gz", "gz"),
    ("image.jpg", "jpg"),
    ("no_extension", ""),
    (".hidden", ""),
    ("dotfile.", ""),
    ("double.extension.zip", "zip"),
    ("complex.file.name.with.many.dots.md", "md"),
])
def test_get_file_extension_returns_extension(file_path: str, expected_result: str):
    # Act: perform method under test & Assert
    assert get_file_extension(file_path) == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(
    ("status_code", "dir_exists_before", "expected_logging"), [
        test_data(200, False, "File 'https://example.com/file.txt' downloaded successfully.",  # noqa: FBT003
                  id="Response '200 OK', directory to download file exists"),
        test_data(200, True, "File 'https://example.com/file.txt' downloaded successfully.",  # noqa: FBT003
                  id="Response '200 OK', directory to download file doesn't exist"),
        test_data(404, False, "Failed to download the file 'https://example.com/file.txt'. Status code: 404",  # noqa: FBT003
                  id="Response '404 Not Found'"),
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


@pytest.mark.unit
@pytest.mark.parametrize(
    ("paths", "expected_result"), [
        test_data(("file.txt",), "/safe/base/file.txt", id="Single file"),
        test_data(("subdir", "file.txt"), "/safe/base/subdir/file.txt", id="Path join"),
        test_data(("dir1", "dir2", "file.txt"), "/safe/base/dir1/dir2/file.txt", id="Nested directories"),
        test_data(("dir with spaces", "file.txt"), "/safe/base/dir with spaces/file.txt",
                  id="Special characters"),
        test_data(("dir%20with%20spaces", "file.txt"), "/safe/base/dir with spaces/file.txt",
                  id="URL-encoded special characters"),
        test_data(("", "file.txt"), "/safe/base/file.txt", id="Empty strings in paths"),
        test_data(("unicode_dir", "файл.txt"), "/safe/base/unicode_dir/файл.txt", id="Unicode characters"),
    ],
)
def test_safe_join_returns_safe_path(paths: tuple[str, ...], expected_result: str):
    # Arrange: init base directory
    base = "/safe/base"
    # Act: perform method under test and get result
    result = safe_join(base, *paths)
    # Assert
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(
    "paths", [
        test_data(("..", "file.txt"), id="Path traversal detection"),
        test_data(("%2E%2E", "file.txt"), id="URL encoded path traversal"),
        test_data(("/etc", "passwd"), id="Absolute path traversal"),
        test_data(("..", "..", "file.txt"), id="Multiple traversal levels"),
        test_data(("subdir", "..", "..", "file.txt"), id="Mixed traversal levels"),
        test_data(("subdir", "%2E%2E", "%2E%2E", "file.txt"), id="Mixed encoded traversal"),
    ],
)
def test_safe_join_for_path_traversals_raises_error(paths: tuple[str, ...]):
    # Arrange: init base directory
    base = "/safe/base"
    # Assert: 'ValueError' error occurs with corresponding message
    with pytest.raises(ValueError, match="Attempted path traversal detected"):
        # Act: perform method under test
        safe_join(base, *paths)

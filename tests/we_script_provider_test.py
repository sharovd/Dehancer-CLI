from unittest.mock import patch

import pytest
from pytest import param as test_data  # noqa: PT013

from src.api.constants import ENCODING_UTF_8
from src.web_ext.we_script_provider import WebExtensionScriptProvider


@pytest.mark.unit
def test_is_original_script_exist_calls_is_file_exist() -> None:
    # Arrange: setup mock object
    with patch("src.web_ext.we_script_provider.is_file_exist", return_value=True) as mock_is_file_exist:
        # Act: perform method under test
        result = WebExtensionScriptProvider._is_original_script_exist() # noqa: SLF001
        # Assert: verify the expected method call
        mock_is_file_exist.assert_called_once_with(str(WebExtensionScriptProvider.ORIGINAL_SCRIPT))
        # Assert: check that the method result contains the expected data
        assert result is True


@pytest.mark.unit
def test_is_obfuscated_script_exist_calls_is_file_exist() -> None:
    # Arrange: setup mock object
    with patch("src.web_ext.we_script_provider.is_file_exist", return_value=True) as mock_is_file_exist:
        # Act: perform method under test
        result = WebExtensionScriptProvider._is_obfuscated_script_exist() # noqa: SLF001
        # Assert: verify the expected method call
        mock_is_file_exist.assert_called_once_with(str(WebExtensionScriptProvider.OBFUSCATED_SCRIPT))
        # Assert: check that the method result contains the expected data
        assert result is True


@pytest.mark.unit
def test_get_original_script_minified_data_calls_read_text_and_jsmin() -> None:
    original_script_content = "function test() { console.log('original'); }"
    minified_script_content = "function test(){console.log('original');}"
    # Arrange: setup mock objects
    with patch("pathlib.Path.read_text", return_value=original_script_content) as mock_read_text, \
         patch("src.web_ext.we_script_provider.jsmin", return_value=minified_script_content) as mock_jsmin:
        # Act: perform method under test
        result = WebExtensionScriptProvider._get_original_script_minified_data() # noqa: SLF001
        # Assert: verify all the expected method calls
        mock_read_text.assert_called_once_with(encoding=ENCODING_UTF_8)
        mock_jsmin.assert_called_once_with(original_script_content)
        # Assert: check that the method result contains the expected data
        assert result == minified_script_content


@pytest.mark.unit
def test_get_obfuscated_script_data_calls_read_text() -> None:
    obfuscated_script_content = "(function(_0x299a1d,_0x48c891)"
    # Arrange: setup mock object
    with patch("pathlib.Path.read_text", return_value=obfuscated_script_content) as mock_read_text:
        # Act: perform method under test
        result = WebExtensionScriptProvider._get_obfuscated_script_data() # noqa: SLF001
        # Assert: verify the expected method call
        mock_read_text.assert_called_once_with(encoding=ENCODING_UTF_8)
        # Assert: check that the method result contains the expected data
        assert result == obfuscated_script_content


@pytest.mark.unit
@pytest.mark.parametrize(("is_original_script_exist", "is_obfuscated_script_exist",
                          "original_script_minified_data", "obfuscated_script_data",
                          "expected_result"), [
    test_data(True, True, "original", "obfuscated", "obfuscated", # noqa: FBT003
              id="Original and obfuscated scripts available"),
    test_data(True, False, "original", "obfuscated", "original", # noqa: FBT003
              id="Only original script available"),
    test_data(False, True, "original", "obfuscated", "obfuscated", # noqa: FBT003
              id="Only obfuscated script available"),
])
def test_get_script_content_returns_expected_content(is_original_script_exist: bool, is_obfuscated_script_exist: bool,  # noqa: FBT001
                                                     original_script_minified_data: str, obfuscated_script_data: str,
                                                     expected_result: str):
    # Arrange: setup mock objects
    with (patch.object(WebExtensionScriptProvider, "_is_original_script_exist",
                       return_value=is_original_script_exist),
          patch.object(WebExtensionScriptProvider, "_is_obfuscated_script_exist",
                       return_value=is_obfuscated_script_exist),
          patch.object(WebExtensionScriptProvider, "_get_original_script_minified_data",
                       return_value=original_script_minified_data),
          patch.object(WebExtensionScriptProvider, "_get_obfuscated_script_data",
                       return_value=obfuscated_script_data)):
        # Act: perform method under test
        content = WebExtensionScriptProvider.get_script_content()
        # Assert: check that the method result contains the expected data
        assert content == expected_result


@pytest.mark.unit
def test_get_script_content_throws_fnf_error():
    # Arrange: setup mock objects
    with (patch.object(WebExtensionScriptProvider, "_is_original_script_exist", return_value=False),
          patch.object(WebExtensionScriptProvider, "_is_obfuscated_script_exist", return_value=False),
          # Assert: check that the expected failure caused by the tested method
          pytest.raises(FileNotFoundError, match="Script not found")):
        # Act: perform method under test
        WebExtensionScriptProvider.get_script_content()

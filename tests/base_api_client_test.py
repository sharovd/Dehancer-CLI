from unittest.mock import Mock, patch

import pytest
from pytest import param as test_data  # noqa: PT013
from requests import Session
from requests.models import Response
from requests.structures import CaseInsensitiveDict

from src.api.clients.base_api_client import LARGE_BODY_PLACEHOLDER, BaseAPIClient


@pytest.fixture
def base_api_client() -> BaseAPIClient:
    return BaseAPIClient()


@pytest.mark.unit
def test_init_have_session_initialization(base_api_client: BaseAPIClient):
    assert isinstance(base_api_client.session, Session), \
        "Session should be initialized as a requests.Session instance"


@pytest.mark.unit
def test_init_have_logging_hook(base_api_client: BaseAPIClient):
    assert base_api_client.logging_hook in base_api_client.session.hooks["response"], \
        "Logging hook should be added to session hooks"


@pytest.mark.unit
def test_set_session_cookies_with_empty_dict_do_nothing(base_api_client: BaseAPIClient):
    # Act: perform method under test
    base_api_client.set_session_cookies({})
    # Assert: check that there are no cookies in the session
    assert len(base_api_client.session.cookies) == 0


@pytest.mark.unit
def test_set_session_cookies_with_single_value_adds_it(base_api_client: BaseAPIClient):
    # Arrange: define test data
    cookies = {"test-cookie": "test-value"}
    # Act: perform method under test
    base_api_client.set_session_cookies(cookies)
    # Assert: check expected cookies in the session
    assert base_api_client.session.cookies["test-cookie"] == "test-value"


@pytest.mark.unit
def test_set_session_cookies_with_multiple_values_adds_it(base_api_client: BaseAPIClient):
    # Arrange: define test data
    cookies = {
        "cookie1": "value1",
        "cookie2": "value2",
        "cookie3": "value3",
    }
    # Act: perform method under test
    base_api_client.set_session_cookies(cookies)
    # Assert: check expected cookies in the session
    for name, value in cookies.items():
        assert base_api_client.session.cookies[name] == value


@pytest.mark.unit
def test_set_session_cookies_overwrites_existing_cookie(base_api_client: BaseAPIClient):
    # Arrange: define test data
    base_api_client.session.cookies.set("cookie", "old-value")
    # Act: perform method under test
    cookies = {"cookie": "new-value"}
    base_api_client.set_session_cookies(cookies)
    # Assert: check expected cookies in the session
    assert base_api_client.session.cookies["cookie"] == "new-value"


@pytest.mark.unit
@pytest.mark.parametrize(("request_body", "request_headers", "response_headers", "expected_raw_data"), [
    test_data(
        b"text request",
        CaseInsensitiveDict({"Content-Type": "text/plain"}),
        CaseInsensitiveDict({"Content-Type": "text/plain"}),
        "Mock dump output",
        id="Text content without replacement",
    ),
    test_data(
        b"binary data",
        CaseInsensitiveDict({"Content-Type": "image/jpeg", "Content-Length": "1000000"}),
        CaseInsensitiveDict({"Content-Type": "text/plain"}),
        "headers\n\n<body removed: binary content>",
        id="Large binary request body",
    ),
    test_data(
        b"small request",
        CaseInsensitiveDict({"Content-Type": "text/plain"}),
        CaseInsensitiveDict({"Content-Type": "image/jpeg", "Content-Length": "1000000"}),
        "headers\n\n<body removed: binary content>",
        id="Large binary response body",
    ),
])
def test_logging_hook_logs_request_and_response_data_with_debug_level(request_body: bytes,
                                                                      request_headers: CaseInsensitiveDict,
                                                                      response_headers: CaseInsensitiveDict,
                                                                      expected_raw_data: str):
    with patch("src.api.clients.base_api_client.dump.dump_all") as mock_dump_all, \
            patch("src.api.clients.base_api_client.logging.debug") as mock_logging_debug:
        # Arrange: setup mock objects
        mock_request = Mock()
        mock_request.body = request_body
        mock_request.headers = request_headers
        mock_response = Mock(spec=Response)
        mock_response.request = mock_request
        mock_response.headers = response_headers
        mock_dump_all.return_value = expected_raw_data.encode("utf-8")
        # Act: perform method under test
        BaseAPIClient.logging_hook(mock_response)
        # Assert: check that the expected methods have been called
        mock_dump_all.assert_called_once_with(mock_response, request_prefix=b"> ", response_prefix=b"< ")
        if BaseAPIClient.should_replace_large_body(request_headers):
            # Assert: Check that the large request body has been replaced in the placeholder
            mock_logging_debug.assert_called_once()
            logged_data = mock_logging_debug.call_args[0][0]
            assert LARGE_BODY_PLACEHOLDER in logged_data
            assert request_body.decode("utf-8", errors="replace") not in logged_data
        elif BaseAPIClient.should_replace_large_body(response_headers):
            # Assert: Check that the large response body has been replaced in the placeholder
            mock_logging_debug.assert_called_once()
            logged_data = mock_logging_debug.call_args[0][0]
            assert LARGE_BODY_PLACEHOLDER in logged_data
            assert "headers\n\n" in logged_data
        else:
            # Assert: check that the raw data has been logged without having changed
            mock_logging_debug.assert_called_once_with(expected_raw_data)


@pytest.mark.unit
@pytest.mark.parametrize(("headers", "max_size", "expected_result"), [
    test_data(CaseInsensitiveDict({"Content-Length": "50000"}), 100_000, False, # noqa: FBT003
              id="Content smaller than max size"),
    test_data(CaseInsensitiveDict({"Content-Length": "150000"}), 100_000, True, # noqa: FBT003
              id="Content larger than max size"),
    test_data(CaseInsensitiveDict({"Content-Length": "100000"}), 100_000, False, # noqa: FBT003
              id="Content equal to max size"),
    test_data(CaseInsensitiveDict({}), 100_000, False, # noqa: FBT003
              id="No Content-Length header"),
    test_data(CaseInsensitiveDict({"Content-Length": "invalid"}), 100_000, False, # noqa: FBT003
              id="Invalid Content-Length value"),
    test_data(CaseInsensitiveDict({"Content-Length": "-1"}), 100_000, False, # noqa: FBT003
              id="Negative Content-Length value"),
])
def test_is_large_content_checks_content_size(headers: CaseInsensitiveDict, max_size: int, expected_result: bool):  # noqa: FBT001
    # Act: perform method under test
    actual_result = BaseAPIClient.is_large_content(headers, max_size)
    # Assert
    assert actual_result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(("headers", "expected_result"), [
    test_data(CaseInsensitiveDict({"Content-Type": "image/jpeg"}), True, # noqa: FBT003
              id="Image content type"),
    test_data(CaseInsensitiveDict({"Content-Type": "video/mp4"}), True, # noqa: FBT003
              id="Video content type"),
    test_data(CaseInsensitiveDict({"Content-Type": "audio/mpeg"}), True, # noqa: FBT003
              id="Audio content type"),
    test_data(CaseInsensitiveDict({"Content-Type": "application/octet-stream"}), True, # noqa: FBT003
              id="Octet-stream content type"),
    test_data(CaseInsensitiveDict({"Content-Type": "text/plain"}), False, # noqa: FBT003
              id="Text content type"),
    test_data(CaseInsensitiveDict({"Content-Type": "application/json"}), False, # noqa: FBT003
              id="JSON content type"),
    test_data(CaseInsensitiveDict({}), False, # noqa: FBT003
              id="No Content-Type header"),
    test_data(CaseInsensitiveDict({"Content-Type": ""}), False, # noqa: FBT003
              id="Empty Content-Type"),
])
def test_is_binary_content_checks_content_type(headers: CaseInsensitiveDict, expected_result: bool):  # noqa: FBT001
    # Act: perform method under test
    actual_result = BaseAPIClient.is_binary_content(headers)
    # Assert
    assert actual_result == expected_result


@pytest.mark.unit
@pytest.mark.parametrize(("headers", "expected_result"), [
    test_data(CaseInsensitiveDict({
        "Content-Type": "image/jpeg",
        "Content-Length": "50000",
    }), True, id="Binary content with normal size"), # noqa: FBT003
    test_data(CaseInsensitiveDict({
        "Content-Type": "application/octet-stream",
        "Content-Length": "150000",
    }), True, id="Binary content with large size"),  # noqa: FBT003
    test_data(CaseInsensitiveDict({
        "Content-Type": "text/plain",
        "Content-Length": "150000",
    }), True, id="Text content with large size"), # noqa: FBT003
    test_data(CaseInsensitiveDict({
        "Content-Type": "application/json",
        "Content-Length": "50000",
    }), False, id="JSON content with normal size"), # noqa: FBT003
    test_data(CaseInsensitiveDict({
        "Content-Type": "text/plain",
        "Content-Length": "50000",
    }), False, id="Text content with normal size"), # noqa: FBT003
    test_data(CaseInsensitiveDict({}), False, # noqa: FBT003
              id="No headers"),
])
def test_should_replace_large_body_content_size_and_type(headers: CaseInsensitiveDict, expected_result: bool): # noqa: FBT001
    # Act: perform method under test
    actual_result = BaseAPIClient.should_replace_large_body(headers)
    # Assert
    assert actual_result == expected_result

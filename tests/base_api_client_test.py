from unittest.mock import Mock, patch

import pytest
from requests import Session
from requests.models import Response

from src.api.clients.base_api_client import BaseAPIClient


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
def test_logging_hook_logs_request_and_response_data_with_debug_level(base_api_client: BaseAPIClient):
    with patch("src.api.clients.base_api_client.dump.dump_all") as mock_dump_all, \
            patch("src.api.clients.base_api_client.logging.debug") as mock_logging_debug:
        # Arrange: setup mock objects
        mock_response = Mock(spec=Response, content=b"Mock content")
        mock_dump_all.return_value = b"Mock dump output"
        # Act: perform method under test
        base_api_client.logging_hook(mock_response)
        # Assert: check that the expected method have been called by the tested method
        mock_dump_all.assert_called_once_with(mock_response)
        # Assert: check that the expected message has been printed in the logs
        mock_logging_debug.assert_called_once_with("Mock dump output")

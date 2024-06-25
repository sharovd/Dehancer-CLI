from unittest.mock import Mock, patch

import pytest
from requests import Session
from requests.models import Response

from src.api.clients.base_api_client import BaseAPIClient


@pytest.fixture()
def base_api_client():
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

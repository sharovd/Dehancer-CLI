import shutil
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest
from diskcache import Cache

from src.cache.cache_manager import CacheManager


@pytest.fixture()
def cache_manager() -> Iterator[CacheManager]:
    cache_manager = CacheManager("test-application")
    yield cache_manager
    shutil.rmtree(cache_manager.cache_dir, ignore_errors=True)


@pytest.mark.unit
def test_cache_manager_initialization_on_unix_machine():
    # Arrange: setup mock objects
    with patch("src.cache.cache_manager.Cache") as mock_cache, \
            patch("pathlib.Path.mkdir") as mock_mkdir, \
            patch("os.name", "posix"):
        # Act: perform method under test
        cache_manager = CacheManager(application_name="test-application")
        expected_cache_dir = Path.home() / ".test-application"
        # Assert: check that the expected methods have been called by the tested method
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_cache.assert_called_once_with(directory=str(expected_cache_dir))
        # Assert: check that the cache directory after initialization contains the expected result
        assert cache_manager.cache_dir == expected_cache_dir


@pytest.mark.unit
def test_cache_manager_initialization_on_windows_machine(monkeypatch):  # noqa: ANN001
    # Arrange: setup mock objects
    monkeypatch.setenv("FORCE_WINDOWS_PATH", "1")
    monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\Test\\AppData\\Local")
    with patch("src.cache.cache_manager.Cache") as mock_cache, patch("pathlib.Path.mkdir") as mock_mkdir:
        # Act: perform method under test
        cache_manager = CacheManager(application_name="test-application")
        expected_cache_dir = Path("C:\\Users\\Test\\AppData\\Local") / "test-application"
        # Assert: check that the expected methods have been called by the tested method
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_cache.assert_called_once_with(directory=str(expected_cache_dir))
        # Assert: check that the cache directory after initialization contains the expected result
        assert cache_manager.cache_dir == expected_cache_dir


@pytest.mark.unit
def test_set_cache_calls_set_method(cache_manager: CacheManager):
    # Arrange: setup mock objects
    with patch.object(Cache, "set") as mock_cache_set:
        # Act: perform method under test
        cache_manager.set("test_key", "test_value", expire=3600)
        # Assert: check that the expected method have been called by the tested method
        mock_cache_set.assert_called_once_with("test_key", "test_value", expire=3600)


@pytest.mark.unit
def test_get_cache_for_existent_key_returns_value(cache_manager: CacheManager):
    # Arrange: setup mock objects
    with patch.object(Cache, "get", return_value="cached_value") as mock_cache_get:
        # Act: perform method under test
        result = cache_manager.get("test_key")
        # Assert: check that the expected method have been called by the tested method
        mock_cache_get.assert_called_once_with("test_key")
        # Assert: check that the method result contains the expected result
        assert result == "cached_value"


@pytest.mark.unit
def test_get_cache_for_nonexistent_key_returns_none(cache_manager: CacheManager):
    # Act: perform method under test
    actual_result = cache_manager.get("nonexistent_key")
    # Assert: check that the method result contains the expected result
    assert actual_result is None


@pytest.mark.unit
def test_delete_cache_calls_delete_method(cache_manager: CacheManager):
    # Arrange: setup mock objects
    with patch.object(Cache, "delete") as mock_cache_delete:
        # Act: perform method under test
        cache_manager.delete("test_key")
        # Assert: check that the expected method have been called by the tested method
        mock_cache_delete.assert_called_once_with("test_key")


@pytest.mark.unit
def test_clear_cache_calls_clear_method(cache_manager: CacheManager):
    with patch.object(Cache, "clear") as mock_cache_clear:
        # Act: perform method under test
        cache_manager.clear()
        # Assert: check that the expected method have been called by the tested method
        mock_cache_clear.assert_called_once()

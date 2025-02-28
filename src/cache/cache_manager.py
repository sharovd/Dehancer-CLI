from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from diskcache import Cache

from src import app_name

T = TypeVar("T")

class CacheManager:
    """
    A cache manager class for handling disk-based caching operations.

    This class provides methods for storing and retrieving cached data, with configurable location and expiration time,
    As well as methods for deleting cached data by key and clearing all cached data.

    Attributes
    ----------
    cache_dir: Path
        The directory where cache files are stored.
    cache: Cache
        The disk-based cache instance.

    """

    def __init__(self, application_name: str = app_name) -> None:
        self.cache_dir = self._get_cache_directory(application_name)
        self.cache = Cache(directory=str(self.cache_dir))

    @staticmethod
    def _get_cache_directory(application_name: str) -> Path:
        r"""
        Get application cache directory.

        Directory structure examples:
            - Windows: C:\\Users\\<username>\\AppData\\Local\\<application_name>
            - Linux/Mac: ~/.<application_name>

        Args:
        ----
            application_name (str): Application name.

        Returns:
        -------
            Path: Cache directory path.

        """
        if os.name == "nt" or os.getenv("FORCE_WINDOWS_PATH") == "1":  # Windows or test mode for unit-tests on Unix
            base_dir = Path(os.getenv("LOCALAPPDATA", ""))
            cache_dir = base_dir / application_name
        else:  # Linux/Mac
            base_dir = Path.home()
            cache_dir = base_dir / f".{application_name.lower()}"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def get(self, key: str) -> T | None:
        """
        Return the value from cache.

        Args:
        ----
            key (str): The key to retrieve from cache.

        Returns:
        -------
            T | None: The cached value if it exists and hasn't expired, None otherwise.

        """
        return self.cache.get(key)

    def set(self, key: str, value: T, expire: int = 86400) -> None:
        """
        Set a value in the cache.

        Args:
        ----
            key (str): The key under which to store the value.
            value (T): The value to store.
            expire (int): Time in seconds after which the value expires. Defaults to 86400 seconds (1 day).

        """
        self.cache.set(key, value, expire=expire)

    def delete(self, key: str) -> None:
        """
        Delete a value in the cache.

        Args:
        ----
            key (str): The key under which to delete the value.

        """
        self.cache.delete(key)

    def clear(self) -> None:
        """
        Clear all cached data.

        Returns
        -------
            None

        """
        self.cache.clear()

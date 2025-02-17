from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cache.cache_manager import CacheManager


class CacheBackupContext:
    """
    A context manager class for backing up and restoring cache data.

    This class provides functionality to backup cache data
    before performing certain operations and to restore them afterward.
    It ensures that any cache data modified or created during the operations are removed,
    and the original state of the cache is restored.
    """

    def __init__(self, cache_manager: CacheManager, keys_to_backup: list[str]) -> None:
        """
        Initialize the CacheBackupContext with the specified cache manager and keys.

        Parameters
        ----------
        cache_manager : CacheManager
            The cache manager instance.
        keys_to_backup : list[str]
            The list of cache keys to be backed up and restored.

        """
        self.cache_manager = cache_manager
        self.keys_to_backup = keys_to_backup
        self.backup_data = {}

    def backup_cache(self) -> None:
        """Backup cache values for the specified keys."""
        for key in self.keys_to_backup:
            value = self.cache_manager.get(key)
            if value is not None:
                self.backup_data[key] = value

    def restore_cache(self) -> None:
        """Restore backed-up cache values."""
        for key, value in self.backup_data.items():
            self.cache_manager.set(key, value)

    def __enter__(self) -> "CacheBackupContext":  # noqa: UP037
        """
        Enter the context manager, backing up cache values.

        Returns
        -------
        CacheBackupContext
            The context manager instance with cache values backed up.

        """
        self.backup_cache()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """
        Exit the context manager, restoring cached values.

        Parameters
        ----------
        exc_type
            The exception type, if any exception was raised.
        exc_val
            The exception instance, if any exception was raised.
        exc_tb
            The traceback object, if any exception was raised.

        """
        self.restore_cache()

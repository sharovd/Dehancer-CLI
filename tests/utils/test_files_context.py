import shutil
import time
from pathlib import Path


class FileBackupContext:
    """
    A context manager class for backing up and restoring files in a directory.

    This class provides functionality to backup files in a specified directory
    before performing certain operations and to restore them afterward.
    It ensures that any files modified or created during the operations are removed,
    and the original state of the directory is restored.
    """

    def __init__(self, path_to_backup: str) -> None:
        """
        Initialize the FileBackupContext with the specified directory or file path.

        Parameters
        ----------
        path_to_backup: str
            The path to the directory or file to be backed up and restored.

        """
        self.path_to_backup = Path(path_to_backup)
        self.files_to_backup = []
        self.backup_path = self._get_backup_path()

    def _get_backup_path(self) -> Path:
        """Determine the backup path based on whether it's a file or directory."""
        if self.path_to_backup.is_dir():
            return self.path_to_backup.parent / f"backup_{self.path_to_backup.name}_{int(time.time())}"
        return self.path_to_backup.with_name(f"backup_{self.path_to_backup.name}")

    def _backup_directory(self) -> None:
        """Backup all files in the specified directory."""
        if not self.path_to_backup.exists():
            return
        self.backup_path.mkdir(parents=True, exist_ok=True)
        for file in self.path_to_backup.iterdir():
            if not file.name.startswith("backup_"):
                backup_file_path = self.backup_path / file.name
                if file.is_dir():
                    shutil.copytree(file, backup_file_path)
                else:
                    shutil.copy(file, backup_file_path)
                self.files_to_backup.append((file, backup_file_path))

    def _backup_file(self) -> None:
        """Backup the specified file."""
        if self.path_to_backup.exists():
            shutil.copy(self.path_to_backup, self.backup_path)
            self.files_to_backup.append((self.path_to_backup, self.backup_path))

    def _restore_directory(self) -> None:
        """Restore files in the directory from the backup."""
        for file in self.path_to_backup.iterdir():
            if not file.name.startswith("backup_"):
                if file.is_dir():
                    shutil.rmtree(file)
                else:
                    file.unlink()
        for original_path, backup_path in self.files_to_backup:
            if backup_path.is_dir():
                shutil.copytree(backup_path, original_path)
            else:
                shutil.copy(backup_path, original_path)

    def _restore_file(self) -> None:
        """Restore the file from the backup."""
        if self.backup_path.exists():
            shutil.copy(self.backup_path, self.path_to_backup)

    def backup(self) -> None:
        """Perform backup based on whether the path is a file or directory."""
        if self.path_to_backup.is_dir():
            self._backup_directory()
        elif self.path_to_backup.is_file():
            self._backup_file()

    def restore(self) -> None:
        """Restore from backup based on whether the path is a file or directory."""
        if self.path_to_backup.is_dir():
            self._restore_directory()
            shutil.rmtree(self.backup_path)
        elif self.path_to_backup.is_file():
            self._restore_file()
            self.backup_path.unlink()

    def __enter__(self) -> "FileBackupContext":
        """
        Enter the context manager, backing up files in the specified directory or single file.

        Returns
        -------
        FileBackupContext
            The context manager instance with files backed up.

        """
        self.backup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """
        Exit the context manager, restoring files to their original locations.

        Parameters
        ----------
        exc_type
            The exception type, if any exception was raised.
        exc_val
            The exception instance, if any exception was raised.
        exc_tb
            The traceback object, if any exception was raised.

        """
        self.restore()

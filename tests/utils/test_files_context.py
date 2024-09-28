import os
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
        backup_name = f"backup_{int(time.time())}_{self.path_to_backup.name}"
        if self.path_to_backup.is_dir():
            return self.path_to_backup.parent / backup_name
        return self.path_to_backup.with_name(backup_name)

    def backup_directory(self) -> None:
        """
        Backs up files in the specified directory, excluding any existing backup directories.

        This method creates a backup of all files and subdirectories in the specified directory,
        except those beginning with 'backup_'.
        It then removes the original files and directories to prepare for new operations.
        """
        if Path(self.path_to_backup).exists() and len(os.listdir(self.path_to_backup)) != 0:
            Path(self.backup_path).mkdir(parents=True)
            for file in os.listdir(self.path_to_backup):
                if not file.startswith("backup_"):
                    src_path = os.path.join(self.path_to_backup, file)
                    backup_path = os.path.join(self.backup_path, file)
                    if Path(src_path).is_dir():
                        shutil.copytree(src_path, backup_path)
                        shutil.rmtree(src_path)
                    else:
                        shutil.copy(src_path, backup_path)
                        Path(src_path).unlink()
                    self.files_to_backup.append((src_path, backup_path))

    def backup_file(self) -> None:
        """
        Backs up single file.

        This method creates a backup of the file in the specified path.
        It then removes the original file to prepare for new operations.
        """
        if Path(self.path_to_backup).exists() and Path(self.path_to_backup).is_file():
            shutil.copy(self.path_to_backup, self.backup_path)
            Path(self.path_to_backup).unlink()
            self.files_to_backup.append((self.path_to_backup, self.backup_path))

    def restore_files(self) -> None:
        """
        Restore files from the backup directory to their original locations.

        This method clears the specified directory of any new files or directories created during operations,
        and then restores the original files and directories from the backup.
        The backup directory is removed after the restoration.
        """
        if Path(self.path_to_backup).is_dir():
            # Clear the directory before restoring files
            for file in os.listdir(self.path_to_backup):
                if not file.startswith("backup_"):
                    file_path = os.path.join(self.path_to_backup, file)
                    if Path(file_path).is_dir():
                        shutil.rmtree(file_path)
                    else:
                        Path(file_path).unlink()
        # Restore files from the backup
        for src_path, backup_path in self.files_to_backup:
            if Path(backup_path).is_dir():
                shutil.copytree(backup_path, src_path)
            else:
                shutil.copy(backup_path, src_path)
        # Remove the backup directory
        if self.backup_path is not None and Path(self.backup_path).is_dir():
            shutil.rmtree(self.backup_path)
        # Remove the backup file
        if self.backup_path is not None and Path(self.backup_path).is_file():
            Path(self.backup_path).unlink()

    def __enter__(self) -> "FileBackupContext":
        """
        Enter the context manager, backing up files in the specified directory or single file.

        Returns
        -------
        FileBackupContext
            The context manager instance with files backed up.

        """
        if Path(self.path_to_backup).is_dir():
            self.backup_directory()
        if Path(self.path_to_backup).is_file():
            self.backup_file()
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
        self.restore_files()

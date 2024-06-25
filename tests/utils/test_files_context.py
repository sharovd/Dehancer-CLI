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

    def __init__(self, directory: str) -> None:
        """
        Initialize the FileBackupContext with the specified directory.

        Parameters
        ----------
        directory : str
            The path to the directory where files will be backed up and restored.

        """
        self.directory = directory
        self.backup_dir = os.path.join(directory, f"backup_{int(time.time())}")
        self.files_to_backup = []

    def backup_files(self) -> None:
        """
        Backs up files in the specified directory, excluding any existing backup directories.

        This method creates a backup of all files and subdirectories in the specified directory,
        except those beginning with 'backup_'.
        It then removes the original files and directories to prepare for new operations.
        """
        if len(os.listdir(self.directory)) != 0:
            Path(self.backup_dir).mkdir(parents=True)
            for file in os.listdir(self.directory):
                if not file.startswith("backup_"):
                    src_path = os.path.join(self.directory, file)
                    backup_path = os.path.join(self.backup_dir, file)
                    if Path(src_path).is_dir():
                        shutil.copytree(src_path, backup_path)
                        shutil.rmtree(src_path)
                    else:
                        shutil.copy(src_path, backup_path)
                        Path(src_path).unlink()
                    self.files_to_backup.append((src_path, backup_path))

    def restore_files(self) -> None:
        """
        Restore files from the backup directory to their original locations.

        This method clears the specified directory of any new files or directories created during operations,
        and then restores the original files and directories from the backup.
        The backup directory is removed after the restoration.
        """
        # Clear the directory before restoring files
        for file in os.listdir(self.directory):
            if not file.startswith("backup_"):
                file_path = os.path.join(self.directory, file)
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
        if Path(self.backup_dir).is_dir():
            shutil.rmtree(self.backup_dir)

    def __enter__(self) -> "FileBackupContext":
        """
        Enter the context manager, backing up files in the specified directory.

        Returns
        -------
        FileBackupContext
            The context manager instance with files backed up.

        """
        self.backup_files()
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

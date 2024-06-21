import os
import time
import shutil


class FileBackupContext:

    def __init__(self, directory):
        self.directory = directory
        self.backup_dir = os.path.join(directory, f"backup_{int(time.time())}")
        self.files_to_backup = []

    def backup_files(self) -> None:
        if not len(os.listdir(self.directory)) == 0:
            os.makedirs(self.backup_dir, exist_ok=True)
            for file in os.listdir(self.directory):
                if not file.startswith("backup_"):
                    src_path = os.path.join(self.directory, file)
                    backup_path = os.path.join(self.backup_dir, file)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, backup_path)
                        shutil.rmtree(src_path)
                    else:
                        shutil.copy(src_path, backup_path)
                        os.remove(src_path)
                    self.files_to_backup.append((src_path, backup_path))

    def restore_files(self) -> None:
        # Clear the directory before restoring files
        for file in os.listdir(self.directory):
            if not file.startswith("backup_"):
                file_path = os.path.join(self.directory, file)
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        # Restore files from the backup
        for src_path, backup_path in self.files_to_backup:
            if os.path.isdir(backup_path):
                shutil.copytree(backup_path, src_path)
            else:
                shutil.copy(backup_path, src_path)
        # Remove the backup directory
        if os.path.isdir(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def __enter__(self):
        self.backup_files()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore_files()

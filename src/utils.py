import os
import imghdr
import mimetypes
from typing import Dict
import requests
import logging.config
import logging.handlers


def get_logger_config_file_path() -> str:
    """
    Returns the file path of the logger configuration file.
    Returns:
        str: The file path of the logger configuration file.
    """
    return "{root_dir}/configs/log_config.ini".format(root_dir=os.path.dirname(os.path.dirname(__file__)))


logging.config.fileConfig(get_logger_config_file_path())
logger = logging.getLogger()


def read_settings_file(file_path: str) -> dict[str, float]:
    """
    Reads a settings file and returns the settings as a dictionary.

    The settings file should have key-value pairs separated by '=' on each line.
    The method reads the file, splits each line into key-value pairs, and stores
    them in a dictionary. The values are converted to integers.

    Args:
        file_path (str): The path to the settings file.
    Returns:
        dict: A dictionary containing the settings with keys as strings and values as floats.
    Example:
        If the settings file contains:
        contrast=5
        exposure=10
        The returned dictionary will be: {'contrast': 5, 'exposure': 10}
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    settings = {}
    with open(file_path, "r") as file:
        for line in file:
            key_and_value = line.strip().split("=")
            if len(key_and_value) == 2 and key_and_value[1].strip():
                key, value = key_and_value
                try:
                    settings[key.strip()] = float(value.strip())
                except ValueError:
                    continue
    return settings


def is_file_exist(file_path: str) -> bool:
    """
    Checks if the file exists.
    Args:
        file_path (str): The path to the file to check.
    Returns:
        bool: True if the file is of a valid image type, False otherwise.
    """
    return os.path.isfile(file_path)


def is_supported_format_file(file_path: str, valid_types: Dict[str, str]) -> bool:
    """
    Checks if the specified file is of a supported format.

    This method checks if the file at the given file path matches any of the
    formats provided in the valid_types dictionary.
    It first uses the imghdr module to determine the file type
    and then checks the MIME type as a fallback.

    Args:
        file_path (str): The path to the file to check.
        valid_types (Dict[str, str]): A dictionary mapping file extensions to
                                      their corresponding MIME types.
    Returns:
        bool: True if the file matches any of the supported formats, False otherwise.
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    # Check format using imghdr
    file_type = imghdr.what(file_path)
    if file_type in valid_types:
        return True
    # Additional check using mimetypes (for types not covered by imghdr)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type in valid_types.values():
        return True
    return False


def get_filename_without_extension(file_path: str) -> str:
    """
    Extracts and returns the filename without its extension from the given file path.
    Args:
        file_path (str): The full path to the file.
    Returns:
        str: The filename without its extension.
    Example:
        >>> get_filename_without_extension("/path/to/file/example.txt")
        'example'
        >>> get_filename_without_extension("/path/to/file/archive.tar.gz")
        'archive.tar'
    """
    filename_with_extension = os.path.basename(file_path)
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    return filename_without_extension


def download_file(file_url: str, file_dir: str) -> None:
    """
    Downloads a file from the given URL and saves it to the specified directory.

    The method makes an HTTP GET request to the specified file URL and saves the response content to the specified directory.
    If the directory does not exist, it is created.
    The method logs a debug message upon successful download, or an error message if the download fails.

    Args:
        file_url (str): The URL of the file to be downloaded.
        file_dir (str): The directory where the file should be saved, including the file name.
    Returns:
        None
    Raises:
        Exception: If the file cannot be downloaded or saved.
    Example:
        download_file("https://example.com/file.txt", "/path/to/save/file.txt")
    """
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        directory = os.path.dirname(file_dir)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_dir, "wb") as fp:
            fp.write(response.content)
        logger.debug(f"File '{file_url}' downloaded successfully.")
    else:
        logger.error(f"Failed to download the file '{file_url}'. Status code: {response.status_code}")

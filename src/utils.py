from __future__ import annotations

import imghdr
import logging.config
import logging.handlers
import mimetypes
import urllib.parse
from pathlib import Path

import requests


def get_logger_config_file_path() -> str:
    """
    Return the file path of the logger configuration file.

    Returns
    -------
        str: The file path of the logger configuration file.

    """
    return f"{Path(Path(__file__).parent).parent}/configs/log_config.ini"


logging.config.fileConfig(get_logger_config_file_path())
logger = logging.getLogger()


def read_settings_file(file_path: str) -> dict[str, float]:
    """
    Read a settings file and return the settings as a dictionary.

    The settings file should have key-value pairs separated by '=' on each line.
    The method reads the file, splits each line into key-value pairs, and stores
    them in a dictionary. The values are converted to integers.

    Args:
    ----
        file_path (str): The path to the settings file.

    Returns:
    -------
        dict: A dictionary containing the settings with keys as strings and values as floats.

    Example:
    -------
        If the settings file contains:
        contrast=5
        exposure=10
        The returned dictionary will be: {'contrast': 5, 'exposure': 10}

    Raises:
    ------
        FileNotFoundError: If the file does not exist.

    """
    length_of_key_value_pair = 2
    if not Path(file_path).exists():
        msg = f"The file {file_path} does not exist."
        raise FileNotFoundError(msg)
    settings = {}
    with Path(file_path).open("r") as file:
        for line in file:
            key_and_value = line.strip().split("=")
            if len(key_and_value) == length_of_key_value_pair and key_and_value[1].strip():
                key, value = key_and_value
                try:
                    settings[key.strip()] = float(value.strip())
                except ValueError:
                    continue
    return settings


def is_file_exist(file_path: str) -> bool:
    """
    Check if the file exists.

    Args:
    ----
        file_path (str): The path to the file to check.

    Returns:
    -------
        bool: True if the file is of a valid image type, False otherwise.

    """
    return Path(file_path).is_file()


def is_supported_format_file(file_path: str, valid_types: dict[str, str]) -> bool:
    """
    Check if the specified file is of a supported format.

    This method checks if the file at the given file path matches any of the
    formats provided in the valid_types dictionary.
    It first uses the imghdr module to determine the file type
    and then checks the MIME type as a fallback.

    Args:
    ----
        file_path (str): The path to the file to check.
        valid_types (dict[str, str]): A dictionary mapping file extensions to
                                      their corresponding MIME types.

    Returns:
    -------
        bool: True if the file matches any of the supported formats, False otherwise.

    Raises:
    ------
        FileNotFoundError: If the file does not exist.

    """
    if not Path(file_path).exists():
        msg = f"The file {file_path} does not exist."
        raise FileNotFoundError(msg)
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
    Extract and returns the filename without its extension from the given file path.

    Args:
    ----
        file_path (str): The full path to the file.

    Returns:
    -------
        str: The filename without its extension.

    Example:
    -------
        >>> get_filename_without_extension("/path/to/file/example.txt")
        'example'
        >>> get_filename_without_extension("/path/to/file/archive.tar.gz")
        'archive.tar'

    """
    path = Path(file_path)
    # Handle dotfiles and files without extensions
    if path.name.startswith("."):
        return path.name
    if "." not in path.stem:
        return path.stem
    return ".".join(path.name.split(".")[:-1])


def download_file(file_url: str, file_dir: str) -> None:
    """
    Download a file from the given URL and save it to the specified directory.

    The method makes an HTTP GET request to the specified file URL
    and saves the response content to the specified directory.
    If the directory does not exist, it is created.
    The method logs a debug message upon successful download, or an error message if the download fails.

    Args:
    ----
        file_url (str): The URL of the file to be downloaded.
        file_dir (str): The directory where the file should be saved, including the file name.

    Returns:
    -------
        None

    Raises:
    ------
        Exception: If the file cannot be downloaded or saved.

    Example:
    -------
        download_file("https://example.com/file.txt", "/path/to/save/file.txt")

    """
    response = requests.get(file_url, stream=True, timeout=120)
    if response.status_code == requests.codes.ok:
        directory = Path(file_dir).parent
        if not Path(directory).exists():
            Path(file_dir).parent.mkdir(parents=True, exist_ok=True)
        with Path(file_dir).open("wb") as fp:
            fp.write(response.content)
        logger.debug("File '%s' downloaded successfully.", file_url)
    else:
        logger.error("Failed to download the file '%s'. Status code: %s", file_url, response.status_code)


def safe_join(base: str, *paths: str) -> str:
    """
    Safely join one or more path components to a base path, preventing directory traversal attacks.

    Parameters
    ----------
    base : str
        The base directory path.
    paths : str
        Additional path components to be joined to the base path.

    Returns
    -------
    str
        The safely joined absolute path.

    Raises
    ------
    ValueError
        If the final path attempts to traverse outside the base directory.

    """
    base = Path(base).resolve()
    paths = [urllib.parse.unquote(p) for p in paths]
    final_path = Path(base).joinpath(*paths).resolve()
    if not str(final_path).startswith(str(base)):
        msg = "Attempted path traversal detected"
        raise ValueError(msg)
    return str(final_path)

from __future__ import annotations

import logging.config
import logging.handlers
import mimetypes
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING

import puremagic
import pyperclip
import requests
import yaml
from yaml.scanner import ScannerError

from src import app_name
from src.api.models.preset import PresetSettings, PresetSettingsState
from src.cache.cache_keys import ACCESS_TOKEN, AUTH

if TYPE_CHECKING:
    from src.cache.cache_manager import CacheManager  # pragma: no cover


def get_logger_config_dict() -> dict:
    """
    Return the logger configuration.

    Returns
    -------
        dict: The logger configuration.

    """
    return {
        "version": 1,
        "formatters": {
            "console_formatter": {
                "format": "%(message)s",
            },
            "file_formatter": {
                "format": "%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console_handler": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console_formatter",
                "stream": "ext://sys.stdout",
            },
            "file_handler": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "file_formatter",
                "filename": f"{app_name.lower()}.log",
                "mode": "w",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": "INFO",
                "handlers": ["console_handler", "file_handler"],
            },
        },
    }


logging.config.dictConfig(get_logger_config_dict())
logger = logging.getLogger()


def read_settings_file(file_path: str) -> PresetSettings:
    """
    Read a settings file in YAML format and return the settings as a PresetSettings object.

    The method reads the *.yaml file, parses the contents and returns a PresetSettings object with the parsed values.

    Args:
    ----
        file_path (str): The path to the settings file.

    Returns:
    -------
        PresetSettings: An object containing the settings with values as floats
        or 'Off' for grain, bloom, halation and vignette exposure.

    Raises:
    ------
        FileNotFoundError: If the file does not exist.

    """
    def to_float(value: any) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    if not Path(file_path).exists():
        msg = f"The file {file_path} does not exist."
        raise FileNotFoundError(msg)
    with Path(file_path).open("r") as file:
        try:
            data = yaml.safe_load(file) or {}
        except ScannerError:
            data = {}
    adjustments = data.get("adjustments", {}) or {}
    effects = data.get("effects", {}) or {}
    effects_vignette = effects.get("vignette", {}) or {}
    return PresetSettings(
        exposure=to_float(adjustments.get("exposure", 0)),
        contrast=to_float(adjustments.get("contrast", 0)),
        temperature=to_float(adjustments.get("temperature", 0)),
        tint=to_float(adjustments.get("tint", 0)),
        color_boost=to_float(adjustments.get("color_boost", 0)),
        bloom=PresetSettingsState.from_value(effects.get("bloom", "Off")),
        halation=PresetSettingsState.from_value(effects.get("halation", "Off")),
        grain=PresetSettingsState.from_value(effects.get("grain", "Off")),
        vignette_exposure=PresetSettingsState.from_value(effects_vignette.get("exposure", "Off")),
        vignette_size=to_float(effects_vignette.get("size", 55.0)),
        vignette_feather=to_float(effects_vignette.get("feather", 15.0)),
    )


def update_auth_data_in_cache(cache_manager: CacheManager, auth_data: dict[str, str]) -> None:
    """
    Update the 'access-token' and 'auth' values in the cache.

    This method writes the provided auth data to the cache, overwriting any existing content.
    The auth data will only be written if it is not None or an empty dict.
    It is used to store the latest auth data for future use.

    Args:
    ----
        cache_manager (CacheManager): The caching manager that stores and provides auth data.
        auth_data (dict[str, str]): The 'access-token' and 'auth' values to be written to the file.

    Returns:
    -------
        None

    """
    if auth_data and len(auth_data) > 0:
        for name, value in auth_data.items():
            cache_manager.set(name, value)


def get_auth_data_from_cache(cache_manager: CacheManager) -> dict[str, str | None]:
    """
    Get the 'access-token' and 'auth' values from the cache.

    Returns
    -------
        dict[str, str]: The 'access-token' and 'auth' values read from the cache.

    """
    return {
        "access-token": cache_manager.get(ACCESS_TOKEN),
        "auth": cache_manager.get(AUTH),
    }


def delete_access_token_and_auth_data_in_cache(cache_manager: CacheManager) -> None:
    """
    Delete the 'access-token' and 'auth' values in the cache.

    Returns
    -------
        None

    """
    cache_manager.delete(ACCESS_TOKEN)
    cache_manager.delete(AUTH)


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
    It first uses the puremagic module to determine the file type
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
    # Check format using puremagic
    file_type = puremagic.what(file_path)
    if file_type in valid_types:
        return True
    # Additional check using mimetypes (for types not covered by puremagic)
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type in valid_types.values()


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


def get_file_extension(file_path: str) -> str:
    """
    Extract and return the file extension from the given file path, excluding the leading dot.

    This method returns the extension of the file without the leading dot.
    If the file has no extension, an empty string is returned.

    Args:
    ----
        file_path (str): The full path to the file.

    Returns:
    -------
        str: The file extension without the leading dot, or an empty string if no extension is present.

    Example:
    -------
        >>> get_file_extension("/path/to/file/example.txt")
        'txt'
        >>> get_file_extension("/path/to/file/archive.tar.gz")
        'gz'
        >>> get_file_extension("/path/to/file/no_extension")
        ''
        >>> get_file_extension("/path/to/file/.dotfile")
        ''

    """
    path = Path(file_path)
    # Return an empty string if the file has no extension or is a dotfile
    if not path.suffix or (path.name.startswith(".") and path.suffix == ""):
        return ""
    return path.suffix.lstrip(".")


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


def is_clipboard_available() -> bool:
    """
    Check if the system clipboard is available for read and write operations.

    This function attempts to access the system clipboard by reading its content.
    If clipboard access is supported and no exception is raised, the clipboard is considered available.
    Otherwise, clipboard unavailability is assumed (e.g., due to missing system dependencies or headless environment).

    The method is tested on macOS and Ubuntu platforms and provides a more reliable availability check
    than pyperclip's built-in `is_available()` method.

    Returns
    -------
    bool
        True if clipboard access is available, False otherwise.

    """
    try:
        pyperclip.paste()
    except pyperclip.PyperclipException:
        return False
    return True

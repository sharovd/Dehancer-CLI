from __future__ import annotations

import logging.config
import logging.handlers
import os
from dataclasses import replace
from pathlib import Path

import click

from src import utils
from src.api.clients.dehancer_online_client import DehancerOnlineAPIClient
from src.api.constants import DEHANCER_ONLINE_API_BASE_URL, IMAGE_VALID_TYPES
from src.api.models.preset import ImageSize, Preset, PresetSettings
from src.utils import get_filename_without_extension, is_supported_format_file, read_settings_file

logging.config.fileConfig(utils.get_logger_config_file_path())
logger = logging.getLogger()


dehancer_api_client = DehancerOnlineAPIClient(DEHANCER_ONLINE_API_BASE_URL)


def print_presets() -> None:
    """
    Fetch and prints the available presets from the Dehancer API client.

    This method retrieves a list of available presets using the Dehancer API client, sorts them, and prints each preset
    with its index and caption. The presets are printed in a formatted list, each on a new line with its index.

    Returns
    -------
        None
    Example:
        >>> print_presets()
        The next presets are available:
        [1]     'AGFA Chrome RSX II 200 (Exp. 2006)'
        [2]     'Adox Color Implosion 100'
        ...
        [n]     'Preset Caption'

    """
    available_presets = dehancer_api_client.get_available_presets()
    logger.info("The next presets are available:")
    for idx, preset in enumerate(available_presets, 1):
        logger.info("[%d]\t%s", idx, preset.caption)


def print_contacts(file_path: str) -> None:
    """
    Create contacts for an image.

    This method performs the following steps:
    1. Logs the initiation of contact creation for the provided image file.
    2. Fetches available presets from the Dehancer API client.
    3. Uploads the image via the Dehancer API client and retrieves an image ID.
    4. Requests contacts for the image using the small image size and available presets.
    5. Renders images using the available presets and default settings, then downloads the rendered images.

    Args:
    ----
        file_path (str): The path to the image file for which contacts are to be created.

    Returns:
    -------
        None
    Example:
        >>> print_contacts("path/to/image.jpg")
        Create contacts for the image 'path/to/image.jpg':
        1. 'AGFA Chrome RSX II 200 (Exp. 2006)' : 'https://dho-m2.dehancer.com/local/<image_id>/<rendered_image_id>.jpeg'
        2. 'Adox Color Implosion 100' : 'https://dho-m2.dehancer.com/local/<image_id>/<rendered_image_id>.jpeg'
        ...
        n. 'Preset Caption' : 'https://dho-m2.dehancer.com/local/<image_id>/<rendered_image_id>.jpeg'
        ...

    """
    logger.info("Create contacts for the image '%s':", file_path)
    available_presets = dehancer_api_client.get_available_presets()
    image_id = dehancer_api_client.upload_image(file_path)
    requested_presets = dehancer_api_client.get_pane(image_id, ImageSize.SMALL, available_presets)
    presets_default_settings = PresetSettings(0, 0, 0, 0, 0, 0, 0, 0)
    for idx, preset in enumerate(requested_presets, 1):
        image_url = dehancer_api_client.render_image(image_id, available_presets[idx-1], presets_default_settings)
        logger.info("%d. '%s' : %s", idx, preset, image_url)
        utils.download_file(image_url, f"out/{get_filename_without_extension(file_path)}_{preset}.jpeg")


def __process_image(file_path: str, preset: Preset, preset_settings: PresetSettings, preset_number: int) -> None:
    """
    Upload an image, applies the given preset with specified settings and downloads the processed image.

    Args:
    ----
        file_path (str): The path to the image file.
        preset (Preset): The preset object used for processing.
        preset_settings (PresetSettings): The preset settings object applied to the preset.
        preset_number (int): The preset number.

    Returns:
    -------
        None

    """
    image_id = dehancer_api_client.upload_image(file_path)
    image_url = dehancer_api_client.render_image(image_id, preset, preset_settings)
    logger.info("%d. '%s' : %s", preset_number, preset.caption, image_url)
    utils.download_file(image_url, f"out/{get_filename_without_extension(file_path)}_{preset.caption}.jpeg")


def develop_images(path: str, preset_number: int, custom_preset_settings: dict[str, float]) -> None:
    """
    Develop images in the specified path using the specified preset and settings.

    If the path is a file, it processes the single file.
    If the path is a directory, it processes all image files in the directory.

    Args:
    ----
        path (str): The path to the file or directory.
        preset_number (int): The preset number.
        custom_preset_settings (Dict[str, float]): Custom settings for the preset.

    """
    available_presets = dehancer_api_client.get_available_presets()
    preset = available_presets[preset_number - 1]
    preset_settings = PresetSettings(0, 0, 0, 0, 0, 0, 0, 0)
    preset_settings = replace(preset_settings, **custom_preset_settings)
    if Path(path).is_file():
        __process_image(path, preset, preset_settings, preset_number)
    elif Path(path).is_dir():
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if Path.is_file(file_path) and is_supported_format_file(file_path, IMAGE_VALID_TYPES):
                __process_image(file_path, preset, preset_settings, preset_number)


def enable_debug_logs() -> None:
    """
    Enable debug-level logging.

    This function sets the logging level to DEBUG for the global logger,
    allowing detailed debug messages to be captured in the logs.

    Returns
    -------
    None

    """
    logger.setLevel(logging.DEBUG)


@click.group()
@click.option("-l", "--logs", type=int, default=0, help="Enable debug logs (1 for enabled, 0 for disabled).")
def cli(logs: int) -> None:
    """
    Entry point for the CLI application.

    This function sets up the CLI group and handles the global option for enabling debug logs.

    Parameters
    ----------
    logs : int
        Enable debug logs (1 for enabled, 0 for disabled).

    Returns
    -------
    None

    """
    if logs == 1:
        enable_debug_logs()


@cli.command()
@click.option("-l", "--logs", type=int, default=0,
              help="Enable debug logs (1 for enabled, 0 for disabled).")
def presets(logs: int) -> None:
    """
    Command to print available film presets.

    This function prints the available film presets using the Dehancer API client.

    Parameters
    ----------
    logs : int
        Enable debug logs (1 for enabled, 0 for disabled).

    Returns
    -------
    None

    """
    if logs == 1:
        enable_debug_logs()
    print_presets()


@cli.command()
@click.argument("input")
@click.option("-l", "--logs", type=int, default=0,
              help="Enable debug logs (1 for enabled, 0 for disabled).")
def contacts(input, logs: int) -> None:  # noqa: A002, ANN001
    """
    Command to create contacts for an image.

    This function creates contacts for the provided image file and downloads the results.

    Parameters
    ----------
    input : str
        The path to the image file.
    logs : int
        Enable debug logs (1 for enabled, 0 for disabled).

    Returns
    -------
    None

    """
    if logs == 1:
        enable_debug_logs()
    print_contacts(input)


@cli.command()
@click.argument("input")
@click.option("-p", "--preset", "preset",
              type=int, required=True, help="Preset number.")
@click.option("-s", "--set_contrast", "contrast",
              type=float, help="Contrast setting.")
@click.option("-e", "--set_exposure", "exposure",
              type=float, help="Exposure setting.")
@click.option("-t", "--set_temperature", "temperature",
              type=float, help="Temperature setting.")
@click.option("-i", "--set_tint", "tint",
              type=float, help="Tint setting.")
@click.option("-b", "--set_color_boost", "color_boost", type=float, help="Color boost setting.")
@click.option("-settings", "--settings_file", type=click.Path(exists=True), help="Settings file.")
@click.option("-l", "--logs", type=int, default=0, help="Enable debug logs (1 for enabled, 0 for disabled).")
def develop(input, preset: int,  # noqa: A002, ANN001, PLR0913
            contrast: float, exposure: float, temperature: float, tint: float, color_boost: float,
            settings_file: click.Path(exists=True), logs: int) -> None:
    """
    Command to develop images with specified film preset and settings.

    This function processes images in the specified path
    using the provided film preset number, custom settings and downloads the results.

    Parameters
    ----------
    input : str
        The path to the file or directory.
    preset : int
        The film preset number.
    contrast : float
        Contrast setting.
    exposure : float
        Exposure setting.
    temperature : float
        Temperature setting.
    tint : float
        Tint setting.
    color_boost : float
        Color boost setting.
    settings_file : click.Path
        Path to the settings file.
    logs : int
        Enable debug logs (1 for enabled, 0 for disabled).

    Returns
    -------
    None

    """
    if logs == 1:
        enable_debug_logs()
    settings = {}
    if settings_file:
        settings.update(read_settings_file(settings_file))
    if contrast is not None:
        settings["contrast"] = contrast
    if exposure is not None:
        settings["exposure"] = exposure
    if temperature is not None:
        settings["temperature"] = temperature
    if tint is not None:
        settings["tint"] = tint
    if color_boost is not None:
        settings["color_boost"] = color_boost
    develop_images(input, preset, settings)


if __name__ == "__main__":
    cli()

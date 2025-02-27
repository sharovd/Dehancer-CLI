from __future__ import annotations

import getpass
import logging.config
import logging.handlers
import os
from dataclasses import asdict, replace
from pathlib import Path

import click
import pyperclip

from src import app_name, app_version, utils
from src.api.clients.dehancer_online_client import DehancerOnlineAPIClient
from src.api.constants import DEHANCER_ONLINE_API_BASE_URL, ENCODING_UTF_8, IMAGE_VALID_TYPES
from src.api.enums import ExportFormat, ImageQuality, ImageSize, UnknownImageQualityError
from src.api.models.preset import Preset, PresetSettings
from src.cache.cache_manager import CacheManager
from src.utils import (
    get_file_extension,
    get_filename_without_extension,
    is_clipboard_available,
    is_supported_format_file,
    read_settings_file,
    safe_join,
)
from src.web_ext.we_script_provider import WebExtensionScriptProvider

logging.config.dictConfig(utils.get_logger_config_dict())
logger = logging.getLogger()

cache_manager = CacheManager()
dehancer_api_client = DehancerOnlineAPIClient(DEHANCER_ONLINE_API_BASE_URL, cache_manager)


def login(email: str, password: str) -> None:
    """
    Login to Dehancer Online via the API using the email and password provided and save auth data in the cache.

    This method attempts to authenticate as an user using the provided email and password.
    If the authentication is successful, it updates the 'access-token' and 'auth' values in the cache.
    If the authentication fails, an error message is displayed.

    Args:
    ----
        email (str): The email address of the user.
        password (str): The password of the user.

    """
    is_authorized = dehancer_api_client.login(email, password)
    if is_authorized:
        click.echo(f"User '{email}' successfully authorized.")
    else:
        click.echo(f"User '{email}' is not authorised. Please check email and password and try again.", err=True)


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
    -------
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
    requested_presets = dehancer_api_client.get_image_previews(image_id, ImageSize.SMALL, available_presets)
    for idx, preset in enumerate(requested_presets, 1):
        image_url = dehancer_api_client.render_image(image_id, available_presets[idx-1])
        logger.info("%d. '%s' : %s", idx, preset, image_url)
        output_dir = f"{app_name.lower()}-output-images"
        safe_filename = safe_join(output_dir, f"{get_filename_without_extension(file_path)}_{preset}.jpeg")
        utils.download_file(image_url, safe_filename)


def __process_image(file_path: str, preset: Preset, export_format: ExportFormat,
                    preset_settings: PresetSettings, preset_number: int) -> None:
    """
    Upload an image, applies the given preset with specified settings and downloads the processed image.

    Args:
    ----
        file_path (str): The path to the image file.
        preset (Preset): The preset object used for processing.
        export_format (ExportFormat): The export format object used for processing.
        preset_settings (PresetSettings): The preset settings object applied to the preset.
        preset_number (int): The preset number.

    Returns:
    -------
        None

    """
    image_id = dehancer_api_client.upload_image(file_path)
    image_file_extension = "jpeg"
    if dehancer_api_client.is_authorized:
        logger.info(
            "Develop the image '%s'\n"
            "  - Preset: '%s'\n"
            "  - Quality: '%s'\n"
            "  - Settings (adjustments): %s\n"
            "  - Settings (effects): %s",
            file_path,
            preset.caption,
            ImageQuality.from_export_format(export_format).name.title(),
            preset_settings.get_adjustments_str(),
            preset_settings.get_effects_str(),
        )
        export_image_response_data = dehancer_api_client.export_image(image_id, preset, export_format, preset_settings)
        image_url = export_image_response_data.get("url")
        image_file_extension = get_file_extension(export_image_response_data.get("filename"))
    else:
        logger.info(
            "Develop the image '%s'\n"
            "  - Preset: '%s'\n"
            "  - Settings (adjustments): %s\n"
            "  - Settings (effects): %s",
            file_path,
            preset.caption,
            preset_settings.get_adjustments_str(),
            preset_settings.get_effects_str(),
        )
        image_url = dehancer_api_client.render_image(image_id, preset, preset_settings)
    logger.info("%d. '%s' : %s", preset_number, preset.caption, image_url)
    utils.download_file(image_url, f"{app_name.lower()}-output-images/"
                                   f"{get_filename_without_extension(file_path)}_{preset.caption}.{image_file_extension}")


def develop_images(path: str, preset_number: int, quality: str, custom_preset_settings: PresetSettings) -> None:
    """
    Develop images in the specified path using the specified preset, quality and settings.

    If the path is a file, it processes the single file.
    If the path is a directory, it processes all image files in the directory.

    Args:
    ----
        path (str): The path to the file or directory.
        preset_number (int): The preset number.
        quality (str): The quality level for image develop ["low" (default), "medium", "high"].
        custom_preset_settings (Dict[str, float]): Custom settings for the preset.

    """
    available_presets = dehancer_api_client.get_available_presets()
    preset = available_presets[preset_number - 1]
    preset_settings = PresetSettings.default()
    preset_settings = replace(preset_settings, **asdict(custom_preset_settings))
    export_format = ImageQuality.LOW.value
    try:
        export_format = ImageQuality.from_string(quality).value
    except UnknownImageQualityError:
        logger.warning("Unknown quality level '%s'. Default '%s' is used instead.",
                       quality, ImageQuality.from_export_format(export_format).name.title())
    if Path(path).is_file():
        __process_image(path, preset, export_format, preset_settings, preset_number)
    elif Path(path).is_dir():
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if Path.is_file(Path(file_path)) and is_supported_format_file(file_path, IMAGE_VALID_TYPES):
                __process_image(file_path, preset, export_format, preset_settings, preset_number)


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


def clear_cache_data() -> None:
    """
    Clear all application cached data.

    This function deletes all application cached data such as auth data, API responses, etc.

    Returns
    -------
    None

    """
    cache_manager.clear()


def copy_web_extension_script_to_cb() -> None:
    """
    Copy the content of a web extension script to the system clipboard.

    This function retrieves the content of the web extension script from the WebExtensionScriptProvider.
    If the content is not empty, it attempts to copy the content to the system clipboard using the pyperclip library.
    If copying to the clipboard fails, the script content will be written to the 'web-extension-script.txt' text file.

    Returns
    -------
    None

    Raises
    ------
    pyperclip.PyperclipException
        If an error occurs while attempting to copy the script content to the clipboard.

    """
    web_extension_script_content = WebExtensionScriptProvider().get_script_content()
    if web_extension_script_content:
        if is_clipboard_available():
            pyperclip.copy(web_extension_script_content)
            click.echo("Web extension script copied into clipboard!")
        else:
            click.echo("Web extension script wasn't copied due the error with copy/paste mechanism for your system.\n"
                       "On Linux, you can run `sudo apt-get install xclip` "
                       "or `sudo apt-get install xselect` to install a copy/paste mechanism.", err=True)
            # Write the content of a web extension script to the file if copying to the clipboard is not possible.
            web_extension_file_name = "web-extension-script.txt"
            with Path(web_extension_file_name).open("wb") as fp:
                fp.write(web_extension_script_content.encode(encoding=ENCODING_UTF_8))
                click.echo(f"Web extension script, as a workaround, written to file '{web_extension_file_name}'.")
    else:
        click.echo("Web extension script wasn't copied to clipboard because it was empty.", err=True)


@click.group()
@click.version_option(prog_name=app_name, version=app_version, message="%(prog)s %(version)s")
@click.option("--logs", type=int, default=0, help="Enable debug logs (1 for enabled, 0 for disabled).")
def cli(logs: int) -> None:
    """
    Unofficial command line application that interacts with the Dehancer Online API to process images
    using various film presets. It allows you to view available presets, create contacts for an image,
    and develop images using specific film presets and settings.
    """  # noqa: D205
    if logs == 1:
        enable_debug_logs()


@cli.command()
@click.option("--logs", type=int, default=0,
              help="Enable debug logs (1 for enabled, 0 for disabled).")
def clear_cache(logs: int) -> None:
    """
    Command to clear all application cached data.

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
    clear_cache_data()


@cli.command()
@click.option("--logs", type=int, default=0,
              help="Enable debug logs (1 for enabled, 0 for disabled).")
def web_ext(logs: int) -> None:
    """
    Command to copy the content of a web extension script to the clipboard.

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
    copy_web_extension_script_to_cb()


@cli.command()
@click.argument("input")
@click.option("--logs", type=int, default=0,
              help="Enable debug logs (1 for enabled, 0 for disabled).")
def auth(input, logs: int) -> None:  # noqa: A002, ANN001
    """
    Command to authorize and save auth data.

    This command saves access token for provided username and password.

    Parameters
    ----------
    input : str
        The user e-mail for authorization.
    logs : int
        Enable debug logs (1 for enabled, 0 for disabled).

    Returns
    -------
    None

    """
    if logs == 1:
        enable_debug_logs()
    password = getpass.getpass("Password: ")
    login(input, password)


@cli.command()
@click.option("--logs", type=int, default=0,
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
@click.option("--logs", type=int, default=0,
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
@click.option("-q", "--quality", "quality",
              type=str, help="Image quality level ['low', 'medium', 'high'].")
@click.option("-c", "--set_contrast", "contrast",
              type=float, help="Contrast setting (adjustments).")
@click.option("-e", "--set_exposure", "exposure",
              type=float, help="Exposure setting (adjustments).")
@click.option("-t", "--set_temperature", "temperature",
              type=float, help="Temperature setting (adjustments).")
@click.option("-i", "--set_tint", "tint",
              type=float, help="Tint setting (adjustments).")
@click.option("-cb", "--set_color_boost", "color_boost",
              type=float, help="Color boost setting (adjustments).")
@click.option("-g", "--set_grain", "grain",
              type=float, help="Grain setting (effects).")
@click.option("-b", "--set_bloom", "bloom",
              type=float, help="Bloom setting (effects).")
@click.option("-h", "--set_halation", "halation",
              type=float, help="Halation setting (effects).")
@click.option("-v_e", "--set_vignette_exposure", "vignette_exposure",
              type=float, help="Vignette exposure setting (effects).")
@click.option("-v_s", "--set_vignette_size", "vignette_size",
              type=float, help="Vignette size setting (effects).")
@click.option("-v_f", "--set_vignette_feather", "vignette_feather",
              type=float, help="Vignette feather setting (effects).")
@click.option("-settings", "--settings_file", type=click.Path(exists=True), help="Settings file.")
@click.option("--logs", type=int, default=0, help="Enable debug logs (1 for enabled, 0 for disabled).")
def develop(input, preset: int,  # noqa: A002, ANN001, PLR0913
            quality: str,
            contrast: float, exposure: float, temperature: float, tint: float, color_boost: float,
            grain: float, bloom: float, halation: float,
            vignette_exposure: float, vignette_size: float, vignette_feather: float,
            settings_file: click.Path(exists=True), logs: int) -> None:
    """
    Command to develop images with specified film preset, quality and settings.

    This function processes images in the specified path
    using the provided film preset number, quality, custom settings and downloads the results.

    Parameters
    ----------
    input : str
        The path to the file or directory.
    preset : int
        The film preset number.
    quality : str
        The quality level for image develop ["low" (default), "medium", "high"].
    contrast : float
        Contrast setting (adjustments).
    exposure : float
        Exposure setting (adjustments).
    temperature : float
        Temperature setting (adjustments).
    tint : float
        Tint setting (adjustments).
    color_boost : float
        Color boost setting (adjustments).
    grain : float
        Grain setting (effects).
    bloom : float
        Bloom setting (effects).
    halation : float
        Halation setting (effects).
    vignette_exposure : float
        Vignette exposure setting (effects).
    vignette_size : float
        Vignette size setting (effects).
    vignette_feather : float
        Vignette feather setting (effects).
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
    if quality is None:
        quality = "low"
    settings = PresetSettings.default()
    if settings_file:
        settings = replace(settings, **asdict(read_settings_file(settings_file)))
    input_settings = {
        "contrast": contrast,
        "exposure": exposure,
        "temperature": temperature,
        "tint": tint,
        "color_boost": color_boost,
        "grain": grain,
        "bloom": bloom,
        "halation": halation,
        "vignette_exposure": vignette_exposure,
        "vignette_size": vignette_size,
        "vignette_feather": vignette_feather,
    }
    for key, value in input_settings.items():
        if value is not None:
            setattr(settings, key, value)
    develop_images(input, preset, quality, settings)


if __name__ == "__main__":
    cli()

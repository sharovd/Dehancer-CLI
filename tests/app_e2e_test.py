from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path
from secrets import choice

import pytest
from pytest import param as test_data  # noqa: PT013

import tests.utils.test_data_provider as td
from src import app_name, app_version
from src.api.models.preset import PresetSettings, PresetSettingsState
from src.cache.cache_keys import ACCESS_TOKEN, AUTH, PRESETS
from src.cache.cache_manager import CacheManager
from src.utils import get_filename_without_extension
from tests.data.app_outputs.contacts import contacts_success_output
from tests.data.app_outputs.develop import develop_without_auth_success_output
from tests.data.app_outputs.presets import presets_success_output
from tests.utils.comparators import compare_contacts_command_output, compare_develop_command_output
from tests.utils.test_cache_context import CacheBackupContext
from tests.utils.test_files_context import FileBackupContext

project_root = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def test_images():
    return td.get_all_test_images()


@pytest.mark.e2e
def test_presets_command_prints_available_presets():
    # Arrange: define expected output
    expected_output = presets_success_output
    # Act: perform command under test
    result = subprocess.run(  # noqa: S603
        ["python", "dehancer_cli.py", "presets"],  # noqa: S607
        cwd=project_root,
        capture_output=True,
        text=True, check=False,
    )
    # Assert: check command return code and output
    assert result.returncode == 0
    assert result.stdout == expected_output


@pytest.mark.e2e
def test_contacts_command_creates_contacts_for_chosen_image(test_images: list[str]):
    # Arrange: use a random test image as an chosen image for the command
    random_test_image_path = choice(test_images)
    random_test_image_name = get_filename_without_extension(random_test_image_path)
    # Arrange: define expected outputs
    expected_output_dir = "dehancer-cli-output-images"
    expected_output = contacts_success_output
    expected_presets = [name for name in re.findall(r"'(.*?)'", expected_output)
                        if not re.match(r"\{.*}", name)]
    # Act: perform command under test
    with FileBackupContext(expected_output_dir):
        result = subprocess.run(  # noqa: S603
            ["python", "dehancer_cli.py", "contacts", random_test_image_path],  # noqa: S607
            cwd=project_root,
            capture_output=True,
            text=True, check=False,
        )
        # Assert: check command return code and output
        assert result.returncode == 0
        is_expected_output = compare_contacts_command_output(expected_output, result.stdout, random_test_image_path)
        assert is_expected_output
        # Assert: check that expected files are created
        for preset in expected_presets:
            file_path = os.path.join(expected_output_dir, f"{random_test_image_name}_{preset}.jpeg")
            assert Path(file_path).exists


@pytest.mark.e2e
@pytest.mark.parametrize(("preset_settings_file_content", "preset_settings_args", "expected_preset_settings_object"), [
    test_data(None, None, PresetSettings.default(), id="Without settings"),
    test_data("""
adjustments:
    exposure: 0
    contrast: 0
    temperature: 0
    tint: 0
    color_boost: 0
effects:
    grain: Off
    bloom: Off
    halation: Off
    vignette:
        exposure: Off
        size: 55
        feather: 15
""", None, PresetSettings.default(), id="Default settings (from file)"),
    test_data("""
adjustments:
    exposure: 2.2
    contrast: 10
    temperature: -10
    tint: -22
    color_boost: 0
effects:
    grain: 50
    bloom: Off
    halation: Off
    vignette:
        exposure: -1.2
        size: 60
        feather: 20
""", None, PresetSettings(2.2, 10.0, -10.0, -22.0, 0.0,
                          50.0, PresetSettingsState.OFF, PresetSettingsState.OFF,
                          -1.2, 60.0, 20.0),
              id="Custom settings - adjustments and effects (from file)"),
    test_data(None, "-e '-0.8' -c 1.2 -t 30 -i '-10.5' -cb 15 "
                    "-g 80 -b 32.3 -h 44.4 "
                    "-v_e 1.8 -v_s 10 -v_f 25",
              PresetSettings(-0.8, 1.2, 30.0, -10.5, 15.0, 80.0, 32.3, 44.4, 1.8, 10.0, 25.0),
              id="Custom settings - adjustments and effects (from args)"),
    test_data(None, "-cb '-11.3' -t 32 -c 2.1 -i '-10.5' -e '1.8'",
              PresetSettings(1.8, 2.1, 32.0, -10.5, -11.3,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - only adjustments (from args)"),
    test_data(None, "-c 1.1 -e '2.2'",
              PresetSettings(2.2, 1.1, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - partially adjustments (from args)"),
    test_data(None, "-c 10.10",
              PresetSettings(0.0, 10.10, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific adjustments - contrast (from args)"),
    test_data(None, "-e 20.20",
              PresetSettings(20.20, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific adjustments - exposure (from args)"),
    test_data(None, "-t 30.30",
              PresetSettings(0.0, 0.0, 30.30, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific adjustments - temperature (from args)"),
    test_data(None, "-i 40.40",
              PresetSettings(0.0, 0.0, 0.0, 40.40, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific adjustments - tint (from args)"),
    test_data(None, "-cb 50.50",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 50.50,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific adjustments - color boost (from args)"),
    test_data(None, "-h 10 -b 20 -g 30 -v_e -1.2 -v_s 50 -v_f 20",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0, 30.0, 20.0, 10.0, -1.2, 50.0, 20.0),
              id="Custom settings - only effects (from args)"),
    test_data(None, "-h 15.20 -g 35.25",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             35.25, PresetSettingsState.OFF, 15.20,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - partially effects (from args)"),
    test_data(None, "-g 60.60",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             60.60, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific effects - grain (from args)"),
    test_data(None, "-b 60.60",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, 60.60, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific effects - bloom (from args)"),
    test_data(None, "-h 70.70",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, 70.70,
                             PresetSettingsState.OFF, 55.0, 15.0),
              id="Custom settings - specific effects - halation (from args)"),
    test_data(None, "-v_e -1.8",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             -1.8, 55.0, 15.0),
              id="Custom settings - specific effects - vignette exposure (from args)"),
    test_data(None, "-v_s 28.8",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 28.8, 15.0),
              id="Custom settings - specific effects - vignette size (from args)"),
    test_data(None, "-v_f 6.5",
              PresetSettings(0.0, 0.0, 0.0, 0.0, 0.0,
                             PresetSettingsState.OFF, PresetSettingsState.OFF, PresetSettingsState.OFF,
                             PresetSettingsState.OFF, 55.0, 6.5),
              id="Custom settings - specific effects - vignette feather (from args)"),
])
def test_develop_command_wo_auth_develop_image(preset_settings_file_content: str,
                                               preset_settings_args: str,
                                               expected_preset_settings_object: PresetSettings,
                                               test_images: list[str]):
    cache_manager = CacheManager(application_name=app_name)
    run_develop_command_with_settings(cache_manager, preset_settings_file_content, preset_settings_args,
                                      expected_preset_settings_object, test_images)


def run_develop_command_with_settings(cache_manager: CacheManager,
                                      preset_settings_file_content: str,
                                      preset_settings_args: str,
                                      expected_preset_settings_object: PresetSettings,
                                      test_images: list[str]) -> None:
    # Arrange: use a random test image as a chosen image for the command
    random_test_image_path = choice(test_images)
    random_test_image_name = get_filename_without_extension(random_test_image_path)
    # Arrange: define expected outputs
    expected_output_dir = "dehancer-cli-output-images"
    expected_output = develop_without_auth_success_output
    expected_presets = [name for name in re.findall(r"'(.*?)'", contacts_success_output)
                        if not re.match(r"\{.*}", name)]
    # Arrange: use a random preset
    random_preset_name = choice(expected_presets)
    random_preset_number = expected_presets.index(random_preset_name) + 1

    with (FileBackupContext(expected_output_dir), FileBackupContext("settings.yaml"),
          CacheBackupContext(cache_manager, [ACCESS_TOKEN, AUTH])):
        # Create settings.yaml if preset_settings_file_content is provided
        if preset_settings_file_content:
            with Path("settings.yaml").open("w") as settings_file:
                settings_file.write(preset_settings_file_content)
            cmd = ["python", "dehancer_cli.py", "develop", random_test_image_path, "--preset", str(random_preset_number),  # noqa: E501
                 "--settings_file", "settings.yaml"]
        else:
            cmd = ["python", "dehancer_cli.py", "develop", random_test_image_path, "--preset", str(random_preset_number)]  # noqa: E501
            if preset_settings_args:
                cmd += shlex.split(preset_settings_args)
        result = subprocess.run(  # noqa: S603
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
        )
        # Assert: check command return code and output
        assert result.returncode == 0
        is_expected_output = compare_develop_command_output(expected_output, result.stdout, random_test_image_path,
                                                            random_preset_name,
                                                            expected_preset_settings_object.get_adjustments_str(),
                                                            expected_preset_settings_object.get_effects_str(),
                                                            random_preset_number)
        assert is_expected_output
        # Assert: check that expected files are created
        for preset in expected_presets:
            file_path = os.path.join(expected_output_dir, f"{random_test_image_name}_{preset}.jpeg")
            assert Path(file_path).exists


@pytest.mark.e2e
def test_version_command_prints_application_version():
    # Arrange: define expected output
    expected_output = f"{app_name} {app_version}\n"
    # Act: perform command under test
    result = subprocess.run(  # noqa: S603
        ["python", "dehancer_cli.py", "--version"],  # noqa: S607
        cwd=project_root,
        capture_output=True,
        text=True, check=False,
    )
    # Assert: check command return code and output
    assert result.returncode == 0
    assert result.stdout == expected_output


@pytest.mark.e2e
def test_clear_cache_command_clears_all_application_cached_data():
    cache_manager = CacheManager(application_name=app_name)
    # Arrange: perform 'presets' command that stores the result in the cache
    subprocess.run(  # noqa: S603
        ["python", "dehancer_cli.py", "presets"],  # noqa: S607
        cwd=project_root,
        capture_output=True,
        text=True, check=False,
    )
    # Arrange: check that cache isn't empty
    assert cache_manager.get(PRESETS) is not None
    # Act: perform command under test
    result = subprocess.run(  # noqa: S603
        ["python", "dehancer_cli.py", "clear-cache"],  # noqa: S607
        cwd=project_root,
        capture_output=True,
        text=True, check=False,
    )
    # Assert: check command return code and that cache is empty
    assert result.returncode == 0
    assert cache_manager.get(PRESETS) is None

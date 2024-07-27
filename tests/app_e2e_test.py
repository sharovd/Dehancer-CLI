from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from secrets import choice

import pytest

import tests.utils.test_data_provider as td
from src.utils import get_filename_without_extension
from tests.data.app_outputs.contacts import contacts_success_output
from tests.data.app_outputs.presets import presets_success_output
from tests.utils.comparators import compare_command_output
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
    expected_presets = [name for name in re.findall(r"'(.*?)'", expected_output) if not re.match(r"\{.*}", name)]
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
        is_expected_output = compare_command_output(expected_output, result.stdout, random_test_image_path)
        assert is_expected_output
        # Assert: check that expected files are created
        for preset in expected_presets:
            file_path = os.path.join(expected_output_dir, f"{random_test_image_name}_{preset}.jpeg")
            assert Path(file_path).exists

from __future__ import annotations

import re


def _compare_command_output(expected_output: str, actual_output: str, replacements: dict[str, str]) -> bool:
    """
    Compare the expected and actual command outputs with dynamic replacements.

    Args:
    ----
        expected_output (str): The output template or final data that is expected.
        actual_output (str): The actual output received.
        replacements (dict[str, str]): A dictionary where the key is the placeholder in the expected output
        and the value is the and the value is the actual value to replace it with.

    Returns:
    -------
        bool: True if the outputs match, False otherwise.

    """
    # Apply replacements - replace anchor {...} with a real value
    for placeholder, value in replacements.items():
        expected_output = expected_output.replace(f"{{{placeholder}}}", value)
    # Split outputs into separate lines
    expected_lines = expected_output.strip().split("\n")
    actual_lines = actual_output.strip().split("\n")
    if len(expected_lines) != len(actual_lines):
        print(f"Line count mismatch: expected {len(expected_lines)}, got {len(actual_lines)}")  # noqa: T201
        return False
    # Compare each string
    for expected_line, actual_line in zip(expected_lines, actual_lines):
        if "{result_image_link}" in expected_line:
            # Replace anchor {result_image_link} with a regex pattern to match any https URL with jpeg image
            processed_expected_line = re.escape(expected_line).replace(r"\{result_image_link\}",
                                                                       r"https://[^\s]+\.jpeg")
            if not re.match(str(processed_expected_line), actual_line):
                print(f"Mismatch:\nExpected (regex): {processed_expected_line}\nActual: {actual_line}")  # noqa: T201
                return False
        elif expected_line != actual_line:
            print(f"Mismatch:\nExpected: {expected_line}\nActual: {actual_line}")  # noqa: T201
            return False
    return True


def compare_contacts_command_output(expected_output: str, actual_output: str, input_image_path: str) -> bool:
    replacements = {"input_image_path": input_image_path}
    return _compare_command_output(expected_output, actual_output, replacements)


def compare_develop_command_output(expected_output: str, actual_output: str, input_image_path: str,  # noqa: PLR0913
                                   input_preset_name: str,
                                   input_settings_adjustments: str, input_settings_effects: str,
                                   input_preset_number: str | int) -> bool:
    replacements = {
        "input_image_path": input_image_path,
        "preset_name": input_preset_name,
        "settings_adjustments": input_settings_adjustments,
        "settings_effects": input_settings_effects,
        "preset_number": str(input_preset_number),
    }
    return _compare_command_output(expected_output, actual_output, replacements)

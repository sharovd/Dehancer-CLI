develop_without_auth_success_output = """Develop the image '{input_image_path}'
  - Preset: '{preset_name}'
  - Settings (adjustments): {settings_adjustments}
  - Settings (effects): {settings_effects}
{preset_number}. '{preset_name}' : {result_image_link}
"""

develop_with_auth_success_output = """Develop the image '{input_image_path}' with the preset '{preset_name}' in '{quality}' quality:
{preset_number}. '{preset_name}' : {result_image_link}
"""  # noqa: E501

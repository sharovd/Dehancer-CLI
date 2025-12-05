from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EXPECTED_NUMBER_OF_PRESETS = 75

EXPECTED_PRESET_SECTIONS = {
    "0": "Featured",
    "7": "Color films",
    "65": "Black and white films",
}

class PresetModel(BaseModel):
    """
    Representation of a preset definition in the Dehancer Online API.

    This model describes the full structure of a single preset configuration.
    To ensure consistency with the Dehancer Online contract, each field is validated against strict numeric ranges.

    Attributes
    ----------
    caption : str
        Human-readable title of the preset.
    creator : Literal["Dehancer Team"]
        Identifier of the preset creator. Currently limited to ``"Dehancer Team"``.
    preset : str
        Internal preset identifier used by the API.
    exposure : float
        Exposure adjustment, from ``-2.0`` to ``2.0``.
    contrast : float
        Contrast adjustment, from ``-40.0`` to ``40.0``.
    temperature : float
        Color temperature adjustment, from ``-90.0`` to ``90.0``.
    tint : float
        Green-magenta tint adjustment, from ``-90.0`` to ``90.0``.
    color_boost : float
        Saturation/boost adjustment, from ``-90.0`` to ``90.0``.
    is_bloom_enabled : bool
        Indicates whether bloom effect is enabled.
    bloom : float
        Bloom effect intensity, from ``0.0`` up to ``100.0``.
    is_halation_enabled : bool
        Indicates whether the halation effect is enabled.
    halation : float
        Halation effect intensity, from ``0.0`` to ``100.0``.
    is_grain_enabled : bool
        Indicates whether film grain is enabled.
    grain : float
        Grain effect intensity, within ``0.0``-``100.0``.
    is_vignette_enabled : bool
        Indicates whether vignette is enabled.
    vignette_exposure : float
        Exposure modification within vignette effect, from ``-2.0`` to ``2.0``.
    vignette_feather : float
        Vignette effect feathering factor, from ``4.0`` to ``40.0``.
    vignette_size : float
        Vignette effect radius/size percentage, from ``5.0`` to ``99.0``.

    """

    model_config = ConfigDict(extra="forbid")

    caption: str
    creator: Literal["Dehancer Team"]
    preset: str
    exposure: float = Field(ge=-2.0, le=2.0)
    contrast: float = Field(ge=-40.0, le=40.0)
    temperature: float = Field(ge=-90.0, le=90.0)
    tint: float = Field(ge=-90.0, le=90.0)
    color_boost: float = Field(ge=-90.0, le=90.0)
    is_bloom_enabled: bool
    bloom: float = Field(ge=0.0, le=100.0)
    is_halation_enabled: bool
    halation: float = Field(ge=0.0, le=100.0)
    is_grain_enabled: bool
    grain: float = Field(ge=0.0, le=100.0)
    is_vignette_enabled: bool
    vignette_exposure: float = Field(ge=-2.0, le=2.0)
    vignette_feather: float = Field(ge=4.0, le=40.0)
    vignette_size: float = Field(ge=5.0, le=99.0)


class PresetsResponseModel(BaseModel):
    """
    Representation of the presets list response.

    This model describes the structure returned by the Dehancer Online API when requesting available presets.
    It includes the success flag, a list of preset definitions, and a dictionary describing preset section grouping.
    The model additionally enforces strong validation rules to ensure the response matches the API contract.

    Attributes
    ----------
    success : bool
        Whether the server successfully returned the presets list.
    presets : list[PresetModel]
        List of preset definitions.
        The total number must match the expected value defined in ``EXPECTED_NUMBER_OF_PRESETS``.
    preset_sections : dict[str, str]
        Mapping of preset category identifiers to human-readable category names.
        Mapped from the JSON key ``presetSections``.
        Must exactly match the expected structure defined in ``EXPECTED_PRESET_SECTIONS``.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    presets: list[PresetModel]
    preset_sections: dict[str, str] = Field(alias="presetSections")

    @field_validator("presets")
    @classmethod
    def validate_presets_count(cls, value: list[PresetModel]) -> list[PresetModel]:
        """
        Check that the number of items in the presets list is as expected.

        Args:
        ----
            value (list[PresetModel]): List of presets to validate.

        Returns:
        -------
            list[PresetModel]: The original list passes the validation.

        Raises:
        ------
            ValueError: If the number of presets does not match EXPECTED_NUMBER_OF_PRESETS.

        """
        if len(value) != EXPECTED_NUMBER_OF_PRESETS:
            message = f"The expected number of presets is '{EXPECTED_NUMBER_OF_PRESETS}' items, got '{len(value)}'"
            raise ValueError(message)
        return value

    @field_validator("preset_sections")
    @classmethod
    def validate_preset_sections(cls, value: dict[str, str]) -> dict[str, str]:
        """
        Check that the 'presetSections' field contains the expected sections.

        Args:
        ----
            value (dict[str, str]): Dict of preset sections to validate.

        Returns:
        -------
            dict[str, str]: The original dict of preset sections passes the validation.

        Raises:
        ------
            ValueError: If the 'presetSections' field does not match EXPECTED_PRESET_SECTIONS.

        """
        if value != EXPECTED_PRESET_SECTIONS:
            message = (f"The field 'presetSections' does not match the expected contract.\n"
                       f"Expected '{EXPECTED_PRESET_SECTIONS}'\nActual '{value}'")
            raise ValueError(message)
        return value

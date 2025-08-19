from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PresetSettingsState(Enum):  # noqa: D101
    OFF = "Off"
    VALUE = 0  # Placeholder for float values

    def __str__(self) -> str:
        """
        Return the string representation of the PresetSettingsState.

        Returns
        -------
        str: 'Off' if the state is OFF, otherwise 'Value'.

        """
        return self.value

    @classmethod
    def from_value(cls, value: float | str) -> float | PresetSettingsState:  # noqa: D102
        if isinstance(value, (str, bool)) or value is None:
            return cls.OFF
        return float(value)


@dataclass
class Preset:  # noqa: D101
    caption: str
    creator: str
    preset: str
    exposure: float
    contrast: float
    temperature: float
    tint: float
    color_boost: float
    is_bloom_enabled: bool
    bloom: float
    is_halation_enabled: bool
    halation: float
    is_grain_enabled: bool
    grain: float
    is_vignette_enabled: bool
    vignette_exposure: float
    vignette_size: float
    vignette_feather: float


@dataclass
class PresetSettings:  # noqa: D101
    # Adjustments
    exposure: float
    contrast: float
    temperature: float
    tint: float
    color_boost: float
    # Effects
    grain: float | PresetSettingsState
    bloom: float | PresetSettingsState
    halation: float | PresetSettingsState
    vignette_exposure: float | PresetSettingsState
    vignette_size: float
    vignette_feather: float

    def __eq__(self, other: any) -> bool:  # noqa: D105
        if not isinstance(other, PresetSettings):
            return False
        return (
                self.exposure == other.exposure and
                self.contrast == other.contrast and
                self.temperature == other.temperature and
                self.tint == other.tint and
                self.color_boost == other.color_boost and
                self.bloom == other.bloom and
                self.halation == other.halation and
                self.grain == other.grain and
                self.vignette_exposure == other.vignette_exposure and
                self.vignette_size == other.vignette_size and
                self.vignette_feather == other.vignette_feather
        )

    def __hash__(self) -> int:  # noqa: D105
        return hash((
                self.exposure,
                self.contrast,
                self.temperature,
                self.tint,
                self.color_boost,
                self.grain,
                self.bloom,
                self.halation,
                self.vignette_exposure,
                self.vignette_size,
                self.vignette_feather,
            ))

    @staticmethod
    def default() -> PresetSettings:
        """
        Generate a default PresetSettings object with all values set to 0 or 'Off' for effects.

        Returns
        -------
        PresetSettings: A PresetSettings object with default values.

        """
        return PresetSettings(
            exposure=0.0,
            contrast=0.0,
            temperature=0.0,
            tint=0.0,
            color_boost=0.0,
            grain=PresetSettingsState.OFF,
            bloom=PresetSettingsState.OFF,
            halation=PresetSettingsState.OFF,
            vignette_exposure=PresetSettingsState.OFF,
            vignette_size=55.0,
            vignette_feather=15.0,
        )

    def __repr__(self) -> str:
        """
        Customize the string representation of the PresetSettings object.

        Returns
        -------
        str: A string showing all settings in a readable format.

        """
        return (
            f"Exposure: '{self.exposure}', Contrast: '{self.contrast}', Temperature: '{self.temperature}', "
            f"Tint: '{self.tint}', Color boost: '{self.color_boost}'\n"
            f"Grain: '{self.grain}', Bloom: '{self.bloom}', Halation: '{self.halation}'\n"
            f"Vignette exposure: '{self.vignette_exposure}', size: '{self.vignette_size}', feather: '{self.vignette_feather}'"  # noqa: E501
        )

    def get_adjustments_str(self) -> str:
        """Return a formatted string of adjustment settings."""
        return (
            f"Exposure: '{self.exposure}', "
            f"Contrast: '{self.contrast}', "
            f"Temperature: '{self.temperature}', "
            f"Tint: '{self.tint}', "
            f"Color boost: '{self.color_boost}'"
        )

    def get_effects_str(self) -> str:
        """Return a formatted string of effect settings."""
        return (
            f"Grain: '{self.grain}', "
            f"Bloom: '{self.bloom}', "
            f"Halation: '{self.halation}', "
            f"Vignette exposure: '{self.vignette_exposure}', "
            f"Vignette size: '{self.vignette_size}', "
            f"Vignette feather: '{self.vignette_feather}'"
        )

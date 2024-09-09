from dataclasses import dataclass


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


@dataclass
class PresetSettings:  # noqa: D101
    exposure: float
    contrast: float
    temperature: float
    tint: float
    color_boost: float
    bloom: float
    halation: float
    grain: float

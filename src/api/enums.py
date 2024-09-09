from __future__ import annotations

from enum import Enum


class ImageSize(Enum):  # noqa: D101
    SMALL = "small"
    LARGE = "large"


class ExportFormat(Enum):
    """
    Enum representing different export formats for images.

    Format Name    | Description       | Resolution               | Format & Quality
    -------------- | ----------------- | ------------------------ | ------------------
    WEB            | Optimised for web | Resized to 2160x2160     | JPEG 80%
    JPEG           | Best quality      | Max resolution 3024x3024 | JPEG 100%
    TIFF           | Lossless          | Max resolution 3024x3024 | TIFF 16 bit

    """

    WEB = "web"
    JPEG = "jpeg"
    TIFF = "tiff"


class ImageQuality(Enum):
    """
    Enum representing image export quality levels (for UX), mapped to specific export formats (in Dehancer Online API).

    Attributes
    ----------
    LOW : Represents a low quality export, mapped to `ExportFormat.WEB`, which is optimised for web use.
    MEDIUM : Represents a medium quality export, mapped to `ExportFormat.JPEG`, which provides high quality JPEG images.
    HIGH : Represents high quality export, mapped to `ExportFormat.TIFF`, which provides maximum resolution TIFF images.

    """

    LOW = ExportFormat.WEB
    MEDIUM = ExportFormat.JPEG
    HIGH = ExportFormat.TIFF

    @staticmethod
    def from_string(label: str) -> ImageQuality:
        """
        Convert a string to the corresponding ImageQuality enum value.

        Args:
        ----
        label (str): The string input that should be converted.

        Returns:
        -------
        ImageQuality: The corresponding ImageQuality enum value.

        Raises:
        ------
        UnknownImageQualityError: If the input string does not correspond to any ImageQuality value.

        """
        label_mapping = {
            "low": ImageQuality.LOW,
            "medium": ImageQuality.MEDIUM,
            "high": ImageQuality.HIGH,
        }
        try:
            return label_mapping[label.strip().lower()]
        except KeyError as key_error:
            raise UnknownImageQualityError(label) from key_error

    @staticmethod
    def from_export_format(export_format: ExportFormat) -> ImageQuality:
        """
        Convert a ExportFormat enum value to the corresponding ImageQuality enum value.

        Args:
        ----
        export_format (ExportFormat): The export format input that should be converted.

        Returns:
        -------
        ImageQuality: The corresponding ImageQuality enum value.

        Raises:
        ------
        UnknownImageQualityError: If the input export format does not correspond to any ImageQuality value.

        """
        export_format_mapping = {
            ExportFormat.WEB: ImageQuality.LOW,
            ExportFormat.JPEG: ImageQuality.MEDIUM,
            ExportFormat.TIFF: ImageQuality.HIGH,
        }
        try:
            return export_format_mapping[ExportFormat(export_format.name.lower())]
        except KeyError as key_error:
            raise UnknownImageQualityError(export_format) from key_error  # pragma: no cover, all ExportFormat are mapped # noqa: E501
        except AttributeError as attribute_error:
            raise UnknownImageQualityError(export_format) from attribute_error


class UnknownImageQualityError(Exception):
    """
    Exception raised when an unknown image quality is provided.

    This exception is intended to be used when a provided value does not match any predefined ImageQuality values.
    It inherits from the base Exception class and adds a custom error message that includes the unknown value.

    Args:
    ----
    input_value (str | ExportFormat): The unknown image quality label or ExportFormat value that caused the exception.

    Example:
    -------
    >>> raise UnknownImageQualityError("ultra")
    Traceback (most recent call last):
        ...
    UnknownImageQualityError: Unknown quality level: ultra
    >>> raise UnknownImageQualityError(ImageQuality.ULTRA)  # noqa
    Traceback (most recent call last):
        ...
    UnknownImageQualityError: Unknown quality level: ultra

    """

    def __init__(self, input_value: str | ExportFormat) -> None:
        if isinstance(input_value, ExportFormat):
            message = f"Unknown quality level: {input_value.name}"  # pragma: no cover, all ExportFormat are mapped
        else:
            message = f"Unknown quality level: {input_value}"
        super().__init__(message)

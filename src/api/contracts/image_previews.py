from pydantic import AnyUrl, BaseModel, ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo

EXPECTED_NUMBER_OF_IMAGES_URLS = 75

class ImagePreviewsModel(BaseModel):
    """
    Representation of a response containing preview image URLs.

    This model describes the structure returned by the Dehancer Online API when requesting preview images
    for a particular source image and preset configuration.
    It contains a flag that indicates whether the operation was successful, as well as a list of generated preview URLs.
    The number of returned URLs is verified to ensure it matches the expected count.

    Attributes
    ----------
    success : bool
        Whether the server reported the preview generation operation as successful.
    images : list[AnyUrl]
        List of presigned URLs for the preview images.
        Uses pydantic's ``AnyUrl`` for basic URL validation (scheme, host, etc.).
        The list must contain exactly the expected number of preview URLs; otherwise, validation will fail.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    images: list[AnyUrl]

    @field_validator("images")
    @classmethod
    def validate_images_sections(cls, value: list[AnyUrl], info: ValidationInfo) -> list[AnyUrl]:
        """
        Check that the 'images' field contains the expected number of urls.

        Args:
        ----
            value (list[AnyUrl]): List of urls to validate.
            info (ValidationInfo): Contextual validation metadata,
            may optionally include an override for the expected number of preview URLs.

        Returns:
        -------
            list[AnyUrl]: The original list of URLs passes validation.

        Raises:
        ------
            ValueError: If the 'images' field does not match EXPECTED_NUMBER_OF_IMAGES_URLS.

        """
        expected_num_of_imgs_urls = EXPECTED_NUMBER_OF_IMAGES_URLS
        if getattr(info, "context", None):
            expected_num_of_imgs_urls = info.context.get("expected_num_of_imgs_urls",
                                                         EXPECTED_NUMBER_OF_IMAGES_URLS)  # pragma: no cover
        if len(value) != expected_num_of_imgs_urls:
            message = (f"The expected number of images is '{expected_num_of_imgs_urls}' items, "
                       f"got '{len(value)}'")  # pragma: no cover
            raise ValueError(message)  # pragma: no cover
        return value

from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
)


class LastImageModel(BaseModel):
    """
    Representation of the last processed image metadata.

    The model describes the minimal amount of metadata that the Dehancer Online API returns about a previously processed image.
    It is intended to be embedded within a higher-level export response.

    Attributes
    ----------
    image_id : str
        Identifier of the image. It must be a non-empty. It is mapped from the JSON key ``imageId``.
    title : str
        Human-readable preset name associated with the image.
    thumbnail : str
        It must be a non-empty. It is a small preview image (usually in base64 or data URI format).
    updated_at : int
        Unix timestamp (in seconds since the epoch) shows when the image was last updated.
        Must be a positive integer (``gt=0``).

    """  # noqa: E501

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    image_id: str = Field(..., alias="imageId", min_length=1)
    title: str
    thumbnail: str = Field(..., min_length=1)
    updated_at: int = Field(alias="updatedAt", gt=0)


class ImageExportModel(BaseModel):
    """
    Representation of an image export operation result.

    This model describes the response returned by the Dehancer Online API after an image export operation.
    It includes a presigned URL for the exported image, identifying information, and last image processed metadata.

    Attributes
    ----------
    success : bool
        Whether the server reported the image export operation as successful.
    url : AnyUrl
        Presigned URL to download the exported image.
        Uses pydantic's ``AnyUrl`` for basic URL validation (scheme, host, etc.).
    image_id : str
        Identifier of the exported image. It must be a non-empty. It is mapped from the JSON key ``imageId``.
    last_image : LastImageModel
        Metadata for the last processed image (embedded object).
    filename : str
        Suggested filename for the downloaded image. It must be a non-empty.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    url: AnyUrl
    image_id: str = Field(..., alias="imageId", min_length=1)
    last_image: LastImageModel = Field(alias="lastImage")
    filename: str = Field(..., min_length=1)

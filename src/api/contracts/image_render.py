from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class ImageRenderModel(BaseModel):
    """
    Representation of an image render operation result.

    This model describes the response that the Dehancer Online API after requesting a rendered image.
    It contains a success flag and an optional ID for the rendered image, as well as a URL for the rendered output.

    Attributes
    ----------
    success : bool
        Whether the server reported the render operation as successful.
    image_id : str | None
        Identifier of the rendered image. It is mapped from the JSON key ``imageId``.
        May be ``None`` if the server does not provide an ID (e.g., in error scenarios).
    url : AnyUrl
        Presigned URL to download the rendered image.
        Uses pydantic's ``AnyUrl`` for basic URL validation (scheme, host, etc.).

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    image_id: str | None = Field(alias="imageId")
    url: AnyUrl

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, model_validator


class ImageUploadPrepareModel(BaseModel):
    """
    Representation of an image upload preparation operation result.

    This model describes the structure returned by the Dehancer Online API when preparing an image upload.
    The API supports both single-part and multipart workflows:
    - For single-part, one presigned URL is used for upload.
    - For multipart, a list of presigned URLs is used for upload.

    Attributes
    ----------
    success : bool
        Whether the server reported the upload-preparation request as successful.
    image_id : str
        Identifier assigned to the image being uploaded. It is mapped from the JSON key ``imageId``.
    chunk_size : int | None
        Specifies the size of each upload chunk.
        Must be a positive integer (``gt=0``).
    upload_id : str | None
        Identifier for the upload session.
    urls : list[AnyUrl] | None
        List of presigned URLs for uploads in single-part and multipart modes. At least one item must be provided.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    image_id: str = Field(alias="imageId")
    chunk_size: int | None = Field(default=None, alias="chunkSize", gt=0)
    upload_id: str | None = Field(default=None, alias="uploadId")
    urls: list[AnyUrl] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_consistency(self) -> "ImageUploadPrepareModel":  # pragma: no cover
        if not self.success:
            # If API signals failure, treat as invalid contract for this success-model.
            message = "Response indicates failure (success is False)"
            raise ValueError(message)
        return self

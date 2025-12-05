from pydantic import AnyUrl, BaseModel, ConfigDict, Field, model_validator


class ImageUploadPrepareModel(BaseModel):
    """
    Representation of an image upload preparation operation result.

    This model describes the structure returned by the Dehancer Online API when preparing an image upload.
    The API supports both single-part and multipart upload workflows, and the model enforces internal consistency rules
    to ensure that only the fields relevant to the selected upload mode are present.

    Attributes
    ----------
    success : bool
        Whether the server reported the upload-preparation request as successful.
    image_id : str
        Identifier assigned to the image being uploaded. It is mapped from the JSON key ``imageId``.
    url : AnyUrl | None
        Presigned URL for uploading the file in single-part upload mode.
        Present only when ``is_multipart`` is ``False``.
    is_multipart : bool
        Indicates whether multipart upload mode is used. It is mapped from the JSON key ``isMultipart``.
    chunk_size : int | None
        Required only for multipart uploads. Specifies the size of each upload chunk.
        Must be a positive integer (``gt=0``).
    upload_id : str | None
        Identifier for the multipart upload session.
        Required only when ``is_multipart`` is ``True``.
    urls : list[AnyUrl] | None
        List of presigned URLs for multipart upload. Must contain at least one item when provided.

    Notes
    -----
    Model-level validation ensures strong contract guarantees:
    - For single-part uploads, ``url`` must be present.
    - For multipart uploads, ``upload_id``, ``chunk_size``, and ``urls`` must all be provided.

    """

    model_config = ConfigDict(extra="forbid")

    success: bool
    image_id: str = Field(alias="imageId")
    # Single-part: only one url
    url: AnyUrl | None = Field(default=None)
    # Multipart: list of urls
    is_multipart: bool = Field(default=False, alias="isMultipart")
    chunk_size: int | None = Field(default=None, alias="chunkSize", gt=0)
    upload_id: str | None = Field(default=None, alias="uploadId")
    urls: list[AnyUrl] | None = Field(default=None, min_length=1)

    # Model-level validation to enforce contract invariants
    @model_validator(mode="after")
    def _validate_consistency(self) -> "ImageUploadPrepareModel":  # pragma: no cover
        """
        Enforce that either:
         - single-part: `is_multipart` is False and `url` is present; or
         - multipart: `is_multipart` is True and `upload_id`, `chunk_size` and `urls` are present.
        """  # noqa: D205
        if not self.success:
            # If API signals failure, treat as invalid contract for this success-model.
            message = "Response indicates failure (success is False)"
            raise ValueError(message)
        if self.is_multipart:
            missing = []
            if not self.upload_id:
                missing.append("uploadId")
            if not self.chunk_size:
                missing.append("chunkSize")
            if not self.urls:
                missing.append("urls")
            if missing:
                message = "Multipart response is missing required fields: " + ", ".join(missing)
                raise ValueError(message)
        # Single-part expected to have url
        elif not self.url:
            message = "Single-part response must contain 'url' field"
            raise ValueError(message)
        return self

from __future__ import annotations

import logging
import logging.config
from typing import TYPE_CHECKING, Any

from requests import Response, Session
from requests_toolbelt.utils import dump

from src import utils

if TYPE_CHECKING:
    from requests.structures import CaseInsensitiveDict  # pragma: no cover

logging.config.dictConfig(utils.get_logger_config_dict())
logger = logging.getLogger()

LARGE_BODY_PLACEHOLDER = "<body removed: binary content>"


class BaseAPIClient:  # noqa: D101

    def __init__(self) -> None:
        self.session = Session()
        self.session.hooks["response"] = [self.logging_hook]

    def set_session_cookies(self, cookies: dict[str, str]) -> None:
        """Set cookies in the session."""
        if cookies:
            for name, value in cookies.items():
                self.session.cookies.set(name, value)

    @staticmethod
    def is_large_content(headers: CaseInsensitiveDict, max_size: int = 100_000) -> bool:
        """Check if the content is too large to be logged."""
        if not headers:
            return False
        content_length = headers.get("Content-Length")
        return content_length and content_length.isdigit() and int(content_length) > max_size

    @staticmethod
    def is_binary_content(headers: CaseInsensitiveDict) -> bool:
        """Check if the content is binary (image, video, etc.)."""
        content_type = headers.get("Content-Type", "").lower()
        return any(ctype in content_type for ctype in ("image", "video", "audio", "application/octet-stream"))

    @classmethod
    def should_replace_large_body(cls, headers: CaseInsensitiveDict) -> bool:
        """Determine whether to replace the body based on content length or content type."""
        return cls.is_large_content(headers) or cls.is_binary_content(headers)

    @classmethod
    def logging_hook(cls, response: Response, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:  # noqa: ARG003
        """Log request and response, replacing large binary bodies with placeholders."""
        raw_data = (dump.dump_all(response, request_prefix=b"> ", response_prefix=b"< ")
                    .decode("utf-8", errors="replace"))

        # Remove request body if necessary
        request_body = response.request.body
        if isinstance(request_body, bytes) and cls.should_replace_large_body(response.request.headers):
            request_body = request_body.decode("utf-8", errors="replace")
            raw_data = raw_data.replace(request_body, LARGE_BODY_PLACEHOLDER)

        # Remove response body if necessary
        if cls.should_replace_large_body(response.headers):
            header_part, _, _ = raw_data.partition("\n\n")
            raw_data = f"{header_part}\n\n{LARGE_BODY_PLACEHOLDER}"

        logging.debug(raw_data)

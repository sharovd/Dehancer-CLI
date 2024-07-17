import logging
import logging.config
from typing import Any, Dict, Tuple

from requests import Response, Session
from requests_toolbelt.utils import dump

from src import utils

logging.config.dictConfig(utils.get_logger_config_dict())
logger = logging.getLogger()


class BaseAPIClient:  # noqa: D101

    def __init__(self) -> None:
        self.session = Session()
        self.session.hooks["response"] = [self.logging_hook]

    @staticmethod
    def logging_hook(response: Response, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:  # noqa: D102, ARG004, FA100
        data = dump.dump_all(response)
        logging.debug(data.decode("utf-8", errors="replace"))

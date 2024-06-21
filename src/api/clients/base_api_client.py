import logging.config
import logging.handlers
import logging
from requests_toolbelt.utils import dump
from requests import Session

from src import utils

logging.config.fileConfig(utils.get_logger_config_file_path())
logger = logging.getLogger()


class BaseAPIClient:

    def __init__(self):
        self.session = Session()
        self.session.hooks["response"] = [self.logging_hook]

    @staticmethod
    def logging_hook(response, *args, **kwargs):
        data = dump.dump_all(response)
        logging.debug(data.decode('utf-8', errors='replace'))

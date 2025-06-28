from app.utils.config import write_log_to_file
from .base import ItenderBaseSpider

import logging

logger = logging.getLogger(__name__)


class ArbitatSpider(ItenderBaseSpider):
    name = "arbitat"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

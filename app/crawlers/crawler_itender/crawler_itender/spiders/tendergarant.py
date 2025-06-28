from app.utils.config import headers, write_log_to_file
from ..spiders.base import ItenderBaseSpider


class TendergarantSpider(ItenderBaseSpider):
    name = "tendergarant"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "DEFAULT_REQUEST_HEADERS": headers | {"Accept-Encoding": "gzip, deflate"},
    }

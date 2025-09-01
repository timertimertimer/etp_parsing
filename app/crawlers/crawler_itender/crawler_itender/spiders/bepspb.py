from app.utils.config import headers, write_log_to_file
from .base import ItenderBaseSpider


class BepspbSpider(ItenderBaseSpider):
    name = "bepspb"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "DEFAULT_REQUEST_HEADERS": headers | {"Accept-Encoding": "gzip, deflate"},
    }

from general_utils.config import write_log_to_file
from .base import LotOnlineZalogBaseSpider


class LotOnlineZalogRadSpider(LotOnlineZalogBaseSpider):
    name = "rad"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

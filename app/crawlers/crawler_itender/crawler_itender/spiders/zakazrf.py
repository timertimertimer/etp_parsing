from app.utils.config import write_log_to_file
from ..spiders.base import ItenderBaseSpider


class ZakazrfSpider(ItenderBaseSpider):
    name = "zakazrf"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

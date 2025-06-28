from app.utils.config import write_log_to_file
from ..spiders.base import ItenderBaseSpider


class UtenderSpider(ItenderBaseSpider):
    name = "utender"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

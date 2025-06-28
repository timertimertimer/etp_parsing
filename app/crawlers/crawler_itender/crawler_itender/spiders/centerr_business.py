
from app.utils.config import write_log_to_file
from .base import ItenderBaseSpider

# arrested/commercial
class CenterrBusinessSpider(ItenderBaseSpider):  # TODO
    name = "centerr_business"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

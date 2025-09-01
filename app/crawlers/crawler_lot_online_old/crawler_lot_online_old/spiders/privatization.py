from app.utils.config import write_log_to_file
from .base import LotOnlineOldBaseSpider


class LotOnlinePrivatizationSpider(LotOnlineOldBaseSpider):
    name = "privatization"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

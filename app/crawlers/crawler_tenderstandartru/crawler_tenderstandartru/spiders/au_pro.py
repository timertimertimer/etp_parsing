from app.utils.config import write_log_to_file
from .base import TenderstandartBaseSpider


class AuProSpider(TenderstandartBaseSpider):
    name = "au_pro"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

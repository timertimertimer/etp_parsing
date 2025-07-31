from app.utils.config import write_log_to_file
from .base import AltimetaBaseSpider


class RegtorgSpider(AltimetaBaseSpider):
    name = "regtorg"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

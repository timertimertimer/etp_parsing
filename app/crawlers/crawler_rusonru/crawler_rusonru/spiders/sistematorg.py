from app.db.models import AuctionPropertyType
from app.utils.config import write_log_to_file
from .base import RusonBaseSpider


class SistematorgSpider(RusonBaseSpider):
    name = "sistematorg"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

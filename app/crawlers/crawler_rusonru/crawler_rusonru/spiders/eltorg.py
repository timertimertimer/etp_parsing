from app.db.models import AuctionPropertyType
from app.utils.config import write_log_to_file
from .base import RusonBaseSpider


class EltorgBankruptSpider(RusonBaseSpider):
    name = "eltorg_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EltorgCommercialSpider(RusonBaseSpider):
    name = "eltorg_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

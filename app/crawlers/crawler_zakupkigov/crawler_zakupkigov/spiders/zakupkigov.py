import scrapy

from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType


class ZakupkigovBaseSpider(BaseSpider):
    name = "zakupkigov"

    def parse(self, response):
        pass

class ZakupkigovFz44Spider(ZakupkigovBaseSpider):
    name = "zakupkigov_fz44"
    property_type = AuctionPropertyType.fz44

class ZakupkigovCapitalRepairSpider(ZakupkigovBaseSpider):
    name = "zakupkigov_capital_repair"
    property_type = AuctionPropertyType.capital_repair

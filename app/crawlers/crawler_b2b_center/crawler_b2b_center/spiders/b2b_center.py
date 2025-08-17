from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType


class B2bCenterBaseSpider(BaseSpider):
    name = "b2b_center"
    allowed_domains = ["www.b2b-center.ru"]
    start_urls = ["https://www.b2b-center.ru/market"]

    def parse(self, response):
        pass

class B2bCenterFz223Spider(B2bCenterBaseSpider):
    name = "b2b_center_fz223"
    property_type = AuctionPropertyType.fz223

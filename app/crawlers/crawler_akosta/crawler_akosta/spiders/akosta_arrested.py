from app.crawlers.crawler_akosta.crawler_akosta.spiders.base import AkostaBaseSpider
from app.db.models import AuctionPropertyType


class AkostaArrestedSpider(AkostaBaseSpider):
    name = "akosta_arrested"
    property_type = AuctionPropertyType.arrested

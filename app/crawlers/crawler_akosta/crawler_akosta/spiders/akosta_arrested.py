from app.crawlers.crawler_akosta.crawler_akosta.spiders.base import AkostaBaseSpider
from app.db.models import AuctionProperty


class AkostaArrestedSpider(AkostaBaseSpider):
    name = "akosta_arrested"
    auction_property = AuctionProperty.arrested

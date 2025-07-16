from app.crawlers.crawler_sitesoft.crawler_sitesoft.spiders.base import (
    SitesoftBaseSpider,
)
from app.db.models import AuctionPropertyType


class CdtrfBaseSpider(SitesoftBaseSpider):
    name = "cdtrf_arrested"
    property_type = AuctionPropertyType.arrested

from app.db.models import AuctionPropertyType
from .base import AkostaBaseSpider


class AkostaBankruptSpider(AkostaBaseSpider):
    name = "akosta_bankrupt"
    property_type = AuctionPropertyType.bankruptcy
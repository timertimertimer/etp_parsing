from app.db.models import AuctionProperty
from .base import AkostaBaseSpider


class AkostaBankruptSpider(AkostaBaseSpider):
    name = "akosta_bankrupt"
    auction_property = AuctionProperty.bankruptcy
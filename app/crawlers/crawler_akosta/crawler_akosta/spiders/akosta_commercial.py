from app.db.models import AuctionPropertyType
from .base import AkostaBaseSpider


class AkostaCommercialSpider(AkostaBaseSpider):
    name = "akosta_commercial"
    property_type = AuctionPropertyType.commercial

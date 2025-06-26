from .auction import AuctionParse
from .offer import OfferParse


class ComposeTrades:
    def __init__(self, data, url):
        self.auc = AuctionParse(data, url)
        self.offer = OfferParse(data, url)

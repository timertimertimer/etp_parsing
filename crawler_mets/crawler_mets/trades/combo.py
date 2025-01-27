from .auction import AuctionParse
from .offer import OfferParse


class ComposeTrades(OfferParse, AuctionParse):

    def __init__(self, response_):
        self.response = response_
        self.auc = AuctionParse(self.response)
        self.offer = OfferParse(self.response)

from .offer import OfferParse
from .auction import AuctionParse
from .serp import SerpParse


class ComposeTrade(OfferParse):

    def __init__(self, response_):
        super().__init__(response_)
        self.response = response_
        self.offer = OfferParse(self.response)
        self.auc = AuctionParse(self.response)
        self.serp = SerpParse(self.response)
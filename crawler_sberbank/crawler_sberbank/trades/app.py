from .auction import AuctionParse
from .offer import OfferParse
from .competition import CompetitionParse


class ComposeTrades(AuctionParse, OfferParse, CompetitionParse):

    def __init__(self, response_):
        self.response = response_
        self.auc = AuctionParse(self.response)
        self.offer = OfferParse(self.response)
        self.comp = CompetitionParse(self.response)
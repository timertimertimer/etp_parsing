from .auction import AuctionParse
from .offer import OfferParse
from .competition import CompetitionParse


class ComposeTrades(AuctionParse, OfferParse, CompetitionParse):

    def __init__(self, data, url):
        self.auc = AuctionParse(data, url)
        self.offer = OfferParse(data, url)

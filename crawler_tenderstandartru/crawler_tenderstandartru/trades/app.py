from .serp import SerpParse
from .auction import AuctionParse
from .offer import OfferParse
from .files import LotFiles, GeneralFiles


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpParse(self.response)
        self.auc = AuctionParse(self.response)
        self.gen = GeneralFiles(self.response)
        self.lot = LotFiles(self.response)
        self.offer = OfferParse(self.response)

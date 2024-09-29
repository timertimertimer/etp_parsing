from .serp import SerpParse
from .auction import Auction
from .offer import OfferParse
from .files import GeneralFiles, Lot_Files


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpParse(response_=self.response)
        self.auc = Auction(response_=self.response)
        self.offer = OfferParse(response_=self.response)
        self.gen = GeneralFiles(response_=self.response)
        self.lot = Lot_Files(response_=self.response)

from .serp import SerpPage
from .auction import AuctionPage
from .offer import OfferPage
from .files import General
from .files import LotFiles


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpPage(response_=self.response)
        self.auc = AuctionPage(response_=self.response)
        self.offer = OfferPage(response_=self.response)
        self.general = General(response_=self.response)
        self.lot = LotFiles(response_=self.response)

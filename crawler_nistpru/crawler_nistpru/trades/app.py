from .offer import OfferParse
from .auction import AuctionParse
from .serp import SerpParse
from .documents import DocumentGeneral
from .documents import DocumentLot


class Combo:
    def __init__(self, response_):
        self.response = response_
        self.auc = AuctionParse(self.response)
        self.offer = OfferParse(self.response)
        self.serp = SerpParse(self.response)
        self.doc_gen = DocumentGeneral(self.response)
        self.doc_loc = DocumentLot(self.response)

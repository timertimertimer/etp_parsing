from .serp_page import SerpPage
from .auction_page import AucPage
from .offer_page import OfferPage
from .documents_page import DocPage


class Combo:
    def __init__(self, response_):
        self.response = response_
        self.serp = SerpPage(response_=self.response)
        self.auc = AucPage(response=self.response)
        self.offer = OfferPage(response_=self.response)
        self.doc = DocPage(response_=self.response)

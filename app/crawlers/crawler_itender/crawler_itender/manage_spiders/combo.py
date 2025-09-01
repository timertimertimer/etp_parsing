from .manage_auc_page import AuctionPage
from .manage_post import ManagePost
from .manage_serp_info import SerpPageSearchInfo
from .manage_offer_page import OfferPage
from .manage_competition_page import CompetitionPage


class Combo:
    def __init__(self, response):
        self.response = response
        self.mpost = ManagePost(self.response)
        self.serp = SerpPageSearchInfo(self.response)
        self.auc = AuctionPage(self.response)
        self.offer = OfferPage(self.response)
        self.compet = CompetitionPage(self.response)

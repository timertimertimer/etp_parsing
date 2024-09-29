from .serp_pages import SerpPages
from .lot_page import LotPage


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpPages(self.response)
        self.lot = LotPage(self.response)
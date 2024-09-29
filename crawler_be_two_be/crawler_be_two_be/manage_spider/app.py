from .search import Search
from .trade_page import TradePage
from .lot_tab import LotTab
from .lot_page_auc import AuctionLotPage
from .lot_page_offer import OfferLotPage
from .organizer_page import OrgPage
from .documents import DocumentLot, DocumentGeneral


class Combo:
    def __init__(self, response_):
        self.response = response_
        self.search = Search(self.response)
        self.trade = TradePage(self.response)
        self.lt = LotTab(self.response)
        self.auc = AuctionLotPage(self.response)
        self.offer = OfferLotPage(self.response)
        self.org = OrgPage(self.response)
        self.general = DocumentGeneral(self.response)
        self.lotdoc = DocumentLot(self.response)

from .pre_trade import PreTradePage
from .general_info_page import MainTradingPage
from .trade_page_with_tabs import TradePage
from .debtor_tab_page import DebrorTab
from .lot_auction_page import LotAuctionPage
from .lot_offer_page import LotOfferPage


class Combo:

    def __init__(self, _response):
        self.response = _response
        self.pre = PreTradePage(self.response)
        self.main_ = MainTradingPage(self.response)
        self.trade = TradePage(self.response)
        self.deb = DebrorTab(self.response)
        self.auc = LotAuctionPage(self.response)
        self.offer = LotOfferPage(self.response)

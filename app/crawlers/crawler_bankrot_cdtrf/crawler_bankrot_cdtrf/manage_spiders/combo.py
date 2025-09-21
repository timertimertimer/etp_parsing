from app.utils import dedent_func, logger
from .offer_spider import OfferSpider
from .auction_spider import AuctionSpider
from ..locators_and_attributes.locators_attributes import LocatorMain
from bs4 import BeautifulSoup as BS


class Compose:
    def __init__(self, response_):
        super(Compose, self).__init__()
        self.response = response_
        self.offer = OfferSpider(self.response)
        self.auction = AuctionSpider(self.response)
        self.loc = LocatorMain

    @property
    def get_trading_type(self):
        trading_type = self.response.xpath(self.loc.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(
                BS(str(trading_type), features="lxml").get_text()
            ).strip()
            if type_ in [
                "Аукцион",
                "Открытый аукцион",
                "Закрытый аукцион",
                "Конкурс",
                "Открытый конкурс",
                "Закрытый конкурс",
                "Голландский аукцион",
            ]:
                return "auction"
            elif type_ in [
                "Публичное предложение",
                "Открытое публичное предложение",
                "Закрытое публичное предложение",
            ]:
                return "offer"
            else:
                logger.warning(f"{self.response.url} :: INVALID DATA TRADING TYPE")
        return None

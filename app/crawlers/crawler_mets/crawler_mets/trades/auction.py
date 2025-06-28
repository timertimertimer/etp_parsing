import logging
import re

from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, format_time
from ..locators.trade_locator import LocatorAuction

logger = logging.getLogger(__name__)


class AuctionParse:
    def __init__(self, response):
        self.response = response

    def step_price(self, trading_number, lot_num: str):
        trading_number = "".join(trading_number)
        step_price = self.response.xpath(
            LocatorAuction.step_price_loc.format(lot_num)
        ).get()
        try:
            step_price = dedent_func(
                BS(str(step_price), features="lxml").get_text(strip=True)
            )
            pattern = r"^\d+\.\d{1,2}"
            if "руб" in step_price:
                step_price = "".join(re.split(r"руб", step_price, maxsplit=1)[0])
            clean_price = "".join(
                filter(lambda x: x.isdigit() or x == ",", step_price)
            ).replace(",", ".")
            match = "".join(re.findall(pattern, clean_price))
            if match:
                return round(float(match), 2)
        except Exception:
            if not re.match(r"\d{3,}-ОАЗФ", trading_number):
                logger.warning(
                    f"{self.response.url} | LOT {lot_num} INVALID DATA - STEP PRICE - LOT {lot_num}"
                )
        return None

    @property
    def start_date_request(self):
        try:
            td_date = self.response.xpath(LocatorAuction.start_date_request_loc).get()
            td_date = dedent_func(
                BS(str(td_date), features="lxml").get_text(strip=True)
            )
            return format_time(td_date.strip())
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA START DATE REQUEST AUCTION/COMPETITION"
            )
        return None

    @property
    def end_date_request(self):
        try:
            td_date = self.response.xpath(LocatorAuction.end_date_request_loc).get()
            td_date = dedent_func(
                BS(str(td_date), features="lxml").get_text(strip=True)
            )
            return format_time(td_date.strip())
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA END DATE REQUEST AUCTION/COMPETITION"
            )
        return None

    @property
    def start_date_trading(self):
        try:
            td_date = self.response.xpath(LocatorAuction.start_date_trading_loc).get()
            td_date = dedent_func(
                BS(str(td_date), features="lxml").get_text(strip=True)
            )
            return format_time(td_date.strip())
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA START DATE TRADING AUCTION/COMPETITION"
            )
        return None

    @property
    def end_date_trading(self):
        try:
            td_date = self.response.xpath(LocatorAuction.end_date_trading_loc).get()
            td_date = dedent_func(
                BS(str(td_date), features="lxml").get_text(strip=True)
            )
            return format_time(td_date.strip())
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA END DATE TRADING AUCTION/COMPETITION"
            )
        return None

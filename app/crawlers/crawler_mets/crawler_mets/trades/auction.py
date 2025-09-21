import re

from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, DateTimeHelper, logger
from ..locators.trade_locator import LocatorAuction


class AuctionParse:
    def __init__(self, response):
        self.response = response

    def get_step_price(self, trading_number, lot_num: str):
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
        except Exception as e:
            if not re.match(r"\d{3,}-ОАЗФ", trading_number):
                logger.warning(
                    f"{self.response.url} | LOT {lot_num} INVALID DATA - STEP PRICE - LOT {lot_num}"
                )
        return None

    @property
    def start_date_requests(self):
        td_date = self.response.xpath(LocatorAuction.start_date_request_loc).get()
        if not td_date:
            return None
        td_date = dedent_func(BS(str(td_date), features="lxml").get_text(strip=True))
        return DateTimeHelper.smart_parse(td_date.strip()).astimezone(
            DateTimeHelper.moscow_tz
        )

    @property
    def end_date_requests(self):
        td_date = self.response.xpath(LocatorAuction.end_date_request_loc).get()
        if not td_date:
            return None
        td_date = dedent_func(BS(str(td_date), features="lxml").get_text(strip=True))
        return DateTimeHelper.smart_parse(td_date.strip()).astimezone(
            DateTimeHelper.moscow_tz
        )

    @property
    def start_date_trading(self):
        td_date = self.response.xpath(LocatorAuction.start_date_trading_loc).get()
        if not td_date:
            return None
        td_date = dedent_func(BS(str(td_date), features="lxml").get_text(strip=True))
        return DateTimeHelper.smart_parse(td_date.strip()).astimezone(
            DateTimeHelper.moscow_tz
        )

    @property
    def end_date_trading(self):
        td_date = self.response.xpath(LocatorAuction.end_date_trading_loc).get()
        if not td_date:
            return None
        td_date = dedent_func(BS(str(td_date), features="lxml").get_text(strip=True))
        return DateTimeHelper.smart_parse(td_date.strip()).astimezone(
            DateTimeHelper.moscow_tz
        )

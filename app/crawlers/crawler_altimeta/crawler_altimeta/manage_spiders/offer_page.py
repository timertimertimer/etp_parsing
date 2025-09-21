import re
import pandas as pd
from bs4 import BeautifulSoup as BS

from app.utils import DateTimeHelper, make_float, dedent_func, logger
from ..locators.locator_lot_page import LocatorLotPage
from numpy import float64


class OfferPage:
    def __init__(self, response_):
        self.response = response_
        self.loc_lot = LocatorLotPage
        self.soup = BS(
            str(self.response.text).replace("&lt;", "<").replace("&gt;", ">"),
            features="lxml",
        )

    def get_lot_tables(self):
        tables_all = self.response.xpath(self.loc_lot.get_lot_table_offer).getall()
        return tables_all

    def get_table_period(self, table_):
        table = BS(str(table_), features="lxml")
        return table

    def get_start_date_requests(self, table_):
        try:
            table = self.get_table_period(table_)
            table = table.find("table", class_="data inner")
            table = pd.read_html(str(table))
            df = table[0]
            return DateTimeHelper.smart_parse(df.iloc[0][0]).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR start_date_request {e}", exc_info=True
            )
        return None

    def get_end_date_requests(self, table_):
        try:
            table = self.get_table_period(table_)
            table = table.find("table", class_="data inner")
            table = pd.read_html(str(table))
            df = table[0]
            return DateTimeHelper.smart_parse(df.iloc[-1][1]).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR end_date_request {e}", exc_info=True
            )
        return None

    def get_start_date_trading(self, table_):
        return self.get_start_date_requests(table_)

    def get_end_date_trading(self, table_):
        return self.get_end_date_requests(table_)

    def get_start_price_offer(self, table_):
        try:
            table = self.get_table_period(table_)
            table = table.find("table", class_="data inner")
            table = pd.read_html(re.sub(r",", ".", str(table)))
            df = table[0]
            start_price = df.iloc[0][2]
            if isinstance(start_price, str):
                start_price_ = make_float(start_price)
            elif isinstance(start_price, float64):
                start_price_ = round(float(start_price), 2)
            else:
                logger.warning(f"{self.response.url} :: INVALID TYPE START PRICE PRICE")
                start_price_ = None
            return start_price_
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR start_price_offer {e}", exc_info=True
            )
        return None

    def get_period(self, table_):
        check_value = int(10000000000000000000000)
        periods = list()
        table = BS(str(table_), features="lxml")
        table = table.find("table", class_="data inner")
        table = pd.read_html(re.sub(r",", ".", str(table)))
        df = table[0]
        try:
            for t in range(len(df)):
                start_date_request = df.iloc[t][0]
                end_date_request = df.iloc[t][1]
                end_date_trading = df.iloc[t][1]
                current_price = df.iloc[t][2]
                if not re.match(r"nan", str(current_price), re.IGNORECASE):
                    if isinstance(current_price, str):
                        current_price_ = make_float(current_price)
                    elif isinstance(current_price, float64):
                        current_price_ = round(float(current_price), 2)
                    else:
                        logger.warning(
                            f"{self.response.url} :: INVALID TYPE CURRENT PRICE"
                        )
                        current_price_ = None
                    period = {
                        "start_date_requests": DateTimeHelper.smart_parse(start_date_request).astimezone(
                            DateTimeHelper.moscow_tz),
                        "end_date_requests": DateTimeHelper.smart_parse(end_date_request).astimezone(
                            DateTimeHelper.moscow_tz),
                        "end_date_trading": DateTimeHelper.smart_parse(end_date_trading).astimezone(
                            DateTimeHelper.moscow_tz),
                        "current_price": current_price_,
                    }
                    periods.append(period)
                    if check_value < current_price_:
                        logger.critical(
                            f"{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS",
                            df,
                        )
                    check_value = current_price_
            return periods
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: PERIODS ERROR {e}\n{df}", exc_info=True
            )
            return None

    def get_next_page_number(self):
        page = self.response.xpath(self.loc_lot.pagination).get()
        if page:
            return dedent_func(page.strip())
        return None

import pandas as pd
from bs4 import BeautifulSoup

from app.utils import DateTimeHelper, normalize_string, logger


class OfferParse:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, "lxml")

    def start_date_trading(self, lot):
        try:
            table = self.period_table(lot)
            return DateTimeHelper.smart_parse(table.iloc[0, 1]).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID LOT DATA START DATE REQUEST LOT"
            )
            return None

    def end_date_trading(self, lot):
        try:
            table = self.period_table(lot)
            return DateTimeHelper.smart_parse(table.iloc[-1, 1]).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID LOT DATA START DATE REQUEST LOT"
            )
            return None

    def period_table(self, lot):
        try:
            soup = BeautifulSoup(lot, "lxml").find("table", class_="price-table")
            table = pd.read_html(str(soup).replace(",", "."), header=None)[0]
            return table
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID LOT DATA PERIOD TABLE", exc_info=True
            )
            return None

    def get_periods(self, lot):
        periods = list()
        table = self.period_table(lot)
        for p in range(len(table)):
            try:
                start = table.iloc[p, 1]
                end = table.iloc[p, 2]
                price = table.iloc[p, 3]
                if isinstance(price, str):
                    price = normalize_string(price)
                    price = round(float(price.replace(" ", "")), 2)
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception as e:
                logger.warning(f"{self.response.url}", exc_info=True)
                continue
        return periods

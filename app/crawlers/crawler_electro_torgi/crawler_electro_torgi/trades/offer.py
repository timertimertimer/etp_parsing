import re
from itertools import takewhile

import pandas as pd
from bs4 import BeautifulSoup

from app.utils import DateTimeHelper, logger


class Offer:
    def __init__(self, response):
        self.response = response

    def get_period_table(self):
        table = BeautifulSoup(
            self.response.xpath('//table[@id="stepsTable"]').get(), "lxml"
        )
        if table:
            df = pd.read_html(re.sub(r",", ".", str(table)))
            return df[0]
        return None

    @property
    def periods(self):
        check_value = 10000000000000000000000
        periods = list()
        td_periods = self.get_period_table()
        for p in range(len(td_periods)):
            start = td_periods.iloc[p][1]
            end = td_periods.iloc[p][2]
            price_ = td_periods.iloc[p][3]
            price_ = "".join(takewhile(lambda x: x != "р" and x != "Р", price_))
            try:
                if isinstance(price_, str):
                    price = "".join(re.sub(r"\s", "", price_)).replace(",", ".")
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.warning(
                        f"{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS"
                    )
                else:
                    check_value = price
            except Exception as e:
                logger.warning(
                    f"{self.response.url} Period Price - {price_} typeof - {type(price_)}"
                )
                return None
            try:
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception as e:
                continue
        return periods

    @property
    def start_date_trading(self):
        try:
            tbody_periods = self.get_period_table()
            return DateTimeHelper.smart_parse(tbody_periods.iloc[0][1]).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA START DATE REQUEST OFFER \n\n\n",
                e,
            )
            return None

    @property
    def end_date_trading(self):
        try:
            end = self.get_period_table().iloc[-1][2]
            return DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz)
        except Exception as ex:
            logger.warning(
                f"{self.response.url} :: ERROR START DATE REQUEST OFFER {ex}"
            )
            return None

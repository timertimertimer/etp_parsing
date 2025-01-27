import logging
import pandas as pd
from bs4 import BeautifulSoup

from general_utils import format_time_auction, normalize_string

logger = logging.getLogger(__name__)


class OfferParse:
    def __init__(self, response_):
        self.response = response_
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def start_date_trading(self, lot):
        try:
            table = self.period_table(lot)
            return format_time_auction(table.iloc[0, 1])
        except:
            logger.error(f'{self.response.url} :: INVALID LOT DATA START DATE REQUEST LOT')

    def end_date_trading(self, lot):
        try:
            table = self.period_table(lot)
            return format_time_auction(table.iloc[-1, 1])
        except:
            logger.error(f'{self.response.url} :: INVALID LOT DATA START DATE REQUEST LOT')

    def period_table(self, lot):
        try:
            soup = BeautifulSoup(lot, 'lxml').find('table', class_='price-table')
            table = pd.read_html(str(soup).replace(',', '.'), header=None)[0]
            return table
        except:
            logger.error(f'{self.response.url} :: INVALID LOT DATA PERIOD TABLE', exc_info=True)

    def get_periods(self, lot):
        """return dictionary(json object)"""
        periods = list()
        table = self.period_table(lot)
        for p in range(len(table)):
            try:
                start = table.iloc[p, 1]
                end = table.iloc[p, 2]
                price = table.iloc[p, 3]
                if isinstance(price, str):
                    price = normalize_string(price)
                    price = round(float(price.replace(' ', '')), 2)
                period = {
                    'start_date_requests': format_time_auction(start),
                    'end_date_requests': format_time_auction(end),
                    'end_date_trading': format_time_auction(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                logger.error(f'{self.response.url}', exc_info=True)
                ic(table)
                continue
        return periods

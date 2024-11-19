import re
import logging
from itertools import takewhile

from bs4 import BeautifulSoup as BS
import pandas as pd
from ..locators.locator_lot_offer import LoacatorOffer

from crawler_be_two_be.utils.work_with_text_and_number import get_lot_number, make_float, dedent_func, cut_lot_number, \
    delete_extra_symbols
from ..utils.working_with_time import format_time_auction

logger = logging.getLogger(__name__)


class OfferLotPage:
    def __init__(self, response_):
        self.response = response_
        self.loc = LoacatorOffer
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_period_table(self):
        """ get all tag <td> with periods data then create pandas df """
        try:
            td = self.soup.find('td', string=re.compile(r'ериоды стабильной цены лота', re.IGNORECASE))
            if td:
                td = td.findNext('td')
                df = pd.read_html(re.sub(r',', '.', str(td)), header=0)
                return df[0]
            else:
                logger.error(f'{self.response.url} :: ERROR PERIODS OFFER')
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA PERIOD TABLE {ex}')

    def return_periods(self):
        """return list object with all periods of lot(offer)"""
        check_value = 10000000000000000000000
        periods = list()
        td_periods = self.get_period_table()
        for p in range(len(td_periods)):
            start = td_periods.iloc[p][0]
            end = td_periods.iloc[p][1]
            price_ = td_periods.iloc[p][2]
            price_ = "".join(takewhile(lambda x: x != "р" and x != "Р", price_))
            try:
                if isinstance(price_, str):
                    price = ''.join(re.sub(r"\s", "", price_)).replace(',', '.')
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.critical(
                        f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS')
                else:
                    check_value = price
            except:
                logger.error(f'{self.response.url} Period Price - {price_} typeof - {type(price_)}')
                return None
            try:
                period = {
                    'start_date_requests': format_time_auction(start),
                    'end_date_requests': format_time_auction(end),
                    'end_date_trading': format_time_auction(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                continue
        return periods

    def start_date_request_offer(self):
        """ return start date request """
        try:
            start = self.get_period_table().iloc[0][0]
            return format_time_auction(start)
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR START DATE REQUEST OFFER {ex}')
            return None

    def end_date_request_offer(self):
        """ return end date request """
        try:
            end = self.get_period_table().iloc[-1][1]
            return format_time_auction(end)
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR START DATE REQUEST OFFER {ex}')
            return None

    def start_date_trading_offer(self):
        """ :return start date trading - the same as request """
        return self.start_date_request_offer()

    def end_date_trading_offer(self):
        """ :return end date trading - the same as end request """
        return self.end_date_request_offer()

    def lot_id_numbers(self):
        """ :return lot id """
        return ''.join(re.findall(r'\d+/?$', self.response.url)).replace('/', '').strip()
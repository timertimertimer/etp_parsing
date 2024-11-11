# -*- coding: utf-8 -*-
import logging
import re
from bs4 import BeautifulSoup as BS

from ..utils.work_with_text_and_number import dedent_func
from ..locators.trade_locator import LocatorAuction
from ..utils.working_with_time import *

logger = logging.getLogger(__name__)


class AuctionParse:
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorAuction

    def step_price(self, trading_number, lot_num: str):
        """:arg lot_number
           :return step price
            """
        trading_number = ''.join(trading_number)
        step_price = self.response.xpath(self.loc.step_price_loc.format(lot_num)).get()
        try:
            step_price = dedent_func(BS(str(step_price), features='lxml').get_text())
            pattern = r'^\d+\.\d{1,2}'
            if 'руб' in step_price:
                step_price = ''.join(re.split(r'руб', step_price, maxsplit=1)[0])
            clean_price = ''.join(filter(lambda x: x.isdigit() or x == ',', step_price)).replace(',', '.')
            match = ''.join(re.findall(pattern, clean_price))
            if match:
                return round(float(match), 2)
            else:
                if not re.match(r'\d{3,}-ОАЗФ', trading_number):
                    logger.error(
                        f'{self.response.url} :: INVALID DATA STEP PRICE - LOT {lot_num}')
                return None
        except:
            if not re.match(r'\d{3,}-ОАЗФ', trading_number):
                logger.error(
                    f'{self.response.url} :: LOT {lot_num} INVALID DATA - STEP PRICE - LOT {lot_num}')
            return None

    @property
    def start_date_request(self):
        """return start requests - format date"""
        try:
            td_date = self.response.xpath(self.loc.start_date_request_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text())
            return format_time(td_date.strip())
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST AUCTION/COMPETITION')
            return None

    @property
    def end_date_request(self):
        """return start requests - format date"""
        try:
            td_date = self.response.xpath(self.loc.end_date_request_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text())
            return format_time(td_date.strip())
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST AUCTION/COMPETITION')
            return None

    @property
    def start_date_trading(self):
        """return start requests - format date"""
        try:
            td_date = self.response.xpath(self.loc.start_date_trading_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text())
            return format_time(td_date.strip())
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA START DATE TRADING AUCTION/COMPETITION')
            return None

    @property
    def end_date_trading(self):
        """return start requests - format date"""
        try:
            td_date = self.response.xpath(self.loc.end_date_trading_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text())
            return format_time(td_date.strip())
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA END DATE TRADING AUCTION/COMPETITION')
            return None

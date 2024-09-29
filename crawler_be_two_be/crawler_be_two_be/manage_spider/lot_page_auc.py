import re
import logging
from bs4 import BeautifulSoup as BS
from itertools import takewhile
from ..locators.locator_lot_auc import LoacatorAuction

from crawler_be_two_be.utils.work_with_text_and_number import get_lot_number, make_float, dedent_func, cut_lot_number, \
    delete_extra_symbols

logger = logging.getLogger(__name__)


class AuctionLotPage:
    def __init__(self, response_):
        self.response = response_
        self.loc = LoacatorAuction
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @get_lot_number
    def get_lot_number(self):
        """ :return lot number """
        try:
            _h1 = self.soup.find("div", class_="s2").previous.strip()
            return _h1
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR LOT NUMBER {ex}')

    @delete_extra_symbols
    @cut_lot_number
    def get_short_name(self):
        """ :return short name of lot. Information in tag <h2> """
        try:
            h2 = self.soup.h2
            h2 = BS(str(h2).replace('<br/>', ' ').replace('<br>', ' '), features='lxml').get_text()
            text = dedent_func(h2.strip())
            return text
        except Exception as ex:
            logger.error(f'{self.response.url} ERROR SHORT NAME {ex}')
            return None

    def get_lot_info(self):
        """ :return lot info """
        try:
            td = self.soup.find('b', string=re.compile(r'Подробное описание продукции:', re.IGNORECASE))
            if td:
                td = td.parent
                lot_info = re.split(r':', td.get_text(), maxsplit=1)[-1].strip()
                return dedent_func(lot_info)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR LOT INFO {e}')
            return None

    def get_start_price_auc(self):
        """ :return start price auction """
        try:
            price = self.response.xpath(self.loc.start_price).get()
            price = BS(str(price), features='lxml').get_text().lower().replace(',', '.')
            price = "".join(takewhile(lambda x: x != "р" and x != "Р", price))
            price = re.sub(r'\s', '', price)
            return make_float(price)
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR WHILE GETTING START PRICE AUCTION {ex}')

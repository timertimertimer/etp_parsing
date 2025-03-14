import logging
import pathlib
import re

from bs4 import BeautifulSoup

from .config import data_origin, search_link

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')

    def get_total_lots(self):
        return int(self.soup.find('span', class_='search-category__counter').text)

    def get_trade_links(self):
        return [
            trade.find('a', class_='search-item__subject-link').get('href')
            for trade in self.soup.find_all('div', class_='search-item')
        ]

    def get_next_page_link(self):
        if next_link := self.soup.find('button', class_='pagination__btn--next'):
            return search_link + next_link.get('data-href')

    def download_general(self): ...

    def download_lot(self): ...

    @property
    def trading_id(self): ...

    @property
    def trading_link(self): ...

    @property
    def trading_number(self): ...

    @property
    def trading_type(self): ...

    @property
    def trading_form(self): ...

    @property
    def trading_org(self): ...

    @property
    def trading_org_contacts(self): ...

    @property
    def status(self): ...

    @property
    def category(self):
        ...

    @property
    def index(self):
        ...

    @property
    def address(self):
        ...

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    @property
    def lot_number(self): ...

    @property
    def short_name(self): ...

    @property
    def lot_info(self): ...

    @property
    def property_information(self): ...

    @property
    def start_date_requests(self): ...

    @property
    def end_date_requests(self): ...

    @property
    def start_date_trading(self): ...

    @property
    def end_date_trading(self): ...

    @property
    def start_price(self): ...

    @property
    def min_price(self):
        ...

    @property
    def deposit(self):
        ...

    @property
    def step_price(self): ...

    @property
    def periods(self): ...

    @property
    def quantity(self):
        ...

    @property
    def unit(self):
        ...

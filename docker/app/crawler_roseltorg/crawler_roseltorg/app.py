import logging
import pathlib
import re

from bs4 import BeautifulSoup

from .config import data_origin, search_link
from .locator import SerpLocator

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')

    def get_trading_cards(self):
        return self.soup.find_all('div', class_='search-item')

    def get_next_page_link(self):
        if next_link := self.soup.find('button', class_='pagination__btn--next'):
            return search_link + next_link.get('data-href')

    def download_general(self):
        ...

    def download_lot(self):
        ...

    def trading_id(self, trading_card: BeautifulSoup):
        id_ = trading_card.find('a', class_='search-item__lot')
        if id_:
            return id_.get_text(strip=True).split()[0]
        logger.error(f'{self.response.url} :: Trading id not found')

    def trading_link(self, trading_card: BeautifulSoup):
        return trading_card.find('a', class_='search-item__subject-link').get('href')

    def trading_number(self, trading_card: BeautifulSoup):
        return self.trading_id(trading_card)

    def trading_type(self, trading_card: BeautifulSoup):
        type_ = trading_card.find('a', class_='search-item__apply-value')
        if not type_:
            logger.error(f'{self.response.url} :: Trading type not found')
            return
        type_ = type_.get_text(strip=True)
        d = {
            'auction': [
                'аукцион с открытой формой подачи предложений', 'аукцион', 'аукцион на повышение',
                'аукцион на понижение', 'аукцион с закрытой формой подачи предложений',
            ],
            'offer': ['запрос предложений', 'продажа посредством публичного предложения'],
            'competition': [
                'конкурс', 'конкурс с открытой формой подачи предложений',
                'конкурс с закрытой формой подачи предложений',
            ],
        }
        for key, value in d.items():
            if type_.lower() in value:
                return key
        logger.error(f'{self.response.url} :: Unknown type - {type_}')

    def trading_form(self, trading_card: BeautifulSoup):
        return 'open'

    def trading_org(self, trading_card: BeautifulSoup):
        org = trading_card.find('a', class_='search-item__type-value')
        if org:
            return org.get_text(strip=True)
        logger.error(f'{self.response.url} :: Trading org not found')

    @property
    def trading_org_inn(self):
        return

    @property
    def trading_org_contacts(self):
        return

    @property
    def msg_number(self):
        return

    @property
    def case_number(self):
        return

    @property
    def debtor_inn(self):
        return

    @property
    def address(self):
        ...

    @property
    def arbit_manager(self):
        ...

    @property
    def arbit_manager_inn(self):
        ...

    @property
    def arbit_manager_org(self):
        ...

    @property
    def status(self):
        ...

    @property
    def categories(self):
        ...

    @property
    def lot_id(self): ...

    @property
    def lot_link(self): ...

    @property
    def lot_number(self):
        ...

    @property
    def short_name(self):
        ...

    @property
    def lot_info(self):
        ...

    @property
    def property_information(self):
        ...

    @property
    def start_date_requests(self):
        ...

    @property
    def end_date_requests(self):
        ...

    @property
    def start_date_trading(self):
        ...

    @property
    def end_date_trading(self):
        ...

    @property
    def start_price(self):
        ...

    @property
    def step_price(self):
        ...

    @property
    def periods(self):
        ...

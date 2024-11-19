import logging
from bs4 import BeautifulSoup

from ..utils.work_with_text_and_number import contains
from ..utils.working_with_time import format_time
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class AuctionParse:
    def __init__(self, response_):
        self.response = response_
        self.soup = BeautifulSoup(self.response.text, 'lxml')
        self.url = UrlConfig()

    @property
    def start_date_trading(self):
        date = self.soup.find('td', text=contains("Начало подачи предложений о цене имущества"))
        if date:
            return format_time(date.find_next_sibling('td').get_text())
        return None

    @property
    def end_date_trading(self):
        date = self.soup.find('td', text=contains("Дата и время подведения результатов торгов"))
        if date:
            return format_time(date.find_next_sibling('td').get_text())
        return None

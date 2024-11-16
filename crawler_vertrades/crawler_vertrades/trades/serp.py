import logging

from bs4 import BeautifulSoup as BS
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)

class SerpParse:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(self.response.text, 'lxml')
        self.url = UrlConfig()

    def get_trading_links(self):
        """ return set with unique links  """
        try:
            links = self.soup.find_all('a', class_='row-link')
            links = set([l.get('href') for l in links])
            return links
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA DURING FETCHING TRADING LINKS {e}', exc_info=True)
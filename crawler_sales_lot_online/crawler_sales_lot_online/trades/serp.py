from bs4 import BeautifulSoup as BS
import logging
import re

logger = logging.getLogger(__name__)


class SerpParse:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_trading_links(self):
        """ return set with unique links  """
        try:
            links = self.soup.find_all(href=re.compile(r'auctionLotProperty.xhtml\?parm=lot'))
            links = set([l.get('href') for l in links])
            return links
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA DURING FETCHING TRADING LINKS {e}', exc_info=True)

    def get_next_button(self):
        """ :return button (true) if exists or None if not exists """
        button = self.soup.find('a', id='formMain:clNext')
        if button:
            return button
        else:
            return None

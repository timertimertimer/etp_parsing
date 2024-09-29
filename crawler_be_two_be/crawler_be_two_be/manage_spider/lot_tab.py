import re
import logging
from bs4 import BeautifulSoup as BS
from ..locators.lot_tab_locator import LocatorLotTab
from ..utils.working_with_url import UrlConfig
from ..utils.config import _data_origin

logger = logging.getLogger(__name__)


class LotTab:
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorLotTab
        self.url = UrlConfig()
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_links_to_lot(self) -> list:
        """ :return list with links to lots"""
        try:
            links = self.response.xpath(self.loc.links_to_lots).getall()
            return links
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA WHILE GETTING LINKS TO LOTS {ex}')
            return list()

    def pagination_tab_lots(self) -> str or None:
        """ return link to next page or none """
        try:
            next_page = self.soup.find('a', string=re.compile('Следующая страница', re.IGNORECASE))
            page_link = next_page.get('href') if next_page else None
            if page_link:
                return self.url.url_join(_data_origin['b2b'], page_link)
        except Exception as e:
            logger.error(f'{self.response.url} ::{e}:: INVALID DATA LOT PAGINATION', exc_info=True)

